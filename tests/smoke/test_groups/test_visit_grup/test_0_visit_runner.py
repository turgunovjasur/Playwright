import allure
import pytest

from tests.smoke.test_groups.test_visit_grup.test_01_mobile_visit import (
    run_mobile_visit_check,
)
from tests.smoke.test_groups.test_visit_grup.test_02_mobile_order_visit import (
    run_mobile_order_visit_check,
)


pytestmark = [
    pytest.mark.smoke_group("visit", independent=True),
    allure.epic("Visit Group"),
    allure.feature("Visit Group Runner"),
    allure.story("Mobile API → Web"),
]


@allure.title("Mobile API orqali minimal vizit yaratish va webdan tekshirish")
def test_visit_01_mobile_visit(group_session_page, load_data, save_data):
    run_mobile_visit_check(group_session_page, load_data, save_data)


@allure.title("Mobile API orderli vizitini yaratish va webdan tekshirish")
def test_visit_02_mobile_visit_with_order(group_session_page, load_data, save_data):
    run_mobile_order_visit_check(group_session_page, load_data, save_data)
