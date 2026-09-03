import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_modal import fill_nps_survey
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Price Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_price_type_usa(page, code, save_data):
    """Testcase: USA narx turini yaratib, ish zonasiga biriktirish.

    1. Справочники -> Цены ro'yxatini ochish.
    2. Yangi narx turiga kod va nom kiritib, room-pw{code} ish zonasini tanlash.
    3. Saqlab, ro'yxatda narx turini tekshirish va keyingi flowlar uchun nomini saqlash.
    4. View formasini ochib, USA price type IDni data_store ga saqlash.
    5. View formasini yopib, narx turlari ro'yxatiga qaytish.
    """
    price_type_code = f"c_p_t_usa_pw{code}"
    price_type_name = f"Price Type USA-pw{code}"
    room_name = f"room-pw{code}"
    base = BasePage(page)

    with allure.step("1 - Narxlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - Yangi narx turi formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Цена (создание)")
        base.input(label="Код", value=price_type_code)
        base.input(label="Название", value=price_type_name)
        base.multiselect(label="Рабочие зоны", value=room_name)
        base.b_input(label="Валюта", value="Доллар США", clear=True)
        base.radio(label="Цена продажи", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Цены")
        base.grid_controller(search=price_type_name)
        base.grid(price_type_name)
        save_data("price_type_name_USA", price_type_name)

    with allure.step("4 - View formasidan USA price type IDni olish va saqlash"):
        base.grid(price_type_name, click=True)
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Цена (просмотр)", url="price_type_view?price_type_id=")
        base.text(price_type_name, price_type_code, "Активный")
        save_data("price_type_id_usa", query_int_from_url(page.url, "price_type_id"))

    with allure.step("5 - View formasini yopib, narx turlari ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Цены", url="price_type_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Narx turi (USA) yaratish")
def test_price_type_usa(page, code, logger, save_data):
    authorization(page, who="user", code=code)
    with allure.step("Precondition - Optional NPS Survey modalini qayta ishlash"):
        fill_nps_survey(page, logger)
    run_price_type_usa(page, code, save_data)
