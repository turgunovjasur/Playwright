"""Guruhga tegishli KG va dona mahsulotlari bilan Order amallari."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.regression.test_orders.business_cases.discounts.test_manual_discount import _line_amount
from tests.regression.test_orders.helpers.discounts import parse_amount
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, open_order_summary, product_loaded, save_order_by_reference,
    select_client_product, select_order_product,
)
from tests.regression.test_orders.helpers.flows.settlement import _columns
from tests.smoke.test_life_cycle.flow_order.order_regression import ORDER_LISTS
from utils.base_pages.auto_base_page import AutoBasePage


def open_saved(case, order, *, status="Черновик"):
    base = AutoBasePage(case.page)
    base.open_route("trade/tdeal/order/order_view?deal_id=" + order["id"], heading="Заказ / Просмотр")
    for label, value in (("ИД заказа", order["id"]), ("Номер ТТН", order["reference"]),
                         ("Клиент", case.client), ("Статус", status)):
        base.form_view(label=label, expect_value=value)
    return base


def check_line(case, product, price_type, *, quantity, price, discount, net):
    base = AutoBasePage(case.page)
    grid = case.page.locator("smt-table:visible").filter(has=case.page.get_by_text(product, exact=True))
    expect(grid).to_have_count(1)
    row = base.grid(product, price_type, "Основной склад", root=grid)
    columns = [" ".join(label.split()) for label in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество продажи", quantity), ("Цена", price),
                            ("Сумма скидки/наценки", discount), ("Итого", net)):
        if columns.count(label) != 1:
            raise AssertionError(f"Orderda {label} ustuni yagona bo‘lishi kerak")
        value = base.grid_cell(row, columns.index(label), return_value=True).strip()
        case.check(f"{product} · {label}", Decimal(str(expected)), parse_amount(value or "0"))


def start_goods(case):
    open_new_order(case.page)
    return select_client_product(case.page, case.client, case.product, case.price_type)


def save_draft(case, total):
    base = AutoBasePage(case.page)
    open_order_summary(case.page, expected_total=str(total))
    base.b_input(label="Тип оплаты", value="Перечисление")
    base.input(label="Номер товарно-транспортной накладной", value=case.reference)
    base.ui_select(label="Статус", value="Черновик")
    return save_order_by_reference(case.page, case.reference)


def check_mixed_rows(case, piece_type):
    base = AutoBasePage(case.page)
    base.form_view(label="Сумма заказа", expect_value="3750", remove_spaces=True)
    check_line(case, case.product, case.price_type, quantity="2.5", price=1000, discount=-250, net=2250)
    check_line(case, case.bonus_product, piece_type, quantity=1, price=1500, discount=0, net=1500)


@allure.step("Ikki mahsulotli qoralamani saqlash va qatorlarini qayta o‘qish")
def run_mixed_draft(case, catalog):
    base = AutoBasePage(case.page)
    piece_type = catalog["mixed_prices"]["piece"]["name"]
    oid = existing_order(case)
    if not oid:
        with product_loaded(case.page, catalog["goods"]["id"], case.baseline["price_type_id_uzb"]):
            row = start_goods(case)
        base.input(label="Кол-во", value="2.5", press_tab=True)
        _line_amount(case, row, -100)
        with product_loaded(case.page, catalog["bonus"]["id"], catalog["mixed_prices"]["piece"]["id"]):
            piece = select_order_product(case.page, case.bonus_product, piece_type, index=1)
        base.input(locator=piece.locator("[data-smt-col-key=quantity] input"), value="1", press_tab=True)
        oid = save_draft(case, 3750)
    case.remember_order(oid)
    order = {"id": oid, "reference": case.reference}
    case.workflow["mixed_order"] = order
    case.checkpoint()
    open_saved(case, order)
    check_mixed_rows(case, piece_type)


@allure.step("Orderni {list_name} ro‘yxatida aniq ID bo‘yicha tanlash")
def select_saved_order(case, order, list_name):
    page, base = case.page, AutoBasePage(case.page)
    base.navigate_to(tab="Продажа", name=list_name)
    base.expect_page(heading=list_name, url=dict(ORDER_LISTS.values())[list_name])
    col = _columns(page, {"id": "ИД заказа"}, search_name="ИД заказа")["id"]
    base.grid_controller(search=order["id"])
    row = base.grid(order["id"], case.client, click=True)
    expect(base.grid_cell(row, col)).to_have_text(order["id"])
