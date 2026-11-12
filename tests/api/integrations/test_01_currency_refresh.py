"""Markaziy bank kursi — baseline tayyorlovidan mustaqil tashqi integratsiya."""
from datetime import datetime
from decimal import Decimal
import allure
import pytest
from tests.api.client import APIError

pytestmark = [pytest.mark.api_external, allure.epic("API"),
              allure.feature("Tashqi xizmatlar"), allure.story("Markaziy bank kursi")]


def run_currency_refresh(state):
    """1. Markaziy bankdan USD kursini yangilash.
    2. Saqlangan kurslar ro‘yxati bo‘sh emasligini va eng yangi kurs musbatligini tekshirish.
    HTTP 500 haqiqiy FAIL; xato yashirilmaydi, qo‘lda kurs bilan almashtirilmaydi.
    Dam olish kunida bugungi kurs bo‘lishini majburlamaydi.
    """
    with allure.step("1 - Markaziy bankdan USD kursini yangilash"):
        api = state.user()
        api.call("anor/mk/currency_view:update_currency_rate", api.context(currency_id=state["currency_id"]))
    with allure.step("2 - Saqlangan eng yangi kurs sanasi va musbat qiymati"):
        rates = api.table("anor/mk/currency_view:currency_rates", ["rate_date", "rate"], data={"currency_id": state["currency_id"]})
        if not rates:
            raise APIError("Kurs yangilanganidan keyin saqlangan kurslar ro‘yxati bo‘sh")
        latest = max(rates, key=lambda row: datetime.strptime(row["rate_date"], "%d.%m.%Y"))
        if Decimal(str(latest["rate"])) <= 0:
            raise APIError("Saqlangan eng yangi kurs musbat emas")
        allure.attach(f"Sana: {latest['rate_date']}\nKurs: {latest['rate']}", "Saqlangan kurs", allure.attachment_type.TEXT)


@allure.title("EXT-01: Markaziy bankdan USD kursini yangilash")
def test_currency_refresh(currency_baseline):
    run_currency_refresh(currency_baseline)
