import allure
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import skip_license_flow_if_needed
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

MANDATORY_LICENSE = "Smartup ERP: Базовый пользователь (Обязательный)"
REGULAR_LICENSE = "Smartup ERP: Базовый пользователь"
MANDATORY_LICENSE_ROW_TIMEOUT = 3_000
LICENSE_BALANCE_TIMEOUT = 5_000

# ----------------------------------------------------------------------------------------------------------------------

def run_buy_license(page, logger):
    """Testcase: Администрирование filialida litsenziya sotib olish.

    1. Администрирование filialida Лицензии sahifasini ochib, balansni tekshirish.
    2. Покупка formasini ochish.
    3. To'lovchi, kontrakt va boshlanish sanasini tanlash.
    4. Majburiy license qatori visible bo'lsa default 5 bilan, aks holda oddiy qatorni 1 dona tanlash.
    5. Tanlangan litsenziyani sotib olish va natija modalini yopish.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa — butun step skip qilinadi.
    switch_filial shu run_ ichida: setup zanjirida bu — Администрирование filialiga
    o'tuvchi birinchi qadam (chain shunga suyanadi). authorization esa test_buy_license
    wrapper'ida (standalone/debug uchun).
    """
    base = BasePage(page)

    if skip_license_flow_if_needed(logger, "Litsenziya sotib olish"):
        return

    with allure.step("1 - Litsenziyalar sahifasiga o'tish va balansni tekshirish"):
        base.switch_filial(name="Администрирование")
        base.navigate_to(tab="Главное", name="Лицензии")
        base.expect_page(heading="Лицензии")
        base.text(root=page.locator('p.text-success[ng-if="q.balance > 0"]'), timeout=LICENSE_BALANCE_TIMEOUT)
        logger.info("Balans musbat — Success")

    with allure.step("2 - Litsenziya sotib olish formasini ochish"):
        base.click(name="Покупка", role="link")
        base.wait_for_loader()
        base.expect_page(heading="Покупка 1")

    with allure.step("3 - Sotib olish ma'lumotlarini tanlash"):
        base.b_input(label="Плательщик", value="AUTOTEST GWS", clear=True)
        base.b_input(label="Договор", value="Договор № bn от 01.01.2025", clear=True)
        base.date_picker(label="Дата начала", date="today")
        base.wait_for_loader()

    with allure.step("4 - License turini UI ro'yxatidan tanlash"):
        purchase_table = page.locator("table:visible").filter(has=page.get_by_role("columnheader", name="Тип лицензии", exact=True)).first
        try:
            base.text(MANDATORY_LICENSE, root=purchase_table, timeout=MANDATORY_LICENSE_ROW_TIMEOUT)
            license_row = purchase_table.get_by_role("row").filter(has=page.get_by_text(MANDATORY_LICENSE, exact=True)).first
            quantity = license_row.get_by_role("textbox").first
            expect(quantity).to_have_value("5")
            logger.info("Majburiy bazaviy litsenziya tanlandi: default miqdor 5")
        except (AssertionError, PlaywrightTimeoutError):
            license_row = purchase_table.get_by_role("row").filter(has=page.get_by_text(REGULAR_LICENSE, exact=True)).first
            expect(license_row).to_be_visible()
            quantity = license_row.get_by_role("textbox").first
            quantity.fill("1")
            expect(quantity).to_have_value("1")
            logger.info("Oddiy bazaviy litsenziya tanlandi: miqdor 1")

    with allure.step("5 - Tanlangan litsenziyani sotib olish"):
        base.click(name="Купить")
        terms = page.locator("span").filter(has_text="Я ознакомился с тем").first
        expect(terms).to_be_visible()
        terms.click()
        base.click(name="Да", exact=True)
        base.wait_for_loader()
        # base.close_biruni_alert()
        logger.info("Litsenziya olindi")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Litsenziya sotib olish")
def test_buy_license(page, logger):
    authorization(page, who="admin")
    run_buy_license(page, logger)
