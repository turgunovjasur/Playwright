import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("Finance"),
    allure.story("Client Offset"),
]


# ----------------------------------------------------------------------------------------------------------------------


def run_offset_client_balance(page, code, require_data):
    """Testcase: client debt va prepaymentini o'zaro hisob-kitob qilish.

    1. Settlement listida teng debt va prepaymentni tekshirib, clientni tanlash.
    2. Offset modalini ochib, default sana va optionlarni tekshirish.
    3. Offsetni tasdiqlab, clientning net debt/prepayment qoldig'ini tekshirish.
    """
    base = BasePage(page)
    client = f"natural_client-pw{code}"
    payment_amount = 7_000
    baseline = require_data("group_0_offset_baseline")
    debt_before_offset = baseline["debt"] + payment_amount
    prepayment_before_offset = baseline["prepayment"] + payment_amount
    expected_order = baseline["order"]
    expected_reserved_prepayment = baseline["reserved_prepayment"]
    expected_balance = baseline["balance"]

    with allure.step("1 - Client debt va prepaymentini settlementda tekshirish"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        base.grid_controller(search=client)
        row = base.grid(client, root="b-grid:visible")
        base.grid_cell(row, 1, expect_value=client)
        base.grid_cell(row, 2, expect_value="Узбекский сум")
        base.grid_cell(row, 3, expect_value=debt_before_offset, remove_spaces=True)
        base.grid_cell(row, 4, expect_value=prepayment_before_offset, remove_spaces=True)
        base.grid_cell(row, 5, expect_value=expected_order, remove_spaces=True)
        base.grid_cell(row, 6, expect_value=expected_reserved_prepayment, remove_spaces=True)
        base.grid_cell(row, 7, expect_value=expected_balance, remove_spaces=True)

    with allure.step("2 - Взаиморасчет modalini ochib defaultlarni tekshirish"):
        base.click(name="Взаиморасчет", exact=True)
        modal = page.get_by_role("dialog").filter(has=page.get_by_role("heading", name="Взаиморасчет", exact=True))
        base.expect_page(heading="Взаиморасчет", root=modal)
        base.input(placeholder="Выбрать дату", expect_value=base.date(), root=modal)
        for label in (
            "с учетом консигнации",
            "по проекту",
            "по договору",
            "по типу оплаты",
        ):
            base.checkbox(label=label, expect_checked=True, root=modal)

    with allure.step("3 - Offsetni tasdiqlab, client summalarini tekshirish"):
        base.click(name="Подтвердить", exact=True, root=modal)
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        net_prepayment = prepayment_before_offset - debt_before_offset
        expected_debt = max(-net_prepayment, 0)
        expected_prepayment = max(net_prepayment, 0)

        base.grid_controller(search=client)
        expected_values = (expected_debt, expected_prepayment, expected_order, expected_reserved_prepayment, expected_balance)
        if any(expected_values):
            row = base.grid(client, root="b-grid:visible")
            base.grid_cell(row, 1, expect_value=client)
            base.grid_cell(row, 2, expect_value="Узбекский сум")
            base.grid_cell(row, 3, expect_value=expected_debt, remove_spaces=True)
            base.grid_cell(row, 4, expect_value=expected_prepayment, remove_spaces=True)
            base.grid_cell(row, 5, expect_value=expected_order, remove_spaces=True)
            base.grid_cell(row, 6, expect_value=expected_reserved_prepayment, remove_spaces=True)
            base.grid_cell(row, 7, expect_value=expected_balance, remove_spaces=True)
        elif base.grid(client, root="b-grid:visible", return_bool=True):
            row = base.grid(client, root="b-grid:visible")
            base.grid_cell(row, 1, expect_value=client)
            base.grid_cell(row, 2, expect_value="Узбекский сум")
            base.grid_cell(row, 3, expect_value=0, remove_spaces=True)
            base.grid_cell(row, 4, expect_value=0, remove_spaces=True)
            base.grid_cell(row, 5, expect_value=0, remove_spaces=True)
            base.grid_cell(row, 6, expect_value=0, remove_spaces=True)
            base.grid_cell(row, 7, expect_value=0, remove_spaces=True)
        else:
            base.grid(root="b-grid:visible", state="empty")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Client debt va prepaymentini o'zaro hisob-kitob qilish")
def test_offset_client_balance(page, code, require_data):
    authorization(page, who="user", code=code)
    run_offset_client_balance(page, code, require_data)
