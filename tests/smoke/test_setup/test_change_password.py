import allure
from tests.smoke.flows.flow_authorization import (
    USER_PASS,
    dashboard,
    login,
    user_email_for,
)
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_change_password(page, code):
    """Testcase: foydalanuvchi parolini "Пароль (изменение)" formasida tasdiqlash.

    1. user-pw{code} sifatida kirib, majburiy parol o'zgartirish formasi ochilishini tekshirish.
    2. Текущий/Новый/Подтверждение парол maydonlarini to'ldirib "Подтвердить" bilan tasdiqlash.
    3. Password-change sessiyasini davom ettirmasdan, user bilan yangidan login qilib dashboardni tekshirish.

    Bu run_ o'zi user sifatida login qiladi (authorization wrapper'da chaqirilmaydi).
    "Пароль (изменение)" — user qo'shilganda (birinchi login), user paroli o'zgartirilganda
    yoki profildan "Изменить пароль" orqali ochiladigan bir xil forma (URL biruni/md/change_password).
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        login(page, email=user_email_for(code), password=USER_PASS)
        base.text(root=".alert-icon")

    with allure.step("2 - Yangi parol kiritish va tasdiqlash"):
        base.input(label="Текущий пароль", value=USER_PASS)
        base.input(label="Новый пароль", value=USER_PASS, press_tab=True)
        base.input(label="Подтверждение пароля", value=USER_PASS)

        page.get_by_role("button", name="Подтвердить").click()
        base.confirm_biruni()

    with allure.step("3 - Parol tasdiqlangandan keyin majburiy qayta login"):
        login(page, email=user_email_for(code), password=USER_PASS)
        dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi parolini o'zgartirish")
def test_change_password(page, code):
    run_change_password(page, code)
