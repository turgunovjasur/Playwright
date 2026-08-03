import allure
from faker import Faker

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Legal Person")]

# ----------------------------------------------------------------------------------------------------------------------

fake_ru = Faker("ru_RU")


def run_legal_person(page, code, save_data):
    """Testcase: yangi yuridik shaxs (legal person) yaratish.

    1. Joriy company admini bilan authorization qilib, session code ni saqlash.
    2. Справочники -> Юридические лица ro'yxatini ochish.
    3. "Создать" -> Код (c_l_p_pw{code}) va Полное название (faker nomi) ni kiritish,
       Статус = Активный bo'lishini tekshirish.
    4. Saqlab, Юридические лица ro'yxatiga qaytishni tasdiqlash.
    5. Ro'yxatda yaratilgan yuridik shaxs kodi, nomi va "Активный" statusini tekshirish.
    6. View formasini ochib, yaratilgan qiymatlarni tekshirish.
    7. View formasini yopib, ro'yxatga qaytish.
    8. legal_person_code va legal_person_name ni data_store ga saqlash.
    """
    base = BasePage(page)
    legal_code = f"c_l_p_pw{code}"
    legal_name = f"{fake_ru.company()} legal_person-pw{code}"

    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")
        save_data("code", code)

    with allure.step("2 - Yuridik shaxslar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Юридические лица")
        base.expect_page(heading="Юридические лица", url="legal_person_list")

    with allure.step("3 - Yangi yuridik shaxs formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Юридическое лицо (создание)")
        base.input(label="Код", value=legal_code)
        base.input(label="Полное название", value=legal_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("4 - Saqlash va ro'yxatga qaytishni tasdiqlash"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить")
        base.expect_page(heading="Юридические лица")

    with allure.step("5 - Ro'yxatda yaratilgan yuridik shaxsni tekshirish"):
        base.grid_controller(search=legal_code)
        base.grid(legal_code, legal_name, "Активный", click=True)

    with allure.step("6 - Yuridik shaxs view formasini ochish va tekshirish"):
        base.click(name="Просмотреть")
        base.expect_page(heading="Юридическое лицо (просмотр)", url="legal_person_view")
        base.text(legal_code, legal_name, "Активный")

    with allure.step("7 - View formasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Юридические лица", url="legal_person_list")

    with allure.step("8 - Muhim ma'lumotlarni data storega saqlash"):
        save_data("legal_person_code", legal_code)
        save_data("legal_person_name", legal_name)


@allure.title("Yuridik shaxs yaratish")
def test_legal_person(page, code, save_data):
    run_legal_person(page, code, save_data)
