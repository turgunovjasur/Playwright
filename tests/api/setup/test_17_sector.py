"""API equivalent of UI setup step 17: Sector."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Sector")]


def run_sector(api_setup):
    """1 - Create the setup TMC set linked to the room
    2 - Verify the TMC set in the server table
    """
    s = api_setup
    with allure.step("1 - Create the setup TMC set linked to the room"):
        api = s.user()
        result = s.send(api, "sector")
        s.save_id("sector_id", result["sector_id"])
    with allure.step("2 - Verify the TMC set in the server table"):
        row = api.one("anor/mr/sector_list:table", ["sector_id", "name", "code", "state"], filters=["sector_id", "=", s["sector_id"]])
        require_fields(row, name=f"sector-pw{s.code}", code=f"c_s_pw{s.code}", state="A")


@allure.title("API 17 - Sector")
def test_17_sector(api_setup):
    run_sector(api_setup)
