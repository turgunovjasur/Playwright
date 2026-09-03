import allure

from tests.smoke.flows.flow_authorization import authorization, USER_PASS, user_email_for
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_user(page, code, save_data):
    """Testcase: yangi foydalanuvchi (user) yaratish.

    1. Пользователи ro'yxatini ochish.
    2. "Создать" -> Логин (user-pw{code}), Пароль, Физическое лицо (natural_person-pw{code})
       va Штат (robot-pw{code}) ni to'ldirish; Штат tanlanganda "Админ" roli ko'rinishini tekshirish.
    3. Saqlab, ro'yxatda user login-email (user_email_for(code)) va "Активный" statusini tekshirish.
    4. User view formasini ochib, yaratilgan qiymatlarni tekshirish.
    5. View URLdan user IDni olib, data_store ga saqlash.
    6. View formasini yopib, Пользователи ro'yxatiga qaytish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da (run_room shu filialga o'tgan),
    shuning uchun bu yerda switch_filial qilinmaydi — standalone debug uchun filialga o'tish
    test_user wrapper'ida bajariladi.
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")

    with allure.step("2 - Yangi foydalanuvchi formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Пользователь (создание)")
        base.input(label="Логин", value=f"user-pw{code}")
        base.input(label="Пароль", value=USER_PASS)
        base.b_input(label="Физическое лицо", value=f"natural_person-pw{code}")
        base.b_input(label="Штат", value=f"robot-pw{code}")
        base.form_view(label="Роли", expect_value="Админ")
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Пользователи")
        base.grid(f"natural_person-pw{code}", user_email_for(code), "Активный")

    with allure.step("4 - Foydalanuvchi view formasini ochish va tekshirish"):
        base.grid(f"natural_person-pw{code}", user_email_for(code), "Активный", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Пользователь (просмотр)", url="user_view?user_id=")
        base.text(f"natural_person-pw{code}", user_email_for(code), "Активный")

    with allure.step("5 - User IDni olish va saqlash"):
        save_data("user_id", query_int_from_url(page.url, "user_id"))

    with allure.step("6 - View formasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Пользователи")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchi yaratish")
def test_user(page, code, save_data):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_user(page, code, save_data)
