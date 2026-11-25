"""SCN-022. Ikki mahsulotga umumiy foizli chegirma."""
import allure
import pytest

from tests.regression.test_orders.business_cases.discounts.test_apply_all import run_apply_all, run_check_saved_discount
from tests.regression.test_orders.setup_cases.test_margin import run_prepare_margin
from tests.regression.test_orders.setup_cases.test_mixed_unit_prices import run_mixed_prices
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_stock,
)

GROUP = "discount_apply_all"
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
    run_mixed_prices(business_baseline, catalog_data, regression_case_dir, GROUP, change_price=False)


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP,
                      goods_on_balance="N", second_sale_product=True)


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="apply-all", kind="discount", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_margin(order_page, business_baseline, workflow_data, regression_case_dir):
    run_prepare_margin(order_page, business_baseline, workflow_data, regression_case_dir, percent="17")


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client", "test_00_prepare_margin")
def test_01_apply_all(workflow_order, catalog_data):
    run_apply_all(workflow_order, catalog_data)


@order_report_case
@pytest.mark.order_requires("test_01_apply_all")
def test_02_reopen_discount(workflow_order, catalog_data):
    run_check_saved_discount(workflow_order, catalog_data)
