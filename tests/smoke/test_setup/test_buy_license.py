import allure
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import attach_license_policy_skip_note, license_policy_disabled
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

MANDATORY_LICENSE = "Smartup ERP: Базовый пользователь (Обязательный)"
REGULAR_LICENSE = "Smartup ERP: Базовый пользователь"
MANDATORY_LICENSE_ROW_TIMEOUT = 3_000

# ----------------------------------------------------------------------------------------------------------------------

def run_buy_license(page, logger):
    """Testcase: Администрирование filialida litsenziya sotib olish.

    1. Администрирование filialida Лицензии sahifasini ochib, balansni tekshirish.
    2. Покупка formasida to'lovchi, kontrakt va sanani tanlash.
    3. Majburiy license qatori visible bo'lsa default 5 bilan, aks holda oddiy qatorni 1 dona sotib olish.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa — butun step skip qilinadi.
    switch_filial shu run_ ichida: setup zanjirida bu — Администрирование filialiga
    o'tuvchi birinchi qadam (chain shunga suyanadi). authorization esa test_buy_license
    wrapper'ida (standalone/debug uchun).
    """
    base = BasePage(page)

    if license_policy_disabled():
        attach_license_policy_skip_note(logger, "Litsenziya sotib olish")
        return

    with allure.step("1 - Litsenziyalar sahifasiga o'tish va balansni tekshirish"):
        base.switch_filial(name="Администрирование")
        base.navigate_to(tab="Главное", name="Лицензии")
        base.expect_page(heading="Лицензии")
        base.text(root=page.locator('p.text-success[ng-if="q.balance > 0"]'))
        logger.info("Balans musbat — Success")

    with allure.step("2 - Sotib olish ma'lumotlarini tanlash"):
        page.get_by_role("link", name="Покупка").click()
        base.wait_for_loader()
        base.b_input(label="Плательщик", value="AUTOTEST GWS", clear=True)
        base.b_input(label="Договор", value="Договор № bn от 01.01.2025", clear=True)
        base.date_picker("Дата начала", date="today")
        base.wait_for_loader()

    with allure.step("3 - License turini UI ro'yxatidan tanlash"):
        purchase_table = page.locator("table:visible").filter(
            has=page.get_by_role("columnheader", name="Тип лицензии", exact=True)
        ).first
        try:
            base.text(MANDATORY_LICENSE, root=purchase_table, timeout=MANDATORY_LICENSE_ROW_TIMEOUT)
            license_row = purchase_table.get_by_role("row").filter(
                has=page.get_by_text(MANDATORY_LICENSE, exact=True)
            ).first
            quantity = license_row.get_by_role("textbox").first
            expect(quantity).to_have_value("5")
            logger.info("Majburiy bazaviy litsenziya tanlandi: default miqdor 5")
        except (AssertionError, PlaywrightTimeoutError):
            license_row = purchase_table.get_by_role("row").filter(
                has=page.get_by_text(REGULAR_LICENSE, exact=True)
            ).first
            expect(license_row).to_be_visible()
            quantity = license_row.get_by_role("textbox").first
            quantity.fill("1")
            expect(quantity).to_have_value("1")
            logger.info("Oddiy bazaviy litsenziya tanlandi: miqdor 1")

    with allure.step("4 - Tanlangan litsenziyani sotib olish"):
        page.get_by_role("button", name="Купить").click()
        terms = page.locator("span").filter(has_text="Я ознакомился с тем").first
        expect(terms).to_be_visible()
        terms.click()
        page.get_by_role("button", name="Да", exact=True).click()
        base.wait_for_loader()
        logger.info("Litsenziya olindi")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Litsenziya sotib olish")
def test_buy_license(page, logger):
    authorization(page, who="admin")
    run_buy_license(page, logger)
