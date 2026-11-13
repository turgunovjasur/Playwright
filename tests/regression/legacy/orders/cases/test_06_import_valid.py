"""ORD-06: own SKU Excel importidan saqlangan orderga aniq ko'chishi."""

import re

import allure
import pytest
from openpyxl import Workbook
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_import import apply_order_import, read_order_import_settings, restore_order_import
from tests.smoke.test_life_cycle.flow_order.order_regression import edit_saved_order, open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Podbor va Excel import")]


def run_import_valid(page, order_case):
    """Bitta valid Excel satrini parse, transfer va fresh editgacha tekshirish.

    1. Own product ID / quantity 2 / balance Y bo'lgan headersiz XLSX yaratish.
    2. Own klient orderining mahsulotlar bosqichini ochish.
    3. Importni own ombor va narx turi bilan ochish.
    4. Joriy user mappingini saqlab, uch ustunli ID/quantity/balance mappingini qo'yish.
    5. Faylni yuklab bitta valid satr, 2 dona, 100 USD narx va xatolar yo'qligini tekshirish.
    6. Original mappingni tiklash va parsed satr saqlanganini tekshirish.
    7. Parsed satrni orderga o'tkazib 2 dona × 100 USDni tekshirish.
    8. Yakuniy bosqichda 200 USD Draftni tayyorlash.
    9. Saqlab fresh viewda 2 dona va 200 USDni tekshirish.
    10. Fresh editda miqdor va narx qolganini tekshirish.
    11. Yakuniy bosqichda 200 USD qolganini tekshirish.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'
    products = 'b-pg-grid[name="products"]'
    errors = 'b-pg-grid[name="error_messages"]'
    saved_goods = "b-grid:visible"
    workbook_path = case.directory / "order-valid.xlsx"

    with allure.step("1 - Own product ID, 2 dona va Y qiymatli XLSX yaratish"):
        if case.product_id is None:
            raise ValueError("Import uchun fixture own mahsulot ID sini yaratgan bo'lishi kerak")
        workbook = Workbook()
        workbook.active.append([case.product_id, 2, "Y"])
        workbook.save(workbook_path)
        workbook.close()
        allure.attach.file(str(workbook_path), name="ORD-06 valid import workbook", extension="xlsx")

    with allure.step("2 - Own klient orderining mahsulotlar bosqichini ochish"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)

    with allure.step("3 - Importni own ombor va narx turi bilan ochish"):
        base.click(name="Импорт", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        base.b_input(ng_model="q.warehouse_name", value=case.warehouse, clear=True)
        base.b_input(ng_model="q.price_type_name", value=case.price_type, clear=True)

    with allure.step("4 - Oldingi mappingni saqlab ID / quantity / balance ustunlarini sozlash"):
        case.import_settings = read_order_import_settings(page)
        apply_order_import(page, ending_row="")

    with allure.step("5 - Faylni parse qilib bitta valid 2 dona / 100 USD satrni tekshirish"):
        page.locator('input[type="file"]').set_input_files(workbook_path)
        base.click(name="Загрузить файл", exact=True)
        base.confirm_biruni(expected_text="Загрузить выбранный файл?")
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        row = base.grid(case.product, case.warehouse, root=products)
        expect(page.locator(products).locator(".tbl-row:visible")).to_have_count(1)
        headers = page.locator(products).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        base.input(ng_model="row.quantity", expect_value="2", root=row)
        expect(base.grid_cell(row, columns.index("Цена"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        base.grid(state="empty", root=errors)

    with allure.step("6 - Original mappingni tiklab parsed satr saqlanganini tekshirish"):
        restore_order_import(page, case.import_settings)
        case.import_settings = None
        row = base.grid(case.product, case.warehouse, root=products)
        base.input(ng_model="row.quantity", expect_value="2", root=row)

    with allure.step("7 - Parsed satrni orderga o'tkazib 2 dona × 100 USDni tekshirish"):
        base.click(name="Добавить выбранные поля", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add(?:[?#]|$)"))
        base.b_input(label="Название", expect_value=case.product, root=goods)
        base.input(ng_model="item.quantity", expect_value="2", root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)

    with allure.step("8 - Yakuniy bosqichda 200 USD Draftni tayyorlash"):
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)

    with allure.step("9 - Saved orderda 2 dona / 200 USDni tekshirish"):
        order_id = save_order(page, client=case.client)
        case.orders.append(order_id)
        open_saved_order(page, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Номер ТТН", expect_value=case.reference)
        base.form_view(label="Валюта", expect_value=case.currency)
        base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*2(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Цена"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*200(?:\.0+)?\s*$"))

    with allure.step("10 - Fresh editda 2 dona va 100 USD narx qolganini tekshirish"):
        edit_saved_order(page, order_id)
        base.input(ng_model="item.quantity", expect_value="2", root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)

    with allure.step("11 - Yakuniy bosqichda 200 USD qolganini tekshirish"):
        base.click(name="Далее")
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)
        open_saved_order(page, order_id)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-06: Valid Excel import, orderga transfer va saqlangan qiymatlar")
def test_import_valid(page, order_case):
    run_import_valid(page, order_case)
