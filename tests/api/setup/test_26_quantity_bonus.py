"""API equivalent of UI setup step 26: Quantity Bonus."""

import allure
import pytest

from tests.api.client import require_fields
from tests.api.client import positive_id
from tests.api.promotion import verify_promotion

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Quantity Bonus")]


def run_quantity_bonus(api_setup):
    """1 - Create the Quantity Bonus promotion with the UI setup conditions
    2 - Verify the saved promotion name, dates, type and state
    3 - Verify persisted promotion rules and bonus values
    4 - Save promotion metadata for API setup consumers
    """
    s = api_setup
    with allure.step("1 - Create the Quantity Bonus promotion with the UI setup conditions"):
        api = s.user()
        payload = s.payload("quantity_bonus")
        s.send(api, "quantity_bonus")
    with allure.step("2 - Verify the saved promotion name, dates, type and state"):
        row = api.one("anor/mcg/action_list:table", ["action_id", "name", "calc_kind_name", "start_date", "end_date", "action_state"], filters=["name", "=", payload["name"]])
        require_fields(row, name=payload["name"], start_date=payload["start_date"], end_date=payload["end_date"], action_state="A", calc_kind_name="Кол-во" if payload["calc_kind"] == "Q" else "Сумма")
        action_id = positive_id(row["action_id"])
    with allure.step("3 - Verify persisted promotion rules and bonus values"):
        verify_promotion(api, action_id, payload)
    with allure.step("4 - Save promotion metadata for API setup consumers" ):
        rule = payload["conditions"][0]["rules"][0]
        bonus = payload["conditions"][0]["bonuses"][0]
        s.save(**{"action_quantity_bonus": {"action_id": action_id, "name": payload["name"], "code": payload["code"], "start_date": payload["start_date"], "end_date": payload["end_date"], "threshold": rule["main_value"], "bonus_value": bonus["products"][0]["value"], "product_name": f"product-pw{s.code}", "room_name": f"room-pw{s.code}", "price_type_name": f"Price Type UZB-pw{s.code}"}})


@allure.title("API 26 - Quantity Bonus")
def test_26_quantity_bonus(api_setup):
    run_quantity_bonus(api_setup)
