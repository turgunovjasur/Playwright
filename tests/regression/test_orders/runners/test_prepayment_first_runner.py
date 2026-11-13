"""SCN-005: Orderdan oldin olingan avans."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case

from tests.regression.test_orders.business_cases.payments.test_prepayment_first import (
    run_post_advance,
    run_archive_after_advance,
    run_apply_advance,
)
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "prepayment_first"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES["prepayment_first"]),
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
        business_baseline, purpose="payment", kind="prepayment-first", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires('test_00_prepare_client')
def test_01_post_advance(workflow_order):
    run_post_advance(workflow_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_01_post_advance')
def test_02_archive_after_advance(workflow_order):
    run_archive_after_advance(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_02_archive_after_advance")
def test_03_apply_advance(workflow_order):
    run_apply_advance(workflow_order)
