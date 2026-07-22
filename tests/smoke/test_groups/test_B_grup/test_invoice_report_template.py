import json
import re
from pathlib import Path

import allure
import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from tests.smoke.flows.flow_authorization import authorization, logout
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("Invoice Report Template"),
    allure.story("Custom Invoice Report"),
]


# Custom invoice report fayl download bo'lmaydi — OnlyOffice spreadsheet editorda
# (office.smartup.online) yangi popupda ochiladi; shuning uchun download emas, editor
# popup ochilishi tekshiriladi.
ONLYOFFICE_EDITOR_HOST = "office.smartup.online"
INVOICE_SHORT_CHECK_TIMEOUT = 1_000
INVOICE_COMPONENT_TIMEOUT = 30_000
INVOICE_REPORT_LOAD_TIMEOUT = 60_000
INVOICE_PAGE_TRANSITION_TIMEOUT = 120_000


def _grid_row_is_visible(page, text):
    return BasePage(page).grid(text, is_visible=True)


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
                text = locator.nth(index).inner_text(timeout=INVOICE_SHORT_CHECK_TIMEOUT).strip()
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
        body_text = report_page.locator("body").inner_text(timeout=INVOICE_SHORT_CHECK_TIMEOUT)
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
    with page.context.expect_page(timeout=INVOICE_REPORT_LOAD_TIMEOUT) as report_info:
        _clickable_dropdown_option(report_option).click(timeout=INVOICE_COMPONENT_TIMEOUT)
    report_page = report_info.value

    try:
        report_page.wait_for_load_state("domcontentloaded", timeout=INVOICE_REPORT_LOAD_TIMEOUT)

        editor_frame = _find_onlyoffice_editor_frame(report_page)
        if editor_frame is None and not report_page.is_closed():
            try:
                editor_frame = report_page.wait_for_event(
                    "framenavigated",
                    predicate=lambda frame: (
                        ONLYOFFICE_EDITOR_HOST in (frame.url or "")
                        and "spreadsheeteditor" in (frame.url or "")
                    ),
                    timeout=INVOICE_PAGE_TRANSITION_TIMEOUT,
                )
            except PlaywrightTimeoutError:
                editor_frame = _find_onlyoffice_editor_frame(report_page)

        if editor_frame is None:
            _attach_editor_open_diagnostics(report_page, template_name)
            raise AssertionError(
                f"{template_name} bosildi, lekin {INVOICE_PAGE_TRANSITION_TIMEOUT // 1000} sekund ichida "
                f"OnlyOffice spreadsheet editor ({ONLYOFFICE_EDITOR_HOST}) ochilmadi"
            )

        editor_frame.wait_for_load_state("domcontentloaded", timeout=INVOICE_REPORT_LOAD_TIMEOUT)
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


