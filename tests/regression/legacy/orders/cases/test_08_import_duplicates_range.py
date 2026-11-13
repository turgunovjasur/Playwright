"""ORD-08: bir SKUning duplicate qatorlari va import row-range chegarasi."""

import re
from decimal import Decimal

import allure
import pytest
from openpyxl import Workbook
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_import import apply_order_import, read_order_import_settings, restore_order_import
from tests.smoke.test_life_cycle.flow_order.order_regression import edit_saved_order, open_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Podbor va Excel import")]


def run_import_duplicates_range(page, order_case, ending_row, expected_quantities, expected_total):
    """1. Bir SKUning qty1/qty2 XLSX fayli. 2. Barcha yoki birinchi qatorni parse qilish.

    3. Preview miqdorlari va xatolar yo'qligi. 4. Saved total va fresh editda
    umumiy miqdor saqlanishi; serverning duplicate satrlarni birlashtirishi shart emas.
    Har parametr alohida pytest item va o'z order_case fixture'ini oladi.
    """
    base = AutoBasePage(page)
    path = order_case.directory / "duplicate-product.xlsx"
    workbook = Workbook()
    workbook.active.append([order_case.product_id, 1, "Y"])
    workbook.active.append([order_case.product_id, 2, "Y"])
    workbook.save(path)
    workbook.close()
    allure.attach.file(str(path), name="ORD-08 input", extension="xlsx")

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Import formasini ochish"):
        base.click(name="Импорт", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
    order_case.import_settings = read_order_import_settings(page)
    apply_order_import(page, ending_row=ending_row)
    with allure.step(f"2 - Range {ending_row or 'barcha'} bo'yicha faylni parse qilish"):
        base.b_input(ng_model="q.warehouse_name", value=order_case.warehouse, clear=True)
        base.b_input(ng_model="q.price_type_name", value=order_case.price_type, clear=True)
        page.locator('input[type="file"]').set_input_files(path)
        base.click(name="Загрузить файл", exact=True)
        base.confirm_biruni()
        quantities = page.locator('b-pg-grid[name="products"] input[ng-model="row.quantity"]:visible')
        expect(quantities).to_have_count(len(expected_quantities))
        for index, value in enumerate(expected_quantities):
            expect(quantities.nth(index)).to_have_value(value)
        base.grid(state="empty", root='b-pg-grid[name="error_messages"]')
    restore_order_import(page, order_case.import_settings)
    order_case.import_settings = None
    with allure.step("3 - Parsed qatorlarni orderga ko'chirish"):
        base.click(name="Добавить выбранные поля", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add"))
        quantities = page.locator('b-pg-grid[name="goods_items"] input[ng-model="item.quantity"]:visible')
        expect(quantities).to_have_count(len(expected_quantities))
        for index, value in enumerate(expected_quantities):
            expect(quantities.nth(index)).to_have_value(value)
        base.click(locator="#anor279-button-next_step")
        base.form_view(label="ИТОГО", expect_value=expected_total, remove_spaces=True)
        base.ui_select(label="Статус", value="Черновик")
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)
    with allure.step(f"4 - Saqlangan exact ID va {expected_total} USD"):
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Сумма заказа", expect_value=expected_total, remove_spaces=True)
    edit_saved_order(page, order_id)
    with allure.step("5 - Qayta ochilganda umumiy miqdor yo'qolmagan yoki ortmagan"):
        quantities = page.locator('b-pg-grid[name="goods_items"] input[ng-model="item.quantity"]:visible')
        expect(quantities.first).to_be_visible()
        total_quantity = sum((Decimal(field.input_value().replace(" ", "").replace(",", ".")) for field in quantities.all()), Decimal("0"))
        expected_quantity = sum((Decimal(value) for value in expected_quantities), Decimal("0"))
        if total_quantity != expected_quantity:
            pytest.fail(f"Saved import quantity: expected={expected_quantity}, actual={total_quantity}")
        base.click(locator="#anor279-button-next_step")
        base.form_view(label="ИТОГО", expect_value=expected_total, remove_spaces=True)


@allure.title("ORD-08: Duplicate import va row range — {ending_row}")
@pytest.mark.parametrize("ending_row,expected_quantities,expected_total", [pytest.param("", ("1", "2"), "300", id="duplicate_rows"), pytest.param("1", ("1",), "100", id="first_row_only")])
def test_import_duplicates_range(page, order_case, ending_row, expected_quantities, expected_total):
    run_import_duplicates_range(page, order_case, ending_row, expected_quantities, expected_total)
