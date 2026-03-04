import time
from playwright.sync_api import Page, expect
from flows.flow_navigate import navigate_to, switch_filial


# ----------------------------------------------------------------------------------------------------------------------

def test_natural_person(page: Page, i) -> None:
    switch_filial(page, name=f"filial-pw{i}")
    navigate_to(page, tab="Справочники", name="Физические лица")

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox", name="Поиск").first.click()
    page.locator("b-input").filter(has_text="Поиск").get_by_placeholder("Поиск").fill(f"natural_person-pw{i}")
    expect(page.get_by_text("Активный")).to_be_visible()
    page.get_by_role("button", name="Сохранить").click()
    page.get_by_role("button", name="да").click()
    expect(page.get_by_text(f"natural_person-pw{i}", exact=True)).to_be_visible()
    time.sleep(1)

# ----------------------------------------------------------------------------------------------------------------------
