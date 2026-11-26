"""SCN-017. Qo‘lda va Excel’dan kiritilgan tovar uchun A5→B1 bonusi."""

import allure
import pytest

from tests.regression.test_orders.business_cases.promotions.excel_import_promotion import (
    run_direct_entry_control, run_promotion_after_excel_import,
)
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)
from tests.regression.test_orders.setup_cases.excel_import_promotion import run_prepare_import_promotion

GROUP = "excel_import_promotion"
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
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, GROUP, goods_on_balance="N")


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="excel-import", kind="promotion", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_001_prices")
def test_01_prepare_promotion(business_baseline, workflow_data, regression_case_dir):
    run_prepare_import_promotion(business_baseline, workflow_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client", "test_01_prepare_promotion")
def test_02_direct_entry_control(workflow_order):
    run_direct_entry_control(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client", "test_01_prepare_promotion", "test_02_direct_entry_control")
def test_03_promotion_after_excel_import(workflow_order, catalog_data):
    run_promotion_after_excel_import(workflow_order, product_code=catalog_data["goods"]["code"])
