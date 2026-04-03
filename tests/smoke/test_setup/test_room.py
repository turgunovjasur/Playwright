import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def test_room(page: Page, code) -> None:
    switch_filial(page, name=f"filial-pw{code}")
    navigate_to(page, tab="Справочники", name="Рабочие зоны")

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox").first.fill(f"code_room_pw{code}")
    page.get_by_role("textbox").nth(1).fill(f"room-pw{code}")
    expect(page.get_by_text("Активный").first).to_be_visible()

    page.get_by_role("button", name="Сохранить").click()
    expect(page.get_by_text(f"room-pw{code}")).to_be_visible()
    expect(page.get_by_text(f"code_room_pw{code}")).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------
