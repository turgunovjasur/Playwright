"""Deterministic currency rate prerequisite for the API baseline."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Currency")]


def run_currency(api_setup):
    """1 - Save the deterministic manual rate used by the regression baseline
    2 - Read back today's rate
    """
    s = api_setup
    with allure.step("1 - Test uchun belgilangan valyuta kursini saqlash"):
        api = s.user()
        payload = s.payload("currency_rate")
        s.send(api, "currency_rate")
    with allure.step("2 - Bugungi saqlangan kursni qayta o‘qib tekshirish"):
        row = api.one("anor/mk/currency_view:currency_rates", ["rate_date", "rate"], filters=["rate_date", "=", payload["rate_date"]], data={"currency_id": s["currency_id"]})
        require_fields(row, rate=payload["rate"])


@allure.title("API 15 - Currency")
def test_15_currency(api_setup):
    run_currency(api_setup)
