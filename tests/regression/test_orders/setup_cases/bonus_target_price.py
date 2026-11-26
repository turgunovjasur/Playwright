"""Ikkinchi UZS narx turi aksiya qo‘llanmaydigan sotuv uchun."""
from copy import deepcopy
from decimal import Decimal

from tests.api.client import positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.helpers.retry.reconcile import exact_row
from tests.regression.helpers.retry.state import RetryBlocked, stable_uuid
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def run_prepare_target_price(baseline, workflow, directory):
    """1. Guruh uchun narx turini topish yoki yaratish. 2. Ikkala narxni tekshirish."""
    suffix = stable_uuid("bonus_target_price").hex[:12]
    code, name = f"bp-{suffix}", f"Order bonus UZS-{suffix}"
    state = RegressionSetupState(directory / "target-price-state.json", deepcopy(baseline))
    try:
        api = state.user()
        row = exact_row(api, "anor/mkr/price_type_list:table", "price_type_id", "code", code)
        if row is None:
            payload = state.payload("price_type_uzb")
            payload.update(code=code, name=name)
            row = api.call(CONTRACTS["price_type_uzb"]["endpoint"], payload)
        target = positive_id(row["price_type_id"])
        require_fields(api.model("anor/mkr/price_type_view", price_type_id=target),
                       name=name, code=code, state="A", currency_name="Узбекский сум")
        room_types = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"],
                               data={"room_id": baseline["room_id"], "attached": "Y"})
        original = str(baseline["price_type_id_uzb"])
        if target == original or target not in {str(row["price_type_id"]) for row in room_types}:
            raise RetryBlocked("Xonada ikkinchi mustaqil UZS narx turi kerak")

        def prices():
            rows = api.model("anor/mr/product/product_set_price", product_id=baseline["product_id"])["prices"]
            return {str(r[0]): Decimal(str(r[5])) for r in rows if str(r[3]) == "-1" and r[5] not in ("", None)}

        before = prices()
        if before.get(original) != 1000 or before.get(target) not in (None, 1500):
            raise RetryBlocked("Guruh mahsulotining boshlang‘ich narxlari mos emas")
        if target not in before:
            api.call("anor/mr/product/product_set_price$save", {"product_id": baseline["product_id"],
                     "prices": [{"price_type_id": target, "card_id": "-1", "price": "1500"}]})
        if prices() != {**before, target: Decimal(1500)}:
            raise AssertionError("Mahsulotning eski va yangi narxlari saqlanmadi")
        workflow["target_price"] = name
    finally:
        state.close()
