"""Barcha forma runnerlari uchun markaziy kuzatuv, tahlil va hisobot xizmati."""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from urllib.parse import urlsplit

import allure
from playwright.sync_api import Error as PlaywrightError

from tests.smoke.progress import emit_progress_event
from tests.smoke.smoke_reporting import safe_page_screenshot
from tests.smoke.test_forms.form_checks import (
    FORM_STATUSES,
    NOT_CHECKED,
    NOT_OPENED,
    OPENED_WITH_DEFECT,
    PASSED,
    TEST_BLOCKED,
    allowed_warning_text as _allowed_warning_text,
    assert_healthy_form_state as _assert_healthy_form_state,
    classify_form_failure,
    clean_text as _clean_text,
    evaluate_checks,
    normalize_allowed_warnings as _normalize_allowed_warnings,
    reason_description,
    title_verified as _title_verified,
)
from tests.smoke.test_forms.flow import (
    build_form_result,
    canonical_form_path,
    form_step_title,
    format_form_result,
    write_terminal_report,
)
from tests.smoke.test_forms.skipped_forms import skipped_form

ALERT_SELECTORS = (
    "#biruniAlertExtended:visible",
    "#biruniAlert:visible",
    "[role='alert']:visible",
    ".alert-danger:visible",
    "[role='dialog']:visible .alert-danger:visible",
    "[role='dialog']:visible [data-testid*='error' i]",
)

ALERT_WAIT_MS = 1200

MAX_PAGE_EVENTS = 20

CAPTURE_JS_ERROR_SCRIPT = """
(() => {
  if (window.__formMonitorCaptureInstalled) {
    return;
  }
  window.__formMonitorCaptureInstalled = true;
  window.__formMonitorCaptureErrors = [];
  window.__formMonitorCaptureCount = 0;
  window.__formMonitorResourceErrors = [];
  window.__formMonitorResourceCount = 0;
  window.__formMonitorPromiseRejections = [];
  window.__formMonitorPromiseRejectionCount = 0;
  const SAMPLE_LIMIT = 50;
  const withoutQuery = (value) => String(value || "").split("?")[0];
  window.addEventListener(
    "error",
    (event) => {
      // Capture fazasi resurs yuklanish xatosini ham beradi (img/script/link).
      // Ular JS exception emas va network kanali ularni allaqachon qamraydi,
      // shuning uchun alohida ro'yxatga tushadi.
      const target = event && event.target;
      if (target && target !== window && target.tagName) {
        window.__formMonitorResourceCount += 1;
        if (window.__formMonitorResourceErrors.length < SAMPLE_LIMIT) {
          window.__formMonitorResourceErrors.push(
            target.tagName + " " + withoutQuery(target.src || target.href)
          );
        }
        return;
      }
      const error = event && event.error;
      const message =
        (event && event.message) ||
        (error && error.message) ||
        (event && event.type) ||
        "noma'lum error eventi";
      let label = String(message);
      if (event && event.filename) {
        label += " @ " + withoutQuery(event.filename) + ":" + event.lineno;
      }
      window.__formMonitorCaptureCount += 1;
      if (window.__formMonitorCaptureErrors.length < SAMPLE_LIMIT) {
        window.__formMonitorCaptureErrors.push(label);
      }
    },
    true
  );
  window.addEventListener(
    "unhandledrejection",
    (event) => {
      const reason = event && event.reason;
      const message =
        (reason && reason.message) ||
        String(reason || "noma'lum promise rejection");
      window.__formMonitorPromiseRejectionCount += 1;
      if (window.__formMonitorPromiseRejections.length < SAMPLE_LIMIT) {
        window.__formMonitorPromiseRejections.push(message);
      }
    },
    true
  );
})();
"""

CAPTURE_READ_SCRIPT = """
({
  js: window.__formMonitorCaptureErrors || [],
  jsCount: window.__formMonitorCaptureCount || 0,
  resources: window.__formMonitorResourceErrors || [],
  resourceCount: window.__formMonitorResourceCount || 0,
  promiseRejections: window.__formMonitorPromiseRejections || [],
  promiseRejectionCount: window.__formMonitorPromiseRejectionCount || 0,
})
"""

CAPTURE_RESET_SCRIPT = """
(() => {
  window.__formMonitorCaptureErrors = [];
  window.__formMonitorCaptureCount = 0;
  window.__formMonitorResourceErrors = [];
  window.__formMonitorResourceCount = 0;
  window.__formMonitorPromiseRejections = [];
  window.__formMonitorPromiseRejectionCount = 0;
})()
"""

EMPTY_CAPTURE_SIGNALS = {
    "js_errors": [],
    "js_error_count": 0,
    "resource_errors": [],
    "resource_error_count": 0,
    "promise_rejections": [],
    "promise_rejection_count": 0,
}


def _safe_page_title(page):
    try:
        return _clean_text(page.title())
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def _safe_locator_visible(locator):
    """``is_visible`` kutmaydi — bu ataylab lahzalik surat."""
    try:
        return bool(locator.is_visible())
    except (PlaywrightError, AttributeError, TypeError):
        return False


def _safe_locator_count(locator):
    try:
        return int(locator.count())
    except (PlaywrightError, AttributeError, TypeError, ValueError):
        return 0


def _safe_inner_text(locator, *, timeout=750):
    try:
        return _clean_text(locator.inner_text(timeout=timeout))
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def _safe_visible_headings(page):
    try:
        headings = (
            page.get_by_role("heading")
            .filter(visible=True)
            .all_inner_texts()
        )
    except (PlaywrightError, AttributeError, TypeError):
        return []
    return [_clean_text(heading) for heading in headings if _clean_text(heading)]


