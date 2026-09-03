import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("Order"),
    allure.story("Archive And Debt"),
]


# ----------------------------------------------------------------------------------------------------------------------


def run_archive_base_order(page, code, load_data):
    """Testcase: 0-01 yaratgan aniq orderni archive qilib, qarz detailda tekshirish.

    1. Saqlangan order IDni olib, order listini ochish.
    2. Aynan shu orderni `Архив` statusiga o'tkazish.
    3. Client settlement listini ochish.
    4. Debt detailda order ID, summa va archive statusini tekshirish.
    """
    base = BasePage(page)
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
        status_button = page.locator(f"#status-btn-{order_id}")
        order_row = status_button.locator("xpath=ancestor::div[contains(@class, 'tbl-row')][1]")
        base.text(client, "7 000", "Новый", root=order_row)

    with allure.step("2 - Aynan shu orderni Архив statusiga o'tkazish"):
        status_button.locator(".dropdown-toggle").click()
        base.click(name="Архив", root=status_button)
        base.confirm_biruni(expected_text="Изменить статус на Архив?")
        base.expect_page(heading="Заказы", url="order_list")
        expect(page.locator(f"#status-btn-{order_id}")).to_have_count(0)

    with allure.step("3 - Взаиморасчеты с клиентами sahifasini ochish"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        base.grid_controller(search=client)
        row = base.grid(client, root="b-grid:visible", click=True)
        base.grid_cell(row, 1, expect_value=client)
        base.grid_cell(row, 2, expect_value="Узбекский сум")
        base.grid_cell(row, 3, expect_value=expected_debt, remove_spaces=True)
        base.grid_cell(row, 4, expect_value=expected_prepayment, remove_spaces=True)
        base.grid_cell(row, 5, expect_value=expected_order, remove_spaces=True)
        base.grid_cell(row, 6, expect_value=expected_reserved_prepayment, remove_spaces=True)
        base.grid_cell(row, 7, expect_value=expected_balance, remove_spaces=True)

    with allure.step("4 - Debt detailda archive orderni tekshirish"):
        base.click(name="Детали", exact=True, root=row)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")
        base.grid(order_id, client, "7 000", "Архив")
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Exact orderni Архивga o'tkazish va debt detailda tekshirish")
def test_archive_base_order(page, code, load_data):
    authorization(page, who="user", code=code)
    run_archive_base_order(page, code, load_data)
