"""Arxivdan tiklash va bekor qilish."""
import allure
import pytest

from tests.regression.test_orders.helpers.flows.mixed_units import run_mixed_draft
from tests.regression.test_orders.business_cases.statuses.test_archive_restore import (
    check_no_debt, check_stock, run_archive, run_cancel, run_forward, run_restore,
)
from tests.regression.test_orders.setup_cases.test_mixed_unit_prices import run_mixed_prices
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_stock,
)

GROUP = "archive_restore"
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
        business_baseline, purpose="archive_restore", kind="restore", directory=regression_case_dir,
    )


@order_report_case
@pytest.mark.order_requires("test_002_stock", "test_00_prepare_client")
def test_01_mixed_draft(workflow_order, catalog_data):
    run_mixed_draft(workflow_order, catalog_data)


@order_report_case
@pytest.mark.order_requires("test_01_mixed_draft")
def test_02_reserve(workflow_order, catalog_data):
    run_forward(workflow_order, "Черновик", "Новый")
    check_stock(workflow_order, catalog_data, sold=0, reserved=1)


@order_report_case
@pytest.mark.order_requires("test_02_reserve")
def test_03_ship(workflow_order, catalog_data):
    run_forward(workflow_order, "Новый", "Отгружен")
    check_stock(workflow_order, catalog_data, sold=1, reserved=0)


@order_report_case
@pytest.mark.order_requires("test_03_ship")
def test_04_archive(workflow_order):
    run_archive(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_04_archive")
def test_05_restore_delivered(workflow_order):
    run_restore(workflow_order, current="Архив", target="Доставлен", list_name="Архив заказов",
                endpoint="trade/tdeal/order/order_history_list:change_status")


@order_report_case
@pytest.mark.order_requires("test_05_restore_delivered")
def test_06_cancel(workflow_order, catalog_data):
    run_cancel(workflow_order, catalog_data)


@order_report_case
@pytest.mark.order_requires("test_06_cancel")
def test_07_restore_draft(workflow_order, catalog_data):
    run_restore(workflow_order, current="Отменен", target="Черновик", list_name="Отмененные заказы",
                endpoint="trade/tdeal/order/order_cancelled_list$change_status")
    check_stock(workflow_order, catalog_data, sold=0, reserved=0)
    check_no_debt(workflow_order)
