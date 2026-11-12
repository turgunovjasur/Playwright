"""Tayyor foiz, summali chegirmalar va bonus bilan ishlash."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.preparations.test_workflows import run_discount_client,run_workflow_promotions
from tests.regression.test_orders.preparations.test_margin import run_prepare_margin
from tests.regression.test_orders.discounts.test_preset_discount import run_preset_discount
from tests.regression.test_orders.discounts.test_manual_discount import run_line_amount,run_order_amount,run_amounts_with_bonus
pytestmark=[pytest.mark.regression,pytest.mark.order_positive,pytest.mark.order_group("manual_discounts"),allure.epic("Regression"),allure.feature(GROUP_FEATURES["manual_discounts"])]

from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "manual_discounts")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "manual_discounts")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "manual_discounts")

@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline,workflow_data,regression_case_dir):
    run_discount_client(business_baseline,workflow_data,regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_01_prepare_promotions(business_baseline,workflow_data):
    run_workflow_promotions(business_baseline,workflow_data)

@order_report_case
@pytest.mark.order_requires()
def test_02_prepare_margin(order_page,business_baseline,workflow_data,regression_case_dir):
    run_prepare_margin(order_page,business_baseline,workflow_data,regression_case_dir)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client', 'test_02_prepare_margin')
def test_03_preset_discount(workflow_order):
    run_preset_discount(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client')
def test_04_line_amount(workflow_order):
    run_line_amount(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client')
def test_05_order_amount(workflow_order):
    run_order_amount(workflow_order)

@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client', 'test_01_prepare_promotions')
def test_06_amounts_with_bonus(workflow_order):
    run_amounts_with_bonus(workflow_order)
