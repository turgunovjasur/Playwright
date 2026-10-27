"""API equivalent of UI setup step 02: Filial."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Filial")]


def run_filial(api_setup):
    """1 - Resolve UZS and USD currency IDs from this company
    2 - Create the filial linked to the legal person
    3 - Verify the filial and legal-person link
    """
    s = api_setup
    with allure.step("1 - Resolve UZS and USD currency IDs from this company"):
        api = s.admin(head_filial=True)
        for code, key in (("860", "currency_id_uzb"), ("840", "currency_id")):
            row = api.one("anor/mr/filial+add:currencies", ["currency_id", "code", "name"], filters=["code", "=", code])
            s.save_id(key, row["currency_id"])
    with allure.step("2 - Create the filial linked to the legal person"):
        result = s.send(api, "filial")
        s.save_id("filial_id", result["filial_id"])
    with allure.step("3 - Verify the filial and legal-person link"):
        view = api.model("anor/mr/filial_view", filial_id=s["filial_id"])
        require_fields(view, name=f"filial-pw{s.code}", legal_person_code=s["legal_person_code"], base_currency_name="Узбекский сум", state="A")
        s.save(filial_name=view["name"], filial_legal_person_code=s["legal_person_code"], filial_currency="Узбекский сум")


@allure.title("API 02 - Filial")
def test_02_filial(api_setup):
    run_filial(api_setup)
