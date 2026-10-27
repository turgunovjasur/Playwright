"""API equivalent of UI setup step 13: Price Type UZB."""

import allure
import pytest

from tests.api.client import APIError, require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Price Type UZB")]


def run_price_type_uzb(api_setup):
    """1 - Create the Price Type UZB price type and link it to the setup room
    2 - Verify the price type, currency and room
    """
    s = api_setup
    with allure.step("1 - Create the Price Type UZB price type and link it to the setup room"):
        api = s.user()
        result = s.send(api, "price_type_uzb")
        s.save_id("price_type_id_uzb", result["price_type_id"])
    with allure.step("2 - Verify the price type, currency and room"):
        model = api.model("anor/mkr/price_type_view", price_type_id=s["price_type_id_uzb"])
        require_fields(model, name="Price Type UZB-pw" + s.code, currency_name="Узбекский сум", price_type_kind_name="Цена продажи", state="A")
        rooms = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"], data={"room_id": s["room_id"], "attached": "Y"})
        if not any(str(row["price_type_id"]) == s["price_type_id_uzb"] for row in rooms):
            raise APIError("UZS price type is not attached to the setup room")
        s.save(**{"price_type_name_UZB": model["name"]})


@allure.title("API 13 - Price Type UZB")
def test_13_price_type_uzb(api_setup):
    run_price_type_uzb(api_setup)
