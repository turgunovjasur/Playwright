import re

import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages import UI_TIMEOUT_MS
from tests.shared.list_search import find_list_record
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Init Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def _ensure_posted_balance(base, number, currency, product_code, product_name, quantity, price):
    table = "init_inventory_balance_list"
    existing = find_list_record(base, table, "balance_number", number)
    if existing is None:
        with allure.step(f"{currency} · {number} qoldiq hujjatini yaratish"):
            base.click(name="Создать")
            base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)", url=re.compile(r"init_inventory_balance(?:\+|%2[bB])add"))
            base.input(label="Номер", value=number)
            base.b_input(label="Склад", value="Основной склад", clear=True)
            base.b_input(label="Валюта", value=currency, clear=True)
            base.b_input(label="Название", value=product_code, expect_value=product_name)
            base.input(label="Кол-во", value=quantity)
            base.input(label="Цена", value=price)
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni("Сохранить?")
            base.expect_page(heading="Ввод начальных остатков ТМЦ", url=table)
            existing = find_list_record(base, table, "balance_number", number)
    if not existing or existing["warehouse_name"] != "Основной склад" or existing["currency_name"] != currency:
        raise AssertionError(f"{number}: qoldiq hujjati, ombor yoki valyuta tasdiqlanmadi")

    # The shorter UZS number can also match the USD document in the same grid.
    cell = base.page.get_by_text(number, exact=True).filter(visible=True)
    cell.click()
    if existing["posted"] == "N":
        with allure.step(f"{currency} · {number} qoldiq hujjatini o‘tkazish"):
            base.click(name="Провести")
            base.confirm_biruni(f"Провести документ № {number}?")
            base.expect_page(heading="Ввод начальных остатков ТМЦ", url=table)
            posted = find_list_record(base, table, "balance_number", number)
            if not posted or posted["balance_id"] != existing["balance_id"] or posted["posted"] != "Y":
                raise AssertionError(f"{number}: hujjat o‘tkazilgani tasdiqlanmadi")
            cell.click()
    elif existing["posted"] != "Y":
        raise AssertionError(f"{number}: hujjat holati noma’lum")


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
    base = AutoBasePage(page)
    document_number = str(code)
    document_usa_number = f"1{code}"
    quantity = "100"

    with allure.step("1 - Boshlang'ich qoldiq hujjatlari ro'yxatini ochish"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="anor/mkw/init_balance/init_inventory_balance_list")

    _ensure_posted_balance(base, document_number, "Узбекский сум", f"c_p_pw{code}",
                           f"product-pw{code}", quantity, "5000")

    with allure.step("5 - UZS provodkalarida miqdor va summani tekshirish"):
        with page.expect_popup(timeout=UI_TIMEOUT_MS) as postings_page_info:
            base.click(name="Проводки")
        postings_page = postings_page_info.value
        expect(postings_page.get_by_role("rowgroup")).to_contain_text(quantity)
        expect(postings_page.get_by_role("rowgroup")).to_contain_text("500 000")
        postings_page.close()

    _ensure_posted_balance(base, document_usa_number, "Доллар США", f"c_p_usa_pw{code}",
                           f"product-usa-pw{code}", quantity, "1")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("UZS va USD mahsulotlari uchun boshlang'ich qoldiqlar")
def test_init_balance(page, code):
    authorization(page, who="user", code=code)
    run_init_balance(page, code)
