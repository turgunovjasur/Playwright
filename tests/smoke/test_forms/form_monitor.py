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
from tests.smoke.test_forms.flow import (
    build_form_result,
    canonical_form_path,
    form_step_title,
    format_form_result,
    write_terminal_report,
)
from tests.smoke.test_forms.skipped_forms import is_form_skipped


PASSED = "PASSED"
OPENED_WITH_DEFECT = "OPENED_WITH_DEFECT"
NOT_OPENED = "NOT_OPENED"
TEST_BLOCKED = "TEST_BLOCKED"
NOT_CHECKED = "NOT_CHECKED"

FORM_STATUSES = {
    PASSED,
    OPENED_WITH_DEFECT,
    NOT_OPENED,
    TEST_BLOCKED,
    NOT_CHECKED,
}

REASON_DESCRIPTIONS = {
    "TITLE_MISMATCH": (
        "Target URLga yetildi va forma kontenti yuklandi, lekin sahifa title'i "
        "kutilgan forma nomiga mos emas."
    ),
    "CONTENT_VALIDATION_FAILED": (
        "Target URLga yetildi, lekin forma uchun belgilangan tekshiruv "
        "muvaffaqiyatli tugamadi."
    ),
    "URL_MISMATCH": "Navigatsiyadan keyin kutilgan forma o'rniga boshqa URL ochildi.",
    "NAVIGATION_FAILED": (
        "Menu, action yoki page-link bosqichida target forma URLiga o'tib bo'lmadi."
    ),
    "APPLICATION_ERROR": "Target sahifada aniq UI xato xabari ko'rindi.",
    "JS_ERROR": (
        "Forma ochilishida brauzerda JS exception yuz berdi; sahifa jim buzilgan "
        "bo'lishi mumkin."
    ),
    "LOADER_NOT_FINISHED": "Forma yuklanish indikatori belgilangan vaqtda tugamadi.",
    "CONTENT_NOT_READY": "Target URLga yetildi, ammo forma kontenti tayyor bo'lmadi.",
    "FILIAL_SWITCH_FAILED": (
        "Kerakli filialga o'tib bo'lmadi; forma tekshiruvi boshlanmadi."
    ),
    "AUTHORIZATION_FAILED": (
        "Avtorizatsiya tugamadi; forma tekshiruvi boshlanmadi."
    ),
    "PRECONDITION_FAILED": (
        "Forma testidan oldingi majburiy tayyorlov bosqichi bajarilmadi."
    ),
    "BLOCKED_BY_PRECONDITION": (
        "Oldingi majburiy tayyorlov xatosi sabab bu forma tekshirilmadi."
    ),
    "NOT_EXECUTED": "Bu forma uchun tekshiruv ishga tushmadi.",
}

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
})();
"""

CAPTURE_READ_SCRIPT = """
({
  js: window.__formMonitorCaptureErrors || [],
  jsCount: window.__formMonitorCaptureCount || 0,
  resources: window.__formMonitorResourceErrors || [],
  resourceCount: window.__formMonitorResourceCount || 0,
})
"""

CAPTURE_RESET_SCRIPT = """
(() => {
  window.__formMonitorCaptureErrors = [];
  window.__formMonitorCaptureCount = 0;
  window.__formMonitorResourceErrors = [];
  window.__formMonitorResourceCount = 0;
})()
"""

EMPTY_CAPTURE_SIGNALS = {
    "js_errors": [],
    "js_error_count": 0,
    "resource_errors": [],
    "resource_error_count": 0,
}


def reason_description(reason_code):
    return REASON_DESCRIPTIONS.get(reason_code, "")


def _clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_allowed_warnings(value):
    if value is None:
        return []
    values = [value] if isinstance(value, str) else list(value)
    return [_clean_text(item) for item in values if _clean_text(item)]


def _allowed_warning_text(case, state):
    visible_error = _clean_text(state.get("visible_error"))
    warning_text = re.sub(r"^×\s*", "", visible_error).strip()
    if warning_text in _normalize_allowed_warnings(case.get("allowed_warnings")):
        return warning_text
    return ""


def _unexpected_visible_error(case, state):
    visible_error = _clean_text(state.get("visible_error"))
    if visible_error and _allowed_warning_text(case, state):
        return ""
    return visible_error


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
    """A2'da ``preventDefault`` yutib yuboradigan JS xatosini o'qiydi.

    Bosqich 7, 1-qadam — hozircha **faqat kuzatuv**, statusga ta'sir qilmaydi.
    ``CAPTURE_JS_ERROR_SCRIPT`` app bundle'dan oldin ishlagani uchun A2
    ilovaning global ``error`` listeneri ``preventDefault()`` chaqirsa ham bu
    massivga yetib keladi — `page.on("pageerror")` esa aynan shu holatda ko'r.

    Resurs yuklanish xatolari (`img`/`script`/`link`) **alohida** qaytadi: ular
    JS exception emas, ularni network kanali allaqachon qamraydi va bir joyga
    qo'shib yuborish `JS_ERROR` ni yolg'on qizil qilardi.
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

    ``capture_signals`` esa shu yerning o'zida, ``page.evaluate`` orqali
    darhol o'qiladi (Bosqich 7, 1-qadam) — A2'da ``preventDefault`` tufayli
    ``js_errors`` ko'r bo'lgan holatni ham ko'radi, lekin hozircha faqat
    kuzatuv: statusga, ``usable``ga yoki klassifikatsiyaga ta'sir qilmaydi.
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
            "[aria-busy='true']:visible",
        )
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
    }


