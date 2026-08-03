import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("Finance"),
    allure.story("Client Payment"),
]


# ----------------------------------------------------------------------------------------------------------------------


def run_post_client_payment(page, code, require_data):
    """Testcase: archive order qarziga teng client paymentni post qilish.

    1. Client payment listini ochish.
    2. Yangi payment formasini ochish.
    3. Client, summa, payment type va cashboxni to'ldirish.
    4. Avtomatik offsetni yoqmasdan paymentni post qilish.
    5. Settlement rowda debt va prepayment alohida saqlanganini tekshirish.
    """
    base = BasePage(page)
    client = f"natural_client-pw{code}"
    payment_amount = 7_000
    baseline = require_data("group_0_offset_baseline")
    expected_debt = baseline["debt"] + payment_amount
    expected_prepayment = baseline["prepayment"] + payment_amount
    expected_order = baseline["order"]
    expected_reserved_prepayment = baseline["reserved_prepayment"]
    expected_balance = baseline["balance"]

    with allure.step("1 - Оплаты от клиентов sahifasini ochish"):
        base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")

    with allure.step("2 - Yangi client payment formasini ochish"):
        base.click(name="Создать")
        base.expect_page(heading="Оплата от клиента / Создание", url="cashin+add")

    with allure.step("3 - Client payment maydonlarini to'ldirish"):
        base.b_input(label="Клиент", value=client)
        base.form_view(label="Баланс", expect_value=str(baseline["prepayment"] - expected_debt), remove_spaces=True)
        base.input(label="Сумма", value="7000")
        base.b_input(label="Тип оплаты", value="Наличные деньги")
        base.b_input(label="Касса", value="Основная касса")
        base.checkbox(label="Провести взаимозачёт", expect_checked=False)

    with allure.step("4 - Paymentni Провести qilish"):
        base.click(name="Провести")
        base.confirm_biruni(expected_text="Провести?")
        base.expect_page(heading="Оплата от клиента / Создание", url="cashin+add")

    with allure.step("5 - Debt va prepayment settlementda tekshiriladi"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        base.grid_controller(search=client)
        row = base.grid(client, root="b-grid:visible")
        base.grid_cell(row, 1, expect_value=client)
        base.grid_cell(row, 2, expect_value="Узбекский сум")
        base.grid_cell(row, 3, expect_value=expected_debt, remove_spaces=True)
        base.grid_cell(row, 4, expect_value=expected_prepayment, remove_spaces=True)
        base.grid_cell(row, 5, expect_value=expected_order, remove_spaces=True)
        base.grid_cell(row, 6, expect_value=expected_reserved_prepayment, remove_spaces=True)
        base.grid_cell(row, 7, expect_value=expected_balance, remove_spaces=True)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Client paymentni Провести qilish")
def test_post_client_payment(page, code, require_data):
    authorization(page, who="user", code=code)
    run_post_client_payment(page, code, require_data)
