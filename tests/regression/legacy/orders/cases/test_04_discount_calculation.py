"""ORD-04: satr summaviy chegirmasi per-unit, hujjat chegirmasi bir martalik."""

import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import edit_saved_order, open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order yaratish va tahrirlash")]


def run_discount_calculation(page, order_case):
    """2×100 USD, satrga har birlik uchun -1 va hujjatga bir marta -1.

    1. Own mahsulotdan 2 dona × 100 USD qo'shish.
    2. Satrni summaviy chegirma rejimiga o'tkazib -1: satr 198 USD.
    3. Hujjatga -1 summaviy chegirma berib 197 USD Draft saqlash.
    4. Fresh viewda -2 satr chegirmasi/198 satr summasi/-1 hujjat/197 totalni tekshirish.
    5. Editga qaytib ikkala -1 qiymat saqlanganini tekshirish.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'
    saved_goods = "b-grid:visible"

    with allure.step("1 - 2 dona × 100 USD mahsulot qo'shish"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)
        base.b_input(label="Название", value=case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)
        base.input(ng_model="item.quantity", value="2", press_tab=True, root=goods)

    with allure.step("2 - Satr summaviy chegirmasi har birlikka bir martadan ishlashi"):
        # UI foiz ikonkasini bosish pul rejimiga o'tkazadi (manual UI 18.10.2026).
        base.click(name="\uf295", exact=True, root=goods)
        base.input(ng_model="item.margin_value", value="-1", press_tab=True, root=goods)
        base.click(name="Далее")
        base.form_view(label="ИТОГО", expect_value="198", remove_spaces=True)

    with allure.step("3 - Hujjatga -1 bir martalik chegirma berib 197 USD saqlash"):
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.click(name="\uf295", exact=True, root='form[name="step2"]')
        base.input(ng_model="d.margin_value", value="-1", press_tab=True)
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.form_view(label="ИТОГО", expect_value="197", remove_spaces=True)
        order_id = save_order(page, client=case.client)
        case.orders.append(order_id)

    with allure.step("4 - Fresh viewda satr va hujjat chegirmalarini alohida tekshirish"):
        open_saved_order(page, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="197", remove_spaces=True)
        base.form_view(label="Сумма скидки/наценки на заказ", expect_value="-1", remove_spaces=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*2(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Сумма скидки/наценки"))).to_have_text(re.compile(r"^\s*-2(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*198(?:\.0+)?\s*$"))

    with allure.step("5 - Edit qayta ochilganda ikki summaviy -1 qiymati saqlangan bo'lishi"):
        edit_saved_order(page, order_id)
        base.input(ng_model="item.quantity", expect_value="2", root=goods)
        base.input(ng_model="item.margin_value", expect_value="-1", root=goods)
        base.click(name="Далее")
        base.input(ng_model="d.margin_value", expect_value="-1")
        base.form_view(label="ИТОГО", expect_value="197", remove_spaces=True)
        open_saved_order(page, order_id)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-04: Per-unit satr chegirmasi va bir martalik hujjat chegirmasi")
def test_discount_calculation(page, order_case):
    run_discount_calculation(page, order_case)
