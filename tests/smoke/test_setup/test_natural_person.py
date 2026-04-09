import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def test_natural_person(page: Page, code) -> None:
    switch_filial(page, name=f"filial-pw{code}")
    navigate_to(page, tab="Справочники", name="Физические лица")

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox", name="Поиск").first.click()
    page.locator("b-input").filter(has_text="Поиск").get_by_placeholder("Поиск").fill(f"natural_person-pw{code}")
    expect(page.get_by_text("Активный")).to_be_visible()
    page.get_by_role("button", name="Сохранить").click()
    page.get_by_role("button", name="да").click()
    expect(page.get_by_text(f"natural_person-pw{code}", exact=True)).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

def test_natural_person_for_client_1(page: Page, code) -> None:
    navigate_to(page, tab="Справочники", name="Физические лица")

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox", name="Поиск").first.click()
    page.locator("b-input").filter(has_text="Поиск").get_by_placeholder("Поиск").fill(f"natural_client-pw{code}")
    expect(page.get_by_text("Активный")).to_be_visible()
    page.get_by_text("Клиент", exact=True).click()

    page.get_by_role("button", name="Сохранить").click()
    page.get_by_role("button", name="да").click()
    expect(page.get_by_text(f"natural_client-pw{code}", exact=True)).to_be_visible()

    navigate_to(page, tab="Справочники", name="Клиенты")
    expect(page.get_by_role("heading")).to_contain_text("Клиенты")
    expect(page.locator("b-grid")).to_contain_text(f"natural_client-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------
