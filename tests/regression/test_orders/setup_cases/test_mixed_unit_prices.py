"""Alohida KG va dona mahsulotlarining narx turlari. KG uchun target narx bo‘sh."""
from copy import deepcopy
from decimal import Decimal

from tests.api.client import positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.helpers.preparation.ensure import ensure_preparation
from tests.regression.helpers.preparation.models import PreparationResult, PreparationSpec
from tests.regression.helpers.preparation.registry import Registry
from tests.regression.helpers.retry.reconcile import exact_row
from tests.regression.helpers.retry.state import RetryBlocked, digest
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def run_mixed_prices(baseline, catalog, directory, group, *, change_price):
    registry = Registry(baseline)
    suffix = digest({"run": registry.data["root_run"], "group": group})[:12]
    products = {k: catalog[k]["id"] for k in ("goods", "bonus")}
    spec = PreparationSpec("prices", group, {**products, "change_price": change_price}, ("catalog",))
    state = RegressionSetupState(directory / "mixed-price-state.json", deepcopy(baseline))
    try:
        api = state.user()
        entry = registry.entry(spec)
        types = {}
        for kind in (("piece", "target") if change_price else ("piece",)):
            code = f"mp-{suffix}-{kind}"
            name = f"Order {kind} {suffix}"
            row = exact_row(api, "anor/mkr/price_type_list:table", "price_type_id", "code", code)
            previous = entry["entities"].get(kind)
            if previous and (not row or str(row["price_type_id"]) != previous["id"]):
                raise RetryBlocked("Oldin tasdiqlangan narx turi o‘zgargan")
            if row is None:
                payload = state.payload("price_type_uzb")
                payload.update(name=name, code=code)
                row = api.call(CONTRACTS["price_type_uzb"]["endpoint"], payload)
            identity = positive_id(row["price_type_id"])
            require_fields(api.model("anor/mkr/price_type_view", price_type_id=identity),
                           name=name, state="A", code=code, currency_name="Узбекский сум")
            types[kind] = {"id": identity, "name": name}
            registry.checkpoint(spec, **{kind: types[kind]})

        attached = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"],
                             data={"room_id": baseline["room_id"], "attached": "Y"})
        attached_ids = {str(row["price_type_id"]) for row in attached}
        if not {price_type["id"] for price_type in types.values()} <= attached_ids:
            raise RetryBlocked("Narx turi guruhning ish zonasiga biriktirilmagan")

        prices = {"goods": {str(baseline["price_type_id_uzb"]): Decimal(1000)},
                  "bonus": {entry["id"]: Decimal(1500) for entry in types.values()}}

        def current(kind):
            rows = api.model("anor/mr/product/product_set_price", product_id=products[kind])["prices"]
            result = {}
            for row in rows:
                if str(row[3]) == "-1" and row[5] not in (None, ""):
                    key = str(row[0])
                    if key in result:
                        raise RetryBlocked("Bir mahsulotning narx turi takrorlangan")
                    result[key] = Decimal(str(row[5]))
            if change_price and kind == "goods" and types["target"]["id"] in result:
                raise RetryBlocked("KG uchun yangi narx bo‘sh bo‘lishi kerak")
            for key, price in prices[kind].items():
                if key in result and result[key] != price:
                    raise RetryBlocked("Guruh mahsulotining mavjud narxi kutilgan narxga mos emas")
            return result

        def probe(entry):
            ready = all(prices[k].items() <= current(k).items() for k in products)
            return PreparationResult("ready" if ready else "partial", types,
                                     "KG uchun 1 000, dona mahsulot uchun 1 500 so‘mlik narxlar")

        def prepare(entry):
            for kind, wanted in prices.items():
                if wanted.items() <= current(kind).items():
                    continue
                api.call("anor/mr/product/product_set_price$save", {"product_id": products[kind],
                         "prices": [{"price_type_id": key, "card_id": "-1", "price": str(value)}
                                    for key, value in wanted.items()]})
        ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        catalog["mixed_prices"] = types
    finally:
        state.close()