def _failed_request_label(response):
    """4xx/5xx javobni qisqa yorliqqa aylantiradi; query string yozilmaydi."""
    try:
        status = int(response.status)
        if status < 400:
            return ""
        parts = urlsplit(str(response.url or ""))
    except (AttributeError, TypeError, ValueError):
        return ""
    return f"{status} {parts.netloc}{parts.path}"


def _js_error_label(error):
    message = _clean_text(getattr(error, "message", None) or error)
    return message[:300]


def _read_capture_signals(page):
    """A2 JS xatosi va observation-only browser signallarini o'qiydi.

    Capture-fazadagi JS exception A2 shell uchun effective ``JS_ERROR`` manbasi.
    Resurs xatolari va unhandled promise rejectionlar alohida kuzatiladi; ular
    hozircha status yoki ``usable`` qiymatiga ta'sir qilmaydi.
    """
    try:
        raw = page.evaluate(CAPTURE_READ_SCRIPT)
    except (PlaywrightError, AttributeError, TypeError):
        return dict(EMPTY_CAPTURE_SIGNALS)
    if not isinstance(raw, dict):
        return dict(EMPTY_CAPTURE_SIGNALS)

    def labels(values):
        return [text for text in (_clean_text(item)[:300] for item in values or []) if text]

    return {
        "js_errors": labels(raw.get("js")),
        "js_error_count": int(raw.get("jsCount") or 0),
        "resource_errors": labels(raw.get("resources")),
        "resource_error_count": int(raw.get("resourceCount") or 0),
        "promise_rejections": labels(raw.get("promiseRejections")),
        "promise_rejection_count": int(raw.get("promiseRejectionCount") or 0),
    }


def _reset_capture_signals(page):
    try:
        page.evaluate(CAPTURE_RESET_SCRIPT)
    except (PlaywrightError, AttributeError, TypeError):
        pass


def _wait_for_any_visible(page, selectors, *, timeout):
    """Birinchi ko'rinadigan selektorni kutadi; hech biri chiqmasa jim qaytadi."""
    try:
        page.locator(", ".join(selectors)).first.wait_for(
            state="visible",
            timeout=timeout,
        )
    except (PlaywrightError, AttributeError, TypeError):
        return


def _visible_error_text(page):
    """Faqat aniq error komponentlarini o'qiydi; oddiy dialog xato hisoblanmaydi.

    Server validatsiya xatosi heading chiqqandan keyin 300-500 ms kechikib
    kelishi mumkin, shuning uchun lahzalik surat emas — alert kutiladi.
    """
    _wait_for_any_visible(page, ALERT_SELECTORS, timeout=ALERT_WAIT_MS)
    for selector in ALERT_SELECTORS:
        locator = page.locator(selector).first
        if not _safe_locator_visible(locator):
            continue
        text = _safe_inner_text(locator, timeout=500)
        if text:
            return text
    return ""


def _generic_a2_content_ready(page):
    main = page.locator("main").first
    if not _safe_locator_visible(main):
        return False
    if _safe_inner_text(main):
        return True
    try:
        child = main.locator(":scope > *").filter(visible=True).first
    except (PlaywrightError, AttributeError, TypeError):
        return False
    return _safe_locator_visible(child)


def capture_form_state(page, *, ready=None):
    """URL/title/content/error signallarini false-pass bermaydigan tarzda o'qiydi.

    ``js_errors`` bo'sh boshlanadi — u sahifadan o'qilmaydi, listener orqali
    yig'iladi va ``FormMonitor._capture_state`` uni shu yerga qo'shadi. Bitta
    dict bo'lgani uchun klassifikatsiya, ``checks`` va assertlar bir manbadan
    o'qiydi.

    ``capture_signals`` shu yerning o'zida ``page.evaluate`` orqali o'qiladi.
    ``FormMonitor._capture_state`` A2 shell uchun capture JS exceptionlarini,
    legacy shell uchun esa Playwright ``pageerror`` kanalini effective manba
    sifatida tanlaydi.
    """
    actual_url = getattr(page, "url", "") or ""
    ready_visible = False

    if ready:
        ready_visible = _safe_locator_visible(page.locator(ready).first)
        content_ready = ready_visible
    elif "/a2/" in actual_url:
        content_ready = _generic_a2_content_ready(page)
    else:
        content_ready = any(
            _safe_locator_visible(page.locator(selector).first)
            for selector in ("b-page:visible", ".subheader:visible")
        )

    loader_visible = any(
        _safe_locator_visible(page.locator(selector).first)
        for selector in (
            ".block-ui-overlay:visible",
            ".smt-skeleton:visible",
        )
    )
    busy_visible_count = _safe_locator_count(
        page.locator("[aria-busy='true']:visible")
    )

    document_title = _safe_page_title(page)
    is_a2 = "/a2/" in actual_url
    title_candidates = [document_title] if is_a2 and document_title else []
    if not is_a2:
        title_candidates = _safe_visible_headings(page)
    actual_form_title = " | ".join(title_candidates) or document_title

    return {
        "actual_url": actual_url,
        "actual_title": actual_form_title,
        "js_errors": [],
        "capture_signals": _read_capture_signals(page),
        "document_title": document_title,
        "title_candidates": title_candidates,
        "title_source": "document" if is_a2 else "visible_heading",
        "canonical_path": canonical_form_path(actual_url),
        "visible_error": _visible_error_text(page),
        "ready_required": bool(ready),
        "ready_visible": ready_visible,
        "content_ready": content_ready,
        "loader_visible": loader_visible,
        "busy_visible": busy_visible_count > 0,
        "busy_visible_count": busy_visible_count,
    }


