import allure
import pytest

from tests.smoke.test_groups.test_B_grup.order_helpers import (
    run_create_order_with_consignment_limit,
    run_edit_order_with_consignment_limit,
    run_order_invoice_reports,
)
from tests.smoke.test_groups.test_B_grup.test_invoice_report_template import (
    run_create_custom_invoice_report_template,
)

pytestmark = [
    pytest.mark.smoke_group("B"),
    allure.epic("B Group"),
    allure.feature("B Group Runner"),
    allure.story("Order Consignment"),
]

@allure.title("B-01 - Konsignatsiya limiti bilan zakaz yaratish")
def test_b_01_create_order_with_consignment_limit(group_user_page, code, save_data):
    run_create_order_with_consignment_limit(group_user_page, code, save_data)


@allure.title("B-02 - Konsignatsiyali zakazni edit qilish va split qilish")
def test_b_02_edit_order_with_consignment_limit(group_user_page, code, load_data, save_data):
    run_edit_order_with_consignment_limit(group_user_page, code, load_data, save_data)


@allure.title("B-03 - Draft zakaz Накладные reportlarini tekshirish")
def test_b_03_order_invoice_reports(group_user_page, code, load_data):
    run_order_invoice_reports(group_user_page, code, load_data)


@allure.title("B-04 - Custom invoice report template yaratish va orderda tekshirish")
def test_b_04_invoice_report_template(group_session_page, code, load_data):
    run_create_custom_invoice_report_template(group_session_page, code, load_data)
