"""FormMonitor natija modeli, schema va user-readable hisobotlari."""

from __future__ import annotations

from collections import Counter

from tests.smoke.test_forms.monitoring.checks import (
    FORM_STATUSES,
    NOT_CHECKED,
    NOT_OPENED,
    OBSERVED_ONLY,
    OPENED_WITH_DEFECT,
    PASSED,
    TEST_BLOCKED,
)


def form_navigation_track(
    *,
    navbar_tab,
    menu_column,
    menu_item,
    page_links=None,
    action=None,
    add_icon=False,
):
    """Navbar, menu, forma, action va page-linklardan user-visible yo'l yasaydi."""
    parts = [navbar_tab, menu_column, menu_item]
    if action is not None:
        parts.extend(["Создать dropdown", action])
    if add_icon:
        parts.append("+add icon")
    parts.extend(page_links or [])
    return " → ".join(str(part) for part in parts if part is not None)


# ----------------------------------------------------------------------------------------------------------------------


def form_step_title(
    *,
    number,
    filial,
    navbar_tab,
    menu_column,
    title,
):
    """Allure daraxtida bir qarashda tushunarli forma step nomini qaytaradi."""
    menu = menu_column or "—"
    return (
        f"{number:03d} | Filial: {filial} | Forma: {title} | "
        f"Tab: {navbar_tab} | Menu: {menu}"
    )


# ----------------------------------------------------------------------------------------------------------------------


def build_form_result(
    *,
    number,
    filial,
    navbar_tab,
    menu_column,
    menu_item,
    title,
    expected_path,
    actual_url,
    status,
    page_links=None,
    action=None,
    add_icon=False,
    detail="",
    reason_code="",
    reason_summary="",
    failed_stage="",
    expected_title=None,
    actual_title="",
    opened=None,
    checks=None,
    shell=None,
    suite=None,
    duration_ms=None,
    page_reached=None,
    test_started=None,
    test_completed=None,
    validation_completed=None,
    validation_passed=None,
    usable=None,
    label=None,
    test_identity=None,
):
    """Terminal va Allure uchun yagona strukturali forma natijasini yaratadi."""
    links = list(page_links or [])
    signal_details = dict(checks or {})
    hard_checks = dict(signal_details.get("hard_checks") or {})
    url_check = dict(hard_checks.get("url") or {})
    loader_check = dict(hard_checks.get("loader") or {})
    application_error_check = dict(hard_checks.get("application_error") or {})
    content_ready_check = dict(hard_checks.get("content_ready") or {})
    title_check = dict(hard_checks.get("title") or {})
    diagnostics = dict(signal_details.get("diagnostics") or {})
    enabled_checks = list(signal_details.get("enabled_checks") or [])
    enabled_diagnostics = list(
        signal_details.get("enabled_diagnostics") or []
    )
    status_icons = {
        "PASSED": "✅",
        "OBSERVED_ONLY": "👁️",
        "OPENED_WITH_DEFECT": "⚠️",
        "NOT_OPENED": "❌",
        "TEST_BLOCKED": "⛔",
        "NOT_CHECKED": "⬜",
    }
    inferred_page_reached = (
        status in {"PASSED", "OBSERVED_ONLY"}
        if opened is None
        else bool(opened)
    )
    if page_reached is None:
        page_reached = inferred_page_reached
    if test_started is None:
        test_started = status not in {"TEST_BLOCKED", "NOT_CHECKED"}
    if test_completed is None:
        test_completed = bool(test_started)
    if validation_completed is None:
        validation_completed = status in {"PASSED", "OPENED_WITH_DEFECT"}
    if validation_passed is None:
        validation_passed = status == "PASSED"
    if usable is None:
        usable = status == "PASSED"
    return {
        "number": number,
        "filial": filial,
        "navbar_tab": navbar_tab,
        "menu_column": menu_column,
        "menu_item": menu_item,
        "title": title,
        "page_links": links,
        "action": action,
        "add_icon": bool(add_icon),
        "label": label or form_navigation_track(
            navbar_tab=None,
            menu_column=None,
            menu_item=menu_item,
            page_links=links,
            action=action,
            add_icon=add_icon,
        ),
        "identity": test_identity or "",
        "test_identity": test_identity or "",
        "track": form_navigation_track(
            navbar_tab=navbar_tab,
            menu_column=menu_column,
            menu_item=menu_item,
            page_links=links,
            action=action,
            add_icon=add_icon,
        ),
        "expected_path": expected_path or "—",
        "actual_url": actual_url,
        "ok": status == "PASSED",
        "status": status,
        "status_icon": status_icons.get(status, "•"),
        "reason_code": reason_code,
        "reason_summary": reason_summary,
        "failed_stage": failed_stage,
        "expected_title": expected_title or title,
        "actual_title": actual_title,
        "opened": bool(page_reached),
        "page_reached": bool(page_reached),
        "test_started": bool(test_started),
        "test_completed": bool(test_completed),
        "validation_completed": bool(validation_completed),
        "validation_passed": bool(validation_passed),
        "usable": bool(usable),
        # ``checks`` schema-v3 consumerlar uchun flat compatibility maydonidir.
        # Schema-v4 consumerlar ``hard_checks`` va ``diagnostics``ni o'qiydi.
        "checks": signal_details,
        "hard_checks": hard_checks,
        "diagnostics": diagnostics,
        "enabled_checks": enabled_checks,
        "enabled_diagnostics": enabled_diagnostics,
        "url_timeout_ms": url_check.get("timeout_ms"),
        "loader_timeout_ms": loader_check.get("timeout_ms"),
        "visible_loaders": list(loader_check.get("visible_loaders") or []),
        "loader_count": int(loader_check.get("loader_count") or 0),
        "application_error_timeout_ms": application_error_check.get(
            "timeout_ms"
        ),
        "matched_error_selector": (
            application_error_check.get("matched_selector") or ""
        ),
        "error_text": application_error_check.get("error_text") or "",
        "modal_cleanup_attempted": bool(
            application_error_check.get("modal_cleanup_attempted")
        ),
        "modal_cleanup_succeeded": bool(
            application_error_check.get("modal_cleanup_succeeded")
        ),
        "modal_cleanup_error": (
            application_error_check.get("modal_cleanup_error") or ""
        ),
        "content_ready_timeout_ms": content_ready_check.get("timeout_ms"),
        "ready_source": content_ready_check.get("ready_source") or "",
        "expected_ready": content_ready_check.get("expected_ready") or "",
        "matched_ready_selector": (
            content_ready_check.get("matched_selector") or ""
        ),
        "content_observation": (
            content_ready_check.get("content_observation") or ""
        ),
        "title_timeout_ms": title_check.get("timeout_ms"),
        "title_source": title_check.get("title_source") or "",
        "title_candidates": list(title_check.get("title_candidates") or []),
        "direct_probe_enabled": bool(url_check.get("direct_probe_enabled")),
        "direct_probe_executed": bool(url_check.get("direct_probe_executed")),
        "direct_expected_url": url_check.get("direct_expected_url") or "",
        "direct_actual_url": url_check.get("direct_actual_url") or "",
        "direct_url_reached": bool(url_check.get("direct_url_reached")),
        "direct_error": url_check.get("direct_error") or "",
        "direct_summary": url_check.get("direct_summary") or "",
        "evidence": list(url_check.get("evidence") or []),
        "shell": shell,
        "suite": suite,
        "duration_ms": duration_ms,
        "detail": detail,
    }


