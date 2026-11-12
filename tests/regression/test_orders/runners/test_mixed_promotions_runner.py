"""Majburiy B1 va ixtiyoriy 10% aksiyasi: alohida tayyorlov va qat’iy UI ketma-ketlik."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case

from tests.regression.test_orders.preparations.test_mixed_promotions import (
    run_prepare_price, run_prepare_mandatory_bonus, run_prepare_optional_discount,
)
from tests.regression.test_orders.promotions.test_mixed_promotions import run_toggle_discount, run_quantity_boundary

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("mixed_promotions"),
              allure.epic("Regression"), allure.feature(GROUP_FEATURES["mixed_promotions"])]


from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "mixed_promotions")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "mixed_promotions")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "mixed_promotions")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_00_prepare_price(business_baseline, mixed_promotions_data, regression_case_dir):
    run_prepare_price(business_baseline, mixed_promotions_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_00_prepare_price')
def test_01_prepare_mandatory_bonus(business_baseline, mixed_promotions_data, regression_case_dir):
    run_prepare_mandatory_bonus(business_baseline, mixed_promotions_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_00_prepare_price')
def test_02_prepare_optional_discount(business_baseline, mixed_promotions_data, regression_case_dir):
    run_prepare_optional_discount(business_baseline, mixed_promotions_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_01_prepare_mandatory_bonus', 'test_02_prepare_optional_discount')
def test_03_toggle_discount(mixed_order):
    run_toggle_discount(mixed_order)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_01_prepare_mandatory_bonus', 'test_02_prepare_optional_discount')
def test_04_quantity_boundary(mixed_order):
    run_quantity_boundary(mixed_order)
