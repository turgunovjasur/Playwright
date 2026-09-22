"""REG-PROD-REQUIRED: majburiy nom/birliksiz ТМЦ saqlanmasligi."""

import re
from uuid import uuid4

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_products.flow_product.product_form import fill_product_card
from tests.regression.test_products.product_cases import product_case
from tests.shared.authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("Majburiy maydonlar")]

REQUIRED_FIELDS = ("Название", "Ед. изм.")


def run_product_required_field(page, code, field):
    """Testcase: bitta majburiy maydonni bo'shatib, saqlash rad etilishini tekshirish.

    1. ТМЦ listini ochish.
    2. Noyob mahsulot kartasini to'ldirish; faqat tekshirilayotgan maydonni bo'shatish.
    3. Saqlashga urinish: forma ochiq qolishi va tegishli control invalid bo'lishi.
    4. Formani yopish: listda kod bo'yicha yashirin saqlangan mahsulot bo'lmasligi.
    """
    if field not in REQUIRED_FIELDS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan required field: {field}")
    product = product_case(code, "LOW", prefix=f"reg-required-{uuid4().hex[:8]}")
    base = AutoBasePage(page)
    with allure.step("1 - ТМЦ ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")
    with allure.step(f"2 - ТМЦ kartasida {field} maydonini bo'shatish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="ТМЦ (создание)")
        fill_product_card(page, product)
        if field == "Название":
            control = base.input(label=field, value="", press_tab=True)
            invalid_class = "ng-invalid-required"
        else:
            control = base.b_input(label=field, clear=True)
            control.press("Tab")
            invalid_class = "ng-invalid-model-key"
    with allure.step(f"3 - {field} bo'lmasa saqlash rad etilishini tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ (создание)", url="inventory+add")
        expect(control).to_have_value("")
        expect(control).to_have_class(re.compile(rf"\b{invalid_class}\b"))
    with allure.step("4 - Listda xatoli mahsulot saqlanmaganini tekshirish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product["code"])
        base.grid(state="empty")


@pytest.mark.parametrize("field", REQUIRED_FIELDS, ids=("name", "measure"))
@allure.title("REG-PROD-REQUIRED: {field} bo'lmasa saqlanmasligi")
def test_product_required_field(page, code, field):
    authorization(page, who="user", code=code)
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product_required_field(page, code, field)
