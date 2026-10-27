"""API equivalent of UI setup step 06: User."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("User")]


def run_user(api_setup):
    """1 - Create a user linked to the person and staff
    2 - Verify user, staff and filial links
    """
    s = api_setup
    with allure.step("1 - Create a user linked to the person and staff"):
        api = s.admin()
        result = s.send(api, "user", user_id=s["user_person_id"])
        s.save_id("user_id", result["user_id"])
    with allure.step("2 - Verify user, staff and filial links"):
        view = api.model("anor/mr/user_view", user_id=s["user_id"])
        require_fields(view, login=f"user-pw{s.code}", person_name=f"natural_person-pw{s.code}", robot_names=f"robot-pw{s.code}", filial_names=f"filial-pw{s.code}", state="A")


@allure.title("API 06 - User")
def test_06_user(api_setup):
    run_user(api_setup)
