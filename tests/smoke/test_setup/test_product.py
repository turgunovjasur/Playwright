import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------

def test_product(page: Page, code) -> None:
    navigate_to(page, tab="Справочники", name="ТМЦ")

    expect(page.get_by_role("heading")).to_contain_text("ТМЦ")
    page.get_by_role("button", name="Создать").click()

    expect(page.get_by_role("heading")).to_contain_text("ТМЦ (создание)")
    page.locator("#anor66-input-text-name").get_by_role("textbox").fill(f"product-pw{code}")
    page.locator("#anor66-input-text-measure_short_name").get_by_role("textbox", name="Поиск").click()
    page.get_by_text("шт", exact=True).click()
    page.locator(".col-sm-12.mb-4 > .form-control").fill(f"code_product-pw{code}")
    expect(page.locator("b-page")).to_contain_text(f"sector-pw{code}")
    page.get_by_text("Товар", exact=True).click()

    page.get_by_role("button", name="Сохранить").click()
    expect(page.get_by_role("heading")).to_contain_text("ТМЦ")
    expect(page.locator("b-grid")).to_contain_text(f"code_product-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------
