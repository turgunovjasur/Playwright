"""API equivalent of UI setup step 18: Product UZS."""

import allure
import pytest

from tests.api.client import APIError, require_fields
from decimal import Decimal

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Product UZS")]


def run_product(api_setup):
    """1 - Resolve the unit of measure
    2 - Create the product in the setup TMC set
    3 - Set the product price to 7000
    4 - Read back product fields and price
    """
    s = api_setup
    with allure.step("1 - Resolve the unit of measure"):
        api = s.user()
        measure = api.one("anor/mr/product/inventory+add:measures", ["measure_id", "short_name"], filters=["short_name", "=", "шт"])
        s.save_id("measure_id", measure["measure_id"])
    with allure.step("2 - Create the product in the setup TMC set"):
        result = s.send(api, "product")
        s.save_id("product_id", result["product_id"])
    with allure.step("3 - Set the product price to 7000"):
        api.call("anor/mr/product/product_set_price$save", {"product_id": s["product_id"], "prices": [{"price_type_id": s["price_type_id_uzb"], "card_id": "-1", "price": "7000"}]})
    with allure.step("4 - Read back product fields and price"):
        view = api.model("anor/mr/product/inventory_view", product_id=s["product_id"])
        payload = s.payload("product")
        require_fields(view, name=payload["name"], code=payload["code"], state="A")
        model = api.model("anor/mr/product/product_set_price", product_id=s["product_id"])
        rows = [row for row in model["prices"] if str(row[0]) == str(s["price_type_id_uzb"]) and str(row[3]) == "-1"]
        if len(rows) != 1 or Decimal(str(rows[0][5])) != Decimal("7000"):
            raise APIError("Product selling price was not persisted")


@allure.title("API 18 - Product UZS")
def test_18_product(api_setup):
    run_product(api_setup)
