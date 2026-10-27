"""API equivalent of UI setup step 08: Role."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Role")]


def run_role(api_setup):
    """1 - Read all Admin role functions
    2 - Enable every role permission
    3 - Verify every requested permission was persisted
    """
    s = api_setup
    with allure.step("1 - Read all Admin role functions"):
        api = s.admin()
        model = api.model("trade/tr/role+edit", role_id=s["role_id"])
        functions = model["functions"]
        if not functions:
            raise APIError("Admin role returned no permission functions")
    with allure.step("2 - Enable every role permission"):
        payload = {key: model[key] for key in ("role_id", "name", "order_no", "state", "pcode")}
        payload["function_ids"] = [row["function_id"] for row in functions]
        api.call("trade/tr/role+edit:save", payload, timeout=(20, 600))
    with allure.step("3 - Verify every requested permission was persisted"):
        actual = api.model("trade/tr/role+edit", role_id=s["role_id"])["functions"]
        enabled = {str(row["function_id"]) for row in actual if row["state"] == "Y"}
        if not set(payload["function_ids"]).issubset(enabled):
            raise APIError("Admin role has permissions that were not enabled")


@allure.title("API 08 - Role")
def test_08_role(api_setup):
    run_role(api_setup)