# ----------------------------------------------------------------------------------------------------------------------


def _failed_check_lines(result):
    checks = result.get("checks") or {}
    hard_checks = result.get("hard_checks") or checks.get("hard_checks") or {}
    enabled = [name for name, item in hard_checks.items() if item.get("enabled")]
    lines = [f"  Yoqilgan checklar   : {', '.join(enabled) or 'o‘chirilgan'}"]
    for name, item in hard_checks.items():
        if not item.get("enabled") or item.get("passed") is not False:
            continue
        actual = item.get("actual")
        if isinstance(actual, list):
            actual = "; ".join(str(value) for value in actual)
        lines.append(
            f"  Failed check        : {name} | "
            f"{item.get('reason_code') or '—'} | "
            f"actual={actual if actual not in (None, '') else '—'}"
        )
        if name == "loader":
            lines.append(
                f"  Loader timeout      : {item.get('timeout_ms') or '—'} ms | "
                f"count={item.get('loader_count') or 0} | "
                f"visible={item.get('visible_loaders') or []}"
            )
        if name == "application_error":
            lines.append(
                f"  Error kutish        : {item.get('timeout_ms') or '—'} ms | "
                f"selector={item.get('matched_selector') or '—'} | "
                f"matn={item.get('error_text') or '—'}"
            )
            cleanup_status = (
                "BAJARILMADI"
                if not item.get("modal_cleanup_attempted")
                else (
                    "MUVAFFAQIYATLI"
                    if item.get("modal_cleanup_succeeded")
                    else "MUVAFFAQIYATSIZ"
                )
            )
            lines.append(
                f"  Biruni cleanup      : {cleanup_status}"
                + (
                    f" | {item.get('modal_cleanup_error')}"
                    if item.get("modal_cleanup_error")
                    else ""
                )
            )
        if name == "content_ready":
            lines.append(
                f"  Kontent kutish      : {item.get('timeout_ms') or '—'} ms | "
                f"source={item.get('ready_source') or '—'}"
            )
            lines.append(
                f"  Kutilgan kontent    : {item.get('expected_ready') or '—'} | "
                f"topildi={item.get('matched_selector') or '—'}"
            )
            lines.append(
                f"  Kontent kuzatuvi    : "
                f"{item.get('content_observation') or '—'}"
            )
        if name == "title":
            lines.append(
                f"  Title kutish        : {item.get('timeout_ms') or '—'} ms | "
                f"source={item.get('title_source') or '—'}"
            )
            lines.append(
                f"  Kutilgan title      : {item.get('expected_title') or item.get('expected') or '—'}"
            )
            lines.append(
                f"  Haqiqiy title       : {item.get('actual_title') or item.get('actual') or '—'} | "
                f"candidates={item.get('title_candidates') or []}"
            )
    not_run_items = [
        (name, item)
        for name, item in hard_checks.items()
        if item.get("enabled") and item.get("execution_status") == "NOT_RUN"
    ]
    not_run = [name for name, _ in not_run_items]
    if not_run:
        blocked_by = sorted(
            {
                item.get("blocked_by")
                for _, item in not_run_items
                if item.get("blocked_by")
            }
        )
        lines.append(
            "  Bajarilmagan checklar: "
            f"{', '.join(not_run)} | "
            f"bloklovchi gate={', '.join(blocked_by) or '—'}"
        )
    return lines


