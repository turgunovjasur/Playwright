import time
from playwright.sync_api import Page, expect
from flows.flow_navigate import navigate_to, switch_filial

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
    time.sleep(1)

# ----------------------------------------------------------------------------------------------------------------------

def test_user_attach_form(page: Page, i) -> None:

    # page.goto("https://smartup.online/#/!11ksdjl0sp/anor/mr/user_list")
    expect(page.get_by_text(f"natural_person-pw{i}").first).to_be_visible()
    page.get_by_text(f"natural_person-pw{i}").first.click()

    page.get_by_role("button", name="Просмотреть").click()
    expect(page.get_by_text(f"natural_person-pw{i}").first).to_be_visible()

    page.get_by_role("link", name=" Формы").click()
    page.get_by_role("button", name="Доступные").click()
    page.get_by_role("button", name=" 50 /").click()
    page.get_by_role("link", name="1000").click()
    page.wait_for_load_state("networkidle")

    checkbox = page.locator(".checkbox").first
    checkbox.evaluate("el => el.click()")
    # time.sleep(1)
    # if not page.get_by_role("button", name="Прикрепить").is_visible():
    #     checkbox.evaluate("el => el.click()")
    expect(page.get_by_role("button", name="Прикрепить")).to_be_visible()
    page.get_by_role("button", name="Прикрепить").click()
    page.get_by_role("button", name="да").click()
    expect(page.locator("b-page")).to_contain_text("нет данных")
    time.sleep(1)

# ----------------------------------------------------------------------------------------------------------------------
