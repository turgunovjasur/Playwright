import re
from urllib.parse import urlsplit

import allure
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


FORM_TIMEOUT = 15_000


def canonical_form_path(url):
    """Volatile ``#/!<token>/`` qismini olib, formaning canonical pathini qaytaradi."""
    parsed = urlsplit(url)
    fragment = parsed.fragment.lstrip("/")
    if fragment.startswith("!"):
        parts = fragment.split("/", 1)
        fragment = parts[1] if len(parts) == 2 else ""
    if not fragment and "/a2/" in parsed.path:
        fragment = parsed.path.split("/a2/", 1)[1]
    return fragment.split("?", 1)[0].strip("/")


# ----------------------------------------------------------------------------------------------------------------------


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
):
    """Terminal va Allure uchun yagona strukturali forma natijasini yaratadi."""
    links = list(page_links or [])
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
        "checks": dict(checks or {}),
        "shell": shell,
        "suite": suite,
        "duration_ms": duration_ms,
        "detail": detail,
    }


# ----------------------------------------------------------------------------------------------------------------------


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
        f"  Action             : {action}",
        f"  +add ikonka-link   : {add_icon}",
        f"  Page linklar       : {links}",
        f"  To'liq yo'l        : {result['track']}",
        f"  Kutilgan URL       : {result['expected_path']}",
        f"  Haqiqiy URL        : {result['actual_url'] or '—'}",
    ]
    if status_code == "OBSERVED_ONLY":
        checks = result.get("checks") or {}
        lines.extend(
            [
                "  Holat              : OBSERVED_ONLY",
                "  Izoh               : Navigatsiya bajarildi, hard checklar ishlamadi",
                "  Diagnostikalar     : "
                f"{', '.join(checks.get('enabled_diagnostics') or []) or 'o‘chirilgan'}",
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
        checks = result.get("checks") or {}
        if checks:
            lines.extend(
                [
                    f"  Joriy URL mosmi    : {'HA' if checks.get('url_matches') else 'YOQ'}",
                    f"  Title mosmi        : {'HA' if checks.get('title_matches') else 'YOQ'}",
                    "  Title tekshirildimi: "
                    f"{'HA' if checks.get('title_verified') else 'YOQ (heading topilmadi)'}",
                    f"  Title manbasi      : {checks.get('title_source') or '—'}",
                    f"  Kontent yuklandimi : {'HA' if checks.get('content_ready') else 'YOQ'}",
                    f"  Loader qoldimi     : {'HA' if checks.get('loader_visible') else 'YOQ'}",
                    "  Busy elementlar (kuzatuv): "
                    f"{checks.get('busy_visible_count') or 0}",
                    f"  UI error           : {checks.get('visible_error') or '—'}",
                    "  JS xatolari        : "
                    f"{checks.get('js_error_count') or 0} "
                    f"(manba: {checks.get('js_error_source') or '—'}) "
                    f" {'; '.join(checks.get('js_errors') or []) or '—'}",
                    "  Promise rejectionlar (kuzatuv): "
                    f"{checks.get('promise_rejection_count') or 0} "
                    "(tafsilot markaziy kuzatuv bo'limi/raw JSONda)",
                    "  Capture resurs xatolari (kuzatuv): "
                    f"{checks.get('capture_resource_error_count') or 0} "
                    "(tafsilot markaziy kuzatuv bo'limi/raw JSONda)",
                    "  Muvaffaqiyatsiz so'rovlar: "
                    f"{checks.get('failed_request_count') or 0} "
                    "(tafsilot markaziy signal bo'limi/raw JSONda)",
                ]
            )
        if result.get("screenshot"):
            lines.append(f"  Screenshot         : {result['screenshot']}")
        elif result.get("screenshot_error"):
            lines.append(
                f"  Screenshot         : olinmadi ({result['screenshot_error']})"
            )
        if result.get("duration_ms") is not None:
            lines.append(f"  Bosqich davomiyligi: {result['duration_ms']} ms")
    if result["detail"]:
        lines.append(f"  Xato               : {result['detail']}")
    return "\n".join(lines)


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


# ----------------------------------------------------------------------------------------------------------------------


def _select_operational_filial(names):
    """Filial nomlaridan birinchi ``Администрирование`` bo'lmaganini tanlaydi."""
    cleaned_names = [str(name).strip() for name in names if str(name).strip()]
    for name in cleaned_names:
        if name != "Администрирование":
            return name
    raise AssertionError(
        "'Администрирование' bo'lmagan operatsion filial topilmadi. "
        f"Ko'ringan filiallar: {cleaned_names}"
    )


def first_operational_filial(page):
    """Legacy filial ro'yxatidan birinchi operatsion filial nomini oladi."""
    locations = (
        page.locator(".header-logo.custom-dropdown:visible")
        .filter(has=page.locator(".dropdown-locations-custom"))
        .first
    )
    trigger = locations.locator(".dropdown-locations-custom")
    expect(trigger).to_be_visible(timeout=FORM_TIMEOUT)
    trigger.click(timeout=FORM_TIMEOUT)

    menu = locations.locator(".dropdown-menu")
    expect(menu).to_be_visible(timeout=FORM_TIMEOUT)
    filial_list = menu.locator(".filial-list")
    expect(filial_list).to_be_visible(timeout=FORM_TIMEOUT)
    names = filial_list.get_by_role("link").all_inner_texts()

    trigger.click(timeout=FORM_TIMEOUT)
    expect(menu).to_be_hidden(timeout=FORM_TIMEOUT)

    return _select_operational_filial(names)


# ----------------------------------------------------------------------------------------------------------------------


def switch_forms_filial(page, name):
    """Joriy legacy/A2 shell turiga mos filial selectorini ishlatadi."""
    if "/a2/" in page.url:
        AngularBasePage(page).switch_filial(
            name=name,
            timeout=FORM_TIMEOUT,
        )
    else:
        BasePage(page).switch_filial(
            name=name,
            timeout=FORM_TIMEOUT,
        )


# ----------------------------------------------------------------------------------------------------------------------


def _click_page_links(page, page_links):
    base = BasePage(page)
    for page_link in page_links:
        if "/a2/" in page.url:
            link = page.get_by_role(
                "link",
                name=page_link,
                exact=True,
            ).filter(visible=True).first
        else:
            link = (
                page.locator(".subheader ul.breadcrumb")
                .get_by_role("link", name=page_link, exact=True)
                .filter(visible=True)
            )
        try:
            expect(link).to_have_count(1, timeout=FORM_TIMEOUT)
            expect(link).to_be_visible(timeout=FORM_TIMEOUT)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"page_link='{page_link}' yagona ko'rinadigan link sifatida topilmadi; "
                f"url={page.url}"
            ) from exc
        link.click()
        if "/a2/" in page.url:
            AngularBasePage(page).wait_for_loader(timeout=FORM_TIMEOUT)
        else:
            base.wait_for_loader(timeout=FORM_TIMEOUT)


# ----------------------------------------------------------------------------------------------------------------------


def open_menu_form(
    page,
    *,
    navbar_tab,
    menu_column,
    menu_item,
    page_links=None,
    add_icon=False,
):
    """Menu item yoki uning ``+add`` ikonkasidan forma/page-link zanjirini ochadi."""
    links = [] if page_links is None else list(page_links)
    track = form_navigation_track(
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        menu_item=menu_item,
        page_links=links,
        add_icon=add_icon,
    )

    with allure.step(f"Navigatsiya | Yo'l: {track}"):
        if add_icon:
            BasePage(page).navigate_to_form(
                navbar_tab=navbar_tab,
                menu_column=menu_column,
                menu_item=menu_item,
                add_icon=True,
                timeout=FORM_TIMEOUT,
            )
        elif "/a2/" in page.url:
            AngularBasePage(page).navigate_to(
                tab=navbar_tab,
                name=menu_item,
                timeout=FORM_TIMEOUT,
            )
        else:
            BasePage(page).navigate_to_form(
                navbar_tab=navbar_tab,
                menu_column=menu_column,
                menu_item=menu_item,
                timeout=FORM_TIMEOUT,
            )
        _click_page_links(page, links)


# ----------------------------------------------------------------------------------------------------------------------


def open_create_dropdown_form(
    page,
    *,
    navbar_tab,
    menu_column,
    menu_item,
    action,
    page_links=None,
):
    """Parent listdagi ``Создать`` dropdown actionini va uning page-linklarini ochadi."""
    links = [] if page_links is None else list(page_links)
    open_menu_form(
        page,
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        menu_item=menu_item,
    )

    track = form_navigation_track(
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        menu_item=menu_item,
        action=action,
        page_links=links,
    )
    with allure.step(f"Navigatsiya | Yo'l: {track}"):
        group = (
            page.locator(".btn-group:visible")
            .filter(
                has=page.get_by_role(
                    "button",
                    name="Создать",
                    exact=True,
                )
            )
        )
        try:
            expect(group).to_have_count(1, timeout=FORM_TIMEOUT)
            expect(group).to_be_visible(timeout=FORM_TIMEOUT)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"'{menu_item}' formasida 'Создать' dropdown guruhi topilmadi; "
                f"url={page.url}"
            ) from exc

        toggle = group.locator("button.dropdown-toggle")
        expect(toggle).to_have_count(1, timeout=FORM_TIMEOUT)
        expect(toggle).to_be_visible(timeout=FORM_TIMEOUT)
        toggle.click()

        action_link = group.get_by_role("link", name=action, exact=True)
        try:
            expect(action_link).to_have_count(1, timeout=FORM_TIMEOUT)
            expect(action_link).to_be_visible(timeout=FORM_TIMEOUT)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"'{menu_item}' formasidagi 'Создать' dropdownda action='{action}' topilmadi"
            ) from exc
        action_link.click()
        BasePage(page).wait_for_loader(timeout=FORM_TIMEOUT)
        _click_page_links(page, links)


