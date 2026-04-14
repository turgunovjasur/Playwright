import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Payment Type")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("To'lov turlarini tizimga ulash")
def test_payment_type(page: Page) -> None:
    with allure.step("1 - To'lov turlari ro'yxatiga o'tish"):
        navigate_to(page, tab="Справочники", name="Цены")
        expect(page.get_by_role("heading")).to_contain_text("Цены")
        page.get_by_role("link", name="Типы оплат").click()
        expect(page.get_by_role("heading")).to_contain_text("Типы оплат")

    with allure.step("2 - Barcha to'lov turlarini tanlash va ulash"):
        page.get_by_role("button", name="Прикрепление").click()
        expect(page.get_by_role("heading")).to_contain_text("Тип оплат (прикрепление)")
        page.locator("input[bcheckall]").evaluate("el => el.click()")
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Прикрепить типы оплат в количестве 4?")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        expect(page.locator("b-grid")).to_contain_text("нет данных")
        page.get_by_role("button", name="Закрыть").click()

    with allure.step("3 - To'lov turlari ro'yxatida ko'rinishini tekshirish"):
        expect(page.locator("b-grid")).to_contain_text("Наличные деньги")
        expect(page.locator("b-grid")).to_contain_text("Перечисление")
        expect(page.locator("b-grid")).to_contain_text("Терминал")
        expect(page.locator("b-grid")).to_contain_text("Чековая книжка")

# ----------------------------------------------------------------------------------------------------------------------