"""Bitta klientning ikki orderini bitta kirimdan ketma-ket yopish."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.preparations.test_workflows import run_multi_payment_client
from tests.regression.test_orders.payments.test_multiple_orders import run_first_order, run_second_order, run_shared_cashin, run_partial_first, run_finish_first, run_finish_second
pytestmark=[pytest.mark.regression,pytest.mark.order_positive,pytest.mark.order_group("multi_payments"),allure.epic("Regression"),allure.feature(GROUP_FEATURES["multi_payments"])]

from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "multi_payments")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "multi_payments")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "multi_payments")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00_prepare_client(business_baseline,workflow_data,regression_case_dir):
    run_multi_payment_client(business_baseline,workflow_data,regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client')
def test_01_first_order(workflow_order):
    run_first_order(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_01_first_order')
def test_02_second_order(workflow_order):
    run_second_order(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_second_order')
def test_03_shared_cashin(workflow_order):
    run_shared_cashin(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_03_shared_cashin')
def test_04_partial_first(workflow_order):
    run_partial_first(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_04_partial_first')
def test_05_finish_first(workflow_order):
    run_finish_first(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_05_finish_first')
def test_06_finish_second(workflow_order):
    run_finish_second(workflow_order)
