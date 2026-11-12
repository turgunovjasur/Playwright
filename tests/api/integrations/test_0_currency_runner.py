"""Setupni o‘zgartirmaydigan alohida tashqi kurs runneri."""
import allure
import pytest
from tests.api.integrations.test_01_currency_refresh import run_currency_refresh

pytestmark = [pytest.mark.api_external, allure.epic("API"),
              allure.feature("Tashqi xizmatlar"), allure.story("Markaziy bank kursi")]


@allure.title("EXT-01: Markaziy bankdan USD kursini yangilash")
def test_01_currency_refresh(currency_baseline):
    run_currency_refresh(currency_baseline)
