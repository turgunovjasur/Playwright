"""ТМЦ regressioni: har variant/case alohida pytest va Allure item.

Hozir: 6 manual create, create-cancel, edit-save/cancel, 2 required validation,
2 mahsulotli import va import-cancel. Lug'atlar, barcode/fayl va narx/kirim qamrovi
regression-plan.md bo'yicha bosqichma-bosqich qo'shiladi.
"""

import allure
import pytest

from tests.regression.test_products.product_cases import MANUAL_PRODUCT_KEYS
from tests.regression.test_products.test_01_create_product import run_create_product
from tests.regression.test_products.test_02_product_lifecycle import run_cancel_product_creation, run_edit_product
from tests.regression.test_products.test_03_product_required_fields import REQUIRED_FIELDS, run_product_required_field
from tests.regression.test_products.test_04_product_import import run_cancel_product_import, run_import_products
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("Mahsulotlar")]


@pytest.mark.parametrize("key", MANUAL_PRODUCT_KEYS, ids=MANUAL_PRODUCT_KEYS)
@allure.title("REG-PROD-CREATE-{key}: kengaytirilgan ТМЦ yaratish")
def test_01_create_product(group_user_page, code, key):
    AutoBasePage(group_user_page).switch_filial(name=f"filial-pw{code}")
    run_create_product(group_user_page, code, key, save_baseline=True)


@allure.title("REG-PROD-IMPORT: UZS-B va USD-B importi va filialga biriktirish")
def test_02_import_products(page, code):
    run_import_products(page, code, save_baseline=True)


@allure.title("REG-PROD-CANCEL: ТМЦ yaratishni bekor qilish")
def test_03_cancel_creation(group_user_page, code):
    AutoBasePage(group_user_page).switch_filial(name=f"filial-pw{code}")
    run_cancel_product_creation(group_user_page, code)


@allure.title("REG-PROD-LIFECYCLE: ТМЦ edit-save va edit-cancel")
def test_04_edit_product(group_user_page, code):
    AutoBasePage(group_user_page).switch_filial(name=f"filial-pw{code}")
    run_edit_product(group_user_page, code)


@pytest.mark.parametrize("field", REQUIRED_FIELDS, ids=("name", "measure"))
@allure.title("REG-PROD-REQUIRED: {field} bo'lmasa saqlanmasligi")
def test_05_required_field(group_user_page, code, field):
    AutoBasePage(group_user_page).switch_filial(name=f"filial-pw{code}")
    run_product_required_field(group_user_page, code, field)


@allure.title("REG-PROD-IMPORT-CANCEL: Excel previewni saqlamasdan yopish")
def test_06_cancel_import(page, code):
    run_cancel_product_import(page, code)
