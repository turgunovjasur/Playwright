"""Umumiy bonus limiti uchun alohida narx, klientlar va aksiya tayyorlovi.

API faqat tayyorlovga tegishli. Buyurtma va limit sarfi UI orqali tekshiriladi.
"""
from copy import deepcopy
from decimal import Decimal
import json
from tests.regression.helpers.retry.state import stable_uuid as uuid4
import allure
import pytest
from tests.api.client import APIError, positive_id, require_fields
from tests.api.promotion import verify_promotion
from tests.api.state import CONTRACTS
from tests.regression.test_orders.helpers.preparations.resources import resource_ready, resource_status
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client

pytestmark = [pytest.mark.regression, pytest.mark.order_positive]


def persist(data, directory):
    path = directory / "bonus-limit-setup.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def run_prepare_price(baseline, data, directory):
    """1. Oldingi narx/bog‘lanishlar. 2. Own UZS narx. 3. 7000 va preservation."""
    data.update(status="process", run_id=uuid4("bonus_limit_setup").hex[:12], limit="2", retention="retained")
    for name in ("clients", "prices", "orders"):
        data.setdefault(name, {})
    resource_status(data, "price", "process")
    state = RegressionSetupState(directory / "state.json", deepcopy(baseline))
    try:
        api = state.user()
        with allure.step("1 - Mavjud narxlar va xona bog‘lanishlarini o‘qish"):
            def prices():
                rows = api.model("anor/mr/product/product_set_price", product_id=baseline["product_id"])["prices"]
                return {(str(r[0]), str(r[3])): Decimal(str(r[5])) for r in rows if r[5] not in (None, "")}
            def attached():
                return {str(r["price_type_id"]) for r in api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"], data={"room_id": baseline["room_id"], "attached": "Y"})}
            before, before_ids = prices(), attached()
        with allure.step("2 - Bonus limiti guruhi uchun alohida UZS narx turi"):
            payload = state.payload("price_type_uzb")
            payload.update(name=f"Order bonus limit UZS-pw{state.code}-{data['run_id']}", code=f"quota-{data['run_id']}")
            identity = positive_id(api.call(CONTRACTS["price_type_uzb"]["endpoint"], payload)["price_type_id"])
            data["prices"]["quota"] = {"id": identity, "name": payload["name"], "unit_price": "7000"}
            persist(data, directory)
            require_fields(api.model("anor/mkr/price_type_view", price_type_id=identity), name=payload["name"], currency_name="Узбекский сум", state="A")
        with allure.step("3 - Yangi narx 7000; oldingi narxlar va bog‘lanishlar o‘zgarmagan"):
            api.call("anor/mr/product/product_set_price$save", {"product_id": baseline["product_id"], "prices": [{"price_type_id": identity, "card_id": "-1", "price": "7000"}]})
            if prices() != {**before, (identity, "-1"): Decimal("7000")}:
                raise APIError("Yangi narx yoki oldingi narxlar saqlanishi mos emas")
            if attached() != before_ids | {identity}:
                raise APIError("Xona narx bog‘lanishlari mos emas")
            data["status"] = "price_ready"
            resource_status(data, "price", "passed")
    except Exception:
        data["status"] = "failed"
        resource_status(data, "price", "failed")
        raise
    finally:
        persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), "Umumiy bonus limiti tayyorlovi", allure.attachment_type.JSON)
        state.close()


def run_prepare_client(baseline, data, directory, kind):
    """1. Own aktiv klient. 2. Saved identity. 3. Additive xona attachment."""
    data.setdefault("clients", {})
    data["clients"][kind] = prepare_order_client(baseline, purpose="bonus-limit", kind=kind, directory=directory)
    persist(data, directory)


def run_prepare_action(baseline, data, directory):
    """1. 10 dona uchun bonus1, global cap2. 2. Saved qoida va isolation."""
    if not resource_ready(data, "price"):
        raise APIError("Bonus limiti uchun tekshirilgan narx tayyorlovi kerak")
    resource_status(data, "bonus", "process")
    state = RegressionSetupState(directory / "state.json", deepcopy(baseline))
    try:
        api = state.user()
        with allure.step("1 - 10 dona uchun bonus1, barcha klientlar uchun umumiy limit2"):
            payload = state.payload("cyclic_bonus")
            payload.update(name=f"Order global bonus limit-pw{state.code}-{data['run_id']}", code=f"quota-action-{data['run_id']}", forced="N", price_type_id=[data["prices"]["quota"]["id"]])
            reward = payload["conditions"][0]["bonuses"][0]["products"][0]
            reward.update(product_id=str(baseline["product_id_usa"]), value="1", max_value="")
            payload["bonus_limits"] = [{"product_id": str(baseline["product_id_usa"]), "inventory_kind": "G", "limit_quant": "2"}]
            api.call(CONTRACTS["cyclic_bonus"]["endpoint"], payload)
            row = api.one("anor/mcg/action_list:table", ["action_id", "name"], filters=["name", "=", payload["name"]])
            identity = positive_id(row["action_id"])
            data["bonus"] = {"action_id": identity, "name": payload["name"]}
            persist(data, directory)
        with allure.step("2 - Saved cyclic qoida, boshqa bonus mahsuloti va global limit"):
            verify_promotion(api, identity, payload)
            model = api.model("anor/mcg/action+edit", action_id=identity)
            require_fields(model, forced="N", condition_operator=payload["condition_operator"])
            saved_reward = model["conditions"][0]["bonuses"][0]["products"][0]
            if "max_value" not in saved_reward or saved_reward["max_value"] not in (None, ""):
                raise APIError("Bonus max_value bo‘sh bo‘lishi kerak: global limit boshqa chegara bilan almashtirilmaydi")
            for field, expected in (("price_types", payload["price_type_id"]), ("rooms", payload["room_ids"])):
                if {str(r[0]) for r in model[field]} != {str(v) for v in expected}:
                    raise APIError(f"Global bonus {field} isolation mos emas")
            # Captured action.html maps product_id,name,inventory_kind,kind_name,limit_quant,used_quant.
            limits = model["bonus_limits"]
            if len(limits) != 1 or str(limits[0][0]) != str(baseline["product_id_usa"]) or limits[0][2] != "G" or Decimal(str(limits[0][4])) != 2:
                raise APIError("Saved umumiy bonus limiti mahsulot/tur/miqdori mos emas")
            data["status"] = "passed"
            resource_status(data, "bonus", "passed")
    except Exception:
        data["status"] = "failed"
        resource_status(data, "bonus", "failed")
        raise
    finally:
        persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), "Umumiy bonus limiti tayyorlovi", allure.attachment_type.JSON)
        state.close()
