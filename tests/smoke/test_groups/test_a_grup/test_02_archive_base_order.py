import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_a_grup.flow_settlement.flow_settlement import settlement_columns
from utils.data_store import load_data
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("Order"),
    allure.story("Archive And Debt"),
]


# ----------------------------------------------------------------------------------------------------------------------


def run_archive_base_order(page, code):
    """Testcase: 0-01 yaratgan aniq orderni archive qilib, qarz detailda tekshirish.

    1. Saqlangan order IDni olib, order listini ochish.
    2. Aynan shu orderni `Архив` statusiga o'tkazish.
    3. Client settlement listini ochish.
    4. Debt detailda order ID, summa va archive statusini tekshirish.
    """
    base = AutoBasePage(page)
    client = f"natural_client-pw{code}"
    order_amount = 7_000
    order_id = str(load_data("group_0_order_id"))
    baseline = load_data("group_0_offset_baseline")
    expected_debt = baseline["debt"] + order_amount
    expected_prepayment = baseline["prepayment"]
    expected_order = baseline["order"]
    expected_reserved_prepayment = baseline["reserved_prepayment"]
    expected_balance = baseline["balance"] - order_amount

    with allure.step("1 - Saqlangan order ID bo'yicha order listini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="ИД заказа", search_name="Клиент")
        base.grid_controller(search=client)
        order_matcher = re.compile(rf"(?<!\d){re.escape(order_id)}(?!\d)")
        order_row = base.grid(order_matcher, client, "7 000", "Новый")

    with allure.step("2 - Aynan shu orderni Архив statusiga o'tkazish"):
        base.click(name="Изменить статус", exact=True, root=order_row)
        base.click(name="Архив", role="menuitem", exact=True)
        base.confirm_biruni(expected_text="Изменить статус на Архив?")
        base.expect_page(heading="Заказы", url="order_list")
        expect(order_row).to_have_count(0)

    with allure.step("3 - Взаиморасчеты с клиентами sahifasini ochish"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        columns = settlement_columns(page)
        base.grid_controller(search=client)
        row = base.grid(client, click=True)
        base.grid_cell(row, columns["client"], expect_value=client)
        base.grid_cell(row, columns["currency"], expect_value="Узбекский сум")
        base.grid_cell(row, columns["debt"], expect_value=expected_debt, remove_spaces=True)
        base.grid_cell(row, columns["prepayment"], expect_value=expected_prepayment, remove_spaces=True)
        base.grid_cell(row, columns["order"], expect_value=expected_order, remove_spaces=True)
        base.grid_cell(row, columns["reserved_prepayment"], expect_value=expected_reserved_prepayment, remove_spaces=True)
        base.grid_cell(row, columns["balance"], expect_value=expected_balance, remove_spaces=True)

    with allure.step("4 - Debt detailda archive orderni tekshirish"):
        base.click(name="Детали", exact=True)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")
        base.grid(order_id, client, "7 000", "Архив")
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Exact orderni Архивga o'tkazish va debt detailda tekshirish")
def test_archive_base_order(page, code):
    authorization(page, who="user", code=code)
    run_archive_base_order(page, code)
