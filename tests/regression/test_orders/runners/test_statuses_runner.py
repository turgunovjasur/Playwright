"""Status zanjiri: alohida klient → bir orderning olti statusi."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_status_client import run_prepare_status_client
from tests.regression.test_orders.business_cases.statuses.test_status_cycle import run_status_cycle

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("statuses"),
              allure.epic("Regression"), allure.feature(GROUP_FEATURES["statuses"])]


from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "statuses")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "statuses")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "statuses")

@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    run_prepare_status_client(business_baseline, workflow_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client')
def test_01_status_cycle(workflow_order):
    run_status_cycle(workflow_order)
