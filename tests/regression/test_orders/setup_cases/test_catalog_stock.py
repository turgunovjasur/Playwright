"""Explicit per-group catalog, price and stock steps; API baseline is immutable."""
from copy import deepcopy
from decimal import Decimal
import allure

from tests.api.client import positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.helpers.preparation.models import PreparationSpec, PreparationResult
from tests.regression.helpers.preparation.registry import Registry
from tests.regression.helpers.preparation.ensure import ensure_preparation
from tests.regression.helpers.retry.reconcile import exact_row
from tests.regression.helpers.retry.state import digest, RetryBlocked
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.flows.stock import read_stock

BUDGETS = {"statuses": (2, 0), "promotions": (10, 1), "payments": (12, 1),
    "mandatory": (10, 1), "stock": (2, 0), "bonus_limit": (40, 2),
    "returns": (20, 2), "multi_payments": (5, 0), "manual_discounts": (10, 1),
    "two_warehouses": (5, 0), "mixed_promotions": (10, 1), "recovery": (4, 0),
    "auto_offset": (2, 0), "prepayment_first": (2, 0)}


def run_prepare_catalog(baseline, data, directory, group):
    """1. Exact code lookup. 2. Create only missing own SKU. 3. Saved identity."""
    registry = Registry(baseline)
    spec = PreparationSpec("catalog", group, {"bonus": BUDGETS[group][1] > 0})
    suffix = digest({"root": registry.data["root_run"], "group": group})[:12]
    wanted = {"goods": {"name": f"Order {group} goods-{suffix}", "code": f"rg-{suffix}-a"}}
    if BUDGETS[group][1]:
        wanted["bonus"] = {"name": f"Order {group} bonus-{suffix}", "code": f"rg-{suffix}-b"}
    state = RegressionSetupState(directory / "catalog-api-state.json", deepcopy(baseline))
    try:
        api = state.user()
        def probe(entry):
            found = {}
            for kind, target in wanted.items():
                row = exact_row(api, "anor/mr/product/inventory_list:table", "product_id", "code", target["code"])
                if not row:
                    if kind in entry["entities"]:
                        raise RetryBlocked("Oldin tasdiqlangan own TMZ hozir topilmadi; yangi ID bilan almashtirilmadi")
                    continue
                identity = positive_id(row["product_id"])
                model = api.model("anor/mr/product/inventory_view", product_id=identity)
                require_fields(model, name=target["name"], code=target["code"], state="A")
                found[kind] = {**target, "id": identity}
            registry.checkpoint(spec, **found)
            return PreparationResult("ready" if len(found) == len(wanted) else "partial" if found else "missing",
                                     found, "Own mahsulot ID, kod, nom va faol holat tekshirildi")
        def prepare(entry):
            for kind, target in wanted.items():
                if kind in entry["entities"]:
                    continue
                payload = state.payload("product" if kind == "goods" else "product_usa")
                payload.update(**target)
                with allure.step(f"{group}: {kind} uchun alohida TMZ yaratish"):
                    result = api.call(CONTRACTS["product"]["endpoint"], payload)
                    registry.checkpoint(spec, **{kind: {**target, "id": positive_id(result["product_id"])}})
        result = ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        data.update(result.entities, group=group, status="catalog_ready")
    finally:
        state.close()


def run_prepare_prices(baseline, data, directory, group):
    """1. Read current price. 2. Set only own SKU price. 3. Verify 7000."""
    registry = Registry(baseline)
    price_id = str(baseline["price_type_id_uzb"])
    products = {kind: data[kind] for kind in ("goods", "bonus") if kind in data}
    spec = PreparationSpec("prices", group,
        {"products": {k: v["id"] for k, v in products.items()}, "price_type": price_id, "price": "7000"}, ("catalog",))
    state = RegressionSetupState(directory / "prices-api-state.json", deepcopy(baseline))
    try:
        api = state.user()
        def values():
            found = {}
            for kind, product in products.items():
                rows = api.model("anor/mr/product/product_set_price", product_id=product["id"])["prices"]
                matches = [row for row in rows if str(row[0]) == price_id and str(row[3]) == "-1"]
                if len(matches) > 1:
                    raise RetryBlocked("Own TMZ uchun narx qatori yagona emas")
                # The model includes attached price types before a price is set.
                raw = matches[0][5] if matches else None
                found[kind] = Decimal(str(raw)) if raw not in (None, "") else None
            return found
        def probe(entry):
            actual = values()
            return PreparationResult("ready" if all(v == Decimal(7000) for v in actual.values()) else "partial",
                detail="Own mahsulotlarning saqlangan narxi 7000 so‘m", evidence={k: str(v) for k, v in actual.items()})
        def prepare(entry):
            for kind, actual in values().items():
                if actual == Decimal(7000):
                    continue
                if actual is not None:
                    raise RetryBlocked("Own mahsulot narxi kutilmaganda o‘zgargan; ustidan yozilmadi")
                api.call("anor/mr/product/product_set_price$save", {"product_id": products[kind]["id"],
                    "prices": [{"price_type_id": price_id, "card_id": "-1", "price": "7000"}]})
        ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        data["status"] = "prices_ready"
    finally:
        state.close()


