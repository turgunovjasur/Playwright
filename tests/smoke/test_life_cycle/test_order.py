import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_authorization import authorization_user
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Life Cycle"), allure.story("Order")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Sotuv buyurtmasini yaratish")
def test_order_add(page: Page, code) -> None:
    authorization_user(page, code)
    with allure.step("1 - Zakazlar ro'yxatiga o'tish"):
        navigate_to(page, tab="Продажа", name="Заказы")
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

    with allure.step("2 - Yangi zakaz yaratish va mijozni tanlash"):
        page.get_by_role("button", name="Создать", exact=True).click()
        expect(page.locator("h6.text-dark")).to_contain_text("Заказ (создание)")
        page.get_by_role("button", name=" Далее").click()
        expect(page.locator("h6.text-dark")).to_contain_text("Заказ (создание)")

    with allure.step("3 - Mahsulot qo'shish"):
        page.locator("b-pg-grid").get_by_role("textbox", name="Поиск").click()
        page.get_by_text(f"code_product-pw{code}").click()
        page.locator('[ng-model="item.quantity"]').first.fill("1")
        page.get_by_role("button", name=" Далее").click()
        expect(page.locator("h6.text-dark")).to_contain_text("Заказ (создание)")

    with allure.step("4 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name=" Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Сохранить?")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

# ----------------------------------------------------------------------------------------------------------------------