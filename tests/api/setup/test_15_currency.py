"""UI kabi CBU yangilash va regression uchun manual kursni saqlash."""

import allure
import pytest

from tests.api.client import APIError, require_fields
from tests.api.integrations.test_01_currency_refresh import run_currency_refresh


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Currency")]


def run_currency(api_setup):
    """1 - Save the deterministic manual rate used by the regression baseline
    2 - Read back today's rate
    """
    s = api_setup
    central_bank_error = None
    try:
        run_currency_refresh(s)
    except APIError as error:
        # UI also preserves the manual baseline while reporting the CBU failure.
        central_bank_error = error
    with allure.step("1 - Test uchun belgilangan valyuta kursini saqlash"):
        api = s.user()
        payload = s.payload("currency_rate")
        s.send(api, "currency_rate")
    with allure.step("2 - Bugungi saqlangan kursni qayta o‘qib tekshirish"):
        row = api.one("anor/mk/currency_view:currency_rates", ["rate_date", "rate"], filters=["rate_date", "=", payload["rate_date"]], data={"currency_id": s["currency_id"]})
        require_fields(row, rate=payload["rate"])
    if central_bank_error:
        raise APIError("CBU refresh failed; manual rate was saved and verified") from central_bank_error


@allure.title("API 15 - Currency")
def test_15_currency(api_setup):
    run_currency(api_setup)
