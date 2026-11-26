"""SCN-028. Eski narx turiga bog‘langan bonusning qayta hisoblanishi."""
import allure
import pytest

from tests.regression.test_orders.business_cases.promotions.bonus_recalculation import (
    run_bonus_draft, run_list_price_change, run_recalculation,
)
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.bonus_target_price import run_prepare_target_price
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_promotion_stock,
)
from tests.regression.test_orders.setup_cases.excel_import_promotion import run_prepare_import_promotion
from tests.regression.test_orders.setup_cases.margin import run_prepare_margin

GROUP = "bonus_recalculation"
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
def test_002_stock(business_baseline, catalog_data, regression_case_dir):
    run_prepare_promotion_stock(business_baseline, catalog_data, regression_case_dir, GROUP)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_00_target_price(business_baseline, workflow_data, regression_case_dir):
    run_prepare_target_price(business_baseline, workflow_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="bonus-price", kind="promotion", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires()
def test_00_margin(order_page, business_baseline, workflow_data, regression_case_dir):
    run_prepare_margin(order_page, business_baseline, workflow_data, regression_case_dir, percent="17")


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_01_prepare_promotion(business_baseline, workflow_data, regression_case_dir):
    run_prepare_import_promotion(business_baseline, workflow_data, regression_case_dir, label="Price")


DRAFT_REQUIRES = ("test_002_stock", "test_00_prepare_client", "test_00_margin", "test_01_prepare_promotion")


@order_report_case
@pytest.mark.order_requires(*DRAFT_REQUIRES)
def test_02_picker_draft(workflow_order):
    run_bonus_draft(workflow_order, "picker")


@order_report_case
@pytest.mark.order_requires("test_02_picker_draft", "test_00_target_price")
def test_03_picker_price_change(workflow_order):
    run_list_price_change(workflow_order, "picker")


@order_report_case
@pytest.mark.order_requires("test_03_picker_price_change")
def test_04_picker_recalculation(workflow_order):
    run_recalculation(workflow_order, trigger="picker")


@order_report_case
@pytest.mark.order_requires(*DRAFT_REQUIRES)
def test_05_quantity_draft(workflow_order):
    run_bonus_draft(workflow_order, "quantity")


@order_report_case
@pytest.mark.order_requires("test_05_quantity_draft", "test_00_target_price")
def test_06_quantity_price_change(workflow_order):
    run_list_price_change(workflow_order, "quantity")


@order_report_case
@pytest.mark.order_requires("test_06_quantity_price_change")
def test_07_quantity_recalculation(workflow_order):
    run_recalculation(workflow_order, trigger="quantity")
