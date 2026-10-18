import allure
from playwright.sync_api import expect

from tests.smoke.test_forms.monitoring.checks.url import detect_shell
from tests.smoke.test_forms.monitoring.reporting import (
    build_form_result as _build_form_result,
    form_navigation_track,
    form_step_title as _form_step_title,
    format_form_result as _format_form_result,
    write_terminal_report as _write_terminal_report,
)
from utils.base_pages.auto_base_page import AutoBasePage
from utils.helper_utils import first_non_admin_filial


# Reporting helperlari oldingi consumerlar uchun shu moduldan re-export qilinadi.
build_form_result = _build_form_result
form_step_title = _form_step_title
format_form_result = _format_form_result
write_terminal_report = _write_terminal_report


FORM_TIMEOUT = 30_000
A2_FORM_TIMEOUT = 240_000


def _form_timeout(page):
    """Joriy shell uchun navigatsiya kutish limitini tanlaydi."""
    return A2_FORM_TIMEOUT if detect_shell(page.url) == "a2" else FORM_TIMEOUT


def _select_operational_filial(names):
    """Filial nomlaridan birinchi ``Администрирование`` bo'lmaganini tanlaydi."""
    return first_non_admin_filial(names)


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
    AutoBasePage(page).switch_filial(name=name, timeout=_form_timeout(page))


# ----------------------------------------------------------------------------------------------------------------------


def _click_page_links(page, page_links):
    base = AutoBasePage(page)
    for page_link in page_links:
        base.page_link(name=page_link, timeout=_form_timeout(page))


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
        AutoBasePage(page).navigate_to_form(
            navbar_tab=navbar_tab,
            menu_column=menu_column,
            menu_item=menu_item,
            add_icon=add_icon,
            timeout=_form_timeout(page),
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
        AutoBasePage(page).action(name=action, menu="Создать", timeout=_form_timeout(page))
        _click_page_links(page, links)


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