def form_case(
    *,
    number,
    filial,
    navbar_tab,
    menu_column,
    menu_item,
    title,
    expected_path,
    page_links=None,
    action=None,
    add_icon=False,
    ready=None,
    shell=None,
    section=None,
    screenshot_mask=None,
    allowed_warnings=None,
):
    """Monitor uchun barcha runnerlarda bir xil planned-case yozuvini yaratadi."""
    if not isinstance(number, int) or number < 1:
        raise ValueError(f"Forma raqami musbat int bo'lishi kerak: {number!r}")
    for field_name, value in (
        ("filial", filial),
        ("navbar_tab", navbar_tab),
        ("menu_item", menu_item),
        ("title", title),
        ("expected_path", expected_path),
    ):
        if not _clean_text(value):
            raise ValueError(f"Forma case uchun {field_name} majburiy")
    if action is not None and add_icon:
        raise ValueError("Forma case bir vaqtda action va add_icon ishlata olmaydi")
    case = {
        "number": number,
        "filial": filial,
        "navbar_tab": navbar_tab,
        "menu_column": menu_column,
        "menu_item": menu_item,
        "title": title,
        "expected_path": expected_path,
        "page_links": list(page_links or []),
        "action": action,
        "add_icon": bool(add_icon),
        "ready": ready,
        "shell": shell,
        "section": section,
        "allowed_warnings": _normalize_allowed_warnings(allowed_warnings),
    }
    if screenshot_mask is not None:
        case["screenshot_mask"] = screenshot_mask
    return case


def build_form_case_plan(
    definitions,
    *,
    start_number,
    filial,
    navbar_tab=None,
    shell=None,
    section=None,
):
    """Skip registry'ni chiqarib, yagona ``FormCase`` rejasini yaratadi."""
    return build_form_case_inventory(
        definitions,
        start_number=start_number,
        filial=filial,
        navbar_tab=navbar_tab,
        shell=shell,
        section=section,
    )["planned"]


def build_form_case_inventory(
    definitions,
    *,
    start_number,
    filial,
    navbar_tab=None,
    shell=None,
    section=None,
):
    """Aktiv va ataylab skip qilingan formalarni bitta inventoryda qaytaradi."""
    planned = []
    skipped = []
    for definition in definitions:
        links = list(definition.get("page_links") or [])
        title = (
            definition.get("title")
            or (links[-1] if links else None)
            or definition.get("action")
            or definition["menu_item"]
        )
        expected_path = definition.get("expected_path") or definition.get("path")
        skip_metadata = skipped_form(definition)
        if skip_metadata:
            skipped.append(
                {
                    "filial": filial,
                    "navbar_tab": definition.get("navbar_tab") or navbar_tab,
                    "menu_column": definition.get("menu_column"),
                    "menu_item": definition["menu_item"],
                    "title": title,
                    "expected_path": expected_path,
                    "section": definition.get("section") or section,
                    "reason": skip_metadata["reason"],
                }
            )
            continue
        planned.append(
            form_case(
                number=start_number + len(planned),
                filial=filial,
                navbar_tab=definition.get("navbar_tab") or navbar_tab,
                menu_column=definition.get("menu_column"),
                menu_item=definition["menu_item"],
                title=title,
                expected_path=expected_path,
                page_links=links,
                action=definition.get("action"),
                add_icon=definition.get("add_icon", False),
                ready=definition.get("ready"),
                shell=definition.get("shell") or shell,
                section=definition.get("section") or section,
                screenshot_mask=definition.get("screenshot_mask"),
                allowed_warnings=definition.get("allowed_warnings"),
            )
        )
    return {"planned": planned, "skipped": skipped}


def _status_counts(results):
    counts = Counter(result.get("status") for result in results)
    for status in FORM_STATUSES:
        counts.setdefault(status, 0)
    return counts


def _monitor_metrics(results):
    return {
        "started": sum(bool(result.get("test_started")) for result in results),
        "completed": sum(bool(result.get("test_completed")) for result in results),
        "page_reached": sum(bool(result.get("page_reached")) for result in results),
        "validation_completed": sum(
            bool(result.get("validation_completed")) for result in results
        ),
        "validation_passed": sum(
            bool(result.get("validation_passed")) for result in results
        ),
        "usable": sum(bool(result.get("usable")) for result in results),
    }


def build_monitor_payload(
    *,
    suite_name,
    planned_count,
    results,
    blockers,
    skipped_cases=None,
):
    """Allure JSON va boshqa consumerlar uchun versionlangan yagona payload."""
    skipped = [dict(case) for case in (skipped_cases or [])]
    return {
        "schema_version": 3,
        "suite": suite_name,
        "planned": planned_count,
        "inventory": {
            "total": planned_count + len(skipped),
            "active": planned_count,
            "intentional_skips": len(skipped),
        },
        "skipped": skipped,
        "metrics": _monitor_metrics(results),
        "counts": dict(_status_counts(results)),
        "blockers": list(blockers),
        "results": list(results),
    }


def _known_request_noise(label):
    """Tasdiqlangan, observation-only request shovqinini bucketlaydi."""
    if "/page/tour/" in label:
        return "legacy tour 404"
    if "/a2/assets/i18n/kernel-overlay/" in label:
        return "A2 optional i18n 404"
    return ""


def _known_resource_noise(label):
    """URLsiz browser resource eventlarini bitta tushunarli bucketka yig'adi."""
    if label.strip() in {"SOURCE", "IMG https://smartup.online/"}:
        return "empty resource source"
    return ""


