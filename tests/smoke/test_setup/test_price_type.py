import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_modal import fill_nps_survey
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Price Type")]

# ----------------------------------------------------------------------------------------------------------------------

def test_price_type_uzb(page: Page, code, logger) -> None:
    fill_nps_survey(page, logger)

    navigate_to(page, tab="Справочники", name="Цены")

    expect(page.get_by_role("heading")).to_contain_text("Цены")
    page.get_by_role("button", name="Создать").click()

    page.locator("#anor183-input-text-code").get_by_role("textbox").fill(f"code_price_type_uzb_pw{code}")
    page.locator("#anor183-input-text-name").get_by_role("textbox").fill(f"Price Type UZB-pw{code}")

    page.locator("b-input").filter(has_text="Выбранных").get_by_placeholder("Поиск").click()
    page.get_by_text(f"room-pw{code}").click()
    page.locator("b-input").filter(has_text=f"room-pw{code} 1 Выбранных").get_by_placeholder("Поиск").press("Escape")

    expect(page.get_by_text("Цена продажи")).to_be_visible()
    page.get_by_role("button", name="Сохранить").click()

    page.get_by_role("searchbox", name="Поиск").fill(f"Price Type UZB-pw{code}")
    page.get_by_role("searchbox", name="Поиск").press("Enter")

    expect(page.get_by_text(f"Price Type UZB-pw{code}").first).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------
