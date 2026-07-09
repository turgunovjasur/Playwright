import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization, USER_PASS, user_email_for
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_user(page, code):
    """Testcase: yangi foydalanuvchi (user) yaratish.

    1. Пользователи ro'yxatini ochish.
    2. "Создать" -> Логин (user-pw{code}), Пароль, Физическое лицо (natural_person-pw{code})
       va Штат (robot-pw{code}) ni to'ldirish; Штат tanlanganda "Админ" roli ko'rinishini tekshirish.
    3. Saqlab, ro'yxatda user login-email (user_email_for(code)) va "Активный" statusini tekshirish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da (run_room shu filialga o'tgan),
    shuning uchun bu yerda switch_filial qilinmaydi — standalone debug uchun filialga o'tish
    test_user wrapper'ida bajariladi.
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")

    with allure.step("2 - Yangi foydalanuvchi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Пользователь (создание)")
        base.input(label="Логин", value=f"user-pw{code}")
        base.input(label="Пароль", value=USER_PASS)
        base.b_input(label="Физическое лицо", value=f"natural_person-pw{code}")
        base.b_input(label="Штат", value=f"robot-pw{code}")
        # Штат tanlanganda uning roli "Роли" read-only view'ida (.form-view) auto ko'rinadi — input emas.
        roli_group = page.locator("div.form-group").filter(has=page.get_by_text("Роли", exact=True))
        expect(roli_group.locator(".form-view")).to_contain_text("Админ")

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.expect_page(heading="Пользователи")
        base.grid(f"natural_person-pw{code}", user_email_for(code), "Активный")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi yaratish")
def test_user(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_user(page, code)
