"""A2 order biznes flowlari: API precondition, keyin mustaqil UI caselar."""
import allure
import pytest

from tests.regression.test_orders.helpers.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.setup_cases.test_quantity_discount import run_prepare_quantity_discount

from tests.regression.test_orders.setup_cases.test_bonus import run_business_setup
from tests.regression.test_orders.business_cases.promotions.test_01_quantity_discount import run_quantity_discount
from tests.regression.test_orders.business_cases.promotions.test_02_other_product_bonus import run_other_product_bonus
from tests.regression.test_orders.business_cases.promotions.test_03_bonus_and_discount import run_bonus_and_discount

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("promotions"), allure.epic("Regression"), allure.feature(GROUP_FEATURES["promotions"])]


from tests.regression.test_orders.setup_cases.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "promotions")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "promotions")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "promotions")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00_prepare_promotions(business_baseline, business_promotions):
    run_business_setup(business_baseline, business_promotions)


@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_00a_prepare_discount(business_baseline, business_promotions, regression_case_dir):
    run_prepare_quantity_discount(business_baseline, business_promotions, regression_case_dir)


@pytest.mark.order_positive
@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00a_prepare_discount')
def test_01_quantity_discount(promoted_order):
    run_quantity_discount(promoted_order)


@pytest.mark.order_positive
@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_promotions', 'test_00a_prepare_discount')
def test_02_other_product_bonus(promoted_order):
    run_other_product_bonus(promoted_order)


@pytest.mark.order_positive
@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_promotions', 'test_00a_prepare_discount')
def test_03_bonus_and_discount(promoted_order):
    run_bonus_and_discount(promoted_order)
