import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Payment Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_payment_type(page, save_data):
    """Testcase: global katalogdagi to'lov turlarini company'ga ulash.

    1. Справочники -> Цены ro'yxatini ochish.
    2. Типы оплат ro'yxatini ochish.
    3. Тип оплат (прикрепление) sahifasini ochish.
    4. Barcha mavjud to'lov turlarini tanlab ulash va available grid bo'shligini tekshirish.
    5. Прикрепление sahifasini yopib, Типы оплат ro'yxatiga qaytish.
    6. Company ro'yxatida 4 ta to'lov turi ko'rinishini tekshirish.
    7. Grid setting orqali ИД ustuni va qidiruvini yoqish.
    8. Наличные деньги qatoridan payment type IDni olib, data_store ga saqlash.
    """
    base = BasePage(page)
    with allure.step("1 - Narxlar ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - To'lov turlari ro'yxatini ochish"):
        base.click(name="Типы оплат", role="link")
        base.expect_page(heading="Типы оплат")

    with allure.step("3 - To'lov turlarini biriktirish sahifasini ochish"):
        base.click(name="Прикрепление")
        base.expect_page(heading="Тип оплат (прикрепление)")

    with allure.step("4 - Barcha to'lov turlarini tanlash va ulash"):
        base.grid(checkbox="all")
        base.click(name="Прикрепить")
        base.confirm_biruni("Прикрепить типы оплат в количестве 4?")
        base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("5 - Biriktirish sahifasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Типы оплат")

    with allure.step("6 - To'lov turlarini ro'yxatda tekshirish"):
        base.grid("Наличные деньги")
        base.grid("Перечисление")
        base.grid("Терминал")
        base.grid("Чековая книжка")

    with allure.step("7 - Payment type ID ustuni va qidiruvini yoqish"):
        id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="ИД")

    with allure.step("8 - Naqd to'lov turi ID sini olish va saqlash"):
        cash_row = base.grid("Наличные деньги")
        payment_type_id = base.grid_cell(cash_row, id_column, return_value=True, remove_spaces=True)
        if not payment_type_id.isdigit() or int(payment_type_id) <= 0:
            raise AssertionError(f"Наличные деньги uchun musbat payment_type_id topilmadi: {payment_type_id!r}")
        save_data("payment_type_id", int(payment_type_id))

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("To'lov turlarini tizimga ulash")
def test_payment_type(page, code, save_data):
    authorization(page, who="user", code=code)
    run_payment_type(page, save_data)
