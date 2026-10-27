"""API equivalent of UI setup step 23: Init Balance."""

import allure
import pytest

from tests.api.client import APIError, require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Init Balance")]


def run_init_balance(api_setup):
    """4 - Verify postings contain 100 units and 500 000 UZS
    """
    s = api_setup
    api = s.user()
    for contract, key in (("init_balance_uzb", "init_balance_id_uzb"), ("init_balance_usa", "init_balance_id_usa")):
        with allure.step(f"1 - Save {contract}: 100 units at its setup purchase price"):
            payload = s.payload(contract)
            s.send(api, contract)
        with allure.step(f"2 - Resolve and post the saved {contract} document"):
            endpoint = "anor/mkw/init_balance/init_inventory_balance_list:table"
            columns = ["balance_id", "balance_number", "warehouse_name", "currency_name", "posted"]
            row = api.one(endpoint, columns, filters=["balance_number", "=", payload["balance_number"]])
            s.save_id(key, row["balance_id"])
            require_fields(row, posted="N", warehouse_name="Основной склад")
            api.call("anor/mkw/init_balance/init_inventory_balance_list:post", {"balance_id": s[key]})
        with allure.step(f"3 - Verify {contract} is posted with the expected currency"):
            row = api.one(endpoint, columns, filters=["balance_id", "=", s[key]])
            require_fields(row, posted="Y", currency_name="Узбекский сум" if contract.endswith("uzb") else "Доллар США")
        if contract == "init_balance_uzb":
            with allure.step("4 - Verify postings contain 100 units and 500 000 UZS"):
                rows = api.report_rows(
                    "anor/mkw/init_balance/init_inventory_balance_list:transactions",
                    balance_id=s[key],
                )
                if not any({"100", "500000"}.issubset({cell.replace(" ", "") for cell in row}) for row in rows):
                    raise APIError("UZS inventory posting is missing 100 units / 500 000 UZS")


@allure.title("API 23 - Init Balance")
def test_23_init_balance(api_setup):
    run_init_balance(api_setup)
