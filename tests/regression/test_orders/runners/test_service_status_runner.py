"""SCN-025. Ikki xizmatli buyurtmaning statuslari va nazorat tovari qoldig‘i."""
import allure
import pytest

from tests.regression.test_orders.business_cases.statuses.test_service_status import run_service_draft, run_service_status
from tests.regression.test_orders.helpers.flows.stock import read_stock
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_order_services import run_prepare_services

GROUP = "service_status"
pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group(GROUP),
              allure.epic("Regression"), allure.feature(GROUP_FEATURES[GROUP])]


@order_report_case
@pytest.mark.order_requires()
def test_00_services(business_baseline, workflow_data, regression_case_dir):
    run_prepare_services(business_baseline, workflow_data, regression_case_dir, count=2)


@order_report_case
@pytest.mark.order_requires()
def test_01_client(business_baseline, workflow_data, regression_case_dir):
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="service-status", kind="services", directory=regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_02_control_stock(catalog_order, workflow_data):
    stock = read_stock(catalog_order, "Основной склад")
    catalog_order.check("Nazorat uchun fizik qoldiq mavjud", True, stock["physical"] > 0)
    workflow_data["control_stock"] = {key: str(value) for key, value in stock.items()}


@order_report_case
@pytest.mark.order_requires("test_00_services", "test_01_client", "test_02_control_stock")
def test_03_draft(workflow_order):
    run_service_draft(workflow_order)


@order_report_case
@pytest.mark.order_requires("test_03_draft")
def test_04_new(workflow_order):
    run_service_status(workflow_order, "Черновик", "Новый")


@order_report_case
@pytest.mark.order_requires("test_04_new")
def test_05_shipped(workflow_order):
    run_service_status(workflow_order, "Новый", "Отгружен")


@order_report_case
@pytest.mark.order_requires("test_05_shipped")
def test_06_back_to_draft(workflow_order):
    run_service_status(workflow_order, "Отгружен", "Черновик")