def _path_matches(case, state):
    expected_path = (case.get("expected_path") or "").strip("/")
    actual_path = (state.get("canonical_path") or "").strip("/")
    return not expected_path or actual_path == expected_path


def _title_candidates(state):
    return [
        _clean_text(candidate)
        for candidate in (state.get("title_candidates") or [])
        if _clean_text(candidate)
    ]


def _title_verified(case, state):
    """Title haqiqatan taqqoslandimi — hisobot ``HA`` deb yolg'on aytmasligi uchun.

    Legacy sahifada bironta heading topilmasa ``_title_matches`` taqqoslamasdan
    ``True`` qaytaradi; bu bayroq o'sha holatni hisobotda ochiq ko'rsatadi.
    """
    if not _clean_text(case.get("title")):
        return False
    if not _title_candidates(state) and state.get("title_source") == "visible_heading":
        return False
    return True


def _title_matches(case, state):
    expected_title = _clean_text(case.get("title"))
    candidates = _title_candidates(state)
    if not expected_title:
        return True
    if not candidates and state.get("title_source") == "visible_heading":
        return True
    if not candidates:
        candidates = [_clean_text(state.get("actual_title"))]
    return expected_title in candidates


def classify_form_failure(*, case, stage, detail, state):
    """Kutilgan UI exception va sahifa signallaridan QA holatini chiqaradi."""
    lower_detail = _clean_text(detail).lower()
    path_matches = _path_matches(case, state)
    title_matches = _title_matches(case, state)
    content_ready = bool(state.get("content_ready"))
    visible_error = _unexpected_visible_error(case, state)

    if stage == "suite_precondition":
        lowered_operation = _clean_text(case.get("failed_operation")).lower()
        if "filial" in lowered_operation or "filial" in lower_detail:
            reason_code = "FILIAL_SWITCH_FAILED"
        elif any(
            marker in lowered_operation or marker in lower_detail
            for marker in ("login", "authorization", "avtoriz")
        ):
            reason_code = "AUTHORIZATION_FAILED"
        else:
            reason_code = "PRECONDITION_FAILED"
        return {
            "status": TEST_BLOCKED,
            "reason_code": reason_code,
            "reason_summary": reason_description(reason_code),
            "opened": False,
        }

    if not path_matches:
        reason_code = "URL_MISMATCH" if state.get("canonical_path") else "NAVIGATION_FAILED"
        return {
            "status": NOT_OPENED,
            "reason_code": reason_code,
            "reason_summary": reason_description(reason_code),
            "opened": False,
        }

    if visible_error:
        return {
            "status": OPENED_WITH_DEFECT,
            "reason_code": "APPLICATION_ERROR",
            "reason_summary": reason_description("APPLICATION_ERROR"),
            "opened": True,
        }

    if state.get("js_errors"):
        return {
            "status": OPENED_WITH_DEFECT,
            "reason_code": "JS_ERROR",
            "reason_summary": reason_description("JS_ERROR"),
            "opened": True,
        }

    if state.get("loader_visible"):
        return {
            "status": NOT_OPENED,
            "reason_code": "LOADER_NOT_FINISHED",
            "reason_summary": reason_description("LOADER_NOT_FINISHED"),
            "opened": True,
        }

    if not content_ready:
        return {
            "status": NOT_OPENED,
            "reason_code": "CONTENT_NOT_READY",
            "reason_summary": reason_description("CONTENT_NOT_READY"),
            "opened": True,
        }

    if not title_matches:
        return {
            "status": OPENED_WITH_DEFECT,
            "reason_code": "TITLE_MISMATCH",
            "reason_summary": reason_description("TITLE_MISMATCH"),
            "opened": True,
        }

    if stage == "navigation":
        return {
            "status": NOT_OPENED,
            "reason_code": "NAVIGATION_FAILED",
            "reason_summary": reason_description("NAVIGATION_FAILED"),
            "opened": True,
        }

    return {
        "status": OPENED_WITH_DEFECT,
        "reason_code": "CONTENT_VALIDATION_FAILED",
        "reason_summary": reason_description("CONTENT_VALIDATION_FAILED"),
        "opened": True,
    }


