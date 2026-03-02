import random
from playwright.sync_api import Page, expect
from tests.flow_navigate import navigate_to, switch_filial
from tests.flow_authorization import authorization


def test_filial(page: Page) -> None:
    authorization(page)
    switch_filial(page)
    navigate_to(page, tab="Главное", name="Организации")

    i = random.randint(1000, 9999)

    page.get_by_role("button", name="Создать").click()
    page.get_by_role("textbox").first.fill(f"filial-pw{i}")
    page.locator("b-input").filter(has_text="Код Валюта Добавить Показать все").get_by_placeholder("Поиск").click()
    page.get_by_text("Узбекский сум").click()
    page.get_by_role("button", name="да").click()
    page.locator("b-input").filter(has_text="Код Название Добавить Показать все").get_by_placeholder("Поиск").click()
    page.locator("b-input").filter(has_text="Код Название Добавить Показать все Поиск").get_by_placeholder("Поиск").fill(f"cod_lg_pw{i}")
    page.get_by_text(f"cod_lg_pw{i}").click()
    expect(page.locator("b-input").filter(has_text=f"Код Название cod_lg_pw{i}").get_by_placeholder("Поиск")).to_have_value(f"legal_person-pw{i}")

    page.get_by_role("button", name="Сохранить").click()
    page.get_by_role("button", name="да").click()

    page.get_by_role("searchbox", name="Поиск").fill(f"filial-pw{i}")
    page.get_by_role("searchbox", name="Поиск").press("Enter")

    expect(page.get_by_text(f"cod_lg_pw{i}")).to_be_visible()
    expect(page.get_by_text(f"filial-pw{i}")).to_be_visible()