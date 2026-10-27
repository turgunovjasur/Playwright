"""API equivalent of UI setup step 16: Payment Type."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Payment Type")]


def run_payment_type(api_setup):
    """1 - Read available payment types
    2 - Attach the available payment types to the filial
    3 - Verify the four baseline payment types and save the cash ID
    """
    s = api_setup
    with allure.step("1 - Read available payment types"):
        api = s.user()
        rows = api.table("anor/mkr/payment_type_list+attach:table", ["payment_type_id", "name"], filters=["state", "=", "A"])
    with allure.step("2 - Attach the available payment types to the filial"):
        if rows:
            api.call("anor/mkr/payment_type_list+attach$attach", api.context(payment_type_id=[row["payment_type_id"] for row in rows]))
    with allure.step("3 - Verify the four baseline payment types and save the cash ID"):
        attached = api.table("anor/mkr/payment_type_list:table", ["payment_type_id", "name"], filters=["state", "=", "A"])
        expected = {"Наличные деньги", "Перечисление", "Терминал", "Чековая книжка"}
        if not expected.issubset({row["name"] for row in attached}):
            raise APIError("Required payment types are missing from the filial")
        cash = next(row for row in attached if row["name"] == "Наличные деньги")
        s.save_id("payment_type_id", cash["payment_type_id"])


@allure.title("API 16 - Payment Type")
def test_16_payment_type(api_setup):
    run_payment_type(api_setup)
