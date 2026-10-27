"""API equivalent of UI setup step 10: Buy License."""

import allure
import pytest

from tests.api.client import APIError
from tests.smoke.test_setup.flow_setup.flow_license import license_policy_disabled, license_purchase_server_unsupported

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Buy License")]


def run_buy_license(api_setup):
    """1 - Apply the same server and license-policy conditions as UI setup
    """
    with allure.step("1 - Apply the same server and license-policy conditions as UI setup"):
        if license_policy_disabled():
            pytest.skip("Licensing policy is disabled for the new company")
        if license_purchase_server_unsupported():
            pytest.skip("UI setup also skips license purchase on smartup.online")
        raise APIError(
            "License purchase was skipped by the captured UI setup. "
            "Capture the purchase request on a supported server before enabling this API case."
        )


@allure.title("API 10 - Buy License")
def test_10_buy_license(api_setup):
    run_buy_license(api_setup)
