import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_modal import fill_nps_survey
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Price Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_price_type_uzb(page, code, logger, save_data):
    """Testcase: UZB narx turini yaratib, ish zonasiga biriktirish.

    1. Optional NPS Survey modalini qayta ishlash.
    2. Справочники -> Цены ro'yxatini ochish.
    3. Yangi narx turiga kod va nom kiritib, room-pw{code} ish zonasini tanlash.
    4. Saqlab, ro'yxatda narx turini tekshirish va keyingi flowlar uchun nomini saqlash.
    """
    price_type_code = f"c_p_t_uzb_pw{code}"
    price_type_name = f"Price Type UZB-pw{code}"
    room_name = f"room-pw{code}"
    base = BasePage(page)

    with allure.step("1 - Optional NPS Survey modalini qayta ishlash"):
        fill_nps_survey(page, logger)

    with allure.step("2 - Narxlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("3 - Yangi narx turi formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Цена (создание)")
        base.input(label="Код", value=price_type_code)
        base.input(label="Название", value=price_type_name)
        base.multiselect(label="Рабочие зоны", value=room_name)
        base.b_input(label="Валюта", value="Узбекский сум", clear=True)
        base.radio(label="Цена продажи", expect_checked=True)

    with allure.step("4 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Цены")
        base.grid_controller(search=price_type_name)
        base.grid(price_type_name)
        save_data("price_type_name_UZB", price_type_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Narx turi (UZB) yaratish")
def test_price_type_uzb(page, code, logger, save_data):
    authorization(page, who="user", code=code)
    run_price_type_uzb(page, code, logger, save_data)
