import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Payment Type")]

# ----------------------------------------------------------------------------------------------------------------------

def test_payment_type(page: Page) -> None:
    navigate_to(page, tab="Справочники", name="Цены")
    expect(page.get_by_role("heading")).to_contain_text("Цены")

    page.get_by_role("link", name="Типы оплат").click()
    expect(page.get_by_role("heading")).to_contain_text("Типы оплат")

    page.get_by_role("button", name="Прикрепление").click()
    expect(page.get_by_role("heading")).to_contain_text("Тип оплат (прикрепление)")

    page.locator("input[bcheckall]").evaluate("el => el.click()")

    page.get_by_role("button", name="Прикрепить").click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Прикрепить типы оплат в количестве 4?")
    page.get_by_role("button", name="да").click()
    expect(page.locator("b-grid")).to_contain_text("нет данных")
    page.get_by_role("button", name="Закрыть").click()

    expect(page.locator("b-grid")).to_contain_text("Наличные деньги")
    expect(page.locator("b-grid")).to_contain_text("Перечисление")
    expect(page.locator("b-grid")).to_contain_text("Терминал")
    expect(page.locator("b-grid")).to_contain_text("Чековая книжка")

# ----------------------------------------------------------------------------------------------------------------------
