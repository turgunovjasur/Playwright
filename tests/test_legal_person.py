import random
import time
from playwright.sync_api import Page, expect
from tests.flow_navigate import navigate_to, switch_filial
from tests.flow_authorization import authorization


def test_legal_person(page: Page) -> None:
    authorization(page)
    switch_filial(page)
    navigate_to(page, tab="Справочники", name="Юридические лица")

    i = random.randint(1000, 9999)

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox").nth(4).fill(f"legal_person-pw{i}")
    page.get_by_role("textbox").first.fill(f"cod_lg_pw{i}")
    expect(page.get_by_text("Активный")).to_be_visible()

    page.get_by_role("button", name="Сохранить").click()
    page.get_by_role("button", name="да").click()

    page.get_by_role("searchbox", name="Поиск").fill(f"cod_lg_pw{i}")
    page.get_by_role("searchbox", name="Поиск").press("Enter")

    expect(page.get_by_text(f"cod_lg_pw{i}")).to_be_visible()
    expect(page.get_by_text(f"legal_person-pw{i}").first).to_be_visible()
    time.sleep(1)