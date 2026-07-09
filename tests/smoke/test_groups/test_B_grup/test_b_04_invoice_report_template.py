import json
import re
import time
from pathlib import Path

import allure
import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from tests.smoke.flows.flow_authorization import authorization, logout
from tests.smoke.flows.flow_order.flow_order_list import flow_open_order_list, flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("Invoice Report Template"),
    allure.story("B-04 Custom Invoice Report"),
]


# Custom invoice report fayl download bo'lmaydi — OnlyOffice spreadsheet editorda
# (office.smartup.online) yangi popupda ochiladi; shuning uchun download emas, editor
# popup ochilishi tekshiriladi.
CUSTOM_REPORT_EDITOR_TIMEOUT = 120_000
EDITOR_POLL_INTERVAL = 500
ONLYOFFICE_EDITOR_HOST = "office.smartup.online"


def _search_grid(page, text):
    base = BasePage(page)
    search = page.locator('input[ng-model="o.searchValue"]').first
    expect(search).to_be_visible()
    search.click()
    search.press("ControlOrMeta+A")
    search.press("Backspace")
    search.fill(text)
    search.press("Enter")
    base.wait_for_loader(timeout=120_000)


def _grid_row_is_visible(page, text, timeout=2_000):
    try:
        expect(page.locator("b-grid .tbl-row").filter(has_text=text).first).to_be_visible(timeout=timeout)
        return True
    except (AssertionError, PlaywrightTimeoutError):
        return False


def _visible_error_texts(page):
    selectors = [
        "[role='alert']:visible",
        ".alert-danger:visible",
        ".toast-message:visible",
        ".toast:visible",
        ".swal2-popup:visible",
        ".text-danger:visible",
        ".invalid-feedback:visible",
    ]
    texts = []
    for selector in selectors:
        locator = page.locator(selector)
        try:
            count = min(locator.count(), 3)
        except Exception:
            continue
        for index in range(count):
            try:
                text = locator.nth(index).inner_text(timeout=1_000).strip()
            except Exception:
                continue
            if text and text not in texts:
                texts.append(text[:500])
    return texts


def _find_onlyoffice_editor_frame(report_page):
    """Report popupida OnlyOffice spreadsheet editor iframe'ini qaytaradi (topilmasa None)."""
    for frame in report_page.frames:
        url = frame.url or ""
        if ONLYOFFICE_EDITOR_HOST in url and "spreadsheeteditor" in url:
            return frame
    return None


