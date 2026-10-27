"""API equivalent of UI setup step 14: Price Type USA."""

import allure
import pytest

from tests.api.client import APIError, require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Price Type USA")]


def run_price_type_usa(api_setup):
    """1 - Create the Price Type USA price type and link it to the setup room
    2 - Verify the price type, currency and room
    """
    s = api_setup
    with allure.step("1 - Create the Price Type USA price type and link it to the setup room"):
        api = s.user()
        result = s.send(api, "price_type_usa")
        s.save_id("price_type_id_usa", result["price_type_id"])
    with allure.step("2 - Verify the price type, currency and room"):
        model = api.model("anor/mkr/price_type_view", price_type_id=s["price_type_id_usa"])
        require_fields(model, name="Price Type USA-pw" + s.code, currency_name="Доллар США", price_type_kind_name="Цена продажи", state="A")
        rooms = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"], data={"room_id": s["room_id"], "attached": "Y"})
        if not any(str(row["price_type_id"]) == s["price_type_id_usa"] for row in rooms):
            raise APIError("USD price type is not attached to the setup room")
        s.save(**{"price_type_name_USA": model["name"]})


@allure.title("API 14 - Price Type USA")
def test_14_price_type_usa(api_setup):
    run_price_type_usa(api_setup)
