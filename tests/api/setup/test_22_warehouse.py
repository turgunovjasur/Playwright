"""API equivalent of UI setup step 22: Warehouse."""

import allure
import pytest

from tests.api.client import require_fields


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Warehouse")]


def run_warehouse(api_setup):
    """1 - Resolve the main warehouse in the setup filial
    2 - Read back the active warehouse
    """
    s = api_setup
    with allure.step("1 - Resolve the main warehouse in the setup filial"):
        api = s.user()
        row = api.one("anor/mkw/warehouse_list:table", ["warehouse_id", "name", "state"], filters=["name", "=", "Основной склад"])
        s.save_id("warehouse_id", row["warehouse_id"])
    with allure.step("2 - Read back the active warehouse"):
        view = api.model("anor/mkw/warehouse_view", warehouse_id=s["warehouse_id"])
        require_fields(view, name="Основной склад", state="A")


@allure.title("API 22 - Warehouse")
def test_22_warehouse(api_setup):
    run_warehouse(api_setup)
