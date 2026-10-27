"""API equivalent of UI setup step 15: Currency."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Currency")]


def run_currency(api_setup):
    """1 - Refresh the central-bank USD exchange rate
    2 - Save the same manual rate used by UI setup
    3 - Read back today's rate
    """
    s = api_setup
    with allure.step("1 - Refresh the central-bank USD exchange rate"):
        api = s.user()
        api.call("anor/mk/currency_view:update_currency_rate", api.context(currency_id=s["currency_id"]))
    with allure.step("2 - Save the same manual rate used by UI setup"):
        payload = s.payload("currency_rate")
        s.send(api, "currency_rate")
    with allure.step("3 - Read back today's rate"):
        row = api.one("anor/mk/currency_view:currency_rates", ["rate_date", "rate"], filters=["rate_date", "=", payload["rate_date"]], data={"currency_id": s["currency_id"]})
        require_fields(row, rate=payload["rate"])


@allure.title("API 15 - Currency")
def test_15_currency(api_setup):
    run_currency(api_setup)
