"""API equivalent of UI setup step 08: Role."""

import allure
import pytest

from tests.api.client import APIError
from tests.smoke.test_setup.test_08_role import ROLE_PERMISSIONS


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Role")]


def run_role(api_setup):
    """1 - Resolve the same Admin permissions selected by UI setup
    2 - Enable those permissions without changing unrelated switches
    3 - Verify every requested permission was persisted
    """
    s = api_setup
    with allure.step("1 - Resolve the UI setup Admin permissions"):
        api = s.admin()
        model = api.model("trade/tr/role+edit", role_id=s["role_id"])
        functions = model["functions"]
        if not functions:
            raise APIError("Admin role returned no permission functions")
        requested_ids = set()
        for name in ROLE_PERMISSIONS:
            matches = [row for row in functions if row["name"] == name]
            if len(matches) != 1:
                raise APIError(f"Admin permission {name!r}: expected one function, found {len(matches)}")
            requested_ids.add(str(matches[0]["function_id"]))
        # UI sets its named switches to checked; other switches keep their state.
        expected_enabled = requested_ids | {
            str(row["function_id"]) for row in functions if row["state"] == "Y"
        }
    with allure.step("2 - Enable the same permissions as UI setup"):
        payload = {key: model[key] for key in ("role_id", "name", "order_no", "state", "pcode")}
        payload["function_ids"] = [
            row["function_id"] for row in functions
            if str(row["function_id"]) in expected_enabled
        ]
        api.call("trade/tr/role+edit:save", payload, timeout=(60, 1_200))
    with allure.step("3 - Verify every requested permission was persisted"):
        actual = api.model("trade/tr/role+edit", role_id=s["role_id"])["functions"]
        enabled = {str(row["function_id"]) for row in actual if row["state"] == "Y"}
        if enabled != expected_enabled:
            raise APIError("Admin role permissions differ from the UI setup selection")


@allure.title("API 08 - Role")
def test_08_role(api_setup):
    run_role(api_setup)
