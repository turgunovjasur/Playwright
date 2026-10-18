"""TMZ-1: barcha qadamlar shu test faylida; runner uchun run_* entry pointlar."""

import os
import re
from pathlib import Path

import allure
import pytest

from tests.shared.authorization import authorization, current_company_code
from utils.base_pages.auto_base_page import AutoBasePage
from utils.data_store import save_data
from utils.helper_utils import query_int_from_url

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("Yaratish va narxlash")]

PRODUCT_DATA_PATH = Path(__file__).resolve().with_name("data_store")


def run_product_full(page, code):
    """1. Yaratish. 2. Kod/nom/view tekshiruvi. 3. UZS/USD narx va reopen.

    Barcha product qadamlari shu test ichida; alohida product flow/helper yo'q.
    """
    base = AutoBasePage(page)
    save_data("regression_tmz_1", None, path=PRODUCT_DATA_PATH)

    with allure.step("1 - Test filialida ТМЦ listini ochish"):
        base.switch_filial(name=f"filial-pw{code}")
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("2 - Yangi mahsulot kodi hali yo'qligini tekshirish"):
        base.grid_controller(search=f"tmz-1-{code}")
        base.grid(state="empty")

    with allure.step("3 - ТМЦ yaratish formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="ТМЦ (создание)", url=re.compile(r"inventory(?:\+|%2[bB])add(?:[?#]|$)"))

    with allure.step("4 - Nom, kod, dona, Товар, birinchi to'plam va vazn/hajm"):
        base.input(label="Название", value=f"TMZ-1-{code}")
        base.input(label="Код", value=f"tmz-1-{code}")
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.checkbox(label="Активный", checked=True)
        base.checkbox(label="Товар", checked=True)
        base.checkbox(label="Продукция", checked=False)
        base.checkbox(label="Сырье", checked=False)
        sector = base.multiselect(label="Наборы ТМЦ", clear=True, select_first=True, return_value=True)[0]
        base.input(label="Вес нетто (кг)", value="100")
        base.input(label="Вес брутто (кг)", value="110")
        base.input(label="Литр/Дециметр куб.", value="120")

    with allure.step("5 - Saqlash, listga qaytish va xato yo'qligi"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("6 - Mahsulotni kod va nom orqali alohida qidirish"):
        base.grid_controller(search=f"tmz-1-{code}")
        base.grid(f"tmz-1-{code}", f"TMZ-1-{code}", "шт", "Активный")
        base.grid_controller(search=f"TMZ-1-{code}")
        base.grid(f"tmz-1-{code}", f"TMZ-1-{code}", "шт", "Активный", click=True)

    with allure.step("7 - Viewni ochish va IDni olish"):
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")
        product_id = query_int_from_url(page.url, "product_id")

    with allure.step("8 - View'da nom, kod, Товар va vazn/hajmni solishtirish"):
        base.text(f"TMZ-1-{code}", root="#anor393-span-name")
        base.form_view(label="Тип ТМЦ", expect_value="Товар")
        base.form_view(label="Код", expect_value=f"tmz-1-{code}", root=".b-offcanvas")
        base.form_view(label="Вес нетто:", expect_value="100", root=".b-offcanvas")
        base.form_view(label="Вес брутто:", expect_value="110", root=".b-offcanvas")
        base.form_view(label="Литр/Дециметр куб:", expect_value="120", root=".b-offcanvas")

    with allure.step("9 - Изменить formasida birlik/to'plamni o'qish"):
        base.click(name="Изменить", exact=True)
        base.expect_page(heading="ТМЦ (изменение)", url=re.compile(r"anor/mr/product/inventory(?:\+|%2[bB])edit(?:[?#]|$)"))
        base.b_input(label="Ед. изм.", expect_value="шт")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector)

    with allure.step("10 - O'zgartirishsiz viewga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")

    with allure.step("11 - View'dan listga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("12 - ТМЦ listidan Установить цены formasini ochish"):
        base.grid_controller(search=f"tmz-1-{code}")
        base.grid(f"tmz-1-{code}", f"TMZ-1-{code}", click=True)
        base.click(name="Установить цены", exact=True)
        base.expect_page(heading="ТМЦ (установка цен)", url="anor/mr/product/product_set_price")
        base.text(f"TMZ-1-{code}")

    with allure.step("13 - UZS va USD narxlarini kiritish"):
        base.input(label=f"Price Type UZB-pw{code}", value="5000")
        base.input(label=f"Price Type USA-pw{code}", value="5")

    with allure.step("14 - Narxlarni saqlash va listni tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("15 - Narx formasini qayta ochish va ikkala narxni tekshirish"):
        base.grid_controller(search=f"tmz-1-{code}")
        base.grid(f"tmz-1-{code}", f"TMZ-1-{code}", click=True)
        base.click(name="Установить цены", exact=True)
        base.expect_page(heading="ТМЦ (установка цен)", url="anor/mr/product/product_set_price")
        base.text(f"TMZ-1-{code}")
        base.input(label=f"Price Type UZB-pw{code}", expect_value="5000")
        base.input(label=f"Price Type USA-pw{code}", expect_value="5")

    with allure.step("16 - Narx formasini yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("17 - Tekshirilgan mahsulotni test yonidagi data_store.json ga yozish"):
        save_data("regression_tmz_1", {
            "number": 1, "name": f"TMZ-1-{code}", "code": f"tmz-1-{code}",
            "measure": "шт", "kind": "Товар",
            "weight_netto": "100", "weight_brutto": "110", "volume": "120",
            "price_uzs": "5000", "price_usd": "5",
            "price_type_uzs": f"Price Type UZB-pw{code}",
            "price_type_usd": f"Price Type USA-pw{code}",
            "sector": sector, "product_id": product_id, "run_code": str(code),
            "server": os.environ["COMPANY_URL"].rstrip("/"),
            "company": current_company_code(),
            "card_verified": True, "price_verified": True, "stock_verified": False,
        }, path=PRODUCT_DATA_PATH)


@allure.title("TMZ-1: yaratish, view, 5000 UZS va 5 USD")
def test_01_tmz_1(page, code):
    authorization(page, who="user", code=code)
    run_product_full(page, code)
