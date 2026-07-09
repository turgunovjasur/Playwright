import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_modal import fill_nps_survey
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Price Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_price_type_uzb(page, code, logger, save_data=None):
    base = BasePage(page)
    with allure.step("0 - NPS Survey modalini o'tkazib yuborish"):
        fill_nps_survey(page, logger)

    with allure.step("1 - Narxlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - Yangi narx turi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Цена (создание)")
        base.input(label="Код", value=f"code_price_type_uzb_pw{code}")
        base.input(label="Название", value=f"Price Type UZB-pw{code}")
        page.locator("b-input").filter(has_text="Выбранных").get_by_placeholder("Поиск").click()
        page.get_by_text(f"room-pw{code}").click()
        page.locator("b-input").filter(has_text=f"room-pw{code} 1 Выбранных").get_by_placeholder("Поиск").press("Escape")
        expect(page.get_by_text("Цена продажи")).to_be_visible()

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.wait_for_loader()
        base.expect_page(heading="Цены")
        page.get_by_role("searchbox", name="Поиск").fill(f"Price Type UZB-pw{code}")
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        expect(page.get_by_text(f"Price Type UZB-pw{code}").first).to_be_visible()
        if save_data:
            save_data("price_type_name_UZB", f"Price Type UZB-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Narx turi (UZB) yaratish")
def test_price_type_uzb(page, code, logger, save_data):
    run_price_type_uzb(page, code, logger, save_data=save_data)
