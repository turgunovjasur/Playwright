"""ORD-09: normal operational statuslar, rezerv va open-order saldo."""

from decimal import Decimal

import allure
import pytest

from tests.smoke.test_life_cycle.flow_order.order_regression import change_order_status, open_order, read_settlement, read_stock, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order statuslari")]


def run_status_cycle(page, order_case):
    """1. Own 200 USD Draft. 2. New → Processing → Waiting rezervi.

    3. Shipped → Delivered jismoniy chiqim faqat bir marta. 4. Har statusda saldo.
    """
    base = AutoBasePage(page)
    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Qty2 × 100 USD Draft tayyorlash"):
        goods = 'b-pg-grid[name="goods_items"]'
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)
        base.input(ng_model="item.quantity", value="2", press_tab=True, root=goods)
        base.click(locator="#anor279-button-next_step")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)

    # Expected sonlar biznes qoidani ochiq ifodalaydi, helper ichiga yashirilmaydi.
    states = (("Черновик", "50", "0", "50", "0"), ("Новый", "50", "2", "48", "200"), ("В обработке", "50", "2", "48", "200"), ("В ожидании", "50", "2", "48", "200"), ("Отгружен", "48", "0", "48", "200"), ("Доставлен", "48", "0", "48", "200"))
    for index, (status, physical, booked, available, open_amount) in enumerate(states, start=2):
        if status != "Черновик":
            change_order_status(page, order_id, status)
        with allure.step(f"{index} - {status}: stock va mijoz saldosini tekshirish"):
            base.form_view(label="ИД заказа", expect_value=order_id)
            base.form_view(label="Статус", expect_value=status)
            base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
            expected_stock = {"physical": Decimal(physical), "booked": Decimal(booked), "available": Decimal(available)}
            actual_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
            if actual_stock != expected_stock:
                pytest.fail(f"{status} stock: expected={expected_stock}, actual={actual_stock}")
            expected_saldo = {"debt": Decimal("0"), "prepayment": Decimal("0"), "open_order": Decimal(open_amount), "booked_prepayment": Decimal("0"), "balance": -Decimal(open_amount)}
            actual_saldo = read_settlement(page, order_case.client, order_case.currency, allow_empty=status == "Черновик")
            if actual_saldo != expected_saldo:
                pytest.fail(f"{status} saldo: expected={expected_saldo}, actual={actual_saldo}")


@allure.title("ORD-09: Draft → New → Processing → Waiting → Shipped → Delivered")
def test_status_cycle(page, order_case):
    run_status_cycle(page, order_case)
