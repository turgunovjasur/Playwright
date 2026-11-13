"""Own tayyorlovlardan keyin bir SKUning ikki omborli orderini qat'iy tekshirish."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case

from tests.regression.test_orders.setup_cases.test_two_warehouses import (
    run_prepare_two_warehouse_client, run_prepare_two_warehouses,
    run_prepare_two_warehouse_stock,
)
from tests.regression.test_orders.business_cases.stock.test_two_warehouses import (
    run_create_two_warehouses, run_reserve_two_warehouses,
    run_reallocate_two_warehouses, run_cancel_two_warehouses,
)

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              pytest.mark.order_group("two_warehouses"), allure.epic("Regression"),
              allure.feature(GROUP_FEATURES["two_warehouses"])]


from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "two_warehouses")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "two_warehouses")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "two_warehouses")

@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    run_prepare_two_warehouse_client(business_baseline, workflow_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_00_prepare_client')
def test_01_prepare_warehouses(workflow_order, regression_case_dir):
    run_prepare_two_warehouses(workflow_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_001_prices', 'test_01_prepare_warehouses')
def test_02_prepare_stock(workflow_order, regression_case_dir):
    run_prepare_two_warehouse_stock(workflow_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_02_prepare_stock')
def test_03_create_draft(workflow_order):
    run_create_two_warehouses(workflow_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_03_create_draft')
def test_04_reserve_both(workflow_order):
    run_reserve_two_warehouses(workflow_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_04_reserve_both')
def test_05_reallocate(workflow_order):
    run_reallocate_two_warehouses(workflow_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_05_reallocate')
def test_06_cancel_both(workflow_order):
    run_cancel_two_warehouses(workflow_order)
