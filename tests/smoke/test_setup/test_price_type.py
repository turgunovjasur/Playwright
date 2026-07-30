import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_modal import fill_nps_survey
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Price Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_price_type_uzb(page, code, save_data):
    """Testcase: UZB narx turini yaratib, ish zonasiga biriktirish.

    1. Справочники -> Цены ro'yxatini ochish.
    2. Yangi narx turiga kod va nom kiritib, room-pw{code} ish zonasini tanlash.
    3. Saqlab, ro'yxatda narx turini tekshirish va keyingi flowlar uchun nomini saqlash.
    """
    price_type_code = f"c_p_t_uzb_pw{code}"
    price_type_name = f"Price Type UZB-pw{code}"
    room_name = f"room-pw{code}"
    base = BasePage(page)

    with allure.step("1 - Narxlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - Yangi narx turi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Цена (создание)")
        base.input(label="Код", value=price_type_code)
        base.input(label="Название", value=price_type_name)
        base.multiselect(label="Рабочие зоны", value=room_name)
        base.b_input(label="Валюта", value="Узбекский сум", clear=True)
        base.radio(label="Цена продажи", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.save_and_expect_heading("Цены")
        base.grid_controller(search=price_type_name)
        base.grid(price_type_name)
        save_data("price_type_name_UZB", price_type_name)

# ----------------------------------------------------------------------------------------------------------------------

def run_price_type_usa(page, code, save_data):
    """Testcase: USA narx turini yaratib, ish zonasiga biriktirish.

    1. Справочники -> Цены ro'yxatini ochish.
    2. Yangi narx turiga kod va nom kiritib, room-pw{code} ish zonasini tanlash.
    3. Saqlab, ro'yxatda narx turini tekshirish va keyingi flowlar uchun nomini saqlash.
    """
    price_type_code = f"c_p_t_usa_pw{code}"
    price_type_name = f"Price Type USA-pw{code}"
    room_name = f"room-pw{code}"
    base = BasePage(page)

    with allure.step("1 - Narxlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - Yangi narx turi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Цена (создание)")
        base.input(label="Код", value=price_type_code)
        base.input(label="Название", value=price_type_name)
        base.multiselect(label="Рабочие зоны", value=room_name)
        base.b_input(label="Валюта", value="Доллар США", clear=True)
        base.radio(label="Цена продажи", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.save_and_expect_heading("Цены")
        base.grid_controller(search=price_type_name)
        base.grid(price_type_name)
        save_data("price_type_name_USA", price_type_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Narx turi (UZB) yaratish")
def test_price_type_uzb(page, code, logger, save_data):
    authorization(page, who='user', code=code)
    fill_nps_survey(page, logger)
    run_price_type_uzb(page, code, save_data)
    run_price_type_usa(page, code, save_data)
