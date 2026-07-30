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
):
    """Navbar, menu, forma, action va page-linklardan user-visible yo'l yasaydi."""
    parts = [navbar_tab, menu_column, menu_item]
    if action is not None:
        parts.extend(["Создать dropdown", action])
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
    ok,
    page_links=None,
    action=None,
    detail="",
):
    """Terminal va Allure uchun yagona strukturali forma natijasini yaratadi."""
    links = list(page_links or [])
    return {
        "number": number,
        "filial": filial,
        "navbar_tab": navbar_tab,
        "menu_column": menu_column,
        "menu_item": menu_item,
        "title": title,
        "page_links": links,
        "action": action,
        "track": form_navigation_track(
            navbar_tab=navbar_tab,
            menu_column=menu_column,
            menu_item=menu_item,
            page_links=links,
            action=action,
        ),
        "expected_path": expected_path or "—",
        "actual_url": actual_url,
        "ok": ok,
        "detail": detail,
    }


# ----------------------------------------------------------------------------------------------------------------------


def format_form_result(result):
    """Bitta forma natijasini user o'qiydigan ko'p qatorli matnga aylantiradi."""
    status = "✅ OCHILDI" if result["ok"] else "❌ XATO"
    menu = result["menu_column"] or "— (ustunsiz menu)"
    links = " → ".join(result["page_links"]) or "—"
    action = result["action"] or "—"
    lines = [
        f"[FORMA {result['number']:03d}] {status}",
        f"  Filial             : {result['filial']}",
        f"  Tab                : {result['navbar_tab']}",
        f"  Menu               : {menu}",
        f"  Menyu formasi      : {result['menu_item']}",
        f"  Tekshirilgan forma : {result['title']}",
        f"  Action             : {action}",
        f"  Page linklar       : {links}",
        f"  To'liq yo'l        : {result['track']}",
        f"  Kutilgan URL       : {result['expected_path']}",
        f"  Haqiqiy URL        : {result['actual_url']}",
    ]
    if result["detail"]:
        lines.append(f"  Xato               : {result['detail']}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------------------------------


def print_form_result(result):
    """Bitta forma natijasini terminalga strukturali ko'rinishda chiqaradi."""
    print(f"\n{format_form_result(result)}")


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


def first_operational_filial(page):
    """Legacy filial ro'yxatidan birinchi ``Администрирование`` bo'lmagan nomni oladi."""
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
    names = [
        name.strip()
        for name in filial_list.get_by_role("link").all_inner_texts()
        if name.strip()
    ]

    trigger.click(timeout=FORM_TIMEOUT)
    expect(menu).to_be_hidden(timeout=FORM_TIMEOUT)

    for name in names:
        if name != "Администрирование":
            return name
    raise AssertionError(
        "'Администрирование' bo'lmagan operatsion filial topilmadi. "
        f"Ko'ringan filiallar: {names}"
    )


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
        base.wait_for_loader(timeout=FORM_TIMEOUT)


# ----------------------------------------------------------------------------------------------------------------------


def open_menu_form(page, *, navbar_tab, menu_column, menu_item, page_links=None):
    """Legacy yoki A2 shell menyusidan parent formani va page-link zanjirini ochadi."""
    links = [] if page_links is None else list(page_links)
    track = form_navigation_track(
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        menu_item=menu_item,
        page_links=links,
    )

    with allure.step(f"Navigatsiya | Yo'l: {track}"):
        if "/a2/" in page.url:
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


def _visible_error_text(page):
    for selector in (
        "#biruniAlertExtended:visible",
        "#biruniAlert:visible",
        "[role='alert']:visible",
        ".alert-danger:visible",
    ):
        error = page.locator(selector).first
        try:
            if not error.is_visible():
                continue
            text = re.sub(r"\s+", " ", error.inner_text(timeout=1_000)).strip()
        except Exception:
            continue
        if text:
            return text
    return ""


# ----------------------------------------------------------------------------------------------------------------------


def expect_form_open(page, *, title, path=None):
    """Destination title/path, loader va ko'rinadigan Biruni error holatini tekshiradi."""
    if "/a2/" in page.url:
        AngularBasePage(page).expect_page(
            title=title,
            url=path,
            timeout=FORM_TIMEOUT,
        )
    else:
        BasePage(page).expect_page(
            heading=title,
            url=path,
            timeout=FORM_TIMEOUT,
        )

    canonical_path = canonical_form_path(page.url)
    if not canonical_path or canonical_path in {
        "dashboard",
        "trade/intro/dashboard",
    }:
        raise AssertionError(
            f"Forma canonical pathi ochilmadi: title='{title}', url={page.url}"
        )

    error_text = _visible_error_text(page)
    if error_text:
        raise AssertionError(
            f"Forma ochildi, lekin Biruni error ko'rindi: {error_text}; url={page.url}"
        )
    return canonical_path


# ----------------------------------------------------------------------------------------------------------------------


def _attach_failure_screenshot(page, number, name):
    try:
        allure.attach(
            page.screenshot(full_page=True),
            name=f"{number:03d}-{name}-failure",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------------------------------


def run_form_cases(page, cases, *, navbar_tab, start_number, filial, results):
    """Deklarativ forma caselarini tekshiradi va batch natijalarni ``results``ga yig'adi."""
    number = start_number
    for case in cases:
        title = case.get("title") or (
            case.get("page_links", [None])[-1]
            or case.get("action")
            or case["menu_item"]
        )
        label = case.get("label", title)
        step_title = form_step_title(
            number=number,
            filial=filial,
            navbar_tab=navbar_tab,
            menu_column=case["menu_column"],
            title=title,
        )
        with allure.step(step_title):
            try:
                if case.get("action") is not None:
                    open_create_dropdown_form(
                        page,
                        navbar_tab=navbar_tab,
                        menu_column=case["menu_column"],
                        menu_item=case["menu_item"],
                        action=case["action"],
                        page_links=case.get("page_links"),
                    )
                else:
                    open_menu_form(
                        page,
                        navbar_tab=navbar_tab,
                        menu_column=case["menu_column"],
                        menu_item=case["menu_item"],
                        page_links=case.get("page_links"),
                    )
                with allure.step(
                    f"Tekshiruv | Forma: {title} | Kutilgan URL: {case.get('path')}"
                ):
                    expect_form_open(
                        page,
                        title=title,
                        path=case.get("path"),
                    )
            except (AssertionError, PlaywrightTimeoutError) as exc:
                detail = re.sub(r"\s+", " ", str(exc)).strip()
                result = build_form_result(
                    number=number,
                    filial=filial,
                    navbar_tab=navbar_tab,
                    menu_column=case["menu_column"],
                    menu_item=case["menu_item"],
                    title=title,
                    expected_path=case.get("path"),
                    actual_url=page.url,
                    ok=False,
                    page_links=case.get("page_links"),
                    action=case.get("action"),
                    detail=detail,
                )
                results.append(result)
                _attach_failure_screenshot(page, number, label)
                allure.attach(
                    format_form_result(result),
                    name=f"{number:03d} | {title} | xato tafsilotlari",
                    attachment_type=allure.attachment_type.TEXT,
                )
                print_form_result(result)
            else:
                result = build_form_result(
                    number=number,
                    filial=filial,
                    navbar_tab=navbar_tab,
                    menu_column=case["menu_column"],
                    menu_item=case["menu_item"],
                    title=title,
                    expected_path=case.get("path"),
                    actual_url=page.url,
                    ok=True,
                    page_links=case.get("page_links"),
                    action=case.get("action"),
                )
                results.append(result)
                with allure.step(f"Natija: OCHILDI | Haqiqiy URL: {page.url}"):
                    pass
                print_form_result(result)
        number += 1
    return number


# ----------------------------------------------------------------------------------------------------------------------


def finish_form_results(results, *, terminal_reporter=None):
    """Allure/terminalga jamlanma chiqaradi va muammolar bo'lsa testni yiqitadi."""
    passed = sum(1 for result in results if result["ok"])
    failed = len(results) - passed
    lines = [
        "FORMA OCHILISH HISOBOTI",
        "=" * 80,
        f"Jami: {len(results)}",
        f"Ochildi: {passed}",
        f"Xato: {failed}",
        "",
    ]
    for result in results:
        status = "✅" if result["ok"] else "❌"
        line = (
            f"{status} {result['number']:03d} | Filial: {result['filial']} | "
            f"Tab: {result['navbar_tab']} | Menu: {result['menu_column'] or '—'} | "
            f"Menyu formasi: {result['menu_item']} | Forma: {result['title']} | "
            f"Yo'l: {result['track']} | Kutilgan URL: {result['expected_path']} | "
            f"Haqiqiy URL: {result['actual_url']}"
        )
        if result["detail"]:
            line += f" | Xato: {result['detail']}"
        lines.append(line)
    summary = "\n".join(lines)
    write_terminal_report(summary, terminal_reporter=terminal_reporter)
    allure.attach(
        summary,
        name="Forms hisoboti — filial, tab, menu, forma va URL",
        attachment_type=allure.attachment_type.TEXT,
    )

    if failed:
        failures = [
            (
                f"{result['number']:03d} | Filial: {result['filial']} | "
                f"Yo'l: {result['track']} | Kutilgan URL: {result['expected_path']} | "
                f"Haqiqiy URL: {result['actual_url']} | Xato: {result['detail']}"
            )
            for result in results
            if not result["ok"]
        ]
        raise AssertionError(
            f"{failed}/{len(results)} ta forma navigatsiyasida muammo:\n"
            + "\n".join(failures)
        )
