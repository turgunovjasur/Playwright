"""Yangi Order guruhlari uchun alohida, ko'rinadigan tayyorlov test qadamlari."""
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.preparations.bonus import prepare_business_promotions
from tests.regression.test_orders.helpers.preparations.resources import resource_status


def run_returns_client(baseline, data, directory):
    """1. Own klient yaratish. 2. Saved ID va xona membershipini tekshirish."""
    data["client"] = prepare_order_client(baseline, purpose="returns", kind="promoted", directory=directory)


def run_multi_payment_client(baseline, data, directory):
    """1. Ikki order uchun bitta own klient. 2. Xonaga additive biriktirish."""
    data["client"] = prepare_order_client(baseline, purpose="multi-payment", kind="shared", directory=directory)


def run_discount_client(baseline, data, directory):
    """1. Own skidka klienti. 2. Saved ID va xona membershipini tekshirish."""
    data["client"] = prepare_order_client(baseline, purpose="discounts", kind="manual", directory=directory)


def run_workflow_promotions(baseline, data):
    """1. Guruh uchun ixtiyoriy bonus yaratish. 2. Saqlangan shart va bonusni tekshirish."""
    promotions = data.setdefault("promotions", {})
    resource_status(promotions, "bonus", "process")
    try:
        prepared = prepare_business_promotions(baseline)
    except Exception:
        resource_status(promotions, "bonus", "failed")
        raise
    readiness = {**promotions.get("ready", {}), **prepared.get("ready", {})}
    promotions.update(prepared)
    promotions["ready"] = readiness
