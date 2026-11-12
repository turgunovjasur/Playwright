"""Majburiy aksiyalar: narx tayyorlovi → ikki aksiya → shartlar → chegaralar."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.preparations.test_mandatory import run_prepare_prices as run_prepare_mandatory_prices, run_prepare_action
from tests.regression.test_orders.promotions.test_mandatory_conditions import run_pair, run_payment_change, run_threshold, run_price_change

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group('mandatory'), allure.epic('Regression'), allure.feature(GROUP_FEATURES["mandatory"])]


from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "mandatory")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "mandatory")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "mandatory")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00_prepare_prices(business_baseline, mandatory_data, regression_case_dir):
    run_prepare_mandatory_prices(business_baseline, mandatory_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_001_prices', 'test_00_prepare_prices')
def test_01_prepare_bank_action(business_baseline, mandatory_data, regression_case_dir):
    run_prepare_action(business_baseline, mandatory_data, regression_case_dir, 'bank')


@order_report_case
@pytest.mark.order_requires('test_001_prices', 'test_01_prepare_bank_action')
def test_02_prepare_terminal_action(business_baseline, mandatory_data, regression_case_dir):
    run_prepare_action(business_baseline, mandatory_data, regression_case_dir, 'terminal')


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_03_bank_matching(mandatory_order):
    run_pair(mandatory_order, 'bank', 'bank', 'bank')


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_04_terminal_wrong_price(mandatory_order):
    run_pair(mandatory_order, 'bank', 'terminal', None)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_05_terminal_matching(mandatory_order):
    run_pair(mandatory_order, 'terminal', 'terminal', 'terminal')


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_06_bank_wrong_price(mandatory_order):
    run_pair(mandatory_order, 'terminal', 'bank', None)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_07_payment_change(mandatory_order):
    run_payment_change(mandatory_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_08_quantity_threshold(mandatory_order):
    run_threshold(mandatory_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_terminal_action')
def test_09_price_change(mandatory_order):
    run_price_change(mandatory_order)