def _url_diagnostic_lines(result):
    hard_checks = result.get("hard_checks") or {}
    url_check = hard_checks.get("url") or {}
    if url_check.get("reason_code") != "EXPECTED_URL_NOT_REACHED":
        return []

    if not url_check.get("direct_probe_enabled"):
        direct_status = "O‘CHIRILGAN"
    elif url_check.get("direct_probe_executed"):
        direct_status = "BAJARILDI"
    else:
        direct_status = "BAJARILMADI"
    lines = [
        f"  URL kutish vaqti   : {url_check.get('timeout_ms') or '—'} ms",
        f"  Direct URL probe   : {direct_status}",
    ]
    if url_check.get("direct_probe_executed"):
        lines.extend(
            [
                f"  Direct kutilgan URL: {url_check.get('direct_expected_url') or '—'}",
                f"  Direct haqiqiy URL : {url_check.get('direct_actual_url') or '—'}",
                "  Direct URLga yetdimi: "
                f"{'HA' if url_check.get('direct_url_reached') else 'YOQ'}",
                f"  Direct xulosa      : {url_check.get('direct_summary') or '—'}",
            ]
        )
        if url_check.get("direct_error"):
            lines.append(f"  Direct xato        : {url_check['direct_error']}")
    return lines


def _actionable_diagnostic_lines(result):
    checks = result.get("checks") or {}
    diagnostics = result.get("diagnostics") or checks.get("diagnostics") or {}
    actionable = []
    for name, item in diagnostics.items():
        if not item.get("enabled"):
            continue
        count = int(item.get("count") or 0)
        if name == "busy" and item.get("visible"):
            actionable.append(f"busy={count}")
        elif count:
            actionable.append(f"{name}={count}")
    return [
        "  Diagnostika signali: " + ", ".join(actionable)
    ] if actionable else []


