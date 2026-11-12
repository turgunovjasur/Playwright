"""Order biznes runneri uchun setup baseline'ga qo'shimcha bonus aksiyasi."""

import allure
import pytest

from tests.regression.test_orders.preparations.bonus import prepare_business_promotions


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
    business_promotions.clear()
    business_promotions.update(prepare_business_promotions(business_baseline))


@allure.title("OB-00: Setup mahsulotlari uchun boshqa mahsulot bonusini tayyorlash")
def test_business_setup(business_baseline, business_promotions):
    run_business_setup(business_baseline, business_promotions)
