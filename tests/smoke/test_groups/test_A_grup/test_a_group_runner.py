import allure
import pytest

from tests.smoke.test_groups.test_A_grup.test_create_contract import (
    run_create_contract,
)
from tests.smoke.test_groups.test_A_grup.test_create_contract_with_payment_type import (
    run_create_contract_with_payment_type,
)
from tests.smoke.test_groups.test_A_grup.test_contract_limit_validation_and_valid_order import (
    run_contract_limit_validation_and_valid_order,
)
from tests.smoke.test_groups.test_A_grup.test_edit_order_and_save_as_new import (
    run_edit_order_and_save_as_new,
)
from tests.smoke.test_groups.test_A_grup.test_order_uses_contract_payment_type import (
    run_order_uses_contract_payment_type,
)

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("A Group Runner"),
    allure.story("Contract And Order"),
]

@allure.title("A-01 - UZS contract yaratish")
def test_a_01_create_contract(group_user_page, code, save_data):
    run_create_contract(group_user_page, code, save_data)


@allure.title("A-02 - Tip oplati sharti bilan contract yaratish")
def test_a_02_create_contract_with_payment_type(group_user_page, code, save_data):
    run_create_contract_with_payment_type(group_user_page, code, save_data)


@allure.title("A-03 - Contract limit tekshiruvi va limit ichida zakaz yaratish")
def test_a_03_contract_limit_validation_and_valid_order(group_user_page, code, load_data, save_data):
    run_contract_limit_validation_and_valid_order(group_user_page, code, load_data, save_data)


@allure.title("A-04 - Contract tip oplati auto-fill va limit tekshiruvi")
def test_a_04_order_uses_contract_payment_type(group_user_page, code, load_data, save_data):
    run_order_uses_contract_payment_type(group_user_page, code, load_data, save_data)


@allure.title("A-05 - Order editda statusni Новый qilib saqlash")
def test_a_05_edit_order_and_save_as_new(group_user_page, code, load_data):
    run_edit_order_and_save_as_new(group_user_page, code, load_data)
