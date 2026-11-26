"""Katalog narxi va XML ssenariylari uchun qoralama yaratish va saqlangan narxni o‘qish."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.test_orders.helpers.discounts import parse_amount, save_discount_draft
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, open_order_summary, reopen_order_goods, select_client_product,
)
from tests.regression.test_orders.helpers.navigation import OrderPage


def _check_goods(case, grid, row, columns, expected):
    expect(row).to_have_count(1)
    headers = [" ".join(text.split()) for text in
               grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    base = OrderPage(case.page)
    for label, value in zip(columns, expected, strict=True):
        if headers.count(label) != 1:
            raise AssertionError(f"Mahsulot jadvalida {label!r} ustuni yagona emas")
        actual = base.grid_cell(row, headers.index(label), return_value=True)
        case.check(f"Mahsulot — {label}", Decimal(value), parse_amount(actual))


def check_saved_price_draft(case, order, price):
    base = OrderPage(case.page)
    with allure.step("Aynan saqlangan qoralamani ID bo‘yicha qayta ochish"):
        base.open_route("trade/tdeal/order/order_view?deal_id=" + order["id"], heading="Заказ / Просмотр")
        for label, value in (("ИД заказа", order["id"]), ("Номер ТТН", order["reference"]),
                             ("Клиент", case.client), ("Статус", "Черновик")):
            base.form_view(label=label, expect_value=value)
        total = base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)
        case.check("Qoralamaning saqlangan jami", Decimal(2 * price), parse_amount(total))
        grid = case.page.locator("smt-table:visible").filter(has=case.page.get_by_text(case.product, exact=True))
        expect(grid).to_have_count(1)
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.product, case.price_type, "Основной склад", root=grid)
        _check_goods(case, grid, row, ("Количество продажи", "Цена", "Итого"), (2, price, 2 * price))


def check_edit_price(case, price):
    page = case.page
    grid = page.locator("smt-table:visible").filter(has=page.get_by_text(case.price_type, exact=True))
    row = grid.locator(".smt-data-row").filter(has=page.get_by_text(case.price_type, exact=True))
    expect(row).to_have_count(1)
    OrderPage(page).b_input(placeholder="Выберите...", root=row, expect_value=case.product)
    _check_goods(case, grid, row, ("Кол-во", "Цена", "Сумма к оплате"), (2, price, 2 * price))


def create_price_draft(case, *, key, price, payment_type="Наличные деньги"):
    """1. Qoralamani saqlash. 2. Viewni o‘qish. 3. Yangi narxni fresh Editda tekshirish."""
    order_id = existing_order(case)
    if order_id:
        case.remember_order(order_id)
    else:
        require_available(case, 2)
        open_new_order(case.page)
        select_client_product(case.page, case.client, case.product, case.price_type)
        OrderPage(case.page).input(label="Кол-во", value="2", press_tab=True)
        open_order_summary(case.page, expected_total=2 * price)
        order_id = save_discount_draft(case, 2 * price, payment_type=payment_type)
    order = {"id": order_id, "reference": case.reference}
    if key == "new_draft":
        case.check("Yangi qoralama alohida ID oldi", True, order_id != case.workflow["original_draft"]["id"])
    case.workflow[key] = order
    case.checkpoint()
    check_saved_price_draft(case, order, price)
    if key == "new_draft":
        reopen_order_goods(case.page)
        with allure.step("Yangi qoralamaning tahririda miqdor, narx va jami saqlangan"):
            check_edit_price(case, price)
        open_order_summary(case.page, expected_total=2 * price)
