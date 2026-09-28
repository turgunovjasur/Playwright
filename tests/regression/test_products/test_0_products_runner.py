"""Smoke runner uslubida: har product case uchun alohida pytest wrapper."""

import allure
import pytest

from tests.regression.test_products.test_01_create_product import run_product_full
from tests.regression.test_products.test_02_import_products import run_import_product

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("TMZ yaratish va narxlash")]


@allure.title("TMZ-1: yaratish, view, 5000 UZS va 5 USD")
def test_01_tmz_1(group_user_page, code):
    run_product_full(group_user_page, code)


@allure.title("TMZ-2/3/4/5/6: Excel import, view va Цены listidan UZS/USD narxlash")
def test_02_import_tmz(page, group_user_page, code):
    run_import_product(page, group_user_page, code)
