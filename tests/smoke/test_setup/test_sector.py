import allure
from playwright.sync_api import expect
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Sector")]

# ----------------------------------------------------------------------------------------------------------------------

def run_sector(page, code):
    base = BasePage(page)
    with allure.step("1 - TMC to'plamlari ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")
        page.get_by_role("link", name="Наборы ТМЦ").click()
        base.expect_page(heading="Наборы ТМЦ")

    with allure.step("2 - Yangi to'plam formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Набор ТМЦ (создание)")
        base.input(label="Код", value=f"code_sector_pw{code}")
        base.input(label="Название", value=f"sector-pw{code}")
        page.get_by_role("textbox", name="Поиск").click()
        page.get_by_text(f"room-pw{code}").click()

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.wait_for_loader()
        base.expect_page(heading="Наборы ТМЦ")
        expect(page.locator("b-grid")).to_contain_text(f"code_sector_pw{code}")
        expect(page.locator("b-grid")).to_contain_text(f"sector-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("TMC to'plami (sector) yaratish")
def test_sector(page, code):
    run_sector(page, code)
