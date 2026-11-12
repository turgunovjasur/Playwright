"""Order to'lovlari: tayyorlovdan keyingi ikkita mustaqil biznes case."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.preparations.test_quantity_discount import run_prepare_quantity_discount

from tests.regression.test_orders.preparations.test_bonus import run_business_setup
from tests.regression.test_orders.preparations.test_payment_clients import (
    run_ordinary_payment_client, run_promoted_payment_client,
)
from tests.regression.test_orders.payments.test_partial_full_payment import run_partial_full_payment
from tests.regression.test_orders.payments.test_promoted_order_payment import run_promoted_order_payment

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("payments"),
              allure.epic("Regression"), allure.feature(GROUP_FEATURES["payments"])]


from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "payments")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "payments")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "payments")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00_prepare_promotions(business_baseline, business_promotions):
    run_business_setup(business_baseline, business_promotions)


@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00a_prepare_discount(business_baseline, business_promotions, regression_case_dir):
    run_prepare_quantity_discount(business_baseline, business_promotions, regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_01_prepare_ordinary_client(business_baseline, payment_clients, regression_case_dir):
    run_ordinary_payment_client(business_baseline, payment_clients, regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_02_prepare_promoted_client(business_baseline, payment_clients, regression_case_dir):
    run_promoted_payment_client(business_baseline, payment_clients, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_01_prepare_ordinary_client')
def test_03_partial_full_payment(ordinary_payment_order):
    run_partial_full_payment(ordinary_payment_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_promotions', 'test_00a_prepare_discount', 'test_02_prepare_promoted_client')
def test_04_promoted_order_payment(promoted_payment_order):
    run_promoted_order_payment(promoted_payment_order)
