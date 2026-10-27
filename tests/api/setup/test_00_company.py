"""API equivalent of UI setup step 00: Company."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Company")]


def run_company(api_setup):
    """1 - Require an observed company-create contract
    """
    with allure.step("1 - Require an observed company-create contract"):
        raise APIError(
            "COMPANY_CODE=1 is not supported by this captured API suite yet: "
            "the setup network trace used an existing company. Capture company_add:save "
            "and security requests with a working head account before enabling this mode."
        )


@allure.title("API 00 - Company")
def test_00_company(api_setup):
    run_company(api_setup)
