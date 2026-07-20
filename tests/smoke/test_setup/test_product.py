import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------

def run_product(page, code):
    """Testcase: TMC yaratish va unga UZS narx belgilash.

    1. Справочники -> ТМЦ ro'yxatini ochish.
    2. Yangi TMCga kod, nom, o'lchov birligi va turini kiritish.
    3. Saqlab, TMCni ro'yxat va ko'rish formasida tekshirish.
    4. TMCga UZS narx belgilab, ro'yxatga qaytilganini tekshirish.
    """
    product_name = f"product-pw{code}"
    product_code = f"c_p_pw{code}"
    sector_name = f"sector-pw{code}"
    price_type_name = f"Price Type UZB-pw{code}"
    base = BasePage(page)

    with allure.step("1 - TMC ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")

    with allure.step("2 - Yangi TMC formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="ТМЦ (создание)")
        base.input(label="Код", value=product_code)
        base.input(label="Название", value=product_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step("3 - Saqlash, ro'yxat va ko'rish formasida tekshirish"):
        base.save_and_expect_heading("ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name, click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="ТМЦ (просмотр)")
        base.text(product_code, product_name)
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="ТМЦ")

    with allure.step("4 - TMCga UZS narx belgilash"):
        base.grid(product_code, product_name, click=True)
        page.get_by_role("button", name="Установить цены").click()
        base.expect_page(heading="ТМЦ (установка цен)")
        base.input(label=price_type_name, value="7000")
        base.save_and_expect_heading("ТМЦ", confirm_text="Сохранить?")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Mahsulot (TMC) yaratish va narx belgilash")
def test_product(page, code):
    authorization(page, who="user", code=code)
    BasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product(page, code)
