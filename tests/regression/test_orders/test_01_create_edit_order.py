"""ORD-01: mustaqil klient orderini yaratish va shu IDni tahrirlash."""

import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import edit_saved_order, open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order yaratish va tahrirlash")]


def run_create_edit_order(page, order_case):
    """Draft yaratish va exact IDni tahrirlash.

    1. Own klient uchun 2 dona × 100 USD mahsulot qo'shish.
    2. Draftni TTN/izoh bilan saqlab header va satr qiymatlarini tekshirish.
    3. Shu IDdagi miqdorni 3 ga, TTN va izohni yangi qiymatga almashtirish.
    4. Qayta ochilganda shu ID, 3 dona, 300 USD va yangi metadata qolishini tekshirish.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'
    saved_goods = "b-grid:visible"
    first_note = f"ORD-01 create {case.key}"
    edited_note = f"ORD-01 edit {case.key}"
    edited_reference = f"{case.reference}E"

    with allure.step("1 - Own klientga 2 dona × 100 USD mahsulot qo'shish"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)
        base.b_input(label="Название", value=case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)
        base.input(ng_model="item.quantity", value="2", press_tab=True, root=goods)
        base.click(name="Далее")

    with allure.step("2 - 200 USD Draftni saqlab exact header va satrni tekshirish"):
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.input(ng_model="d.note", value=first_note)
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)
        order_id = save_order(page, client=case.client)
        case.orders.append(order_id)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Рабочая зона", expect_value=case.room)
        base.form_view(label="Штат", expect_value=case.staff)
        base.form_view(label="Тип оплаты", expect_value="Наличные деньги")
        base.form_view(label="Валюта", expect_value=case.currency)
        base.form_view(label="Номер ТТН", expect_value=case.reference)
        base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*2(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Цена"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*200(?:\.0+)?\s*$"))

    with allure.step("3 - Shu order IDda miqdor, TTN va izohni tahrirlash"):
        edit_saved_order(page, order_id)
        base.input(ng_model="item.quantity", expect_value="2", root=goods)
        base.input(ng_model="item.quantity", value="3", press_tab=True, root=goods)
        base.click(name="Далее")
        base.input(ng_model="d.note", expect_value=first_note)
        base.input(ng_model="d.delivery_number", value=edited_reference)
        base.input(ng_model="d.note", value=edited_note)
        base.form_view(label="ИТОГО", expect_value="300", remove_spaces=True)
        save_order(page, client=case.client, order_id=order_id)

    with allure.step("4 - Qayta ochilgan order ID, 3 dona, 300 USD va metadatani tekshirish"):
        open_saved_order(page, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Номер ТТН", expect_value=edited_reference)
        base.form_view(label="Сумма заказа", expect_value="300", remove_spaces=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=saved_goods)
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*3(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*300(?:\.0+)?\s*$"))
        edit_saved_order(page, order_id)
        base.click(name="Далее")
        base.input(ng_model="d.delivery_number", expect_value=edited_reference)
        base.input(ng_model="d.note", expect_value=edited_note)
        open_saved_order(page, order_id)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-01: Draft yaratish, tahrirlash va qayta ochish")
def test_create_edit_order(page, order_case):
    run_create_edit_order(page, order_case)