def _page_event_lines(results):
    """Effective JS kanalini va actionable network signallarini ko'rsatadi."""
    rows = []
    known_noise = Counter()
    for result in results:
        checks = result.get("checks") or {}
        actionable_requests = []
        for label in checks.get("failed_requests") or []:
            bucket = _known_request_noise(label)
            if bucket:
                known_noise[bucket] += 1
            else:
                actionable_requests.append(label)
        if checks.get("js_error_count") or actionable_requests:
            rows.append((result, checks, actionable_requests))

    if not rows and not known_noise:
        return []
    lines = [
        "BRAUZER JS VA NETWORK SIGNALLARI",
        "-" * 88,
        "JS uchun shellga mos yagona effective kanal ishlatiladi; network "
        "signallari statusga ta'sir qilmaydi.",
    ]
    for result, checks, actionable_requests in rows:
        lines.append(
            f"• {result['number']:03d} | {result['title']} | {result['status']}"
        )
        if checks.get("js_error_count"):
            source = checks.get("js_error_source") or "unknown"
            lines.append(
                f"    JS xatolari ({checks['js_error_count']}, manba={source}):"
            )
            for message in checks.get("js_errors") or []:
                lines.append(f"      - {message}")
        if actionable_requests:
            lines.append(
                f"    Tekshirilishi kerak bo'lgan so'rovlar ({len(actionable_requests)}):"
            )
            for label in actionable_requests:
                lines.append(f"      - {label}")
    if known_noise:
        lines.append("    Ma'lum request shovqini (agregatsiya):")
        for bucket, count in sorted(known_noise.items()):
            lines.append(f"      - {bucket}: {count}")
    lines.append("")
    return lines


def _observation_signal_lines(results):
    """Statusga ta'sir qilmaydigan resource va promise signallarini ko'rsatadi."""
    rows = []
    known_noise = Counter()
    for result in results:
        checks = result.get("checks") or {}
        actionable_resources = []
        for label in checks.get("capture_resource_errors") or []:
            bucket = _known_resource_noise(label)
            if bucket:
                known_noise[bucket] += 1
            else:
                actionable_resources.append(label)
        promise_rejections = list(checks.get("promise_rejections") or [])
        if actionable_resources or promise_rejections:
            rows.append(
                (result, checks, actionable_resources, promise_rejections)
            )

    if not rows and not known_noise:
        return []
    lines = [
        "BROWSER KUZATUV SIGNALLARI (statusga ta'sir qilmaydi)",
        "-" * 88,
        "Resource yuklanish xatolari va unhandled promise rejectionlar "
        "diagnostika uchun saqlanadi; raw JSON to'liq inventarni beradi.",
    ]
    for result, checks, resources, promises in rows:
        lines.append(
            f"• {result['number']:03d} | {result['title']} | {result['status']} | "
            f"shell={result.get('shell') or '—'}"
        )
        if resources:
            lines.append(
                f"    Tekshirilishi kerak bo'lgan resource xatolari ({len(resources)}):"
            )
            for message in resources:
                lines.append(f"      - {message}")
        if promises:
            count = checks.get("promise_rejection_count") or len(promises)
            lines.append(f"    Unhandled promise rejectionlar ({count}):")
            for message in promises:
                lines.append(f"      - {message}")
    if known_noise:
        lines.append("    Ma'lum resource shovqini (agregatsiya):")
        for bucket, count in sorted(known_noise.items()):
            lines.append(f"      - {bucket}: {count}")
    lines.append("")
    return lines


def _duration_lines(results, *, slowest_count=5):
    """Sekinlashuvni ko'rsatadi: forma ochilsa ham 2 barobar sekin bo'lishi mumkin.

    Faqat testi boshlangan formalar hisoblanadi — ``TEST_BLOCKED`` yozuvidagi
    ``duration_ms`` precondition vaqti, forma ochilish vaqti emas.
    """
    timed = [
        result
        for result in results
        if result.get("test_started") and result.get("duration_ms") is not None
    ]
    if not timed:
        return []
    total_ms = sum(result["duration_ms"] for result in timed)
    slowest = sorted(timed, key=lambda result: result["duration_ms"], reverse=True)
    lines = [
        "FORMA DAVOMIYLIGI",
        "-" * 88,
        f"Jami                   : {total_ms / 1000:.1f} s ({len(timed)} forma)",
        f"O'rtacha bitta formaga : {total_ms / len(timed) / 1000:.1f} s",
        f"Eng sekin {min(slowest_count, len(slowest))} forma:",
    ]
    for position, result in enumerate(slowest[:slowest_count], start=1):
        lines.append(
            f"  {position}. {result['number']:03d} | {result['title']} | "
            f"{result['duration_ms'] / 1000:.1f} s"
        )
    lines.append("")
    return lines


