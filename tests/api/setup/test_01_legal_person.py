"""API equivalent of UI setup step 01: Legal Person."""

import allure
import pytest
from faker import Faker

from tests.api.client import APIError, require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Legal Person")]


def run_legal_person(api_setup):
    """1 - Login as company admin and load legal-person defaults
    2 - Create the setup legal person
    3 - Read back name, code and active state
    """
    s = api_setup
    legal_name = f"{Faker('ru_RU').company()} legal_person-pw{s.code}"
    legal_code = s.payload("legal_person")["code"]
    with allure.step("1 - Login as company admin and load legal-person defaults"):
        api = s.admin(head_filial=True)
        model = api.model("anor/mr/person/legal_person+add")
    with allure.step("2 - Create the setup legal person"):
        if s.values.get("legal_person_id"):
            raise APIError(
                "Bu setup uchun yuridik shaxs IDsi avval saqlangan. "
                "Yakka yaratish qadamini yangi kod bilan bajarish uchun .env da NEW_CODE=1 qo‘ying."
            )
        result = s.send(api, "legal_person", name=legal_name, person_types=[{"person_group_id": row[0]} for row in model.get("person_groups", [])])
        s.save_id("legal_person_id", result["person_id"])
    with allure.step("3 - Read back name, code and active state"):
        view = api.model("anor/mr/person/legal_person_view", person_id=s["legal_person_id"])
        require_fields(view, name=legal_name, code=legal_code, state="A")
        s.save(legal_person_code=legal_code, legal_person_name=view["name"])


@allure.title("API 01 - Legal Person")
def test_01_legal_person(api_setup):
    run_legal_person(api_setup)
