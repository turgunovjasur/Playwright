from playwright.sync_api import Page, expect

from flows.flow_authorization import authorization
from flows.flow_navigate import navigate_to, switch_filial
from pages.base_page import BasePage

# ----------------------------------------------------------------------------------------------------------------------

def test_user(page: Page, i) -> None:
    switch_filial(page, name=f"filial-pw{i}")
    navigate_to(page, tab="Главное", name="Пользователи")

    page.get_by_role("button", name="Создать").click()

    page.get_by_role("textbox").nth(2).fill(f"user-pw{i}")
    page.locator("#new_password").fill("123456789")
    page.locator("b-input").filter(has_text="Выбранных Добавить").get_by_placeholder("Поиск").click()
    page.get_by_text(f"robot-pw{i}").click()
    page.locator("b-input").filter(has_text="Добавить Показать все").get_by_placeholder("Поиск").click()
    page.get_by_text(f"natural_person-pw{i}").click()
    expect(page.get_by_text("Админ")).to_be_visible()

    page.get_by_role("button", name="Сохранить").click()

    expect(page.get_by_text(f"natural_person-pw{i}").first).to_be_visible()
    expect(page.get_by_text(f"user-pw{i}@autotest")).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

def test_user_attach_form(page: Page, i) -> None:
    base_page = BasePage(page)

    expect(page.get_by_text(f"natural_person-pw{i}").first).to_be_visible()
    page.get_by_text(f"natural_person-pw{i}").first.click()

    page.get_by_role("button", name="Просмотреть").click()
    expect(page.get_by_text(f"natural_person-pw{i}").first).to_be_visible()

    page.get_by_role("link", name=" Формы").click()

    # Формы
    switch_to_tab(page, name="Формы")
    page.get_by_role("button", name="Доступные").click()
    page.get_by_role("button", name=" 50 /").click()
    page.get_by_role("link", name="1000").click()
    expand_list(page, limit="167/167")
    base_page.click(click_js=True)
    attach_and_check_list(page, check_text="нет данных")

    # Отчеты
    switch_to_tab(page, name="Отчеты")
    page.get_by_role("button", name=" 50 /").click()
    page.get_by_role("link", name="1000").click()
    expand_list(page, limit="120/120")
    base_page.click(click_js=True)
    attach_and_check_list(page, check_text="нет данных")

    # Накладные
    switch_to_tab(page, name="Накладные")
    expand_list(page, limit="43/43")
    base_page.click(click_js=True)
    attach_and_check_list(page, check_text="нет данных")

    # Внешние системы
    switch_to_tab(page, name="Внешние системы")
    expand_list(page, limit="75/75")
    base_page.click(click_js=True)
    attach_and_check_list(page, check_text="нет данных")

    page.get_by_role("button", name="Закрыть").click()
    expect(page.get_by_role("heading")).to_contain_text("Пользователи")

# ----------------------------------------------------------------------------------------------------------------------
def attach_and_check_list(page, check_text):
    page.get_by_role("button", name="Прикрепить").click()
    page.get_by_role("button", name="да").click()
    expect(page.locator("b-page")).to_contain_text(check_text)
# ----------------------------------------------------------------------------------------------------------------------
def switch_to_tab(page, name):
    page.get_by_role("tab", name=name).click()
# ----------------------------------------------------------------------------------------------------------------------
def expand_list(page, limit):
    cleaned_limit = limit.replace("/", " / ")
    expect(page.locator("b-page")).to_contain_text(cleaned_limit)
# ----------------------------------------------------------------------------------------------------------------------

def test_role(page: Page, logger) -> None:
    i = 4059
    authorization(page, logger)

    switch_filial(page, name=f"filial-pw{i}")
    navigate_to(page, tab="Главное", name="Пользователи")

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

    logger.info(f"Jami {clicked} ta switch yoqildi")

    page.get_by_role("button", name="Сохранить").click()

    page.get_by_text("Админ", exact=True).wait_for(timeout=120_000)
    page.get_by_text("Админ", exact=True).click()


# ----------------------------------------------------------------------------------------------------------------------
