import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial
from utils.base_page import BasePage

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

def test_room_attachment(page: Page, code) -> None:
    authorization(page, email=f"user-pw{code}@autotest", password="123456789")
    navigate_to(page, tab="Справочники", name="Рабочие зоны")

    expect(page.get_by_role("heading")).to_contain_text("Рабочие зоны")
    page.get_by_text(f"room-pw{code}").click()
    page.get_by_role("button", name="Прикрепление").click()

    expect(page.locator("#kt_content")).to_contain_text(f"Рабочая зона (прикрепление): room-pw{code}")
    
    page.get_by_role("link", name="Типы оплат").click()
    expect(page.locator("b-page")).to_contain_text("Типы оплат")
    page.get_by_role("button", name="Доступные").click()
    BasePage(page).wait_for_loader()
    page.locator('(//b-grid[@name="table_payment_type"]//label)[1]').dispatch_event("click")
    expect(page.locator('(//b-grid[@name="table_payment_type"]//input[@type="checkbox"])[1]')).to_be_checked()
    expect(page.get_by_role("button", name="Прикрепить")).to_be_visible()
    page.get_by_role("button", name="Прикрепить").click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Прикрепить 4?")
    page.get_by_role("button", name="да", exact=True).click()
    expect(page.locator("b-page")).to_contain_text("нет данных")

    page.get_by_role("link", name="Склады").click()
    expect(page.locator("b-page")).to_contain_text("Склады")
    page.get_by_role("button", name="Доступные").click()
    BasePage(page).wait_for_loader()
    page.locator('(//b-grid[@name="table_warehouse"]//label)[1]').dispatch_event("click")
    expect(page.locator('(//b-grid[@name="table_warehouse"]//input[@type="checkbox"])[1]')).to_be_checked()
    page.get_by_role("button", name="Прикрепить").click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Прикрепить 1?")
    page.get_by_role("button", name="да", exact=True).click()
    expect(page.locator("b-page")).to_contain_text("нет данных")

    page.get_by_role("link", name="Кассы").click()
    expect(page.locator("b-page")).to_contain_text("Кассы")
    page.get_by_role("button", name="Доступные").click()
    BasePage(page).wait_for_loader()
    page.locator('(//b-grid[@name="table_cashbox"]//label)[1]').dispatch_event("click")
    expect(page.locator('(//b-grid[@name="table_cashbox"]//input[@type="checkbox"])[1]')).to_be_checked()
    page.get_by_role("button", name="Прикрепить").click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Прикрепить 1?")
    page.get_by_role("button", name="да", exact=True).click()
    expect(page.locator("b-page")).to_contain_text("нет данных")

    page.get_by_role("button", name="Закрыть").click()
    expect(page.get_by_role("heading")).to_contain_text("Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------
