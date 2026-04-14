import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Mahsulot (TMC) yaratish va narx belgilash")
def test_product(page: Page, code) -> None:
    with allure.step("1 - TMC ro'yxatiga o'tish"):
        navigate_to(page, tab="Справочники", name="ТМЦ")
        expect(page.get_by_role("heading")).to_contain_text("ТМЦ")

    with allure.step("2 - Yangi mahsulot formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("ТМЦ (создание)")
        page.locator("#anor66-input-text-name").get_by_role("textbox").fill(f"product-pw{code}")
        page.locator("#anor66-input-text-measure_short_name").get_by_role("textbox", name="Поиск").click()
        page.get_by_text("шт", exact=True).click()
        page.locator(".col-sm-12.mb-4 > .form-control").fill(f"code_product-pw{code}")
        expect(page.locator("b-page")).to_contain_text(f"sector-pw{code}")
        page.get_by_text("Товар", exact=True).click()

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.get_by_role("heading")).to_contain_text("ТМЦ")
        expect(page.get_by_text(f"code_product-pw{code}")).to_be_visible()

    with allure.step("4 - Mahsulotga narx belgilash"):
        page.get_by_text(f"code_product-pw{code}").click()
        page.get_by_role("button", name="Установить цены").click()
        expect(page.get_by_role("heading")).to_contain_text("ТМЦ (установка цен)")
        page.locator("b-pg-grid").get_by_role("textbox").fill("7000")
        page.get_by_role("button", name="Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Сохранить?")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        expect(page.get_by_role("heading")).to_contain_text("ТМЦ")

# ----------------------------------------------------------------------------------------------------------------------