def render_monitor_summary(
    *,
    suite_name,
    planned_count,
    results,
    blockers,
    skipped_cases=None,
):
    """Terminal va Allure uchun bir xil, takrorsiz markaziy hisobot yasaydi."""
    counts = _status_counts(results)
    metrics = _monitor_metrics(results)
    skipped = [dict(case) for case in (skipped_cases or [])]
    lines = [
        "FORMA MARKAZIY MONITORING HISOBOTI",
        "=" * 88,
        f"Suite: {suite_name}",
        f"Inventory jami         : {planned_count + len(skipped)}",
        f"Rejalashtirilgan       : {planned_count}",
        f"Ataylab skip qilingan  : {len(skipped)}",
        f"Testi boshlangan       : {metrics['started']}",
        f"Tekshiruvi yakunlangan : {metrics['completed']}",
        f"Target URLga yetilgan  : {metrics['page_reached']}",
        f"Validatsiya bajarilgan : {metrics['validation_completed']}",
        f"Validatsiyadan o'tgan  : {metrics['validation_passed']}",
        f"Foydalanishga tayyor   : {metrics['usable']}",
        f"✅ Muvaffaqiyatli       : {counts[PASSED]}",
        f"⚠️ Ochildi, nuqson     : {counts[OPENED_WITH_DEFECT]}",
        f"❌ Ochilmadi            : {counts[NOT_OPENED]}",
        f"⛔ Test bloklandi       : {counts[TEST_BLOCKED]}",
        f"⬜ Tekshirilmadi         : {counts[NOT_CHECKED]}",
        "",
    ]

    if skipped:
        lines.extend(["ATAYLAB SKIP QILINGAN FORMALAR", "-" * 88])
        for case in skipped:
            lines.append(
                f"⬜ {case.get('title') or case.get('menu_item') or '—'} | "
                f"Path: {case.get('expected_path') or '—'} | "
                f"Sabab: {case.get('reason') or '—'}"
            )
        lines.append("")

    issues = [
        result
        for result in results
        if result.get("status") in {
            OPENED_WITH_DEFECT,
            NOT_OPENED,
            TEST_BLOCKED,
        }
    ]
    if issues:
        lines.extend(["ASOSIY MUAMMOLAR", "-" * 88])
        for result in issues:
            lines.append(format_form_result(result))
            lines.append("")

    title_unverified = [
        result
        for result in results
        if result.get("checks") and not result["checks"].get("title_verified")
    ]
    if title_unverified:
        lines.extend(["TITLE TAQQOSLANMAGAN FORMALAR", "-" * 88])
        lines.append(
            "Sabab: sahifada ko'rinadigan heading topilmadi — title tekshiruvi "
            "o'tkazib yuborildi."
        )
        for result in title_unverified:
            lines.append(
                f"⚠️ {result['number']:03d} | {result['filial']} | "
                f"{result['track']} | {result['title']}"
            )
        lines.append("")

    not_checked = [result for result in results if result.get("status") == NOT_CHECKED]
    if not_checked:
        lines.extend(["TEKSHIRILMAGAN FORMALAR", "-" * 88])
        blocker_reason = not_checked[0].get("reason_summary") or "Tekshiruv boshlanmadi."
        lines.append(f"Umumiy sabab: {blocker_reason}")
        for result in not_checked:
            lines.append(
                f"⬜ {result['number']:03d} | {result['filial']} | "
                f"{result['track']} | {result['title']}"
            )
        lines.append("")

    unattached_blockers = [
        blocker for blocker in blockers if blocker.get("affected_case_number") is None
    ]
    if unattached_blockers:
        lines.extend(["SUITE BLOKERLARI", "-" * 88])
        for blocker in unattached_blockers:
            lines.append(
                f"⛔ {blocker['operation']} | {blocker['reason_code']} | "
                f"{blocker['detail']}"
            )
        lines.append("")

    lines.extend(_page_event_lines(results))
    lines.extend(_observation_signal_lines(results))
    lines.extend(_duration_lines(results))

    started_results = [result for result in results if result.get("test_started")]
    if started_results:
        lines.extend(["BOSHLANGAN FORMA TESTLARI", "-" * 88])
        for result in started_results:
            lines.append(
                f"{result.get('status_icon', '•')} {result['number']:03d} | "
                f"{result['title']} | {result['status']} | "
                f"Sabab: {result.get('reason_code') or '—'} | "
                f"URL: {result.get('actual_url') or '—'}"
            )
    return "\n".join(lines).rstrip()


def _shell_from_url(url, fallback=None):
    if "/a2/" in (url or ""):
        return "a2"
    if url:
        return "legacy"
    return fallback


