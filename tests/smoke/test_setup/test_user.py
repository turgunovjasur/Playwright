import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_authorization import login
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi yaratish")
def test_user(page: Page, code) -> None:
    with allure.step("1 - Foydalanuvchilar ro'yxatiga o'tish"):
        switch_filial(page, name=f"filial-pw{code}")
        navigate_to(page, tab="Главное", name="Пользователи")
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")

    with allure.step("2 - Yangi foydalanuvchi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Пользователь (создание)")
        page.get_by_role("textbox").nth(2).fill(f"user-pw{code}")
        page.locator("#new_password").fill("123456789")
        page.locator("b-input").filter(has_text="Выбранных Добавить").get_by_placeholder("Поиск").click()
        page.get_by_text(f"robot-pw{code}").click()
        page.locator("b-input").filter(has_text="Добавить Показать все").get_by_placeholder("Поиск").click()
        page.get_by_text(f"natural_person-pw{code}").click()
        expect(page.get_by_text("Админ", exact=True)).to_be_visible()

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")
        expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
        expect(page.get_by_text(f"user-pw{code}@autotest")).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga formalar ulash")
def test_user_attach_form(page: Page, code) -> None:
    base_page = BasePage(page)

    with allure.step("1 - Foydalanuvchi sahifasini ochish"):
        expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
        page.get_by_text(f"natural_person-pw{code}").first.click()
        page.get_by_role("button", name="Просмотреть").click()
        expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
        page.get_by_role("link", name=" Формы").click()

    with allure.step("2 - Формы ulash"):
        page.get_by_role("tab", name="Формы").click()
        page.get_by_role("button", name="Доступные").click()
        page.get_by_role("button", name=" 50 /").click()
        page.get_by_role("link", name="1000").click()
        base_page.wait_for_loader()
        base_page.click_js()
        base_page.wait_for_loader()
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        base_page.wait_for_loader()
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("3 - Отчеты ulash"):
        page.get_by_role("tab", name="Отчеты").click()
        page.get_by_role("button", name=" 50 /").click()
        page.get_by_role("link", name="1000").click()
        base_page.wait_for_loader()
        base_page.click_js()
        base_page.wait_for_loader()
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        base_page.wait_for_loader()
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("4 - Накладные ulash"):
        page.get_by_role("tab", name="Накладные").click()
        base_page.wait_for_loader()
        base_page.click_js()
        base_page.wait_for_loader()
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        base_page.wait_for_loader()
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("5 - Внешние системы ulash"):
        page.get_by_role("tab", name="Внешние системы").click()
        base_page.wait_for_loader()
        base_page.click_js()
        base_page.wait_for_loader()
        page.get_by_role("button", name="Прикрепить").click()
        expect(page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        base_page.wait_for_loader()
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("6 - Foydalanuvchilar ro'yxatiga qaytish"):
        page.get_by_role("button", name="Закрыть").click()
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page: Page) -> None:
    with allure.step("1 - Rollar ro'yxatiga o'tish"):
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")
        page.get_by_role("link", name="Роли").click()
        expect(page.get_by_role("heading")).to_contain_text("Роли")

    with allure.step("2 - Admin rolini o'zgartirish — barcha switchlarni yoqish"):
        page.get_by_text("Админ", exact=True).click()
        page.get_by_role("button", name="Изменить").click()
        expect(page.get_by_role("heading")).to_contain_text("Роль (изменение)")
        page.evaluate("document.getElementById('onboarding-launcher').style.display = 'none'")

        clicked = 0
        while True:
            remaining = page.locator(".switch span").filter(has_text="нет")
            if remaining.count() == 0:
                break
            remaining.first.click()
            page.wait_for_timeout(150)
            clicked += 1

    with allure.step("3 - Saqlash va natijani tekshirish"):
        page.get_by_role("button", name="Сохранить").click()
        BasePage(page).wait_for_loader(timeout=600_000)
        expect(page.get_by_role("heading")).to_contain_text("Роли")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin roliga barcha formalarga ruxsat berish")
def test_role_attach_form(page: Page) -> None:
    with allure.step("1 - Admin roli Formalar sahifasini ochish"):
        page.get_by_text("Админ", exact=True).click()
        page.get_by_role("button", name="Просмотреть").click()
        page.get_by_role("link", name=" Формы").click()

    with allure.step("2 - Barcha formalarga ruxsat berish"):
        page.get_by_role("button", name="Доступ ко всем формам").click()
        page.get_by_role("link", name="Разрешить").click()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")
        BasePage(page).wait_for_loader(timeout=600_000)

    with allure.step("3 - Ruxsatlar berilganini tekshirish"):
        page.get_by_role("button", name="Доступные").click()
        expect(page.locator("b-page")).to_contain_text("нет данных")
        page.get_by_role("button", name="Закрыть").click()
        expect(page.get_by_role("heading")).to_contain_text("Роли")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi parolini o'zgartirish")
def test_change_password(page: Page, code) -> None:
    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        login(page, email=f"user-pw{code}@autotest", password="123456789")
        expect(page.locator(".alert-icon")).to_be_visible()

    with allure.step("2 - Yangi parol kiritish va tasdiqlash"):
        page.locator("#current_password").fill("123456789")
        page.locator("#new_password").fill("123456789")
        page.locator("#rewritten_password").fill("123456789")
        page.get_by_role("button", name="Подтвердить").click()
        page.get_by_role("button", name="да").click()

# ----------------------------------------------------------------------------------------------------------------------
