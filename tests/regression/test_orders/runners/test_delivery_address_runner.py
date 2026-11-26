"""SCN-023. Yetkazish manzilini tanlash, almashtirish va tozalash."""
import allure
import pytest

from tests.regression.test_orders.business_cases.statuses.delivery_address import (
    run_save_first_address, run_change_address,
)
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

GROUP = "delivery_address"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES[GROUP]),
]


@order_report_case
@pytest.mark.order_requires()
def test_000_enable_addresses(delivery_addresses_enabled):
    assert delivery_addresses_enabled, "Ish muhitida turli yetkazish manzillariga ruxsat kerak"


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
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP, goods_on_balance="N")


@order_report_case
@pytest.mark.order_requires("test_000_enable_addresses")
def test_00_prepare_client(delivery_addresses_enabled, business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="delivery-address", kind="two-addresses", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_address_a(delivery_addresses_enabled, workflow_order):
    run_save_first_address(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_01_address_a")
def test_02_address_b(delivery_addresses_enabled, workflow_order):
    run_change_address(workflow_order, clear=False)


@order_report_case
@pytest.mark.order_requires("test_02_address_b")
def test_03_clear_address(delivery_addresses_enabled, workflow_order):
    run_change_address(workflow_order, clear=True)
