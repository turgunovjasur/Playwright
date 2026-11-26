"""Payment testlari uchun runnerda ko'rinadigan ikkita mustaqil tayyorlov."""

import allure
import pytest

from tests.regression.test_orders.helpers.preparations.payment_clients import prepare_payment_client

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Order"),
              allure.story("Payment klientlarini API orqali tayyorlash")]


def run_ordinary_payment_client(business_baseline, payment_clients, regression_case_dir):
    """1. Oddiy payment case uchun unique klient yaratish.
    2. Model va setup xona membershipini tekshirish.
    3. Faqat tekshirilgan klientni ordinary consumerga uzatish.
    """
    payment_clients["ordinary"] = {"status": "process"}
    try:
        payment_clients["ordinary"] = prepare_payment_client(
            business_baseline, kind="ordinary", directory=regression_case_dir)
    except Exception:
        payment_clients["ordinary"]["status"] = "failed"
        raise


def run_promoted_payment_client(business_baseline, payment_clients, regression_case_dir):
    """1. Aksiya payment case uchun boshqa unique klient yaratish.
    2. Model va setup xona membershipini tekshirish.
    3. Faqat tekshirilgan klientni promoted consumerga uzatish.
    """
    payment_clients["promoted"] = {"status": "process"}
    try:
        payment_clients["promoted"] = prepare_payment_client(
            business_baseline, kind="promoted", directory=regression_case_dir)
    except Exception:
        payment_clients["promoted"]["status"] = "failed"
        raise
