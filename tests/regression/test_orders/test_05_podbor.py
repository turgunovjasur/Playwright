"""ORD-05: Подбор orqali tanlash, olib tashlash va orderga qayta o'tkazish."""

import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Podbor va Excel import")]


def run_podbor(page, order_case):
    """Own SKUni Подборda 3 dona tanlab, o'chirib va qayta qo'shib saqlash.

    1. Own klient orderining mahsulotlar bosqichini ochish.
    2. Подборni ochib ombor va narx turini tanlash.
    3. Own SKUdan 3 dona qo'shib Выбранные tabida 300 USDni tekshirish.
    4. Tanlangan satrni o'chirish; Доступные tabidan yana 3 dona qo'shish.
    5. Yopilganda wizardga 3 dona × 100 USD o'tganini tekshirish.
    6. Yakuniy bosqichda 300 USD Draftni tayyorlash.
    7. Saqlab fresh viewda shu SKU, 3 dona va 300 USDni tekshirish.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'
    available = 'b-pg-grid[name="available_products"]'
    selected = "b-pg-grid:visible"
    saved_goods = "b-grid:visible"

    with allure.step("1 - Own klient orderining mahsulotlar bosqichini ochish"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)

    with allure.step("2 - Podborni own klient, ombor va narx turi bilan ochish"):
        base.click(name="Подбор", exact=True)
        base.expect_page(heading=f"Заказ (подбор): {case.client}", url="product_list")
        base.b_input(ng_model="q.warehouse_name", value=case.warehouse, clear=True)
        base.b_input(ng_model="q.price_type_name", value=case.price_type, clear=True)
        base.click(name="Доступные", role="tab", exact=True)
        base.input(ng_model="g.searchValue", value=case.product, root=available).press("Enter")
        row = base.grid(case.product, case.warehouse, case.price_type, root=available)

    with allure.step("3 - 3 dona qo'shib Выбранные tabida 300 USDni tekshirish"):
        base.input(ng_model="row.quantity", value="3", press_tab=True, root=row)
        base.click(name="\uf067", exact=True, root=row)
        base.click(name="Выбранные", role="tab", exact=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=selected)
        headers = page.locator(selected).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        base.input(ng_model="row.quantity", expect_value="3", root=row)
        expect(base.grid_cell(row, columns.index("Цена"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Сумма"))).to_have_text(re.compile(r"^\s*300(?:\.0+)?\s*$"))

    with allure.step("4 - Tanlangan satrni olib tashlab ayni SKUdan 3 dona qayta qo'shish"):
        base.click(name="\uf1f8", exact=True, root=row)
        base.grid(state="empty", root=selected)
        base.click(name="Доступные", role="tab", exact=True)
        base.input(ng_model="g.searchValue", value=case.product, root=available).press("Enter")
        row = base.grid(case.product, case.warehouse, case.price_type, root=available)
        base.input(ng_model="row.quantity", value="3", press_tab=True, root=row)
        base.click(name="\uf067", exact=True, root=row)
        base.click(name="Выбранные", role="tab", exact=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=selected)
        base.input(ng_model="row.quantity", expect_value="3", root=row)
        expect(base.grid_cell(row, columns.index("Сумма"))).to_have_text(re.compile(r"^\s*300(?:\.0+)?\s*$"))

    with allure.step("5 - Podborni yopib wizardga faqat 3 dona o'tganini tekshirish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add(?:[?#]|$)"))
        base.b_input(label="Название", expect_value=case.product, root=goods)
        base.input(ng_model="item.quantity", expect_value="3", root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)

    with allure.step("6 - Yakuniy bosqichda 300 USD Draftni tayyorlash"):
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.form_view(label="ИТОГО", expect_value="300", remove_spaces=True)

    with allure.step("7 - Draftni saqlab exact IDdagi 3 dona va 300 USDni qayta o'qish"):
        order_id = save_order(page, client=case.client)
        case.orders.append(order_id)
        open_saved_order(page, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Номер ТТН", expect_value=case.reference)
        base.form_view(label="Валюта", expect_value=case.currency)
        base.form_view(label="Сумма заказа", expect_value="300", remove_spaces=True)
        row = base.grid(case.product, case.warehouse, case.price_type, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*3(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Цена"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*300(?:\.0+)?\s*$"))


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-05: Podbor tanlash, o'chirish, qayta qo'shish va saqlash")
def test_podbor(page, order_case):
    run_podbor(page, order_case)
