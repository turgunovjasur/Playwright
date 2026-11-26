"""SCN-024. KG qatorining o‘zgarishlar tarixi."""
import allure
import pytest

from tests.regression.test_orders.business_cases.pricing.fractional_quantity import (
    run_fractional_draft, run_rescale,
)
from tests.regression.test_orders.business_cases.pricing.line_history import run_line_history
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "line_history"
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
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, GROUP, initial_price=1000)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP, goods_on_balance="N")


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="line-history", kind="audit", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_discount_at_125(workflow_order):
    run_fractional_draft(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_01_discount_at_125")
def test_02_discount_at_250(workflow_order):
    run_rescale(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_02_discount_at_250")
def test_03_line_history(workflow_order):
    run_line_history(workflow_order)
