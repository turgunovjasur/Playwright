from datetime import datetime

import allure
import pytest
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, select_b_input_option
from utils.base_page import BasePage

pytestmark = [allure.epic("Report Group"), allure.feature("Integration Report"), allure.story("Integration Two")]

SETTING_CHECKBOXES = ["d.edit_person", "d.ignore_updated_deals", "d.show_owner_person_code", "d.send_all_deals"]
OPTIONAL_ALERT_TIMEOUT = 1_500
ALERT_CLOSE_TIMEOUT = 10_000
SETTINGS_BUTTON_TIMEOUT = 60_000

# (exchange_mode value, yuklanadigan fayl prefiksi, begin_date kerakmi)
EXCHANGE_MODES = [
    ("CRMOrder", "import_order", False),
    ("CRMDespatch", "export_order", True),
    ("CRMOrderStatus", "import_order_status", False),
    ("CRMInput", "export_input", True),
]


# ----------------------------------------------------------------------------------------------------------------------

def _close_alert_if_open(page):
    """Generate'dan keyin chiqishi mumkin bo'lgan biruni xato modalini yopadi va yo'qolishini kutadi."""
    for selector in ("#biruniAlertExtended", "#biruniAlert"):
        alert = page.locator(selector)
        try:
            alert.wait_for(state="visible", timeout=OPTIONAL_ALERT_TIMEOUT)
            page.keyboard.press("Escape")
            alert.wait_for(state="hidden", timeout=ALERT_CLOSE_TIMEOUT)
            return
        except Exception:
            continue


# ----------------------------------------------------------------------------------------------------------------------

def run_report_integration_two_check(page, code, load_data, login=True):
    """Report-06: Integration Two (монолит) — sozlamalar va 4 ta exchange rejimi uchun .xml yuklab olish.

    integration_two faqat "Администрирование" filialida ochiladi, shuning uchun sahifa ochishdan oldin
    har doim shu filialga o'tiladi (group chain boshqa report testlar uchun filial-pw{code}ga o'tib qo'ygan
    bo'lishi mumkin). Тип цены user_setup saqlagan data_store kalitidan olinadi.

    Qadamlar (Allure da 6 step):
      1. Администрирование filialiga o'tib integration_two sahifasini ochish
      2. Настройки -> company_id, user, url, ед. измерения, Тип цены (data_store), Характеристика ТМЦ + 4 checkbox -> Сохранить
      3. import_order (CRMOrder) -> .xml yuklab olish
      4. export_order (CRMDespatch) -> begin_date + .xml yuklab olish
      5. import_order_status (CRMOrderStatus) -> .xml yuklab olish
      6. export_input (CRMInput) -> begin_date + .xml yuklab olish
    """
    base = BasePage(page)
    price_type_name = load_data("price_type_name_UZB") if load_data else None
    if not price_type_name:
        pytest.skip("price_type_name_UZB data_store'da yo'q — avval user_setup runnerini ishga tushiring")

    if login:
        authorization(page, who="admin")

    with allure.step("1 - Администрирование filialiga o'tib Integration Two sahifasini ochish"):
        base.switch_filial(name="Администрирование")
        base, _, rest = page.url.partition("#/")
        session_token = rest.split("/", 1)[0]
        page.goto(f"{base}#/{session_token}/trade/rep/integration/integration_two")
        expect(page.locator('button[ng-click="q.show_setting = true"]')).to_be_visible(timeout=SETTINGS_BUTTON_TIMEOUT)

    with allure.step("2 - Настройки: filtrlar va checkboxlar -> saqlash"):
        page.locator('button[ng-click="q.show_setting = true"]').click()
        base.input(ng_model="d.company_id", value="8605425")
        base.input(ng_model="d.user_name", value="123")
        base.input(ng_model="d.url", value="https")
        base.input(ng_model="d.unit_of_quant_measurement", value="шт")
        base.input(ng_model="d.unit_of_box_measurement", value="шт")
        select_b_input_option(page, "price_types", price_type_name, search_text=str(code))
        select_b_input_option(page, "product_groups", "Группа")
        for ng_model in SETTING_CHECKBOXES:
            base.checkbox(ng_model=ng_model, checked=True)
        save_btn = page.locator('button[ng-click="save()"]')
        save_btn.click()
        expect(save_btn).to_be_hidden()

    for i, (value, file_prefix, needs_date) in enumerate(EXCHANGE_MODES, start=3):
        with allure.step(f"{i} - {file_prefix} ({value}) yuklab olish"):
            page.locator(f'label:has(input[value="{value}"])').click()
            if needs_date:
                begin_date = page.locator('input[ng-model="d.begin_date"]')
                if begin_date.count() > 0 and begin_date.first.is_visible():
                    begin_date.first.fill(datetime.now().strftime("%d.%m.%Y"))
                    page.keyboard.press("Escape")
            generate_and_verify_download(
                page,
                page.get_by_role("button", name="Генерировать", exact=True),
                expected_prefix=file_prefix,
                save_name=f"{file_prefix}_pw{code}.xml",
            )
            _close_alert_if_open(page)