def _assert_healthy_form_state(case, state):
    """Custom validate qaytganidan keyin ham markaziy sog'liq shartlarini majburlaydi."""
    if not _path_matches(case, state):
        raise AssertionError(
            "Markaziy holat tekshiruvi [URL_MISMATCH]: "
            f"expected={case.get('expected_path') or '—'}, "
            f"actual={state.get('canonical_path') or '—'}"
        )
    visible_error = _unexpected_visible_error(case, state)
    if visible_error:
        raise AssertionError(
            "Markaziy holat tekshiruvi [APPLICATION_ERROR]: "
            f"{visible_error}"
        )
    js_errors = state.get("js_errors") or []
    if js_errors:
        raise AssertionError(
            f"Markaziy holat tekshiruvi [JS_ERROR] ({len(js_errors)}): "
            f"{'; '.join(js_errors)}"
        )
    if state.get("loader_visible"):
        raise AssertionError("Markaziy holat tekshiruvi [LOADER_NOT_FINISHED]")
    if not state.get("content_ready"):
        ready_note = (
            f"; required selector={case.get('ready')}"
            if case.get("ready")
            else ""
        )
        raise AssertionError(
            f"Markaziy holat tekshiruvi [CONTENT_NOT_READY]{ready_note}"
        )
    if not _title_matches(case, state):
        raise AssertionError(
            "Markaziy holat tekshiruvi [TITLE_MISMATCH]: "
            f"expected={case.get('title') or '—'}, "
            f"actual={state.get('actual_title') or '—'}"
        )


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
    planned = []
    for definition in definitions:
        if is_form_skipped(definition):
            continue
        links = list(definition.get("page_links") or [])
        title = (
            definition.get("title")
            or (links[-1] if links else None)
            or definition.get("action")
            or definition["menu_item"]
        )
        planned.append(
            form_case(
                number=start_number + len(planned),
                filial=filial,
                navbar_tab=definition.get("navbar_tab") or navbar_tab,
                menu_column=definition.get("menu_column"),
                menu_item=definition["menu_item"],
                title=title,
                expected_path=(
                    definition.get("expected_path") or definition.get("path")
                ),
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
    return planned


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


def build_monitor_payload(*, suite_name, planned_count, results, blockers):
    """Allure JSON va boshqa consumerlar uchun versionlangan yagona payload."""
    return {
        "schema_version": 2,
        "suite": suite_name,
        "planned": planned_count,
        "metrics": _monitor_metrics(results),
        "counts": dict(_status_counts(results)),
        "blockers": list(blockers),
        "results": list(results),
    }


def _page_event_lines(results):
    """JS va network signallarining to'liq inventarini beradi.

    JS xatosi formani `JS_ERROR` nuqsoni qiladi; network signallari esa hozircha
    faqat kuzatiladi, shuning uchun signal ko'rinadigan forma `PASSED` bo'lib
    qolishi mumkin va bu bo'lim statusga qaramay ro'yxatlaydi.
    """
    noisy = [
        result
        for result in results
        if (result.get("checks") or {}).get("js_error_count")
        or (result.get("checks") or {}).get("failed_request_count")
    ]
    if not noisy:
        return []
    lines = [
        "JS VA NETWORK SIGNALLARI",
        "-" * 88,
        "JS xatosi formani nuqsonli qiladi (faqat legacy shell — A2 da kanal "
        "ko'r); network signallari faqat kuzatiladi.",
    ]
    for result in noisy:
        checks = result["checks"]
        lines.append(
            f"• {result['number']:03d} | {result['title']} | {result['status']}"
        )
        if checks.get("js_error_count"):
            lines.append(f"    JS xatolari ({checks['js_error_count']}):")
            for message in checks.get("js_errors") or []:
                lines.append(f"      - {message}")
        if checks.get("failed_request_count"):
            lines.append(
                f"    Muvaffaqiyatsiz so'rovlar ({checks['failed_request_count']}):"
            )
            for label in checks.get("failed_requests") or []:
                lines.append(f"      - {label}")
    lines.append("")
    return lines


def _capture_js_error_lines(results):
    """Bosqich 7, 1-qadam: init-script orqali yig'ilgan A2 JS signallari.

    ``page.on("pageerror")`` A2'da ``preventDefault`` tufayli ko'r bo'lgani
    uchun qo'shildi (`ui-patterns.md`). Hozircha **faqat kuzatuv** — real
    shovqin hajmi o'lchanmaguncha statusga ta'sir qilmaydi, shuning uchun bu
    bo'lim ham statusga qaramay ro'yxatlaydi.
    """
    noisy = [
        result
        for result in results
        if (result.get("checks") or {}).get("capture_js_error_count")
        or (result.get("checks") or {}).get("capture_resource_error_count")
    ]
    if not noisy:
        return []
    lines = [
        "CAPTURE-FAZA SIGNALLARI (tajriba — hozircha statusga ta'sir qilmaydi)",
        "-" * 88,
        "init_script orqali yig'ilgan; A2'da page.on('pageerror') preventDefault "
        "tufayli ko'r bo'lgani uchun qo'shildi. Bosqich 7, 1-qadam — hali "
        "qattiqlashtirilmagan.",
        "Resurs xatosi (img/script/link yuklanmadi) JS exception EMAS va alohida "
        "ko'rsatiladi — uni JS_ERROR ga qo'shish yolg'on qizil berardi.",
    ]
    for result in noisy:
        checks = result["checks"]
        lines.append(
            f"• {result['number']:03d} | {result['title']} | {result['status']} | "
            f"shell={result.get('shell') or '—'}"
        )
        if checks.get("capture_js_error_count"):
            lines.append(f"    JS exceptionlar ({checks['capture_js_error_count']}):")
            for message in checks.get("capture_js_errors") or []:
                lines.append(f"      - {message}")
        if checks.get("capture_resource_error_count"):
            lines.append(
                f"    Resurs yuklanish xatolari ({checks['capture_resource_error_count']}):"
            )
            for message in checks.get("capture_resource_errors") or []:
                lines.append(f"      - {message}")
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


def render_monitor_summary(*, suite_name, planned_count, results, blockers):
    """Terminal va Allure uchun bir xil, takrorsiz markaziy hisobot yasaydi."""
    counts = _status_counts(results)
    metrics = _monitor_metrics(results)
    lines = [
        "FORMA MARKAZIY MONITORING HISOBOTI",
        "=" * 88,
        f"Suite: {suite_name}",
        f"Rejalashtirilgan       : {planned_count}",
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
    lines.extend(_capture_js_error_lines(results))
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
    ):
        self.page = page
        self.suite_name = suite_name
        self.planned_cases = [dict(case) for case in planned_cases]
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
        faqat qayd qilinadi (shovqinning 99% i `/page/tour/` 404 lari).

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
        """A2 uchun capture-fazali JS xato kuzatuvini yoqadi (Bosqich 7, 1-qadam).

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
        for case in self.planned_cases:
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
        path_matches = _path_matches(case, state)
        allowed_warning = _allowed_warning_text(case, state)
        visible_error = _unexpected_visible_error(case, state)
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
            "capture_js_errors": list(capture["js_errors"])[:MAX_PAGE_EVENTS],
            "capture_js_error_count": capture["js_error_count"],
            "capture_resource_errors": list(capture["resource_errors"])[:MAX_PAGE_EVENTS],
            "capture_resource_error_count": capture["resource_error_count"],
            "url_matches": path_matches,
            "title_matches": _title_matches(case, state),
            "title_verified": _title_verified(case, state),
            "title_source": state.get("title_source") or "",
            "document_title": state.get("document_title") or "",
            "content_ready": bool(state.get("content_ready")),
            "ready_required": bool(state.get("ready_required")),
            "ready_visible": bool(state.get("ready_visible")),
            "loader_visible": bool(state.get("loader_visible")),
            "visible_error": visible_error,
            "allowed_warning": allowed_warning,
            "usable": usable,
        }

    def _capture_state(self, case=None):
        """Sahifa holatiga shu oynada yig'ilgan JS xatolarini qo'shib qaytaradi."""
        state = capture_form_state(self.page, ready=(case or {}).get("ready"))
        state["js_errors"] = list(self.js_errors)
        return state

    def _case_checks(self, case, state):
        """Sof holat tekshiruvlariga cheklanmagan hisoblar va network signalini qo'shadi.

        JS xatolari ``state`` orqali ``_checks`` ga yetib boradi va statusga
        ta'sir qiladi; network signallari esa hozir faqat qayd qilinadi.
        """
        checks = self._checks(case, state)
        checks["js_error_count"] = self.js_error_count
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
