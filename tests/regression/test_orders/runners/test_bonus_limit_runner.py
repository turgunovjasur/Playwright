"""Umumiy bonus limiti: 4 tayyorlov → 6 biznes qadami, qat’iy tartib."""
import allure
import pytest

from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_case
from tests.regression.test_orders.preparations.test_bonus_limit import run_prepare_price, run_prepare_client, run_prepare_action
from tests.regression.test_orders.promotions.test_bonus_limit import run_quota_order, run_release_limit

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("bonus_limit"), allure.epic("Regression"), allure.feature(GROUP_FEATURES["bonus_limit"])]


from tests.regression.test_orders.preparations.test_catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)

@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """Exact lookup → missing catalog create → saved ID/name verification."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "bonus_limit")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """Read saved prices → set missing own price → verify 7000."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "bonus_limit")

@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """Own posted documents → live UI physical/reserved/free stock."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "bonus_limit")

@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_00_prepare_price(business_baseline, bonus_limit_data, regression_case_dir):
    run_prepare_price(business_baseline, bonus_limit_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires()
def test_01_prepare_first_client(business_baseline, bonus_limit_data, regression_case_dir):
    run_prepare_client(business_baseline, bonus_limit_data, regression_case_dir, "first")


@order_report_case
@pytest.mark.order_requires()
def test_02_prepare_second_client(business_baseline, bonus_limit_data, regression_case_dir):
    run_prepare_client(business_baseline, bonus_limit_data, regression_case_dir, "second")


@order_report_case
@pytest.mark.order_requires('test_00_prepare_price')
def test_03_prepare_action(business_baseline, bonus_limit_data, regression_case_dir):
    run_prepare_action(business_baseline, bonus_limit_data, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_03_prepare_action', 'test_01_prepare_first_client')
def test_04_first_client_uses_bonus(first_limit_order, regression_case_dir):
    run_quota_order(first_limit_order, regression_case_dir, key="first", quantity=10, used_before=0, used_after=1, bonus_expected=True, status="Новый", initial_stock=True)


@order_report_case
@pytest.mark.order_requires('test_04_first_client_uses_bonus', 'test_02_prepare_second_client')
def test_05_second_client_uses_remaining(second_limit_order, regression_case_dir):
    run_quota_order(second_limit_order, regression_case_dir, key="second", quantity=20, used_before=1, used_after=2, bonus_expected=True, status="Новый")


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_05_second_client_uses_remaining')
def test_06_first_client_exhausted(first_limit_order, regression_case_dir):
    run_quota_order(first_limit_order, regression_case_dir, key="exhausted_first", quantity=10, used_before=2, used_after=2, bonus_expected=False, status="Черновик")


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_05_second_client_uses_remaining')
def test_07_second_client_exhausted(second_limit_order, regression_case_dir):
    run_quota_order(second_limit_order, regression_case_dir, key="exhausted_second", quantity=10, used_before=2, used_after=2, bonus_expected=False, status="Черновик")


@order_report_case
@pytest.mark.order_requires('test_05_second_client_uses_remaining')
def test_08_cancel_releases_limit(first_limit_order, regression_case_dir):
    run_release_limit(first_limit_order, regression_case_dir)


@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_08_cancel_releases_limit')
def test_09_second_client_reuses_limit(second_limit_order, regression_case_dir):
    run_quota_order(second_limit_order, regression_case_dir, key="reused_second", quantity=20, used_before=1, used_after=2, bonus_expected=True, status="Новый")
