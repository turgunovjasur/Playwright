"""Payment runnerlari uchun oldingi public entry point saqlanadi."""
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client


def prepare_payment_client(baseline, *, kind, directory):
    """Oldingi payment nomlari va metadata bilan alohida klient tayyorlash."""
    return prepare_order_client(baseline, purpose="payment", kind=kind, directory=directory)
