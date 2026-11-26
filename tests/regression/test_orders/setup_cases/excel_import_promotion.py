"""Excel importiga bog‘liq A5→B1 aksiya tayyorlovi."""

from copy import deepcopy

import allure

from tests.api.client import positive_id, require_fields
from tests.api.promotion import verify_promotion
from tests.api.state import CONTRACTS
from tests.regression.helpers.retry.reconcile import exact_row
from tests.regression.helpers.retry.state import stable_uuid
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def run_prepare_import_promotion(baseline, workflow, directory, *, label="Excel"):
    """1. Guruh SKUlari uchun besh donaga bitta ixtiyoriy bonus yaratish.
    2. Saqlangan aksiya, muddat, ombor, narx va xona shartlarini tekshirish.
    """
    state = RegressionSetupState(directory / "import-promotion-state.json", deepcopy(baseline))
    try:
        api = state.user()
        suffix = stable_uuid("excel_bonus").hex[:12]
        payload = state.payload("quantity_bonus")
        payload.update(name=f"Order {label} 5+1-{suffix}", code=f"{label.lower()}-bonus-{suffix}", forced="N")
        condition = payload["conditions"][0]
        condition["rules"][0]["main_value"] = "5"
        condition["bonuses"][0]["products"][0].update(product_id=baseline["product_id_usa"], value="1")
        table = "anor/mcg/action_list:table"
        with allure.step("1 - Shu guruhning tovari uchun A5 → B1 ixtiyoriy aksiyasini tayyorlash"):
            existing = exact_row(api, table, "action_id", "name", payload["name"])
            if existing is None:
                api.call(CONTRACTS["quantity_bonus"]["endpoint"], payload)
        with allure.step("2 - Saqlangan aksiyaning sharti, bonusi va qo‘llanish doirasini tekshirish"):
            row = api.one(table, ["action_id", "name", "start_date", "end_date", "action_state"],
                          filters=["name", "=", payload["name"]])
            require_fields(row, name=payload["name"], start_date=payload["start_date"],
                           end_date=payload["end_date"], action_state="A")
            action_id = positive_id(row["action_id"])
            verify_promotion(api, action_id, payload)
            model = api.model("anor/mcg/action+edit", action_id=action_id)
            require_fields(model, forced="N")
            for field, expected in (("price_types", payload["price_type_id"]), ("rooms", payload["room_ids"]),
                                    ("payment_types", payload["payment_type_id"])):
                if {str(record[0]) for record in model[field]} != set(map(str, expected)):
                    raise AssertionError(f"Saqlangan aksiyada {field} sharti mos emas")
            workflow["promotions"] = {"unit_price": "1000", "bonus": {"name": payload["name"], "action_id": action_id}}
    finally:
        state.close()