def _attach_editor_open_diagnostics(report_page, template_name):
    frame_urls = []
    for frame in report_page.frames:
        try:
            frame_urls.append(frame.url)
        except Exception:
            pass

    try:
        body_text = report_page.locator("body").inner_text(timeout=1_000)
    except Exception:
        body_text = ""

    allure.attach(
        json.dumps(
            {
                "template_name": template_name,
                "report_page_url": report_page.url if not report_page.is_closed() else "<closed>",
                "frame_urls": frame_urls,
                "visible_errors": _visible_error_texts(report_page),
                "body_excerpt": body_text[:1500],
            },
            ensure_ascii=False,
            indent=2,
        ),
        name="custom-invoice-report-editor-diagnostics",
        attachment_type=allure.attachment_type.JSON,
    )

    try:
        allure.attach(
            report_page.screenshot(full_page=True),
            name="custom-invoice-report-editor-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


def _clickable_dropdown_option(option):
    clickable = option.locator(
        "xpath=ancestor-or-self::a | ancestor-or-self::button | ancestor-or-self::*[@role='menuitem']"
    )
    try:
        if clickable.count() > 0:
            return clickable.first
    except Exception:
        pass
    return option


def _open_custom_report_in_editor_and_assert(page, report_option, template_name):
    """
    Custom invoice report fayl download bo'lmaydi — option bosilganda yangi popup
    ochilib, report OnlyOffice spreadsheet editorida (office.smartup.online) ko'rsatiladi.
    Shu popup ochilib, OnlyOffice editor iframe yuklanganini tekshiradi.
    """
    with page.context.expect_page(timeout=60_000) as report_info:
        _clickable_dropdown_option(report_option).click(timeout=30_000)
    report_page = report_info.value

    try:
        report_page.wait_for_load_state("domcontentloaded", timeout=60_000)

        editor_frame = None
        deadline = time.monotonic() + (CUSTOM_REPORT_EDITOR_TIMEOUT / 1000)
        while time.monotonic() < deadline:
            if report_page.is_closed():
                break
            editor_frame = _find_onlyoffice_editor_frame(report_page)
            if editor_frame is not None:
                break
            report_page.wait_for_timeout(EDITOR_POLL_INTERVAL)

        if editor_frame is None:
            _attach_editor_open_diagnostics(report_page, template_name)
            raise AssertionError(
                f"{template_name} bosildi, lekin {CUSTOM_REPORT_EDITOR_TIMEOUT // 1000} sekund ichida "
                f"OnlyOffice spreadsheet editor ({ONLYOFFICE_EDITOR_HOST}) ochilmadi"
            )

        editor_frame.wait_for_load_state("domcontentloaded", timeout=60_000)
        report_page_url = report_page.url
        allure.attach(
            json.dumps(
                {
                    "template_name": template_name,
                    "report_page_url": report_page_url,
                    "editor_frame_url": editor_frame.url,
                },
                ensure_ascii=False,
                indent=2,
            ),
            name="custom-invoice-report-editor",
            attachment_type=allure.attachment_type.JSON,
        )
        return report_page_url
    finally:
        if not report_page.is_closed():
            report_page.close()


def run_b_group_create_custom_invoice_report_template(
    page,
    code,
    load_data,
    login=True,
):
    """
    Testcase:
    1. Mavjud admin bilan tizimga kirish.
    2. Главное -> Шаблоны накладных sahifasini ochish.
    3. Накладная (заказ) uchun Test_invoice_report-{code} template yaratish yoki mavjudini topish.
    4. data/test_invoice_report.xlsx faylini templatega upload qilish.
    5. Template'ni Админ rolega detach/attach qilib qayta ulash.
    6. Admin profildan chiqib user bilan kirish.
    7. Order list rowidagi Счет-фактуры buttonidan custom template OnlyOffice spreadsheet editorda ochilishini tekshirish.
    """
    base = BasePage(page)
    template_name = f"Test_invoice_report-{code}"
    form_name = "Накладная (заказ)"
    role_name = "Админ"
    template_file = Path("data/test_invoice_report.xlsx")

    if not template_file.exists():
        raise AssertionError(f"Invoice report template fayli topilmadi: {template_file}")

    if login:
        with allure.step("1 - Admin user tizimga kiradi"):
            authorization(page)
            expect(page.locator("body")).to_contain_text("Trade", timeout=120_000)

    with allure.step("2 - Шаблоны накладных sahifasida custom template tayyorlanadi"):
        base.navigate_to(tab="Главное", name="Шаблоны накладных")
        base.expect_page(url="template_list")
        expect(page.locator("body")).to_contain_text("Шаблоны накладных")

        _search_grid(page, template_name)
        if _grid_row_is_visible(page, template_name):
            template_row = page.locator("b-grid .tbl-row").filter(has_text=template_name).first
            expect(template_row).to_contain_text(form_name)
        else:
            page.locator('button[ng-click="add()"]:visible').click()
            expect(page).to_have_url(re.compile(r".*/setting\+add"))
            expect(page.locator("body")).to_contain_text("Настройки шаблонов")
            expect(page.locator("body")).to_contain_text("Файл шаблона")

            origin = page.locator('b-input[name="origin"] input').first
            expect(origin).to_be_visible()
            origin.click()
            origin.fill(form_name)
            option = page.locator('b-input[name="origin"] .hint-item').filter(has_text=form_name).first
            expect(option).to_be_visible(timeout=30_000)
            option.click()
            expect(origin).to_have_value(re.compile(re.escape(form_name)))

            name_input = page.locator('input[ng-model="d.name"]').first
            expect(name_input).to_be_visible()
            name_input.fill(template_name)
            expect(name_input).to_have_value(template_name)

            page.locator('input[type="file"][accept=".xlsx"]').set_input_files(template_file)
            expect(page.locator("body")).to_contain_text(template_file.name, timeout=60_000)

            page.locator('button[ng-click="save()"]').click()
            base.wait_for_loader(timeout=120_000)
            expect(page).to_have_url(re.compile(r".*/template_list"), timeout=60_000)

            _search_grid(page, template_name)
            template_row = page.locator("b-grid .tbl-row").filter(has_text=template_name).first
            expect(template_row).to_be_visible()
            expect(template_row).to_contain_text(form_name)
            expect(template_row).to_contain_text(template_file.name)
            expect(template_row).to_contain_text("Активный")

    with allure.step("3 - Template Админ rolega qayta attach qilinadi"):
        base.navigate_to(tab="Главное", name="Шаблоны накладных")
        base.expect_page(url="template_list")
        _search_grid(page, template_name)

        template_row = page.locator("b-grid .tbl-row").filter(has_text=template_name).first
        expect(template_row).to_be_visible()
        template_row.click()

        attach_roles_button = page.locator("button:visible").filter(has_text="Прикрепить роли").first
        expect(attach_roles_button).to_be_visible()
        attach_roles_button.click()
        expect(page).to_have_url(re.compile(r".*/template_role_list"))
        expect(page.locator("body")).to_contain_text(re.compile("прикрепленные", re.IGNORECASE))
        expect(page.locator("body")).to_contain_text(re.compile("доступные", re.IGNORECASE))

        page.locator("button").filter(has_text=re.compile(r"^\s*Прикрепленные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=120_000)
        _search_grid(page, role_name)
        if _grid_row_is_visible(page, role_name):
            role_row = page.locator("b-grid .tbl-row").filter(has_text=role_name).first
            role_row.click()
            detach_button = page.locator("button:visible").filter(has_text="Открепить").first
            expect(detach_button).to_be_visible()
            detach_button.click()
            try:
                base.confirm_biruni()
            except (AssertionError, PlaywrightTimeoutError):
                pass
            base.wait_for_loader(timeout=120_000)
            _search_grid(page, role_name)
            if _grid_row_is_visible(page, role_name, timeout=1_000):
                raise AssertionError(f"{role_name} role template'dan detach bo'lmadi")

        page.locator("button").filter(has_text=re.compile(r"^\s*Доступные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=120_000)
        _search_grid(page, role_name)
        role_row = page.locator("b-grid .tbl-row").filter(has_text=role_name).first
        expect(role_row).to_be_visible()
        role_row.click()

        attach_button = page.locator("button:visible").filter(has_text="Прикрепить").first
        expect(attach_button).to_be_visible()
        attach_button.click()
        try:
            base.confirm_biruni()
        except (AssertionError, PlaywrightTimeoutError):
            pass
        base.wait_for_loader(timeout=120_000)

        page.locator("button").filter(has_text=re.compile(r"^\s*Прикрепленные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=120_000)
        _search_grid(page, role_name)
        role_row = page.locator("b-grid .tbl-row").filter(has_text=role_name).first
        expect(role_row).to_be_visible()
        expect(role_row).to_contain_text("Активный")

        page.locator("button").filter(has_text=re.compile(r"^\s*Закрыть\s*$", re.IGNORECASE)).first.click()
        base.expect_page(url="template_list")
        expect(page.locator("body")).to_contain_text("Шаблоны накладных")

    with allure.step("4 - User order listda Счет-фактуры custom template OnlyOffice'da ochilishini tekshiradi"):
        created_order_client = load_data("b_group_consignment_order_client") or f"natural_client-pw{code}"

        logout(page)
        authorization(page, who="user", code=code)

        flow_open_order_list(page)
        expect(page.locator("#kt_content")).to_contain_text(created_order_client, timeout=120_000)
        flow_order_list(page, find_row=created_order_client)

        invoice_button = page.locator("button:visible, a:visible").filter(
            # Order-row buttoni "Счёт-фактуры" (ё) deb yoziladi; е/ё ikkalasini ham qabul qil.
            has_text=re.compile(r"Сч[её]т-?фактуры", re.IGNORECASE)
        ).first
        expect(invoice_button).to_be_visible()
        invoice_button.click()

        dropdown = page.locator(".dropdown-menu:visible, .dropdown:visible").filter(has_text=template_name).first
        expect(dropdown).to_be_visible()
        expect(dropdown).to_contain_text(template_name)

        report_option = page.locator(
            ".dropdown-menu:visible a:visible, "
            ".dropdown-menu:visible button:visible, "
            ".dropdown-menu:visible [role='menuitem']:visible, "
            ".dropdown-menu:visible span:visible"
        ).filter(
            has_text=re.compile(rf"^\s*{re.escape(template_name)}\s*$")
        ).first
        expect(report_option).to_be_visible()
        _open_custom_report_in_editor_and_assert(page, report_option, template_name)


@allure.title("B-04 - Custom invoice report template yaratish va orderda tekshirish")
def test_b_04_invoice_report_template(
    group_session_page,
    code,
    load_data,
):
    run_b_group_create_custom_invoice_report_template(
        group_session_page,
        code,
        load_data,
    )
