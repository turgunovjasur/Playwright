"""Narxi yo‘q mahsulotda eski narx turini saqlash."""
import allure
import pytest

from tests.regression.test_orders.business_cases.pricing.test_bulk_missing_price import run_change_price_types
from tests.regression.test_orders.helpers.flows.mixed_units import run_mixed_draft
from tests.regression.test_orders.setup_cases.test_mixed_unit_prices import run_mixed_prices
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_stock,
)

GROUP = "bulk_missing_price"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES[GROUP]),
]


@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, GROUP, kg_goods=True)


@order_report_case
@pytest.mark.order_requires("test_000_catalog")
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    run_mixed_prices(business_baseline, catalog_data, regression_case_dir, GROUP, change_price=True)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP, goods_on_balance="N", second_sale_product=True)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="bulk_missing_price", kind="bulk", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_mixed_draft(workflow_order, catalog_data):
    run_mixed_draft(workflow_order, catalog_data)


@order_report_case
@pytest.mark.order_requires("test_01_mixed_draft")
def test_02_change_price_types(workflow_order, catalog_data):
    run_change_price_types(workflow_order, catalog_data)
