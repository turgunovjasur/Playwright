import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Sector")]

# ----------------------------------------------------------------------------------------------------------------------

def test_sector(page: Page, code) -> None:
    navigate_to(page, tab="Справочники", name="ТМЦ")
    expect(page.get_by_role("heading")).to_contain_text("ТМЦ")

    page.get_by_role("link", name="Наборы ТМЦ").click()
    expect(page.get_by_role("heading")).to_contain_text("Наборы ТМЦ")
    page.get_by_role("button", name="Создать").click()

    expect(page.get_by_role("heading")).to_contain_text("Набор ТМЦ (создание)")
    page.get_by_role("textbox").first.fill(f"code_sector_pw{code}")
    page.get_by_role("textbox").nth(1).fill(f"sector-pw{code}")

    page.get_by_role("textbox", name="Поиск").click()
    page.get_by_text(f"room-pw{code}").click()
    page.get_by_role("button", name="Сохранить").click()

    expect(page.get_by_role("heading")).to_contain_text("Наборы ТМЦ")
    expect(page.locator("b-grid")).to_contain_text(f"code_sector_pw{code}")

# ----------------------------------------------------------------------------------------------------------------------