def run_create_custom_invoice_report_template(
    page,
    code,
    load_data,
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

    with allure.step("1 - Admin user tizimga kiradi"):
        authorization(page, who="admin")

    with allure.step("2 - Шаблоны накладных sahifasida custom template tayyorlanadi"):
        base.navigate_to(tab="Главное", name="Шаблоны накладных")
        base.expect_page(url="template_list")
        base.text("Шаблоны накладных", root="body")

        base.grid_controller(search=template_name)
        if _grid_row_is_visible(page, template_name):
            base.grid(template_name, form_name)
        else:
            page.locator('button[ng-click="add()"]:visible').click()
            base.expect_page(url="setting+add")
            base.text("Настройки шаблонов", "Файл шаблона", root="body")

            origin = page.locator('b-input[name="origin"] input').first
            base.input(locator=origin, value=form_name)
            option = page.locator('b-input[name="origin"] .hint-item').filter(has_text=form_name).first
            expect(option).to_be_visible(timeout=INVOICE_COMPONENT_TIMEOUT)
            option.click()
            base.input(locator=origin, expect_value=re.compile(re.escape(form_name)))

            base.input(ng_model="d.name", value=template_name)

            page.locator('input[type="file"][accept=".xlsx"]').set_input_files(template_file)
            base.text(template_file.name, root="body", timeout=INVOICE_REPORT_LOAD_TIMEOUT)

            base.save_and_expect_heading(
                "Шаблоны накладных",
                exact_button=False,
                timeout=INVOICE_PAGE_TRANSITION_TIMEOUT,
                location_hint="B-04 invoice template add form",
            )
            base.expect_page(url="template_list", timeout=INVOICE_REPORT_LOAD_TIMEOUT)

            base.grid_controller(search=template_name)
            base.grid(template_name, form_name, template_file.name, "Активный")

    with allure.step("3 - Template Админ rolega qayta attach qilinadi"):
        base.navigate_to(tab="Главное", name="Шаблоны накладных")
        base.expect_page(url="template_list")
        base.grid_controller(search=template_name)

        base.grid(template_name, click=True)

        attach_roles_button = page.locator("button:visible").filter(has_text="Прикрепить роли").first
        expect(attach_roles_button).to_be_visible()
        attach_roles_button.click()
        base.expect_page(url="template_role_list")
        base.text(
            re.compile("прикрепленные", re.IGNORECASE),
            re.compile("доступные", re.IGNORECASE),
            root="body",
        )

        page.locator("button").filter(has_text=re.compile(r"^\s*Прикрепленные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=INVOICE_PAGE_TRANSITION_TIMEOUT)
        base.grid_controller(search=role_name)
        if _grid_row_is_visible(page, role_name):
            base.grid(role_name, click=True)
            detach_button = page.locator("button:visible").filter(has_text="Открепить").first
            expect(detach_button).to_be_visible()
            detach_button.click()
            base.confirm_biruni_if_visible(timeout=INVOICE_SHORT_CHECK_TIMEOUT)
            base.wait_for_loader(timeout=INVOICE_PAGE_TRANSITION_TIMEOUT)
            base.grid_controller(search=role_name)
            if _grid_row_is_visible(page, role_name):
                raise AssertionError(f"{role_name} role template'dan detach bo'lmadi")

        page.locator("button").filter(has_text=re.compile(r"^\s*Доступные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=INVOICE_PAGE_TRANSITION_TIMEOUT)
        base.grid_controller(search=role_name)
        base.grid(role_name, click=True)

        attach_button = page.locator("button:visible").filter(has_text="Прикрепить").first
        expect(attach_button).to_be_visible()
        attach_button.click()
        base.confirm_biruni_if_visible(timeout=INVOICE_SHORT_CHECK_TIMEOUT)
        base.wait_for_loader(timeout=INVOICE_PAGE_TRANSITION_TIMEOUT)

        page.locator("button").filter(has_text=re.compile(r"^\s*Прикрепленные\s*$", re.IGNORECASE)).first.click()
        base.wait_for_loader(timeout=INVOICE_PAGE_TRANSITION_TIMEOUT)
        base.grid_controller(search=role_name)
        base.grid(role_name, "Активный")

        page.locator("button").filter(has_text=re.compile(r"^\s*Закрыть\s*$", re.IGNORECASE)).first.click()
        base.expect_page(url="template_list")
        base.text("Шаблоны накладных", root="body")

    with allure.step("4 - User order listda Счет-фактуры custom template OnlyOffice'da ochilishini tekshiradi"):
        created_order_client = load_data("b_group_consignment_order_client")
        if not created_order_client:
            raise AssertionError("B-group order client topilmadi. Avval runnerdagi B-01 testni run qiling.")

        logout(page)
        authorization(page, who="user", code=code)

        base.navigate_to(tab="Продажа", name="Заказы")
        base.text(
            created_order_client,
            root="#kt_content",
            timeout=INVOICE_PAGE_TRANSITION_TIMEOUT,
        )
        flow_order_list(page, find_row=created_order_client)

        invoice_button = page.locator("button:visible, a:visible").filter(
            # Order-row buttoni "Счёт-фактуры" (ё) deb yoziladi; е/ё ikkalasini ham qabul qil.
            has_text=re.compile(r"Сч[её]т-?фактуры", re.IGNORECASE)
        ).first
        expect(invoice_button).to_be_visible()
        invoice_button.click()

        dropdown = page.locator(".dropdown-menu:visible, .dropdown:visible").filter(has_text=template_name).first
        base.text(template_name, root=dropdown)

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


@allure.title("Custom invoice report template yaratish va orderda tekshirish")
def test_invoice_report_template(page, code, load_data):
    run_create_custom_invoice_report_template(page, code, load_data)
