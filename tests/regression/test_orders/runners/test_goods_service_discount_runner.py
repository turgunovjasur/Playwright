"""SCN-026. Tovar va xizmatga umumiy 17% chegirma."""
import allure
import pytest

from tests.regression.test_orders.business_cases.discounts.goods_service_discount import run_mixed_discount, run_reopen_mixed_discount
from tests.regression.test_orders.setup_cases.order_services import run_prepare_services
from tests.regression.test_orders.setup_cases.margin import run_prepare_margin
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "goods_service_discount"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES[GROUP]),
]


@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires("test_000_catalog")
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, GROUP, initial_price=1500)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="mixed-service", kind="discount", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires()
def test_00_services(business_baseline, workflow_data, regression_case_dir):
    run_prepare_services(business_baseline, workflow_data, regression_case_dir, count=1)


@order_report_case
@pytest.mark.order_requires()
def test_00_margin(order_page, business_baseline, workflow_data, regression_case_dir):
    run_prepare_margin(order_page, business_baseline, workflow_data, regression_case_dir, percent="17")


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client", "test_00_services", "test_00_margin")
def test_01_mixed_discount(workflow_order):
    run_mixed_discount(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_01_mixed_discount")
def test_02_reopen(workflow_order):
    run_reopen_mixed_discount(workflow_order)
