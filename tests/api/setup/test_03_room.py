"""API equivalent of UI setup step 03: Room."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Room")]


def run_room(api_setup):
    """1 - Create a distribution work zone in the new filial
    2 - Verify saved work-zone fields
    """
    s = api_setup
    with allure.step("1 - Create a distribution work zone in the new filial"):
        api = s.admin()
        result = s.send(api, "room")
        s.save_id("room_id", result["room_id"])
    with allure.step("2 - Verify saved work-zone fields"):
        view = api.model("anor/mrf/room_view", room_id=s["room_id"])
        require_fields(view, name=f"room-pw{s.code}", code=f"c_rm_pw{s.code}", state="A")


@allure.title("API 03 - Room")
def test_03_room(api_setup):
    run_room(api_setup)
