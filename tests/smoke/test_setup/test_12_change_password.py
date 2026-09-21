import os

import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import (
    dashboard,
    login,
    current_company_code,
)
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_change_password(page, code):
    """Testcase: foydalanuvchi parolini "Пароль (изменение)" formasida tasdiqlash.

    1. user-pw{code} sifatida kirib, majburiy parol o'zgartirish formasi ochilishini tekshirish.
    2. Login ortidan ochilgan e'lon oynasi bo'lsa yopib, forma ochiq qolishini tekshirish.
    3. Текущий/Новый/Подтверждение парол maydonlarini to'ldirib "Подтвердить" bilan tasdiqlash.
    4. Password-change sessiyasini davom ettirmasdan, user bilan yangidan login qilib dashboardni tekshirish.

    Bu run_ o'zi user sifatida login qiladi (authorization wrapper'da chaqirilmaydi).
    "Пароль (изменение)" — user qo'shilganda (birinchi login), user paroli o'zgartirilganda
    yoki profildan "Изменить пароль" orqali ochiladigan bir xil forma (URL biruni/md/change_password).
    """
    user_password = os.environ["USER_PASSWORD"]
    base = AutoBasePage(page)
    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        user_email = f"user-pw{code}@{current_company_code()}"
        login(page, email=user_email, password=user_password)
        base.expect_page(url="change_password")
        base.text(root=".alert-icon")

    with allure.step("2 - Parol formasini to'sgan e'lon oynasini yopish"):
        announcement = page.locator(".announcement_widget")
        if announcement.is_visible():
            announcement.locator(".announcement_dismiss").click()
            expect(announcement).to_be_hidden()

    with allure.step("3 - Yangi parol kiritish va tasdiqlash"):
        base.input(label="Текущий пароль", value=user_password)
        base.input(label="Новый пароль", value=user_password, press_tab=True)
        base.input(label="Подтверждение пароля", value=user_password)

        base.click(name="Подтвердить")
        base.confirm_biruni()

    with allure.step("4 - Parol tasdiqlangandan keyin majburiy qayta login"):
        login(page, email=user_email, password=user_password)
        dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi parolini o'zgartirish")
def test_change_password(page, code):
    run_change_password(page, code)
