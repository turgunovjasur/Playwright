"""Order biznes runneri uchun setup baseline'ga qo'shimcha bonus aksiyasi."""

import allure
import pytest

from tests.regression.test_orders.helpers.preparations.bonus import prepare_business_promotions
from tests.regression.test_orders.helpers.preparations.resources import resource_status


pytestmark = [
    pytest.mark.regression,
    pytest.mark.order_positive,
    allure.epic("Regression"),
    allure.feature("Order biznes flowlari"),
    allure.story("API setup ma'lumotlarini tayyorlash"),
]


def run_business_setup(business_baseline, business_promotions):
    """1. Baseline narxi va mahsulotlarini tekshirish.
    2. 10 dona sotuvga 1 dona boshqa mahsulot bonusini yaratish.
    3. Saqlangan bonus sharti va mahsulotini serverdan qayta o'qish.
    4. Faqat muvaffaqiyatli setup ma'lumotlarini UI testlarga uzatish.
    """
    resource_status(business_promotions, "bonus", "process")
    try:
        prepared = prepare_business_promotions(business_baseline)
    except Exception:
        resource_status(business_promotions, "bonus", "failed")
        raise
    readiness = {**business_promotions.get("ready", {}), **prepared.get("ready", {})}
    business_promotions.update(prepared)
    business_promotions["ready"] = readiness
