"""SCN-018. Ikki muddatli konsignatsiya, shartnoma va to‘lov jurnali."""
import allure
import pytest

from tests.regression.test_orders.business_cases.payments.consignment_dates import run_consignment_dates
from tests.regression.test_orders.business_cases.payments.consignment_settlement import run_consignment_settlement
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import run_prepare_catalog, run_prepare_prices, run_prepare_stock
from tests.regression.test_orders.setup_cases.consignment_bank import run_prepare_consignment_bank
from tests.regression.test_orders.setup_cases.consignment_contract import run_prepare_consignment_project_contract

GROUP = "consignment_due_dates"
pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES[GROUP]),
]


@order_report_case
@pytest.mark.order_requires()
def test_000_prepare_consignment(consignment_enabled):
    if not consignment_enabled:
        raise AssertionError("Filialda konsignatsiya yoqilmadi")


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
        business_baseline, purpose="consignment", kind="due-dates", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_00_prepare_client")
def test_01_prepare_contract(workflow_order):
    run_prepare_consignment_project_contract(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_00_prepare_client")
def test_02_prepare_bank(workflow_order, consignment_bank_binding):
    run_prepare_consignment_bank(workflow_order)
    consignment_bank_binding.ensure()


@order_report_case
@pytest.mark.order_requires("test_000_prepare_consignment", "test_002_stock", "test_01_prepare_contract")
def test_001_consignment_dates(workflow_order, consignment_enabled):
    run_consignment_dates(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_001_consignment_dates", "test_02_prepare_bank")
def test_002_consignment_settlement(workflow_order, consignment_enabled, consignment_bank_binding):
    consignment_bank_binding.ensure()
    run_consignment_settlement(workflow_order)
