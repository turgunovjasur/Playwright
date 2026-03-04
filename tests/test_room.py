import time
from playwright.sync_api import Page, expect
from flows.flow_navigate import navigate_to, switch_filial

# ----------------------------------------------------------------------------------------------------------------------

def test_room(page: Page, i) -> None:
    switch_filial(page, name=f"filial-pw{i}")
    navigate_to(page, tab="Справочники", name="Рабочие зоны")

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox").first.fill(f"code_room_pw{i}")
    page.get_by_role("textbox").nth(1).fill(f"room-pw{i}")
    expect(page.get_by_text("Активный").first).to_be_visible()

    page.get_by_role("button", name="Сохранить").click()
    expect(page.get_by_text(f"room-pw{i}")).to_be_visible()
    expect(page.get_by_text(f"code_room_pw{i}")).to_be_visible()
    time.sleep(1)

# ----------------------------------------------------------------------------------------------------------------------