def run_prepare_stock(case, data, directory, group):
    """1. Own fixed documents. 2. Resume posting. 3. Verify UI physical/free stock.

    Replaying this step never adds another document to compensate business usage.
    Returns deliberately have two source lots (9 + 11), exercising 7 + 1 later.
    """
    registry = Registry(case.baseline)
    goods, bonus = BUDGETS[group]
    targets = [("goods", q, i) for i, q in enumerate((9, 11) if group == "returns" else (goods,))]
    if bonus:
        targets.append(("bonus", bonus, 0))
    spec = PreparationSpec("stock", group, {"warehouse": str(case.baseline["warehouse_id"]),
        "targets": [(k, data[k]["id"], q, i) for k, q, i in targets]}, ("prices",))
    state = RegressionSetupState(directory / "stock-api-state.json", deepcopy(case.baseline))
    route = "anor/mkw/init_balance/init_inventory_balance_list"
    try:
        api = state.user()
        docs = []
        for kind, quantity, index in targets:
            suffix = digest({"root": registry.data["root_run"], "scope": group, "kind": kind, "lot": index})[:12]
            docs.append({"number": "RG" + suffix, "kind": kind, "product_id": data[kind]["id"],
                         "quantity": str(quantity), "card_code": "RG" + suffix})
        def lookup(document):
            row = exact_row(api, route + ":table", "balance_id", "balance_number", document["number"])
            if not row:
                return None
            saved = api.one(route + ":table", ["balance_id", "balance_number", "warehouse_name", "posted"],
                            filters=["balance_id", "=", row["balance_id"]])
            require_fields(saved, balance_number=document["number"], warehouse_name="Основной склад")
            return saved
        def probe(entry):
            found = {}
            ready = True
            for document in docs:
                row = lookup(document)
                if row:
                    found[document["number"]] = {**document, "id": positive_id(row["balance_id"]), "posted": row["posted"]}
                if not row or row["posted"] != "Y":
                    ready = False
            registry.checkpoint(spec, **found)
            return PreparationResult("ready" if ready else "partial" if found else "missing", found,
                                     "Own kirim hujjatlari va posted holati tekshirildi")
        def prepare(entry):
            for document in docs:
                row = lookup(document)
                if not row:
                    payload = state.payload("init_balance_uzb" if document["kind"] == "goods" else "init_balance_usa")
                    payload["balance_number"] = document["number"]
                    payload["items"][0].update(product_id=document["product_id"], quantity=document["quantity"], card_code=document["card_code"])
                    api.call(CONTRACTS["init_balance_uzb"]["endpoint"], payload)
                    row = lookup(document)
                    if not row:
                        raise RetryBlocked("Save’dan keyin own kirim topilmadi; ikkinchi Save yuborilmadi")
                registry.checkpoint(spec, **{document["number"]: {**document, "id": str(row["balance_id"]), "posted": row["posted"]}})
                if row["posted"] == "N":
                    api.call(route + ":post", {"balance_id": str(row["balance_id"])})
                elif row["posted"] != "Y":
                    raise RetryBlocked("Kirim posted holati noma’lum")
        result = ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        data["documents"] = result.entities
        for kind, quantity in (("goods", goods), ("bonus", bonus)):
            if not quantity:
                continue
            actual = read_stock(case, "Основной склад", product_id=data[kind]["id"])
            # This explicit setup step runs before the group's business mutations.
            case.check(f"{group}/{kind}: boshlang‘ich fizik, rezerv va erkin qoldiq",
                {"physical": Decimal(quantity), "booked": Decimal(0), "available": Decimal(quantity)}, actual)
        data["status"] = "passed"
    finally:
        state.close()
