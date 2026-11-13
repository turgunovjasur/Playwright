"""A10 → 10%: faqat iste’molchi Order guruhining alohida tayyorlov testi."""
from copy import deepcopy
import json
from tests.regression.helpers.retry.state import stable_uuid as uuid4

import allure
import pytest

from tests.api.client import positive_id, require_fields
from tests.api.promotion import verify_promotion
from tests.api.state import CONTRACTS
from tests.regression.test_orders.helpers.preparations.resources import resource_status
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Order biznes flowlari"),
              allure.story("Miqdor chegirmasi tayyorlovi")]


def run_prepare_quantity_discount(baseline, promotions, directory):
    """1. Shu guruhning mahsulot va narx tayyorlovidan foydalanish.
    2. 10 dona xaridga 10% ixtiyoriy chegirma yaratish.
    3. ID, muddat, shart va chegirma mahsulotini qayta o‘qish.
    4. Natijani faqat shu guruhga uzatish; umumiy baseline o‘zgarmaydi.
    """
    resource_status(promotions, "discount", "process")
    promotions.setdefault("unit_price", "7000")
    state = RegressionSetupState(directory / "discount-state.json", deepcopy(baseline))
    run_id = uuid4("discount_action").hex[:12]
    path = directory / "discount-setup.json"

    def persist():
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(promotions, ensure_ascii=False, indent=2) + "\n")
        temporary.replace(path)

    persist()
    try:
        with allure.step("1 - Guruh uchun A10 → 10% ixtiyoriy aksiyani tayyorlash"):
            api = state.user()
            payload = state.payload("quantity_discount")
            payload["name"] = f"order-discount-pw{state.code}-{run_id}"
            payload["code"] = f"od-discount-{state.code}-{run_id}"
            payload["forced"] = "N"
            payload["conditions"][0]["rules"][0]["main_value"] = "10"
            payload["conditions"][0]["bonuses"][0]["products"][0]["value"] = "10"
            discount = {key: payload[key] for key in ("name", "code", "start_date", "end_date", "forced")}
            discount.update(threshold="10", bonus_value="10", product_id=str(baseline["product_id"]),
                            product_name=baseline.get("product_name", f"product-pw{state.code}"), room_name=f"room-pw{state.code}",
                            price_type_name=f"Price Type UZB-pw{state.code}")
            promotions["discount"] = discount
            persist()
            api.call(CONTRACTS["quantity_discount"]["endpoint"], payload)
        with allure.step("2 - Saqlangan aksiya IDsi, muddatlari va 10% shartini tekshirish"):
            row = api.one("anor/mcg/action_list:table",
                          ["action_id", "name", "calc_kind_name", "start_date", "end_date", "action_state"],
                          filters=["name", "=", payload["name"]])
            discount["action_id"] = positive_id(row["action_id"])
            persist()
            require_fields(row, name=payload["name"], start_date=payload["start_date"],
                           end_date=payload["end_date"], action_state="A", calc_kind_name="Кол-во")
            verify_promotion(api, discount["action_id"], payload)
            model = api.model("anor/mcg/action+edit", action_id=discount["action_id"])
            require_fields(model, forced="N")
        with allure.step("3 - Tekshirilgan chegirmani shu guruhning orderlariga uzatish"):
            resource_status(promotions, "discount", "passed")
            persist()
    except Exception as error:
        resource_status(promotions, "discount", "failed")
        promotions["error_type"] = type(error).__name__
        persist()
        raise
    finally:
        state.close()
        allure.attach(path.read_text(), "Order biznes setup ma'lumotlari", allure.attachment_type.JSON)


@allure.title("A10 → 10% chegirmani guruh uchun tayyorlash")
def test_prepare_quantity_discount(business_baseline, business_promotions, regression_case_dir):
    run_prepare_quantity_discount(business_baseline, business_promotions, regression_case_dir)
