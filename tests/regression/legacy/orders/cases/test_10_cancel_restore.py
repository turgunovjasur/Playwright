"""ORD-10: bekor qilish va shu order IDni Draftga tiklash."""

from decimal import Decimal

import allure
import pytest

from tests.smoke.test_life_cycle.flow_order.order_regression import change_order_status, open_order, read_settlement, read_stock, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order statuslari")]


def run_cancel_restore(page, order_case):
    """1. Own New qty2 order va rezerv. 2. Cancel rezerv/saldoni qaytaradi.

    3. Active ro'yxatdan chiqish. 4. Canceled Restore shu IDdagi Draftga qaytadi.
    """
    base = AutoBasePage(page)
    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Own 200 USD New orderni tayyorlash"):
        goods = 'b-pg-grid[name="goods_items"]'
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)
        base.input(ng_model="item.quantity", value="2", press_tab=True, root=goods)
        base.click(locator="#anor279-button-next_step")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Новый")
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)
    with allure.step("2 - New rezerv va open-order summasining baseline'i"):
        expected_stock = {"physical": Decimal("50"), "booked": Decimal("2"), "available": Decimal("48")}
        actual_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
        if actual_stock != expected_stock:
            pytest.fail(f"New stock: expected={expected_stock}, actual={actual_stock}")
        expected_saldo = {"debt": Decimal("0"), "prepayment": Decimal("0"), "open_order": Decimal("200"), "booked_prepayment": Decimal("0"), "balance": Decimal("-200")}
        actual_saldo = read_settlement(page, order_case.client, order_case.currency)
        if actual_saldo != expected_saldo:
            pytest.fail(f"New saldo: expected={expected_saldo}, actual={actual_saldo}")

    change_order_status(page, order_id, "Отменен")
    with allure.step("3 - Cancel active ro'yxatdan chiqaradi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="ИД заказа", search_name="ИД заказа")
        base.grid_controller(search=order_id)
        base.grid(state="empty")

    for index, status in enumerate(("Отменен", "Черновик"), start=4):
        if status == "Черновик":
            change_order_status(page, order_id, "Восстановить", listing="canceled")
            base.form_view(label="ИД заказа", expect_value=order_id)
            base.form_view(label="Статус", expect_value="Черновик")
            base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
        with allure.step(f"{index} - {status}: physical 50, rezerv 0, saldo 0"):
            expected_stock = {"physical": Decimal("50"), "booked": Decimal("0"), "available": Decimal("50")}
            actual_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
            if actual_stock != expected_stock:
                pytest.fail(f"{status} stock: expected={expected_stock}, actual={actual_stock}")
            expected_saldo = {key: Decimal("0") for key in ("debt", "prepayment", "open_order", "booked_prepayment", "balance")}
            actual_saldo = read_settlement(page, order_case.client, order_case.currency, allow_empty=True)
            if actual_saldo != expected_saldo:
                pytest.fail(f"{status} saldo: expected={expected_saldo}, actual={actual_saldo}")


@allure.title("ORD-10: Cancel → Canceled list → Restore Draft")
def test_cancel_restore(page, order_case):
    run_cancel_restore(page, order_case)
