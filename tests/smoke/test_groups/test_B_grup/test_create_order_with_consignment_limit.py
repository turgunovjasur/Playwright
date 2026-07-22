import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_B_grup.order_helpers import (
    run_create_order_with_consignment_limit,
)

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("Order Consignment"),
    allure.story("Create Order"),
]

# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Konsignatsiya limiti bilan order yaratish")
def test_create_order_with_consignment_limit(page, code, save_data):
    authorization(page, who="user", code=code)
    run_create_order_with_consignment_limit(page, code, save_data)
