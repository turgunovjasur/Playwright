"""TMZ limiti: mahsulot/klient/kirim/limit → order 6+4 → cancel 6 → edit 4→10."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case

from tests.regression.test_orders.setup_cases.test_product_limit import (
    run_prepare_product, run_prepare_client, run_prepare_stock, run_prepare_limit,
)
from tests.regression.test_orders.business_cases.stock.test_product_limit import (
    run_create_limit_order, run_cancel_first_limit_order, run_reuse_released_product_limit,
)

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              pytest.mark.order_group("product_limit"), allure.epic("Regression"),
              allure.feature(GROUP_FEATURES["product_limit"])]


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_product(business_baseline, product_limit_data, regression_case_dir):
    run_prepare_product(business_baseline, product_limit_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_01_prepare_client(business_baseline, product_limit_data, regression_case_dir):
    run_prepare_client(business_baseline, product_limit_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_00_prepare_product', 'test_01_prepare_client')
def test_02_prepare_stock(product_limit_order, regression_case_dir):
    run_prepare_stock(product_limit_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_00_prepare_product', 'test_01_prepare_client')
def test_03_prepare_limit(product_limit_order, regression_case_dir):
    run_prepare_limit(product_limit_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_02_prepare_stock', 'test_03_prepare_limit')
def test_04_first_order_six(product_limit_order, regression_case_dir):
    run_create_limit_order(product_limit_order, regression_case_dir,
                           key="first", quantity=6, reserved_before=0, reserved_after=6)


@order_report_case
@pytest.mark.order_requires('test_04_first_order_six')
def test_05_second_order_four(product_limit_order, regression_case_dir):
    run_create_limit_order(product_limit_order, regression_case_dir,
                           key="second", quantity=4, reserved_before=6, reserved_after=10)


@order_report_case
@pytest.mark.order_requires('test_05_second_order_four')
def test_06_cancel_first_order(product_limit_order, regression_case_dir):
    run_cancel_first_limit_order(product_limit_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_06_cancel_first_order')
def test_07_reuse_released_limit(product_limit_order, regression_case_dir):
    run_reuse_released_product_limit(product_limit_order, regression_case_dir)
