import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_B_grup.order_helpers import (
    run_edit_order_with_consignment_limit,
)

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("Order Consignment"),
    allure.story("Edit Order"),
]

# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Konsignatsiyali orderni edit qilish va split qilish")
def test_edit_order_with_consignment_limit(page, code, load_data, save_data):
    authorization(page, who="user", code=code)
    run_edit_order_with_consignment_limit(page, code, load_data, save_data)
