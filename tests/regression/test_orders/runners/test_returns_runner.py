"""Bonus+skidkali orderni to'lash va ikki bosqichda qaytarish."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_quantity_discount import run_prepare_quantity_discount
from tests.regression.test_orders.setup_cases.test_return_price import run_prepare_return_price
from tests.regression.test_orders.setup_cases.test_return_stock import run_prepare_return_stock
from tests.regression.test_orders.setup_cases.test_workflows import run_returns_client,run_workflow_promotions
from tests.regression.test_orders.business_cases.returns.test_promoted_return import run_prepare_reason,run_create_promoted_order,run_ship_order,run_pay_order,run_partial_return,run_remaining_return
pytestmark=[pytest.mark.regression,pytest.mark.order_positive,pytest.mark.order_group("returns"),allure.epic("Regression"),allure.feature(GROUP_FEATURES["returns"])]

from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "returns")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "returns")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "returns")

@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline,workflow_data,regression_case_dir):
    run_returns_client(business_baseline,workflow_data,regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_01_prepare_promotions(business_baseline,workflow_data):
    run_workflow_promotions(business_baseline,workflow_data)

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_01a_prepare_discount(business_baseline, workflow_data, regression_case_dir):
    run_prepare_quantity_discount(business_baseline, workflow_data.setdefault("promotions", {}), regression_case_dir)

@order_report_case
@pytest.mark.order_requires()
def test_02_prepare_return_price(business_baseline, workflow_data, regression_case_dir):
    run_prepare_return_price(business_baseline, workflow_data, regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_00_prepare_client')
def test_03_prepare_reason(workflow_order):
    run_prepare_reason(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_001_prices', 'test_00_prepare_client')
def test_03a_prepare_stock(workflow_order, regression_case_dir):
    run_prepare_return_stock(workflow_order, regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client', 'test_01_prepare_promotions', 'test_01a_prepare_discount', 'test_03a_prepare_stock')
def test_04_create_promoted_order(workflow_order):
    run_create_promoted_order(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_04_create_promoted_order')
def test_05_ship_order(workflow_order):
    run_ship_order(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_05_ship_order')
def test_06_pay_order(workflow_order):
    run_pay_order(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_06_pay_order', 'test_02_prepare_return_price', 'test_03_prepare_reason')
def test_07_partial_return(workflow_order):
    run_partial_return(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_07_partial_return')
def test_08_remaining_return(workflow_order):
    run_remaining_return(workflow_order)
