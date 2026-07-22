import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_B_grup.order_helpers import (
    run_order_invoice_reports,
)

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("Order Consignment"),
    allure.story("Invoice Reports"),
]

# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Draft order Накладные reportlarini tekshirish")
def test_order_invoice_reports(page, code, load_data):
    authorization(page, who="user", code=code)
    run_order_invoice_reports(page, code, load_data)
