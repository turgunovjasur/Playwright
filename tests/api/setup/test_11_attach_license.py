"""API equivalent of UI setup step 11: Attach License."""

import allure
import pytest

from tests.api.client import APIError
from tests.smoke.test_setup.flow_setup.flow_license import license_policy_disabled

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Attach License")]


def run_attach_license(api_setup):
    """1 - Resolve the active ERP users license
    2 - Detach current users, matching the UI setup license step
    3 - Attach and verify the setup user
    """
    s = api_setup
    if license_policy_disabled():
        pytest.skip("Licensing policy is disabled for the new company")
    with allure.step("1 - Resolve the active ERP users license"):
        api = s.admin(head_filial=True)
        licenses = api.table("biruni/kl/license_list:table_license", ["license_id", "license_name", "status"], filters=["status", "=", ["A", "P"]], sort=["-created_on"])
        matches = [row for row in licenses if row["license_name"] == "ERP users"]
        if not matches:
            raise APIError("No active ERP users license found")
        # UI chooses the first ERP users row, newest purchase first.
        license_id = matches[0]["license_id"]
        purchased = s.values.get("purchased_license_id")
        if purchased and str(license_id) != str(purchased):
            raise APIError("Newest ERP users license differs from this run's verified purchase")
    with allure.step("2 - Detach current users, matching the UI setup license step"):
        data = {"license_id": license_id, "attached": "Y", "filter_license_id": None}
        attached = api.table("biruni/kl/license_user_list:table", ["user_id", "name"], data=data)
        previous_users = [row["user_id"] for row in attached]
        if previous_users:
            api.call("biruni/kl/license_user_list$detach", {"license_id": license_id, "user_id": previous_users})
    with allure.step("3 - Attach and verify the setup user"):
        api.call("biruni/kl/license_user_list$attach", {"license_id": license_id, "user_id": s["user_id"]})
        actual = api.table("biruni/kl/license_user_list:table", ["user_id"], data=data)
        if {str(row["user_id"]) for row in actual} != {str(s["user_id"])}:
            raise APIError("ERP users license was not assigned to the setup user")
        s.save_id("license_id", license_id)


@allure.title("API 11 - Attach License")
def test_11_attach_license(api_setup):
    run_attach_license(api_setup)
