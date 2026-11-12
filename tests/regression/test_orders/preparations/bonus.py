"""Order biznes caselari uchun API baseline ustiga qo'shiladigan musbat setup.

Shared API/UI baseline o'zgarmaydi. Yangi aksiya va uning dalillari saqlanadi;
order yaratish, chegirmani qo'llash va moliyaviy tekshiruvlar UI testlarda qoladi.
"""

import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from tests.regression.retry.state import stable_uuid as uuid4

import allure

from tests.api.client import APIError, positive_id, require_fields
from tests.api.promotion import verify_promotion
from tests.api.state import CONTRACTS
from tests.regression.test_orders.auth_recovery import RegressionSetupState


ROOT = Path(__file__).resolve().parents[4]


def prepare_business_promotions(baseline):
    """Setup mahsulotlari uchun boshqa mahsulot bonusi yaratib, qayta o'qish.

    1. Setup ma'lumotlari va sotuv narxi 7 000 so'mligini tekshirish.
    2. 10 dona sotuvga 1 dona boshqa mahsulot beradigan ixtiyoriy aksiya yaratish.
    3. Saqlangan aksiya, shart va bonus mahsulotini qayta o'qish.
    4. Bonus metadatasini saqlash; chegirma alohida tayyorlov testida yaratiladi.
    """
    required = (
        "code", "url", "company_code", "filial_id", "user_id", "room_id",
        "warehouse_id", "product_id", "product_id_usa", "price_type_id_uzb",
    )
    if not isinstance(baseline, dict) or any(baseline.get(key) in (None, "", {}) for key in required):
        raise APIError("Order biznes setupi uchun to'liq API baseline kerak")
    if str(baseline["product_id"]) == str(baseline["product_id_usa"]):
        raise APIError("Sotuv va bonus mahsulotlari ikki xil bo'lishi kerak")

    run_id = uuid4("bonus_action").hex[:12]
    directory = ROOT / "test-results/order-business"
    directory.mkdir(parents=True, exist_ok=True)
    from tests.regression.retry.state import ACTIVE
    journal = ACTIVE.get()
    run_directory = journal.directory / ("bonus-" + run_id) if journal else directory / run_id
    run_directory.mkdir(parents=True, exist_ok=False)
    state = RegressionSetupState(run_directory / "state.json", deepcopy(baseline))
    metadata = {
        "status": "process", "run_id": run_id, "code": str(baseline["code"]),
        "url": baseline["url"], "company_code": baseline["company_code"],
        "filial_id": str(baseline["filial_id"]), "room_id": str(baseline["room_id"]),
        "warehouse_id": str(baseline["warehouse_id"]),
        "product_name": baseline.get("product_name", f"product-pw{baseline['code']}"),
        "bonus_product_name": baseline.get("bonus_product_name", f"product-usa-pw{baseline['code']}"),
        "product_id": str(baseline["product_id"]),
        "bonus_product_id": str(baseline["product_id_usa"]),
        "price_type_id": str(baseline["price_type_id_uzb"]),
        "price_type_name": f"Price Type UZB-pw{baseline['code']}",
        "unit_price": "7000", "retention": "retained",
    }

    def persist():
        content = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        (run_directory / "setup.json").write_text(content, encoding="utf-8")
        temporary = directory / "setup.json.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(directory / "setup.json")

    persist()
    try:
        with allure.step("1 - Setup mahsuloti va 7 000 so'm sotuv narxini tekshirish"):
            api = state.user()
            for product_id, product_name in (
                (metadata["product_id"], metadata["product_name"]),
                (metadata["bonus_product_id"], metadata["bonus_product_name"]),
            ):
                model = api.model("anor/mr/product/inventory_view", product_id=product_id)
                require_fields(model, name=product_name, state="A")
            prices = api.model("anor/mr/product/product_set_price", product_id=metadata["product_id"])
            rows = [row for row in prices["prices"]
                    if str(row[0]) == metadata["price_type_id"] and str(row[3]) == "-1"]
            if len(rows) != 1 or Decimal(str(rows[0][5])) != Decimal("7000"):
                raise APIError("Setup mahsulotining narxi 7 000 so'm emas")

        with allure.step("2 - 10 dona mahsulotga 1 dona boshqa mahsulot bonusi yaratish"):
            payload = state.payload("quantity_bonus")
            payload["name"] = f"order-business-bonus-pw{state.code}-{run_id}"
            payload["code"] = f"ob-bonus-{state.code}-{run_id}"
            payload["forced"] = "N"
            payload["conditions"][0]["rules"][0]["main_value"] = "10"
            bonus_product = payload["conditions"][0]["bonuses"][0]["products"][0]
            bonus_product["product_id"] = metadata["bonus_product_id"]
            bonus_product["value"] = "1"
            metadata["bonus"] = {
                "name": payload["name"], "code": payload["code"],
                "start_date": payload["start_date"], "end_date": payload["end_date"],
                "product_id": metadata["product_id"], "bonus_product_id": metadata["bonus_product_id"],
                "threshold": "10", "bonus_value": "1", "forced": "N",
            }
            persist()
            api.call(CONTRACTS["quantity_bonus"]["endpoint"], payload)

        with allure.step("3 - Saqlangan bonus aksiya va boshqa mahsulot ID sini tekshirish"):
            row = api.one(
                "anor/mcg/action_list:table",
                ["action_id", "name", "calc_kind_name", "start_date", "end_date", "action_state"],
                filters=["name", "=", payload["name"]],
            )
            action_id = positive_id(row["action_id"])
            metadata["bonus"]["action_id"] = action_id
            persist()
            require_fields(row, name=payload["name"], calc_kind_name="Кол-во",
                           start_date=payload["start_date"], end_date=payload["end_date"], action_state="A")
            verify_promotion(api, action_id, payload)
            model = api.model("anor/mcg/action+edit", action_id=action_id)
            require_fields(model, forced="N")

        with allure.step("4 - Tekshirilgan bonus ma’lumotlarini guruhga uzatish"):
            metadata["status"] = "passed"
            persist()
            allure.attach(json.dumps(metadata, ensure_ascii=False, indent=2),
                          "Order biznes setup ma'lumotlari", allure.attachment_type.JSON)
        return metadata
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error_type"] = type(error).__name__
        persist()
        raise
    finally:
        state.close()
