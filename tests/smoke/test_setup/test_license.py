import allure
from tests.smoke.flows.flow_authorization import authorization, logout
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial
from utils.base_page import BasePage
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

# ----------------------------------------------------------------------------------------------------------------------

def test_buy_license(page: Page, logger) -> None:
    logout(page)
    authorization(page)
    switch_filial(page, name="Администрирование")
    navigate_to(page, tab="Главное", name="Лицензии")

    expect(page.get_by_role("heading", name="Лицензии")).to_be_visible()

    balance_locator = page.locator('p.text-success[ng-if="q.balance > 0"]')

    try:
        balance_locator.wait_for(state="visible", timeout=5_000)
        logger.info("Balans musbat — Success")
    except Exception:
        logger.fail("Balans musbat emas yoki element topilmadi!")

    page.get_by_role("link", name="Покупка").click()

    base_page = BasePage(page)
    base_page.select_option(ng_model="purchase.payer.name", option_text="AUTOTEST GWS", clear=True)
    base_page.select_option(ng_model="purchase.contract_name", option_text="Договор № bn от 01.01.2025", clear=True)
    base_page.select_date(ng_model="purchase.begin_date", option="first")
    base_page.wait_for_loader()

    if page.get_by_role("cell", name="Smartup ERP: Базовый пользователь (Обязательный)").is_visible():
        expect(page.get_by_role("table")).to_contain_text("Smartup ERP: Базовый пользователь")
        page.locator('input[ng-model="license.count"]').first.fill("1")
        page.get_by_role("button", name="Купить").click()
        page.locator("span").filter(has_text="Я ознакомился с тем").first.click()
        page.get_by_role("button", name="Да").click()
        base_page.wait_for_loader()
        logger.info("Majburiy litsenziya olindi")
    else:
        row = page.locator('tr[ng-repeat="license in purchase.licenses"]').filter(
            has_text="Smartup ERP: Базовый пользователь")
        row.locator('input[ng-model="license.count"]').fill("1")
        page.get_by_role("button", name="Купить").click()
        page.locator("span").filter(has_text="Я ознакомился с тем").first.click()
        page.get_by_role("button", name="Да").click()
        base_page.wait_for_loader()
        logger.info("Oddiy litsenziya olindi")

# ----------------------------------------------------------------------------------------------------------------------

def test_attach_license(page: Page, code, logger) -> None:
    page.get_by_role("link", name="Лицензии и документы").click()
    expect(page.locator("b-page")).to_contain_text("Лицензии и документы")

    page.get_by_text("ERP users").first.click()
    page.get_by_role("button", name="Прикрепить пользователей").click()

    expect(page.get_by_role("heading")).to_contain_text("Прикрепленные пользователи")

    try:
        no_data = page.locator('b-grid[name="table"]').get_by_text("нет данных")
        no_data.wait_for(state="visible", timeout=5_000)
    except PlaywrightTimeoutError:
        page.locator("input[bcheckall]").evaluate("el => el.click()")
        page.get_by_role("button", name="Открепить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Открепить пользователей в количестве")
        page.get_by_role("button", name="да").click()
        expect(page.locator("#kt_content")).to_contain_text("нет данных")
    else:
        page.get_by_role("button", name="Доступные").click()
        page.get_by_role("searchbox", name="Поиск").fill(f"natural_person-pw{code}")
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        page.get_by_text(f"natural_person-pw{code}").first.click()
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.get_by_role("heading", name="Прикрепить пользователя")).to_be_visible()
        page.get_by_role("button", name="да").click()
        page.get_by_role("button", name="Закрыть").click()

# ----------------------------------------------------------------------------------------------------------------------
