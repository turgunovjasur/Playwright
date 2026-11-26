"""SCN-027. Ikki qoralamani XMLga eksport qilish."""
import allure
import pytest

from tests.regression.test_orders.business_cases.pricing.catalog_price_history import (
    run_change_catalog_price,
)
from tests.regression.test_orders.business_cases.pricing.order_xml import run_xml_draft, run_export
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "order_xml"
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
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, GROUP, initial_price=1000)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="xml-export", kind="orders", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_original_draft(workflow_order, catalog_data):
    run_xml_draft(workflow_order, catalog_data, key="original_draft", price=1000)


@order_report_case
@pytest.mark.order_requires("test_01_original_draft")
def test_02_change_catalog_price(business_baseline, catalog_data, workflow_data, regression_case_dir):
    run_change_catalog_price(business_baseline, catalog_data, workflow_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires("test_02_change_catalog_price")
def test_03_new_draft(workflow_order, catalog_data):
    run_xml_draft(workflow_order, catalog_data, key="new_draft", price=1500)


@order_report_case
@pytest.mark.order_requires("test_01_original_draft", "test_03_new_draft")
def test_04_export(workflow_order, regression_case_dir):
    run_export(workflow_order, regression_case_dir)
