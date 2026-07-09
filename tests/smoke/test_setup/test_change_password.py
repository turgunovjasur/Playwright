import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import login, USER_PASS, user_email_for
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_change_password(page, code):
    """Testcase: foydalanuvchi parolini "Пароль (изменение)" formasida tasdiqlash.

    1. user-pw{code} sifatida kirib, majburiy parol o'zgartirish formasi ochilishini tekshirish.
    2. Текущий/Новый/Подтверждение парол maydonlarini to'ldirib "Подтвердить" bilan tasdiqlash.

    Bu run_ o'zi user sifatida login qiladi (authorization wrapper'da chaqirilmaydi).
    "Пароль (изменение)" — user qo'shilganda (birinchi login), user paroli o'zgartirilganda
    yoki profildan "Изменить пароль" orqali ochiladigan bir xil forma (URL biruni/md/change_password).
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        login(page, email=user_email_for(code), password=USER_PASS)
        expect(page.locator(".alert-icon")).to_be_visible()

    with allure.step("2 - Yangi parol kiritish va tasdiqlash"):
        # BasePage.input ishlatilmaydi: u fokus uchun input_el.click() qiladi, bu formada esa
        # parol-validatsiya qoidalari (<label class="checkbox text-success">) inputlar ustiga
        # tushib click'ni bloklaydi (MCP 2026-07). .fill() pointer click qilmay fokuslaydi.
        page.locator("#current_password").fill(USER_PASS)
        page.locator("#new_password").fill(USER_PASS)
        page.locator("#rewritten_password").fill(USER_PASS)
        page.get_by_role("button", name="Подтвердить").click()
        base.confirm_biruni()

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi parolini o'zgartirish")
def test_change_password(page, code):
    run_change_password(page, code)
