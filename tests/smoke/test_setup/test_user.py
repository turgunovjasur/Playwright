import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_authorization import login
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def test_user(page: Page, code) -> None:
    switch_filial(page, name=f"filial-pw{code}")
    navigate_to(page, tab="Главное", name="Пользователи")

    page.get_by_role("button", name="Создать").click()

    page.get_by_role("textbox").nth(2).fill(f"user-pw{code}")
    page.locator("#new_password").fill("123456789")
    page.locator("b-input").filter(has_text="Выбранных Добавить").get_by_placeholder("Поиск").click()
    page.get_by_text(f"robot-pw{code}").click()
    page.locator("b-input").filter(has_text="Добавить Показать все").get_by_placeholder("Поиск").click()
    page.get_by_text(f"natural_person-pw{code}").click()
    expect(page.get_by_text("Админ", exact=True)).to_be_visible()

    page.get_by_role("button", name="Сохранить").click()

    expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
    expect(page.get_by_text(f"user-pw{code}@autotest")).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

def test_user_attach_form(page: Page, code) -> None:
    base_page = BasePage(page)

    expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
    page.get_by_text(f"natural_person-pw{code}").first.click()

    page.get_by_role("button", name="Просмотреть").click()
    expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()

    page.get_by_role("link", name=" Формы").click()

    # Формы
    page.get_by_role("tab", name="Формы").click()
    page.get_by_role("button", name="Доступные").click()
    page.get_by_role("button", name=" 50 /").click()
    page.get_by_role("link", name="1000").click()
    base_page.wait_for_loader()
    base_page.click_js()
    attach_and_check_list(page, check_text="нет данных")

    # Отчеты
    page.get_by_role("tab", name="Отчеты").click()
    page.get_by_role("button", name=" 50 /").click()
    page.get_by_role("link", name="1000").click()
    base_page.wait_for_loader()
    base_page.click_js()
    attach_and_check_list(page, check_text="нет данных")

    # Накладные
    page.get_by_role("tab", name="Накладные").click()
    base_page.wait_for_loader()
    base_page.click_js()
    attach_and_check_list(page, check_text="нет данных")

    # Внешние системы
    page.get_by_role("tab", name="Внешние системы").click()
    base_page.wait_for_loader()
    base_page.click_js()
    attach_and_check_list(page, check_text="нет данных")

    page.get_by_role("button", name="Закрыть").click()
    expect(page.get_by_role("heading")).to_contain_text("Пользователи")

# ----------------------------------------------------------------------------------------------------------------------

def attach_and_check_list(page, check_text):
    btn = page.get_by_role("button", name="Прикрепить")
    btn.wait_for(state="visible")
    btn.click()
    expect(page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)).to_be_visible()
    page.get_by_role("button", name="да").click()
    expect(page.locator("b-page")).to_contain_text(check_text)

# ----------------------------------------------------------------------------------------------------------------------

def verify_list_count(page, limit):
    cleaned_limit = limit.replace("/", " / ")
    expect(page.locator("b-page")).to_contain_text(cleaned_limit)

# ----------------------------------------------------------------------------------------------------------------------

def test_role(page: Page) -> None:
    expect(page.get_by_role("heading")).to_contain_text("Пользователи")

    page.get_by_role("link", name="Роли").click()
    expect(page.get_by_role("heading")).to_contain_text("Роли")

    page.get_by_text("Админ", exact=True).click()
    page.get_by_role("button", name="Изменить").click()

    expect(page.get_by_role("heading")).to_contain_text("Роль (изменение)")

    page.evaluate("document.getElementById('onboarding-launcher').style.display = 'none'")

    # Barcha o'chiq switchlarni yoqish
    clicked = 0
    while True:
        remaining = page.locator(".switch span").filter(has_text="нет")
        if remaining.count() == 0:
            break
        remaining.first.click()
        page.wait_for_timeout(150)
        clicked += 1

    page.get_by_role("button", name="Сохранить").click()

    base_page = BasePage(page)
    base_page.wait_for_loader(timeout=600_000)

    expect(page.get_by_role("heading")).to_contain_text("Роли")

# ----------------------------------------------------------------------------------------------------------------------

def test_role_attach_form(page: Page) -> None:
    page.get_by_text("Админ", exact=True).click()
    page.get_by_role("button", name="Просмотреть").click()
    page.get_by_role("link", name=" Формы").click()
    page.get_by_role("button", name="Доступ ко всем формам").click()
    page.get_by_role("link", name="Разрешить").click()
    page.get_by_role("button", name="да").click()

    base_page = BasePage(page)
    base_page.wait_for_loader(timeout=600_000)

    page.get_by_role("button", name="Доступные").click()
    expect(page.locator("b-page")).to_contain_text("нет данных")
    page.get_by_role("button", name="Закрыть").click()
    expect(page.get_by_role("heading")).to_contain_text("Роли")

# ----------------------------------------------------------------------------------------------------------------------

def test_change_password(page: Page, code) -> None:
    login(page, email=f"user-pw{code}@autotest", password="123456789")

    expect(page.locator(".alert-icon")).to_be_visible()

    page.locator("#current_password").fill("123456789")
    page.locator("#new_password").fill("123456789")
    page.locator("#rewritten_password").fill("123456789")

    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("button", name="да").click()

# ----------------------------------------------------------------------------------------------------------------------
