"""API equivalent of UI setup step 12: Change Password."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Change Password")]


def run_change_password(api_setup):
    """1 - Login as the newly created user
    2 - Confirm the initial password through the observed endpoint
    3 - Authenticate again and verify access to the user dashboard
    """
    s = api_setup
    with allure.step("1 - Login as the newly created user"):
        api = s.user()
        info = api.call("biruni/m:session")
        require_fields(info["user"], password_change_required="Y")
    with allure.step("2 - Confirm the initial password through the observed endpoint"):
        s.send(api, "change_password")
    with allure.step("3 - Authenticate again and verify access to the user dashboard"):
        api = s.user(fresh=True)
        api.call("trade/intro/dashboard:model", api.context())
        info = api.call("biruni/m:session")
        require_fields(info["user"], password_change_required="N")


@allure.title("API 12 - Change Password")
def test_12_change_password(api_setup):
    run_change_password(api_setup)
