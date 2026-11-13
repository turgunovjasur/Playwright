"""Majburiy bonus + ixtiyoriy skidka: faqat shu guruhga tegishli API tayyorlovlar."""
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

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.feature("Majburiy va ixtiyoriy aksiyalar birga")]


def _persist(data, directory):
    path = directory / "mixed-promotions-setup.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_prepare_price(baseline, data, directory):
    """1. Mavjud narxlar, room bog‘lanishlari va bank paymentni o‘qish.
    2. Guruh uchun yangi UZS narx turini yaratish va 7 000 belgilash.
    3. Saqlangan yangi narx, room membership va oldingi qiymatlarni tekshirish.
    """
    data.update(status="process", run_id=uuid4("mixed_promotions_setup").hex[:12], prices={}, payments={},
                unit_price="7000", url=baseline["url"], filial_id=str(baseline["filial_id"]),
                retention="retained")
    resource_status(data, "price", "process")
    state = RegressionSetupState(directory / "state.json", deepcopy(baseline))
    try:
        api = state.user()
        with allure.step("1 - Mavjud narxlar va roomdagi bank to‘lov turini tekshirish"):
            payments = api.table("anor/mrf/room_attachment:table_payment_type", ["payment_type_id", "name"],
                                 data={"room_id": baseline["room_id"], "attached": "Y"})
            bank = [row for row in payments if row["name"] == "Перечисление"]
            if len(bank) != 1:
                raise APIError("Mixed aksiya uchun roomda yagona Перечисление turi kerak")
            data["payments"]["bank"] = {"id": positive_id(bank[0]["payment_type_id"]), "name": bank[0]["name"]}
            rows = api.model("anor/mr/product/product_set_price", product_id=baseline["product_id"])["prices"]
            before = {(str(row[0]), str(row[3])): Decimal(str(row[5])) for row in rows if row[5] not in (None, "")}
            attached = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"],
                                 data={"room_id": baseline["room_id"], "attached": "Y"})
            before_ids = {str(row["price_type_id"]) for row in attached}
            _persist(data, directory)
        with allure.step("2 - Faqat shu guruh uchun UZS narx turi va 7 000 so‘m narx"):
            payload = state.payload("price_type_uzb")
            payload.update(name=f"Order mixed UZS-pw{state.code}-{data['run_id']}", code=f"mixed-{data['run_id']}")
            identity = positive_id(api.call(CONTRACTS["price_type_uzb"]["endpoint"], payload)["price_type_id"])
            data["prices"]["mixed"] = {"id": identity, "name": payload["name"], "unit_price": "7000"}
            _persist(data, directory)
            require_fields(api.model("anor/mkr/price_type_view", price_type_id=identity),
                           name=payload["name"], currency_name="Узбекский сум", state="A")
            api.call("anor/mr/product/product_set_price$save", {"product_id": baseline["product_id"],
                     "prices": [{"price_type_id": identity, "card_id": "-1", "price": "7000"}]})
        with allure.step("3 - Yangi narx va room bog‘lanishi; oldingi narxlar o‘zgarmagan"):
            rows = api.model("anor/mr/product/product_set_price", product_id=baseline["product_id"])["prices"]
            actual = {(str(row[0]), str(row[3])): Decimal(str(row[5])) for row in rows if row[5] not in (None, "")}
            if actual != {**before, (identity, "-1"): Decimal("7000")}:
                raise APIError("Yangi yoki mavjud mahsulot narxlari kutilgan qiymatlarga mos emas")
            attached = api.table("anor/mrf/room_attachment:table_price_type", ["price_type_id"],
                                 data={"room_id": baseline["room_id"], "attached": "Y"})
            if {str(row["price_type_id"]) for row in attached} != before_ids | {identity}:
                raise APIError("Room narx bog‘lanishlari oldingi ro‘yxat + yangi narxga teng emas")
            data["status"] = "price_ready"
            resource_status(data, "price", "passed")
    except Exception as error:
        data.update(status="failed", error_type=type(error).__name__)
        resource_status(data, "price", "failed")
        raise
    finally:
        _persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), "Mixed aksiyalar tayyorlovi", allure.attachment_type.JSON)
        state.close()


def _prepare_action(baseline, data, directory, *, kind):
    if not resource_ready(data, "price"):
        raise APIError("Mixed aksiya uchun narx/to‘lov tayyorlovi tugashi kerak")
    resource_status(data, kind, "process")
    state = RegressionSetupState(directory / "state.json", deepcopy(baseline))
    contract = "quantity_bonus" if kind == "bonus" else "quantity_discount"
    forced, reward = ("Y", "1") if kind == "bonus" else ("N", "10")
    product_id = str(baseline["product_id_usa"] if kind == "bonus" else baseline["product_id"])
    try:
        api = state.user()
        with allure.step(f"1 - {kind}: A10 sharti, majburiy={forced}; alohida narx va bank to‘lovi"):
            payload = state.payload(contract)
            payload.update(name=f"Order mixed {kind}-pw{state.code}-{data['run_id']}",
                           code=f"mixed-{kind}-{data['run_id']}", forced=forced,
                           price_type_id=[data["prices"]["mixed"]["id"]],
                           payment_type_id=[data["payments"]["bank"]["id"]])
            payload["conditions"][0]["rules"][0]["main_value"] = "10"
            payload["conditions"][0]["bonuses"][0]["products"][0].update(product_id=product_id, value=reward)
            data[kind] = {"name": payload["name"], "code": payload["code"], "forced": forced,
                          "threshold": "10", "bonus_value": reward, "product_id": product_id,
                          "start_date": payload["start_date"], "end_date": payload["end_date"]}
            _persist(data, directory)
            api.call(CONTRACTS[contract]["endpoint"], payload)
            row = api.one("anor/mcg/action_list:table", ["action_id", "name"], filters=["name", "=", payload["name"]])
            data[kind]["action_id"] = positive_id(row["action_id"])
            _persist(data, directory)
        with allure.step("2 - Saved shart, bonus/chegirma va aynan shu narx/payment/roomni tekshirish"):
            verify_promotion(api, data[kind]["action_id"], payload)
            model = api.model("anor/mcg/action+edit", action_id=data[kind]["action_id"])
            require_fields(model, forced=forced, condition_operator=payload["condition_operator"])
            for field, expected in (("price_types", payload["price_type_id"]),
                                    ("payment_types", payload["payment_type_id"]), ("rooms", payload["room_ids"])):
                if {str(row[0]) for row in model[field]} != {str(value) for value in expected}:
                    raise APIError(f"Mixed aksiya {field} bog‘lanishi noto‘g‘ri")
            resource_status(data, kind, "passed")
            data["status"] = "passed" if all(resource_ready(data, key) for key in ("bonus", "discount")) else "actions_partial"
    except Exception as error:
        data.update(status="failed", error_type=type(error).__name__)
        resource_status(data, kind, "failed")
        raise
    finally:
        _persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), "Mixed aksiyalar tayyorlovi", allure.attachment_type.JSON)
        state.close()


def run_prepare_mandatory_bonus(baseline, data, directory):
    """1. Yangi narx tayyor. 2. A10 → B1 majburiy aksiyani yaratish va qayta o‘qish."""
    _prepare_action(baseline, data, directory, kind="bonus")


def run_prepare_optional_discount(baseline, data, directory):
    """1. Guruh narxi tayyor. 2. A10 → 10% ixtiyoriy aksiyani yaratish va qayta o‘qish."""
    _prepare_action(baseline, data, directory, kind="discount")
