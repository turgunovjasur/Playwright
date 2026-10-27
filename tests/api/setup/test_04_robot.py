"""API equivalent of UI setup step 04: Robot."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Robot")]


def run_robot(api_setup):
    """1 - Resolve the Admin role
    2 - Create staff linked to the room and role
    3 - Read back staff, room and role
    """
    s = api_setup
    with allure.step("1 - Resolve the Admin role"):
        api = s.admin()
        role = api.one("anor/mrf/robot+add:roles", ["role_id", "name"], filters=["name", "=", "Админ"])
        s.save_id("role_id", role["role_id"])
    with allure.step("2 - Create staff linked to the room and role"):
        result = s.send(api, "robot")
        s.save_id("robot_id", result["robot_id"])
    with allure.step("3 - Read back staff, room and role"):
        view = api.model("anor/mrf/robot_view", robot_id=s["robot_id"])
        require_fields(view, name=f"robot-pw{s.code}", code=f"c_rb_pw{s.code}", room_names=f"room-pw{s.code}", role_names="Админ", state="A")


@allure.title("API 04 - Robot")
def test_04_robot(api_setup):
    run_robot(api_setup)
