import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Filial")]
FILIAL_SAVE_LOADER_TIMEOUT = 60_000

# ----------------------------------------------------------------------------------------------------------------------


def run_filial(page, code, load_data, save_data):
    """Testcase: yangi filial (tashkilot / Организация) yaratish.

    1. Главное -> Организации ro'yxatini ochish.
    2. "Создать" -> Название (filial-pw{code}), Базовая валюта (Узбекский сум) va
       Юридическое лицо (legal_person_code orqali qidirib) ni to'ldirish.
    3. Saqlab, Организации ro'yxatiga qaytishni tasdiqlash.
    4. Ro'yxatda yaratilgan filial nomi, legal_person_code va "Активный" statusini tekshirish.
    5. Filial view formasini ochib, yaratilgan qiymatlar va filial IDni tekshirish.
    6. View formasini yopib, ro'yxatga qaytish.
    7. Filial ID, nomi, valyutasi va bog'langan legal person ma'lumotlarini data_store ga saqlash.
    """
    base = BasePage(page)
    filial_name = f"filial-pw{code}"
    legal_person_code = f"c_l_p_pw{code}"
    legal_person_name = load_data("legal_person_name")
    filial_currency = "Узбекский сум"

    with allure.step("1 - Tashkilotlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Организации")
        base.expect_page(heading="Организации")

    with allure.step("2 - Yangi tashkilot formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Организация (создание)")
        base.input(label="Название", value=filial_name)
        base.b_input(label="Базовая валюта", value=filial_currency, expect_value=filial_currency)
        base.confirm_biruni("Продолжить?")
        base.b_input(label="Юридическое лицо", value=legal_person_code, search_text=legal_person_code, expect_value=legal_person_name)

    with allure.step("3 - Saqlash va ro'yxatga qaytishni tasdiqlash"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить")
        base.wait_for_loader()
        base.expect_page(heading="Организации")

    with allure.step("4 - Ro'yxatda yaratilgan filialni tekshirish"):
        base.grid_controller(search=filial_name)
        base.grid(filial_name, legal_person_code, "Активный")
        page.reload()
        base.wait_for_loader(timeout=FILIAL_SAVE_LOADER_TIMEOUT)

    with allure.step("5 - Filial view formasini ochish va tekshirish"):
        base.grid_controller(search=filial_name)
        base.grid(filial_name, legal_person_code, "Активный", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Организация (просмотр)", url="filial_view?filial_id=")
        base.text(filial_name, filial_currency, legal_person_code, legal_person_name, "Активный")
        filial_id = query_int_from_url(page.url, "filial_id")

    with allure.step("6 - View formasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Организации")

    with allure.step("7 - Muhim ma'lumotlarni data storega saqlash"):
        save_data("filial_id", filial_id)
        save_data("filial_name", filial_name)
        save_data("filial_currency", filial_currency)
        save_data("filial_legal_person_code", legal_person_code)
        save_data("filial_legal_person_name", legal_person_name)


@allure.title("Filial (tashkilot) yaratish")
def test_filial(page, code, load_data, save_data):
    authorization(page, who="admin")
    run_filial(page, code, load_data, save_data)
