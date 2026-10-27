"""API equivalent of UI setup step 09: Role Attach Form."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Role Attach Form")]


def run_role_attach_form(api_setup):
    """1 - Grant the Admin role access to all forms
    2 - Verify the available forms list is empty
    """
    s = api_setup
    with allure.step("1 - Grant the Admin role access to all forms"):
        api = s.admin()
        api.call("biruni/md/role_form_list$access_generate_all", {"role_id": s["role_id"], "generate": "Y"})
    with allure.step("2 - Verify the available forms list is empty"):
        rows = api.table("biruni/md/role_form_list:form_table", ["form"], data={"role_id": s["role_id"], "attached": "N"})
        if rows:
            raise APIError("Admin role still has unavailable forms")


@allure.title("API 09 - Role Attach Form")
def test_09_role_attach_form(api_setup):
    run_role_attach_form(api_setup)
