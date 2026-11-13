"""ORD-11: Archive qarz yaratishi, Restore Delivered va Cancel rollback."""

from decimal import Decimal

import allure
import pytest

from tests.smoke.test_life_cycle.flow_order.order_regression import change_order_status, open_order, read_settlement, read_stock, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order statuslari")]


def run_archive_restore(page, order_case):
    """1. Own New → Shipped → Delivered order. 2. Archive: open order → qarz.

    3. Restore Delivered: qarz → open order, stock qayta chiqmaydi.
    4. Cancel fizik qoldiq va saldoni qaytaradi.
    """
    base = AutoBasePage(page)
    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Own qty2 × 100 USD orderni New saqlash"):
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
    change_order_status(page, order_id, "Отгружен")
    change_order_status(page, order_id, "Доставлен")

    transitions = (("Архив", "active", "Архив", "48", "200", "0"), ("Восстановить", "archive", "Доставлен", "48", "0", "200"), ("Отменен", "active", "Отменен", "50", "0", "0"))
    for index, (action, listing, status, physical, debt, open_amount) in enumerate(transitions, start=2):
        change_order_status(page, order_id, action, listing=listing)
        with allure.step(f"{index} - {action}: {status}, bir xil ID va 200 USD"):
            base.form_view(label="ИД заказа", expect_value=order_id)
            base.form_view(label="Статус", expect_value=status)
            base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
        if status == "Архив":
            with allure.step("Archive order active ro'yxatda qolmasligi"):
                base.navigate_to(tab="Продажа", name="Заказы")
                base.expect_page(heading="Заказы", url="order_list")
                base.grid_setting(menu_name="Настройка таблицы", field_name="ИД заказа", search_name="ИД заказа")
                base.grid_controller(search=order_id)
                base.grid(state="empty")
        with allure.step(f"{index}.1 - {status}: stock va iqtisodiy vektor"):
            expected_stock = {"physical": Decimal(physical), "booked": Decimal("0"), "available": Decimal(physical)}
            actual_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
            if actual_stock != expected_stock:
                pytest.fail(f"{status} stock: expected={expected_stock}, actual={actual_stock}")
            expected_saldo = {"debt": Decimal(debt), "prepayment": Decimal("0"), "open_order": Decimal(open_amount), "booked_prepayment": Decimal("0"), "balance": -Decimal(debt) - Decimal(open_amount)}
            actual_saldo = read_settlement(page, order_case.client, order_case.currency, allow_empty=status == "Отменен")
            if actual_saldo != expected_saldo:
                pytest.fail(f"{status} saldo: expected={expected_saldo}, actual={actual_saldo}")


@allure.title("ORD-11: Archive → Restore Delivered → Cancel")
def test_archive_restore(page, order_case):
    run_archive_restore(page, order_case)