def format_form_result(result):
    """Bitta forma natijasini user o'qiydigan ko'p qatorli matnga aylantiradi."""
    status_code = result["status"]
    status_labels = {
        "PASSED": "✅ OCHILDI",
        "OBSERVED_ONLY": "👁️ FAQAT KUZATILDI — HARD CHECKLAR O‘CHIRILGAN",
        "OPENED_WITH_DEFECT": "⚠️ OCHILDI, LEKIN NUQSON BOR",
        "NOT_OPENED": "❌ OCHILMADI",
        "TEST_BLOCKED": "⛔ TEST BOSHLANISHIDAN OLDIN BLOKLANDI",
        "NOT_CHECKED": "⬜ TEKSHIRILMADI",
    }
    status = status_labels.get(status_code, f"❓ {status_code}")
    stage_labels = {
        "navigation": "Navigatsiya (menu/action/page-link)",
        "validation": "Forma ochilganini tekshirish",
        "suite_precondition": "Testga tayyorlov (login/filial/shell)",
        "not_started": "Tekshiruv boshlanmagan",
    }
    menu = result["menu_column"] or "— (ustunsiz menu)"
    links = " → ".join(result["page_links"]) or "—"
    action = result["action"] or "—"
    add_icon = "HA" if result.get("add_icon") else "YOQ"
    lines = [
        f"[FORMA {result['number']:03d}] {status}",
        f"  Filial             : {result['filial']}",
        f"  Tab                : {result['navbar_tab']}",
        f"  Menu               : {menu}",
        f"  Menyu formasi      : {result['menu_item']}",
        f"  Tekshirilgan forma : {result['title']}",
        f"  Label              : {result.get('label') or '—'}",
        f"  Test identifikatori: {result.get('test_identity') or '—'}",
        f"  Action             : {action}",
        f"  +add ikonka-link   : {add_icon}",
        f"  Page linklar       : {links}",
        f"  To'liq yo'l        : {result['track']}",
        f"  Kutilgan URL       : {result['expected_path']}",
        f"  Haqiqiy URL        : {result['actual_url'] or '—'}",
    ]
    if status_code == "OBSERVED_ONLY":
        checks = result.get("checks") or {}
        enabled_diagnostics = (
            result.get("enabled_diagnostics")
            or checks.get("enabled_diagnostics")
            or []
        )
        lines.extend(
            [
                "  Holat              : OBSERVED_ONLY",
                "  Izoh               : Navigatsiya bajarildi, hard checklar ishlamadi",
                "  Diagnostikalar     : "
                f"{', '.join(enabled_diagnostics) or 'o‘chirilgan'}",
            ]
        )
    elif status_code != "PASSED":
        lines.extend(
            [
                f"  Holat              : {status_code}",
                f"  Xato turi          : {result.get('reason_code') or '—'}",
                f"  Xato sababi        : {result.get('reason_summary') or '—'}",
                "  Xato bosqichi      : "
                f"{stage_labels.get(result.get('failed_stage'), result.get('failed_stage') or '—')}",
                f"  Test boshlandimi   : {'HA' if result.get('test_started') else 'YOQ'}",
                f"  Target URLga yetdimi: {'HA' if result.get('page_reached') else 'YOQ'}",
                f"  Tekshiruv tugadimi : {'HA' if result.get('test_completed') else 'YOQ'}",
                f"  Validatsiya bajarildimi: {'HA' if result.get('validation_completed') else 'YOQ'}",
                f"  Validatsiyadan o'tdimi: {'HA' if result.get('validation_passed') else 'YOQ'}",
                f"  Foydalanishga tayyormi: {'HA' if result.get('usable') else 'YOQ'}",
                f"  Kutilgan sahifa nomi: {result.get('expected_title') or result['title']}",
                f"  Haqiqiy sahifa nomi: {result.get('actual_title') or '—'}",
            ]
        )
        lines.extend(_failed_check_lines(result))
        lines.extend(_url_diagnostic_lines(result))
        lines.extend(_actionable_diagnostic_lines(result))
        if result.get("screenshot"):
            lines.append(f"  Screenshot         : {result['screenshot']}")
        elif result.get("screenshot_error"):
            lines.append(
                f"  Screenshot         : olinmadi ({result['screenshot_error']})"
            )
        if result.get("direct_screenshot"):
            lines.append(f"  Direct screenshot  : {result['direct_screenshot']}")
        elif result.get("direct_screenshot_error"):
            lines.append(
                "  Direct screenshot  : "
                f"olinmadi ({result['direct_screenshot_error']})"
            )
        if result.get("duration_ms") is not None:
            lines.append(f"  Bosqich davomiyligi: {result['duration_ms']} ms")
    if result["detail"]:
        lines.append(f"  Xato               : {result['detail']}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------------------------------


def format_form_result_row(result, *, total=None):
    """Terminal va Allure uchun bitta to'liq kontekstli forma qatorini yasaydi."""
    number = f"{result['number']:03d}"
    if total is not None:
        number = f"{number}/{total:03d}"
    return (
        f"{result.get('status_icon', '•')} {number} | {result['status']} | "
        f"Filial: {result['filial']} | Tab: {result['navbar_tab']} | "
        f"Menu: {result['menu_column'] or '— (ustunsiz menu)'} | "
        f"Tekshirilgan forma: {result['title']} | "
        f"Kutilgan URL: {result.get('expected_path') or '—'} | "
        f"Haqiqiy URL: {result.get('actual_url') or '—'} | "
        f"Sabab: {result.get('reason_summary') or result.get('reason_code') or '—'}"
    )


# ----------------------------------------------------------------------------------------------------------------------


def write_terminal_report(text, terminal_reporter=None):
    """Yakuniy hisobotni pytest terminal-summary bosqichi uchun navbatga qo'yadi."""
    if terminal_reporter is None:
        print(f"\n{text}")
        return

    reports = getattr(terminal_reporter, "_smartup_forms_reports", None)
    if reports is None:
        reports = []
        terminal_reporter._smartup_forms_reports = reports
    reports.append(text)



def status_counts(results):
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


def _signal_coverage(results):
    for result in results:
        checks = result.get("checks") or {}
        hard_checks = result.get("hard_checks") or checks.get("hard_checks") or {}
        diagnostics = (
            result.get("diagnostics") or checks.get("diagnostics") or {}
        )
        if hard_checks or diagnostics:
            return {
                "checks_enabled": sum(
                    bool(item.get("enabled")) for item in hard_checks.values()
                ),
                "checks_total": len(hard_checks),
                "diagnostics_enabled": sum(
                    bool(item.get("enabled")) for item in diagnostics.values()
                ),
                "diagnostics_total": len(diagnostics),
            }
    return {
        "checks_enabled": 0,
        "checks_total": 0,
        "diagnostics_enabled": 0,
        "diagnostics_total": 0,
    }


def build_monitor_payload(
    *,
    suite_name,
    planned_count,
    results,
    blockers,
    skipped_cases=None,
    enabled_checks=None,
    enabled_diagnostics=None,
    url_timeout=None,
    loader_timeout=None,
    application_error_timeout=None,
    content_ready_timeout=None,
    title_timeout=None,
    try_direct_url=None,
):
    """Allure JSON va boshqa consumerlar uchun versionlangan yagona payload."""
    skipped = [dict(case) for case in (skipped_cases or [])]
    return {
        "schema_version": 4,
        "suite": suite_name,
        "config": {
            "enabled_checks": list(enabled_checks or []),
            "enabled_diagnostics": list(enabled_diagnostics or []),
            "url_timeout_ms": url_timeout,
            "loader_timeout_ms": loader_timeout,
            "application_error_timeout_ms": application_error_timeout,
            "content_ready_timeout_ms": content_ready_timeout,
            "title_timeout_ms": title_timeout,
            "try_direct_url": try_direct_url,
        },
        "planned": planned_count,
        "inventory": {
            "total": planned_count + len(skipped),
            "active": planned_count,
            "intentional_skips": len(skipped),
        },
        "skipped": skipped,
        "metrics": _monitor_metrics(results),
        "counts": dict(status_counts(results)),
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


def _request_event_lines(results):
    """Actionable network signallarini ko'rsatadi."""
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
        if actionable_requests:
            rows.append((result, actionable_requests))

    if not rows and not known_noise:
        return []
    lines = [
        "BRAUZER NETWORK SIGNALLARI",
        "-" * 88,
        "Network signallari statusga ta'sir qilmaydi.",
    ]
    for result, actionable_requests in rows:
        lines.append(
            f"• {result['number']:03d} | {result['title']} | {result['status']}"
        )
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
    counts = status_counts(results)
    metrics = _monitor_metrics(results)
    coverage = _signal_coverage(results)
    skipped = [dict(case) for case in (skipped_cases or [])]
    lines = [
        "FORMA MARKAZIY MONITORING HISOBOTI",
        "=" * 88,
        f"Suite: {suite_name}",
        "Hard checklar          : "
        f"{coverage['checks_enabled']}/{coverage['checks_total']} yoqilgan",
        "Diagnostikalar         : "
        f"{coverage['diagnostics_enabled']}/{coverage['diagnostics_total']} yoqilgan",
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
        f"👁️ Faqat kuzatildi      : {counts[OBSERVED_ONLY]}",
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

    lines.extend(_request_event_lines(results))
    lines.extend(_duration_lines(results))

    started_results = [result for result in results if result.get("test_started")]
    if started_results:
        lines.extend(["BOSHLANGAN FORMA TESTLARI", "-" * 88])
        for result in started_results:
            lines.append(format_form_result_row(result))
    return "\n".join(lines).rstrip()
