"""API equivalent of UI setup step 20: Natural Person For Client."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Natural Person For Client")]


def run_natural_person_for_client_1(api_setup):
    """1 - Create a natural person with the Client flag
    2 - Read back the natural person
    3 - Verify the person appears in the client list
    """
    s = api_setup
    with allure.step("1 - Create a natural person with the Client flag"):
        api = s.user()
        result = s.send(api, "natural_client")
        s.save_id("client_person_id", result["person_id"])
    with allure.step("2 - Read back the natural person"):
        view = api.model("anor/mr/person/natural_person_view", person_id=s["client_person_id"])
        require_fields(view, name=f"natural_client-pw{s.code}", code=f"c_n_c_pw{s.code}", state="A")
    with allure.step("3 - Verify the person appears in the client list"):
        row = api.one("anor/mrf/client_list:table", ["client_id", "name"], filters=["client_id", "=", s["client_person_id"]])
        require_fields(row, name=f"natural_client-pw{s.code}")


@allure.title("API 20 - Natural Person For Client")
def test_20_natural_person_for_client_1(api_setup):
    run_natural_person_for_client_1(api_setup)
