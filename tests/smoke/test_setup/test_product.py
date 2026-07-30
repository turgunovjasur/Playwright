import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------

def _create_product_with_price(
    page,
    *,
    product_name,
    product_code,
    sector_name,
    price_type_name,
    price,
    price_label,
):
    """Bitta TMCni yaratib, berilgan price type bo'yicha narx o'rnatadi."""
    base = BasePage(page)

    with allure.step(f"1 - {price_label} TMC ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")

    with allure.step(f"2 - Yangi {price_label} TMC formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="ТМЦ (создание)")
        base.input(label="Код", value=product_code)
        base.input(label="Название", value=product_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step(
        f"3 - {price_label} TMCni saqlash, ro'yxat va ko'rishda tekshirish"
    ):
        base.save_and_expect_heading("ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name, click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="ТМЦ (просмотр)")
        base.text(product_code, product_name)
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="ТМЦ")

    with allure.step(
        f"4 - TMCga {price_label} narx belgilash: {price_type_name}"
    ):
        base.grid(product_code, product_name, click=True)
        page.get_by_role("button", name="Установить цены").click()
        base.expect_page(heading="ТМЦ (установка цен)")
        base.input(label=price_type_name, value=price)
        base.save_and_expect_heading("ТМЦ", confirm_text="Сохранить?")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)


# ----------------------------------------------------------------------------------------------------------------------

def run_product(page, code):
    """Testcase: asosiy TMC yaratish va unga UZS narx belgilash.

    1. Справочники -> ТМЦ ro'yxatini ochish.
    2. `product-pw{code}` TMCsiga kod, nom, o'lchov birligi va turini kiritish.
    3. Saqlab, TMCni ro'yxat va ko'rish formasida tekshirish.
    4. TMCga `Price Type UZB-pw{code}` bo'yicha 7000 UZS narx belgilash.
    """
    _create_product_with_price(
        page,
        product_name=f"product-pw{code}",
        product_code=f"c_p_pw{code}",
        sector_name=f"sector-pw{code}",
        price_type_name=f"Price Type UZB-pw{code}",
        price="7000",
        price_label="UZS",
    )


# ----------------------------------------------------------------------------------------------------------------------

def run_product_usa(page, code):
    """Testcase: ikkinchi TMC yaratish va unga USD narx belgilash.

    1. Справочники -> ТМЦ ro'yxatini ochish.
    2. `product-usa-pw{code}` TMCsiga kod, nom, o'lchov birligi va turini kiritish.
    3. Saqlab, TMCni ro'yxat va ko'rish formasida tekshirish.
    4. TMCga `Price Type USA-pw{code}` bo'yicha 1 USD narx belgilash.
    """
    _create_product_with_price(
        page,
        product_name=f"product-usa-pw{code}",
        product_code=f"c_p_usa_pw{code}",
        sector_name=f"sector-pw{code}",
        price_type_name=f"Price Type USA-pw{code}",
        price="1",
        price_label="USD",
    )

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("UZS va USD mahsulotlarini yaratish va narx belgilash")
def test_product(page, code):
    authorization(page, who="user", code=code)
    BasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product(page, code)
    run_product_usa(page, code)