# ----------------------------------------------------------------------------------------------------------------------




def settle_form_open(page, *, case, enabled_checks, previous_url):
    """Enabled checklar uchun bitta bounded auto-wait qiladi, failure chiqarmaydi.

    Yakuniy pass/fail qarorini ``FormMonitor`` bitta final snapshotdan chiqaradi.
    Bu helper faqat SPA transition tugashiga vaqt beradi va timeout detailini
    diagnostika sifatida qaytaradi.
    """
    enabled = set(enabled_checks)
    expected_path = case.get("expected_path") if "url" in enabled else None
    expected_title = case.get("title") if "title" in enabled else None
    ready = case.get("ready") if "content_ready" in enabled else None

    try:
        if "/a2/" in page.url:
            if expected_path or expected_title or ready:
                AngularBasePage(page).expect_page(
                    title=expected_title,
                    url=expected_path,
                    ready=ready,
                    timeout=FORM_TIMEOUT,
                    check_unblocked=False,
                )
            elif "content_ready" in enabled:
                expect(page.locator("main:visible").first).to_be_visible(
                    timeout=FORM_TIMEOUT
                )
            else:
                expect(page).not_to_have_url(
                    re.compile(rf"^{re.escape(previous_url)}$"),
                    timeout=FORM_TIMEOUT,
                )
        else:
            if expected_path or expected_title:
                BasePage(page).expect_page(
                    heading=expected_title,
                    url=expected_path,
                    timeout=FORM_TIMEOUT,
                    check_unblocked=False,
                )
            elif ready:
                expect(page.locator(ready).first).to_be_visible(timeout=FORM_TIMEOUT)
            elif "content_ready" in enabled:
                expect(
                    page.locator("b-page:visible, .subheader:visible").first
                ).to_be_visible(timeout=FORM_TIMEOUT)
            else:
                expect(page).not_to_have_url(
                    re.compile(rf"^{re.escape(previous_url)}$"),
                    timeout=FORM_TIMEOUT,
                )

        if "loader" in enabled:
            expect(
                page.locator(
                    ".block-ui-overlay:visible, .smt-skeleton:visible"
                )
            ).to_have_count(0, timeout=FORM_TIMEOUT)

        if case.get("add_icon") and "url" in enabled:
            expect(page).to_have_url(
                re.compile(r"\+add(?:$|[?#])"),
                timeout=FORM_TIMEOUT,
            )
    except (AssertionError, PlaywrightTimeoutError) as exc:
        return str(exc)
    return ""


# ----------------------------------------------------------------------------------------------------------------------


def navigate_form_case(page, case):
    """Legacy/A2 case uchun yagona menu/action/page-link navigatsiyasini bajaradi."""
    if case.get("action") is not None:
        open_create_dropdown_form(
            page,
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            menu_item=case["menu_item"],
            action=case["action"],
            page_links=case.get("page_links"),
        )
    else:
        open_menu_form(
            page,
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            menu_item=case["menu_item"],
            page_links=case.get("page_links"),
            add_icon=case.get("add_icon", False),
        )


def run_form_cases(page, cases, *, monitor):
    """Faqat markaziy monitor orqali normalizatsiya qilingan formalarni tekshiradi."""
    if monitor is None:
        raise ValueError("run_form_cases uchun FormMonitor majburiy")
    for case in cases:
        monitor.run_case(
            case,
            navigate=lambda current_case=case: navigate_form_case(page, current_case),
        )
