import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------

def run_product(page, code):
    """Testcase: UZS va USD TMC yaratib, tegishli narxlarni belgilash.

    1. Справочники -> ТМЦ ro'yxatini ochish.
    2. UZS TMC yaratish formasini ochib, majburiy maydonlarni to'ldirish.
    3. UZS TMCni saqlab, ro'yxatda tekshirish.
    4. UZS TMC view formasini ochib, kod va nomni tekshirish.
    5. View formasini yopib, TMC ro'yxatiga qaytish.
    6. UZS TMC uchun narx belgilash formasini ochish.
    7. 7000 UZS narxni saqlab, TMC ro'yxatida tekshirish.
    8. USD TMC yaratish formasini ochib, majburiy maydonlarni to'ldirish.
    9. USD TMCni saqlab, ro'yxatda tekshirish.
    10. USD TMC view formasini ochib, kod va nomni tekshirish.
    11. View formasini yopib, TMC ro'yxatiga qaytish.
    12. USD TMC uchun narx belgilash formasini ochish.
    13. 1 USD narxni saqlab, TMC ro'yxatida tekshirish.
    """
    base = BasePage(page)
    product_name = f"product-pw{code}"
    product_code = f"c_p_pw{code}"
    product_usa_name = f"product-usa-pw{code}"
    product_usa_code = f"c_p_usa_pw{code}"
    sector_name = f"sector-pw{code}"
    price_type_uzb = f"Price Type UZB-pw{code}"
    price_type_usa = f"Price Type USA-pw{code}"

    with allure.step("1 - TMC ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")

    with allure.step("2 - UZS TMC yaratish formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="ТМЦ (создание)")
        base.input(label="Код", value=product_code)
        base.input(label="Название", value=product_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step("3 - UZS TMCni saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

    with allure.step("4 - UZS TMC view formasini ochish va tekshirish"):
        base.grid(product_code, product_name, click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="ТМЦ (просмотр)")
        base.text(product_code, product_name)

    with allure.step("5 - UZS TMC view formasini yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")

    with allure.step("6 - UZS TMC narx formasini ochish"):
        base.grid(product_code, product_name, click=True)
        base.click(name="Установить цены")
        base.expect_page(heading="ТМЦ (установка цен)")

    with allure.step("7 - UZS narxni saqlash va TMCni ro'yxatda tekshirish"):
        base.input(label=price_type_uzb, value="7000")
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

    with allure.step("8 - USD TMC yaratish formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="ТМЦ (создание)")
        base.input(label="Код", value=product_usa_code)
        base.input(label="Название", value=product_usa_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step("9 - USD TMCni saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_usa_code)
        base.grid(product_usa_code, product_usa_name)

    with allure.step("10 - USD TMC view formasini ochish va tekshirish"):
        base.grid(product_usa_code, product_usa_name, click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="ТМЦ (просмотр)")
        base.text(product_usa_code, product_usa_name)

    with allure.step("11 - USD TMC view formasini yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")

    with allure.step("12 - USD TMC narx formasini ochish"):
        base.grid(product_usa_code, product_usa_name, click=True)
        base.click(name="Установить цены")
        base.expect_page(heading="ТМЦ (установка цен)")

    with allure.step("13 - USD narxni saqlash va TMCni ro'yxatda tekshirish"):
        base.input(label=price_type_usa, value="1")
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_usa_code)
        base.grid(product_usa_code, product_usa_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("UZS va USD mahsulotlarini yaratish va narx belgilash")
def test_product(page, code):
    authorization(page, who="user", code=code)
    BasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product(page, code)
