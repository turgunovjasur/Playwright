"""Status zanjiri uchun alohida klient tayyorlovi."""
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client


def run_prepare_status_client(baseline, data, directory):
    """1. Own klient yaratish. 2. Saved ID va xona bog‘lanishini tekshirish."""
    data["client"] = prepare_order_client(
        baseline, purpose="statuses", kind="cycle", directory=directory,
    )
