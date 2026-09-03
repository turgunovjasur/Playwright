import allure
import pytest

from tests.smoke.test_groups.test_a_grup.test_01_create_base_order import (
    run_create_base_order,
)
from tests.smoke.test_groups.test_a_grup.test_02_archive_base_order import (
    run_archive_base_order,
)
from tests.smoke.test_groups.test_a_grup.test_03_post_client_payment import (
    run_post_client_payment,
)
from tests.smoke.test_groups.test_a_grup.test_04_offset_client_balance import (
    run_offset_client_balance,
)

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("0 Group Runner"),
    allure.story("Order Payment Lifecycle"),
]


@allure.title("Setup baseline asosida oddiy order yaratish va IDni saqlash")
def test_0_01_create_base_order(group_user_page, code, save_data):
    run_create_base_order(group_user_page, code, save_data)


@allure.title("Exact orderni Архивga o'tkazish va debt detailda tekshirish")
def test_0_02_archive_base_order(group_user_page, code, load_data):
    run_archive_base_order(group_user_page, code, load_data)


@allure.title("Client paymentni Провести qilish")
def test_0_03_post_client_payment(group_user_page, code, load_data):
    run_post_client_payment(group_user_page, code, load_data)


@allure.title("Client debt va prepaymentini o'zaro hisob-kitob qilish")
def test_0_04_offset_client_balance(group_user_page, code, load_data):
    run_offset_client_balance(group_user_page, code, load_data)
