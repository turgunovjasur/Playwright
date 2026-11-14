import re
from urllib.parse import urlsplit

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.flow_setup.flow_license import open_admin_licenses, skip_license_purchase_if_needed
from tests.smoke.test_setup.flow_setup.flow_license import xtrade_license_rows
from utils.data_store import load_data, save_data
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

MANDATORY_LICENSE = "Smartup ERP: Базовый пользователь (Обязательный)"
REGULAR_LICENSE = "Smartup ERP: Базовый пользователь"
MANDATORY_LICENSE_ROW_TIMEOUT = 12_000
LICENSE_BALANCE_TIMEOUT = 20_000

# ----------------------------------------------------------------------------------------------------------------------

def run_buy_license(page, logger):
    """Testcase: Администрирование filialida litsenziya sotib olish.

    1. Администрирование filialida Лицензии sahifasini ochib, balansni tekshirish.
    2. Покупка formasini ochish.
    3. To'lovchi, kontrakt va bugungi sanani tanlab, mavjud litsenziya davrini hisoblatish.
    4. Majburiy license kerak bo'lsa to'liq oy uchun default 5, aks holda bugundan oddiy 1 dona tanlash.
    5. Tanlangan litsenziyani sotib olish va natija modalini yopish.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa — butun step skip qilinadi.
    switch_filial shu run_ ichida: setup zanjirida bu — Администрирование filialiga
    o'tuvchi birinchi qadam (chain shunga suyanadi). authorization esa test_buy_license
    wrapper'ida (standalone/debug uchun).
    """
    base = AutoBasePage(page)

    if skip_license_purchase_if_needed(logger, "Litsenziya sotib olish"):
        return

    with allure.step("1 - Litsenziyalar sahifasiga o'tish va balansni tekshirish"):
        open_admin_licenses(page, base)
        base.text(re.compile(r"\+\s*(?:[1-9][\d\s.,]*|0[.,]0*[1-9]\d*)"), timeout=LICENSE_BALANCE_TIMEOUT)
        logger.info("Balans musbat — Success")

    with allure.step("2 - Litsenziya sotib olish formasini ochish"):
        xtrade = urlsplit(page.url).path.startswith("/xtrade/a2/")
        if xtrade:
            base.tab("Лицензии и документы", section=True)
            base.wait_for_loader()
            rows = xtrade_license_rows(page)
            # The list can initially be empty; wait for its rendered data/empty state.
            page.locator("main").get_by_text(re.compile(r"^ERP users$|^Нет результатов$")).filter(visible=True).first.wait_for()
            before = set(rows.locator('[data-smt-col-key="created_on"]').all_inner_texts())
        base.tab("Покупка", section=True)
        base.wait_for_loader()
        base.expect_page(heading="Покупка 1")  # navigation: same-url - Purchase is a section of the already-open license page.

    with allure.step("3 - Sotib olish ma'lumotlarini tanlash"):
        base.b_input(label="Плательщик", value="AUTOTEST GWS", clear=True)
        base.b_input(label="Договор", value="Договор № bn от 01.01.2025", clear=True)
        base.date_picker(label="Дата начала", date="today")
        base.wait_for_loader()

    with allure.step("4 - License turini UI ro'yxatidan tanlash"):
        purchase_table = page.get_by_text("Тип лицензии", exact=True).filter(visible=True).locator(
            "xpath=ancestor::*[self::table or self::smt-data-table or self::smt-table][1]"
        )
        try:
            base.text(MANDATORY_LICENSE, root=purchase_table, timeout=MANDATORY_LICENSE_ROW_TIMEOUT)
        except (AssertionError, PlaywrightTimeoutError):
            license_row = base.grid(REGULAR_LICENSE, root=purchase_table)
            quantity = base.grid_cell(license_row, 5).locator("input:visible")
            expected_quantity = "1"
            quantity.fill(expected_quantity)
            base.grid_cell(license_row, 5, expect_value="1")
            logger.info("Oddiy bazaviy litsenziya tanlandi: miqdor 1")
        else:
            base.date_picker(label="Дата начала", date="first_day")
            base.wait_for_loader()
            license_row = base.grid(MANDATORY_LICENSE, root=purchase_table)
            expected_quantity = "5"
            base.grid_cell(license_row, 5, expect_value=expected_quantity)
            logger.info("Majburiy bazaviy litsenziya tanlandi: default miqdor 5")

    with allure.step("5 - Tanlangan litsenziyani sotib olish"):
        base.click(locator=page.get_by_role("button", name=re.compile(r"^(?:Купить|Покупка лицензий)$")).last)
        base.click(locator=page.get_by_text(re.compile(r"^Я ознакомился с тем")).first)
        base.confirm_biruni("Я ознакомился с тем", button_name="Да")
        base.wait_for_loader()
        base.expect_page(heading="Лицензии", url="biruni/kl/license_list")
        if xtrade:
            base.tab("Лицензии и документы", section=True)
            base.wait_for_loader()
            base.grid("ERP users", "Активный")
            cells = rows.locator('[data-smt-col-key="created_on"]').all_inner_texts()
            added = [value for value in cells if value not in before]
            assert len(added) == 1, "Yagona yangi ERP users litsenziyasi aniqlanmadi; xaridni takrorlamang"
            new_row = rows.filter(has=page.get_by_text(added[0], exact=True))
            assert new_row.locator('[data-smt-col-key="status_name"]').inner_text() == "Активный"
            assert new_row.locator('[data-smt-col-key="quant"]').inner_text() == expected_quantity
            save_data("ui_purchased_license", {"code": str(load_data("code")), "created_on": added[0]})
        else:
            base.grid("ERP users", "Активный")
        logger.info("Litsenziya olindi")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Litsenziya sotib olish")
def test_buy_license(page, logger):
    authorization(page, who="admin")
    run_buy_license(page, logger)
