"""Order ombor rezervi: faqat tasdiqlangan API baseline bilan UI case."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.business_cases.stock.test_cancel_reserve import run_cancel_reserve

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group('stock'), allure.epic('Regression'), allure.feature(GROUP_FEATURES["stock"])]


from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "stock")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "stock")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "stock")

@order_report_case
@pytest.mark.order_requires('test_002_stock')
def test_01_cancel_reserve(ordinary_order):
    run_cancel_reserve(ordinary_order)
