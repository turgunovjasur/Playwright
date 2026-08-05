import re
from urllib.parse import urlsplit

import allure
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.test_forms.form_reporting import (
    build_form_result,
    form_navigation_track,
    form_step_title,
    format_form_result,
    write_terminal_report,
)
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
