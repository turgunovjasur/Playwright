"""API equivalent of UI setup step 01: Legal Person."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Legal Person")]


def run_legal_person(api_setup):
    """1 - Login as company admin and load legal-person defaults
    2 - Create the setup legal person
    3 - Read back name, code and active state
    """
    s = api_setup
    with allure.step("1 - Login as company admin and load legal-person defaults"):
        api = s.admin(head_filial=True)
        model = api.model("anor/mr/person/legal_person+add")
    with allure.step("2 - Create the setup legal person"):
        result = s.send(api, "legal_person", person_types=[{"person_group_id": row[0]} for row in model.get("person_groups", [])])
        s.save_id("legal_person_id", result["person_id"])
    with allure.step("3 - Read back name, code and active state"):
        view = api.model("anor/mr/person/legal_person_view", person_id=s["legal_person_id"])
        require_fields(view, name=f"legal_person-pw{s.code}", code=f"c_l_p_pw{s.code}", state="A")
        s.save(legal_person_code=f"c_l_p_pw{s.code}", legal_person_name=view["name"])


@allure.title("API 01 - Legal Person")
def test_01_legal_person(api_setup):
    run_legal_person(api_setup)
