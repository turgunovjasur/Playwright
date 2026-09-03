import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Init Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def run_init_balance(page, code):
    """UZS va USD mahsulotlari uchun boshlang'ich qoldiq yaratish.

    1. Boshlang'ich qoldiq hujjatlari ro'yxatini ochish.
    2. UZS qoldiq hujjati formasini ochib, product-pw{code} uchun qiymatlarni kiritish.
    3. UZS qoldiq hujjatini saqlab, ro'yxatda tekshirish.
    4. UZS qoldiq hujjatini o'tkazish.
    5. UZS provodkalarida 100 dona va 500 000 summani tekshirish.
    6. USD qoldiq hujjati formasini ochib, product-usa-pw{code} uchun qiymatlarni kiritish.
    7. USD qoldiq hujjatini saqlab, ro'yxatda tekshirish.
    8. USD qoldiq hujjatini o'tkazish.
    """
    base = BasePage(page)
    document_number = str(code)
    document_usa_number = f"1{code}"
    quantity = "100"

    with allure.step("1 - Boshlang'ich qoldiq hujjatlari ro'yxatini ochish"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ")

    with allure.step("2 - UZS qoldiq hujjati formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
        base.input(label="Номер", value=document_number)
        base.b_input(ng_model="d.warehouse_name", value="Основной склад", clear=True)
        base.b_input(label="Валюта", value="Узбекский сум", clear=True)
        product_grid = page.locator("b-pg-grid")
        base.b_input(label="Название", value=f"c_p_pw{code}", expect_value=f"product-pw{code}", root=product_grid)
        base.input(label="Кол-во", value=quantity, root=product_grid)
        base.input(label="Цена", value="5000", root=product_grid)

    with allure.step("3 - UZS qoldiq hujjatini saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid(document_number)

    with allure.step("4 - UZS qoldiq hujjatini o'tkazish"):
        base.grid(document_number, click=True)
        base.click(name="Провести")
        base.confirm_biruni(f"Провести документ № {document_number}?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid(document_number)

    with allure.step("5 - UZS provodkalarida miqdor va summani tekshirish"):
        base.grid(document_number, click=True)
        with page.expect_popup(timeout=30_000) as postings_page_info:
            base.click(name="Проводки")
        postings_page = postings_page_info.value
        expect(postings_page.get_by_role("rowgroup")).to_contain_text(quantity)
        expect(postings_page.get_by_role("rowgroup")).to_contain_text("500 000")
        postings_page.close()

    with allure.step("6 - USD qoldiq hujjati formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
        base.input(label="Номер", value=document_usa_number)
        base.b_input(ng_model="d.warehouse_name", value="Основной склад", clear=True)
        base.b_input(label="Валюта", value="Доллар США", clear=True)
        product_grid = page.locator("b-pg-grid")
        base.b_input(label="Название", value=f"c_p_usa_pw{code}", expect_value=f"product-usa-pw{code}", root=product_grid)
        base.input(label="Кол-во", value=quantity, root=product_grid)
        base.input(label="Цена", value="1", root=product_grid)

    with allure.step("7 - USD qoldiq hujjatini saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid(document_usa_number)

    with allure.step("8 - USD qoldiq hujjatini o'tkazish"):
        base.grid(document_usa_number, click=True)
        base.click(name="Провести")
        base.confirm_biruni(f"Провести документ № {document_usa_number}?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid(document_usa_number)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("UZS va USD mahsulotlari uchun boshlang'ich qoldiqlar")
def test_init_balance(page, code):
    authorization(page, who="user", code=code)
    run_init_balance(page, code)
