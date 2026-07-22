import allure
import pytest

from tests.smoke.test_groups.test_C_grup.test_action import (
    run_c_group_create_action,
    run_c_group_order_action_discount,
)

pytestmark = [
    pytest.mark.smoke_group("C"),
    allure.epic("C Group"),
    allure.feature("C Group Runner"),
    allure.story("Marketing Action"),
]

@allure.title("C-01 - Aksiya (Скидка 10%) yaratish")
def test_c_01_create_action(group_user_page, code):
    run_c_group_create_action(group_user_page, code)


@allure.title("C-02 - Orderda aksiya chegirmasini tekshirish")
def test_c_02_order_action_discount(group_user_page, code):
    run_c_group_order_action_discount(group_user_page, code)
