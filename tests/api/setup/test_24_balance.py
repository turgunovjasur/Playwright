"""API equivalent of UI setup step 24: Balance."""

import allure
import pytest

from tests.api.client import APIError
from decimal import Decimal

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Balance")]


def run_balance(api_setup):
    """1 - Query inventory balances in the setup filial
    2 - Verify both setup products have 100 units in the main warehouse
    """
    s = api_setup
    with allure.step("1 - Query inventory balances in the setup filial"):
        api = s.user()
        rows = api.table("anor/mkw/balance/balance_list:table", ["product_code", "warehouse_name", "balance_quant"])
    with allure.step("2 - Verify both setup products have 100 units in the main warehouse"):
        for code in (f"c_p_pw{s.code}", f"c_p_usa_pw{s.code}"):
            matches = [row for row in rows if row["product_code"] == code and row["warehouse_name"] == "Основной склад"]
            if not matches or sum(Decimal(str(row["balance_quant"])) for row in matches) != Decimal("100"):
                raise APIError("Posted setup inventory does not contain 100 units of each product")


@allure.title("API 24 - Balance")
def test_24_balance(api_setup):
    run_balance(api_setup)
