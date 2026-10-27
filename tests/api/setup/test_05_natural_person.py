"""API equivalent of UI setup step 05: Natural Person."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Natural Person")]


def run_natural_person(api_setup):
    """1 - Create the natural person for the new user
    2 - Verify person name, code and state
    """
    s = api_setup
    with allure.step("1 - Create the natural person for the new user"):
        api = s.admin()
        result = s.send(api, "natural_person")
        s.save_id("user_person_id", result["person_id"])
    with allure.step("2 - Verify person name, code and state"):
        view = api.model("anor/mr/person/natural_person_view", person_id=s["user_person_id"])
        require_fields(view, name=f"natural_person-pw{s.code}", code=f"c_n_p_pw{s.code}", state="A")


@allure.title("API 05 - Natural Person")
def test_05_natural_person(api_setup):
    run_natural_person(api_setup)
