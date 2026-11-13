"""SCN-002: Kirimda order qarzini avtomatik yopish."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case

from tests.regression.test_orders.business_cases.payments.test_cashin_auto_offset import (
    run_archive_order,
    run_post_auto_offset,
)
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "auto_offset"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES["auto_offset"]),
]


@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires("test_000_catalog")
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="payment", kind="auto-offset", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_archive_order(workflow_order):
    run_archive_order(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_01_archive_order")
def test_02_post_auto_offset(workflow_order):
    run_post_auto_offset(workflow_order)