class FormMonitor:
    """Forma suite'ini boshidan oxirigacha kuzatuvchi markaziy xizmat."""

    def __init__(
        self,
        page,
        *,
        suite_name,
        planned_cases,
        terminal_reporter=None,
        progress_runner="test_0_forms_runner.py",
        progress_test_id="forms",
        skipped_cases=None,
    ):
        self.page = page
        self.suite_name = suite_name
        self.planned_cases = [dict(case) for case in planned_cases]
        self.skipped_cases = [dict(case) for case in (skipped_cases or [])]
        self.terminal_reporter = terminal_reporter
        self.progress_runner = progress_runner
        self.progress_test_id = progress_test_id
        self.results = []
        self.blockers = []
        self.blocked = False
        self._results_by_number = {}
        self.js_errors = []
        self.failed_requests = []
        self.js_error_count = 0
        self.failed_request_count = 0

        numbers = [case["number"] for case in self.planned_cases]
        duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
        if duplicates:
            raise ValueError(f"Takrorlangan forma raqami bor: {duplicates}")

        self._install_page_listeners()

    def _install_page_listeners(self):
        """``pageerror`` va 4xx/5xx javoblarni yig'ishni yoqadi.

        JS xatosi formani ``JS_ERROR`` nuqsoni qiladi; network signallari esa
        raw payload uchun qayd qilinadi va human hisobotda agregatsiya qilinadi.

        Diqqat: ``pageerror`` **faqat legacy shell'da** ishlaydi. A2 ilovasi
        global ``error`` eventida ``preventDefault()`` chaqiradi, shuning uchun
        A2 formalarida bu kanal ko'r — batafsil `ui-patterns.md`.
        """
        try:
            self.page.on("pageerror", self._record_js_error)
            self.page.on("response", self._record_failed_request)
        except (AttributeError, TypeError):
            self._listeners_installed = False
            return
        self._listeners_installed = True
        self._install_capture_js_error_script()

    def _install_capture_js_error_script(self):
        """A2 uchun canonical capture-fazali JS xato kuzatuvini yoqadi.

        ``add_init_script`` ni olib tashlashning Playwright'da yo'li yo'q, va
        uch suite bitta ``page`` fixture'ni bo'lishadi — shuning uchun har
        ``FormMonitor.__init__`` bu funksiyani qayta chaqiradi. Takroriy
        listener ro'yxatga olinishining oldini skriptning o'zidagi
        ``__formMonitorCaptureInstalled`` bayrog'i oladi: har document yangi
        ``window`` bilan boshlanadi, birinchi qo'shilgan skript bayroqni
        o'rnatadi, qolganlari jim chiqib ketadi.
        """
        try:
            self.page.add_init_script(CAPTURE_JS_ERROR_SCRIPT)
        except (PlaywrightError, AttributeError, TypeError):
            pass

    def _remove_page_listeners(self):
        if not getattr(self, "_listeners_installed", False):
            return
        try:
            self.page.remove_listener("pageerror", self._record_js_error)
            self.page.remove_listener("response", self._record_failed_request)
        except (AttributeError, TypeError, ValueError, KeyError):
            pass
        self._listeners_installed = False

    def _record_js_error(self, error):
        label = _js_error_label(error)
        if not label:
            return
        self.js_error_count += 1
        if len(self.js_errors) < MAX_PAGE_EVENTS:
            self.js_errors.append(label)

    def _record_failed_request(self, response):
        label = _failed_request_label(response)
        if not label:
            return
        self.failed_request_count += 1
        if len(self.failed_requests) < MAX_PAGE_EVENTS:
            self.failed_requests.append(label)

    def _reset_page_events(self):
        """Har case/precondition o'z oynasini oladi — signal qo'shnisiga o'tmaydi."""
        self.js_errors = []
        self.failed_requests = []
        self.js_error_count = 0
        self.failed_request_count = 0
        _reset_capture_signals(self.page)

    def update_filial(self, placeholder, actual_name):
        for case in self.planned_cases + self.skipped_cases:
            if case.get("filial") == placeholder:
                case["filial"] = actual_name

    def _planned_case(self, number):
        return next(
            (case for case in self.planned_cases if case["number"] == number),
            None,
        )

    def planned_case(self, number):
        """Runtime'da actual filial bilan yangilangan planned case'ni qaytaradi."""
        case = self._planned_case(number)
        if case is None:
            raise KeyError(f"Planned forma topilmadi: {number}")
        return case

    def cases(self, *, section=None):
        """Monitor ichidagi aktual case'larni raqam tartibida qaytaradi."""
        cases = self.planned_cases
        if section is not None:
            cases = [case for case in cases if case.get("section") == section]
        return sorted(cases, key=lambda case: case["number"])

    def _write_live_line(self, line):
        if self.terminal_reporter is not None:
            self.terminal_reporter.write_line(line)
        else:
            print(line, flush=True)

    def _append_result(self, result):
        number = result["number"]
        if number in self._results_by_number:
            raise RuntimeError(f"Forma natijasi ikki marta yozilmoqda: {number:03d}")
        self._results_by_number[number] = result
        self.results.append(result)
        reason = result.get("reason_summary") or result.get("reason_code")
        reason_part = f" | Sabab: {reason}" if reason else ""
        line = (
            f"[FORM MONITOR] {number:03d}/{len(self.planned_cases):03d} "
            f"{result.get('status_icon', '•')} {result.get('status')} | "
            f"Forma: {result['title']} | Filial: {result['filial']}"
            f"{reason_part}"
        )
        self._write_live_line(line)
        emit_progress_event(
            event="form_result",
            group="Forms group",
            runner=self.progress_runner,
            test_id=self.progress_test_id,
            title=self.suite_name,
            display=(
                f"{self.suite_name}: {number:03d}/{len(self.planned_cases):03d} "
                f"{result['title']} — {result['status']}"
            ),
            error_type=result.get("reason_code") or None,
            message=reason or None,
            writer=(
                self.terminal_reporter.write_line
                if self.terminal_reporter is not None
                else None
            ),
            form_number=number,
            form_total=len(self.planned_cases),
            form_status=result["status"],
        )
        return result

    def _attach_case_evidence(self, result, *, case=None):
        safe_title = re.sub(r"[^\w.-]+", "-", result["title"], flags=re.UNICODE).strip("-")
        screenshot_name = (
            f"{result['number']:03d}-{safe_title}-{result['status']}-"
            f"{result.get('reason_code') or 'UNKNOWN'}-evidence"
        )
        try:
            allure.attach(
                safe_page_screenshot(
                    self.page,
                    full_page=True,
                    mask_profile=(case or {}).get("screenshot_mask"),
                ),
                name=screenshot_name,
                attachment_type=allure.attachment_type.PNG,
            )
            result["screenshot"] = screenshot_name
            result["screenshot_redacted"] = True
        except (PlaywrightError, OSError, ValueError, AttributeError, TypeError) as exc:
            result["screenshot_error"] = _clean_text(exc)
        allure.attach(
            format_form_result(result),
            name=f"{result['number']:03d} | {result['title']} | monitoring tafsilotlari",
            attachment_type=allure.attachment_type.TEXT,
        )

    @staticmethod
    def _checks(case, state):
        hard_checks = evaluate_checks(case, state)
        path_matches = hard_checks["url"]["passed"]
        allowed_warning = _allowed_warning_text(case, state)
        visible_error = hard_checks["application_error"]["actual"]
        js_errors = list(state.get("js_errors") or [])
        capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
        usable = (
            path_matches
            and bool(state.get("content_ready"))
            and not bool(state.get("loader_visible"))
            and not bool(visible_error)
            and not js_errors
        )
        return {
            "js_errors": js_errors,
            "js_error_count": int(state.get("js_error_count") or 0),
            "js_error_source": state.get("js_error_source") or "",
            "capture_js_errors": list(
                capture.get("js_errors") or []
            )[:MAX_PAGE_EVENTS],
            "capture_js_error_count": int(capture.get("js_error_count") or 0),
            "capture_resource_errors": list(
                capture.get("resource_errors") or []
            )[:MAX_PAGE_EVENTS],
            "capture_resource_error_count": int(
                capture.get("resource_error_count") or 0
            ),
            "promise_rejections": list(
                capture.get("promise_rejections") or []
            )[:MAX_PAGE_EVENTS],
            "promise_rejection_count": int(
                capture.get("promise_rejection_count") or 0
            ),
            "url_matches": path_matches,
            "title_matches": hard_checks["title"]["passed"],
            "title_verified": _title_verified(case, state),
            "title_source": state.get("title_source") or "",
            "document_title": state.get("document_title") or "",
            "content_ready": hard_checks["content_ready"]["passed"],
            "ready_required": bool(state.get("ready_required")),
            "ready_visible": bool(state.get("ready_visible")),
            "loader_visible": not hard_checks["loader"]["passed"],
            "busy_visible": bool(state.get("busy_visible")),
            "busy_visible_count": int(state.get("busy_visible_count") or 0),
            "visible_error": visible_error,
            "allowed_warning": allowed_warning,
            "usable": usable,
        }

    def _capture_state(self, case=None):
        """Shellga mos yagona effective JS kanalini sahifa holatiga qo'shadi."""
        state = capture_form_state(self.page, ready=(case or {}).get("ready"))
        capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
        if "/a2/" in state.get("actual_url", ""):
            state["js_errors"] = list(capture["js_errors"])
            state["js_error_count"] = capture["js_error_count"]
            state["js_error_source"] = "capture"
        else:
            state["js_errors"] = list(self.js_errors)
            state["js_error_count"] = self.js_error_count
            state["js_error_source"] = "pageerror"
        return state

    def _case_checks(self, case, state):
        """Sof holat tekshiruvlariga cheklanmagan hisoblar va network signalini qo'shadi.

        JS xatolari ``state`` orqali ``_checks`` ga yetib boradi va statusga
        ta'sir qiladi; network signallari esa hozir faqat qayd qilinadi.
        """
        checks = self._checks(case, state)
        checks["failed_requests"] = list(self.failed_requests)
        checks["failed_request_count"] = self.failed_request_count
        return checks

    def _failure_result(
        self,
        *,
        case,
        stage,
        exc,
        started_at,
        test_started,
        test_completed,
        state=None,
    ):
        state = state or self._capture_state(case)
        detail = _clean_text(exc)
        analysis = classify_form_failure(
            case=case,
            stage=stage,
            detail=detail,
            state=state,
        )
        checks = self._case_checks(case, state)
        result = build_form_result(
            number=case["number"],
            filial=case["filial"],
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            menu_item=case["menu_item"],
            title=case["title"],
            expected_path=case.get("expected_path"),
            actual_url=state["actual_url"],
            page_links=case.get("page_links"),
            action=case.get("action"),
            add_icon=case.get("add_icon", False),
            detail=detail,
            status=analysis["status"],
            reason_code=analysis["reason_code"],
            reason_summary=analysis["reason_summary"],
            failed_stage=stage,
            expected_title=case["title"],
            actual_title=state["actual_title"],
            opened=analysis["opened"],
            page_reached=(checks["url_matches"] if test_started else False),
            test_started=test_started,
            test_completed=test_completed,
            validation_completed=(stage == "validation" and test_started),
            validation_passed=False,
            usable=(checks["usable"] if test_started else False),
            checks=checks,
            shell=_shell_from_url(state["actual_url"], case.get("shell")),
            suite=self.suite_name,
            duration_ms=int((time.monotonic() - started_at) * 1000),
        )
        return self._append_result(result)

    def run_case(self, case, *, navigate, validate):
        """Bitta formani kuzatadi; kutilgan UI xatosidan keyin davom etadi."""
        if self.blocked:
            return None
        case = dict(self.planned_case(case["number"]))
        self._reset_page_events()
        started_at = time.monotonic()
        stage = "navigation"
        failure_result = None
        state = None
        step_title = form_step_title(
            number=case["number"],
            filial=case["filial"],
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            title=case["title"],
        )

        try:
            with allure.step(step_title):
                try:
                    navigate()
                    stage = "validation"
                    with allure.step(
                        f"Tekshiruv | Forma: {case['title']} | "
                        f"Kutilgan URL: {case.get('expected_path') or '—'}"
                    ):
                        validate()
                        state = self._capture_state(case)
                        _assert_healthy_form_state(case, state)
                except (AssertionError, PlaywrightError) as exc:
                    failure_result = self._failure_result(
                        case=case,
                        stage=stage,
                        exc=exc,
                        started_at=started_at,
                        test_started=True,
                        test_completed=True,
                        state=state,
                    )
                    self._attach_case_evidence(failure_result, case=case)
                    raise

                checks = self._case_checks(case, state)
                result = build_form_result(
                    number=case["number"],
                    filial=case["filial"],
                    navbar_tab=case["navbar_tab"],
                    menu_column=case.get("menu_column"),
                    menu_item=case["menu_item"],
                    title=case["title"],
                    expected_path=case.get("expected_path"),
                    actual_url=state["actual_url"],
                    page_links=case.get("page_links"),
                    action=case.get("action"),
                    add_icon=case.get("add_icon", False),
                    status=PASSED,
                    reason_code="",
                    failed_stage="",
                    expected_title=case["title"],
                    actual_title=state["actual_title"],
                    opened=True,
                    page_reached=True,
                    test_started=True,
                    test_completed=True,
                    validation_completed=True,
                    validation_passed=True,
                    usable=True,
                    checks=checks,
                    shell=_shell_from_url(state["actual_url"], case.get("shell")),
                    suite=self.suite_name,
                    duration_ms=int((time.monotonic() - started_at) * 1000),
                )
                self._append_result(result)
                with allure.step(f"Natija: OCHILDI | Haqiqiy URL: {state['actual_url']}"):
                    pass
        except (AssertionError, PlaywrightError):
            return failure_result

        return result

    def precondition(self, operation, action, *, affected_case_number=None):
        """Login/filial/shell kabi suite amallarini forma xatosidan ajratadi."""
        if self.blocked:
            return None
        self._reset_page_events()
        started_at = time.monotonic()
        value = None
        try:
            with allure.step(f"Suite precondition | {operation}"):
                try:
                    value = action()
                except (AssertionError, PlaywrightError) as exc:
                    self._block_suite(
                        operation=operation,
                        exc=exc,
                        affected_case_number=affected_case_number,
                        started_at=started_at,
                    )
                    raise
        except (AssertionError, PlaywrightError):
            return None
        return value

    def _block_suite(self, *, operation, exc, affected_case_number, started_at):
        self.blocked = True
        case = self._planned_case(affected_case_number) if affected_case_number else None
        if case is None:
            case = next(
                (
                    planned
                    for planned in self.planned_cases
                    if planned["number"] not in self._results_by_number
                ),
                None,
            )
            if case is not None:
                affected_case_number = case["number"]
        state = self._capture_state(case)
        analysis_case = dict(case or {})
        analysis_case["failed_operation"] = operation
        analysis = classify_form_failure(
            case=analysis_case,
            stage="suite_precondition",
            detail=exc,
            state=state,
        )
        blocker = {
            "operation": operation,
            "reason_code": analysis["reason_code"],
            "detail": _clean_text(exc),
            "actual_url": state["actual_url"],
            "actual_title": state["actual_title"],
            "affected_case_number": affected_case_number,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
        }
        self.blockers.append(blocker)

        if case is not None:
            blocked_case = dict(case)
            blocked_case["failed_operation"] = operation
            result = self._failure_result(
                case=blocked_case,
                stage="suite_precondition",
                exc=exc,
                started_at=started_at,
                test_started=False,
                test_completed=False,
                state=state,
            )
            self._attach_case_evidence(result, case=blocked_case)
        else:
            allure.attach(
                json.dumps(blocker, ensure_ascii=False, indent=2),
                name=f"Suite blocker | {operation}",
                attachment_type=allure.attachment_type.JSON,
            )
            try:
                allure.attach(
                    safe_page_screenshot(self.page, full_page=True),
                    name=f"Suite blocker | {operation} | redacted screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except (PlaywrightError, OSError, ValueError, AttributeError, TypeError):
                pass

    def _append_not_checked(self):
        blocker_reason = "BLOCKED_BY_PRECONDITION" if self.blockers else "NOT_EXECUTED"
        for case in self.planned_cases:
            if case["number"] in self._results_by_number:
                continue
            result = build_form_result(
                number=case["number"],
                filial=case["filial"],
                navbar_tab=case["navbar_tab"],
                menu_column=case.get("menu_column"),
                menu_item=case["menu_item"],
                title=case["title"],
                expected_path=case.get("expected_path"),
                actual_url="",
                page_links=case.get("page_links"),
                action=case.get("action"),
                add_icon=case.get("add_icon", False),
                detail="",
                status=NOT_CHECKED,
                reason_code=blocker_reason,
                reason_summary=reason_description(blocker_reason),
                failed_stage="not_started",
                expected_title=case["title"],
                actual_title="",
                opened=False,
                page_reached=False,
                test_started=False,
                test_completed=False,
                validation_completed=False,
                validation_passed=False,
                usable=False,
                checks={},
                shell=case.get("shell"),
                suite=self.suite_name,
                duration_ms=None,
            )
            self._append_result(result)

    def complete_results(self):
        """Planned, ammo ishlamagan formalarni NOT_CHECKED bilan to'ldiradi."""
        self._append_not_checked()
        return sorted(self.results, key=lambda result: result["number"])

    def finish(self):
        """Har qanday yakunda to'liq planned coverage va yagona hisobot chiqaradi."""
        self._remove_page_listeners()
        ordered_results = self.complete_results()
        summary = render_monitor_summary(
            suite_name=self.suite_name,
            planned_count=len(self.planned_cases),
            results=ordered_results,
            blockers=self.blockers,
            skipped_cases=self.skipped_cases,
        )
        write_terminal_report(summary, terminal_reporter=self.terminal_reporter)
        allure.attach(
            summary,
            name=f"{self.suite_name} | markaziy forma monitoring hisoboti",
            attachment_type=allure.attachment_type.TEXT,
        )
        payload = build_monitor_payload(
            suite_name=self.suite_name,
            planned_count=len(self.planned_cases),
            results=ordered_results,
            blockers=self.blockers,
            skipped_cases=self.skipped_cases,
        )
        allure.attach(
            json.dumps(payload, ensure_ascii=False, indent=2),
            name=f"{self.suite_name} | form-monitor.json",
            attachment_type=allure.attachment_type.JSON,
        )

        counts = _status_counts(ordered_results)
        actionable = [
            result
            for result in ordered_results
            if result["status"] not in {PASSED, NOT_CHECKED}
        ]
        if actionable or counts[NOT_CHECKED]:
            failures = "\n".join(
                f"{result['number']:03d} | {result['title']} | "
                f"{result['status']} | {result.get('reason_code') or '—'} | "
                f"{result.get('detail') or '—'}"
                for result in actionable
            )
            raise AssertionError(
                f"{self.suite_name}: reja={len(ordered_results)}, "
                f"muvaffaqiyatli={counts[PASSED]}, "
                f"nuqsonli={counts[OPENED_WITH_DEFECT]}, "
                f"ochilmadi={counts[NOT_OPENED]}, "
                f"bloklandi={counts[TEST_BLOCKED]}, "
                f"tekshirilmadi={counts[NOT_CHECKED]}.\n"
                f"Asosiy muammolar:\n{failures or 'Suite yakunlanmadi.'}"
            )
        return ordered_results
