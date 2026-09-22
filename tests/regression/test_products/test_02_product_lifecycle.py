"""REG-PROD-LIFECYCLE/CANCEL: mustaqil ТМЦ yaratish va tahrirlash caselari."""

from uuid import uuid4

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_products.flow_product.product_form import fill_product_card
from tests.regression.test_products.product_cases import product_case
from tests.regression.test_products.test_01_create_product import check_product_card, run_create_product
from tests.shared.authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("Tahrir va bekor qilish")]


def run_cancel_product_creation(page, code):
    """Testcase: to'ldirilgan ТМЦ yaratishni bekor qilish saqlamasligi kerak.

    1. Noyob mahsulot kodi yo'qligini listda tekshirish.
    2. Barcha qo'llab-quvvatlangan karta maydonlarini to'ldirish.
    3. Saqlamasdan yopib, qidiruvda yangi mahsulot yo'qligini tekshirish.
    """
    product = product_case(code, "UZS-A", prefix=f"reg-cancel-{uuid4().hex[:8]}")
    base = AutoBasePage(page)
    with allure.step("1 - ТМЦ listida yangi cancel kodi yo'qligini tekshirish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product["code"])
        base.grid(state="empty")
    with allure.step("2 - ТМЦ create formasini to'ldirish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="ТМЦ (создание)")
        fill_product_card(page, product)
    with allure.step("3 - Create formasini bekor qilish va saqlanmaganini tekshirish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product["code"])
        base.grid(state="empty")


def run_edit_product(page, code):
    """Testcase: faqat o'zi yaratgan mahsulotni edit-save va edit-cancel qilish.

    1. Alohida mahsulot yaratib barcha dastlabki qiymatlarini tekshirish.
    2. Listdan editni ochish, nom/kod, birlik, turlar, qadoq va vaznni yangilash.
    3. Saqlab, yangi kod bilan listdan topish; eski kod yo'q bo'lishi kerak.
    4. Editni qayta ochib yangi qiymatlarning saqlanganini tekshirish.
    5. Boshqa nom/kod/vazn kiritib saqlamasdan yopish.
    6. Qayta ochganda oxirgi saqlangan qiymatlar qolganini tekshirish.
    7. Listga qaytish; bekor qilingan kod bo'yicha mahsulot topilmasligi kerak.
    """
    base = AutoBasePage(page)
    with allure.step("1 - Shu case uchun mustaqil ТМЦ tayyorlash"):
        original = run_create_product(page, code, "UZS-A", prefix=f"reg-edit-{uuid4().hex[:8]}")
    updated = {**original, "name": original["name"] + " edited", "short_name": original["short_name"] + " e", "code": original["code"] + "_e", "article_code": original["article_code"] + "_e", "order_no": "12", "measure": "кг", "production": True, "material": True, "box": "Блок", "box_qty": "6", "pallet_qty": "8", "weight_netto": "0.625", "weight_brutto": "0.75", "volume": "1.25"}
    cancelled = {**updated, "name": updated["name"] + " cancelled", "code": updated["code"] + "_cancel", "weight_netto": "0.5"}
    with allure.step("2 - Listdan edit formasini ochish va qiymatlarni yangilash"):
        base.grid(original["code"], click=True)
        base.click(name="Изменить", exact=True)
        base.expect_page(heading="ТМЦ (изменение)")
        fill_product_card(page, updated)
        base.checkbox(label="Новинка", checked=True)
    with allure.step("3 - Editni saqlash va yangi/eski kodni solishtirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=updated["code"])
        base.grid(updated["code"], updated["name"], updated["measure"], "Активный")
        # Search substring bo'lgani uchun eski kodni bo'sh grid bilan tekshirib bo'lmaydi.
        # Aynan eski kodli cell yo'qligi Playwright exact text bilan tekshiriladi.
        base.grid_controller(search=original["code"])
        expect(page.locator("b-grid:visible").get_by_text(original["code"], exact=True)).to_have_count(0)
    with allure.step("4 - Saqlangan editni qayta ochish va solishtirish"):
        base.grid(updated["code"], click=True)
        base.click(name="Изменить", exact=True)
        base.expect_page(heading="ТМЦ (изменение)")
        check_product_card(page, updated)
        base.checkbox(label="Новинка", expect_checked=True)
        fill_product_card(page, cancelled)
        base.checkbox(label="Новинка", checked=False)
    with allure.step("5 - Ikkinchi editni saqlamasdan yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")
    with allure.step("6 - Bekor qilingan edit oldingi saqlangan qiymatlarni buzmaganini tekshirish"):
        base.grid_controller(search=updated["code"])
        base.grid(updated["code"], click=True)
        base.click(name="Изменить", exact=True)
        base.expect_page(heading="ТМЦ (изменение)")
        check_product_card(page, updated)
        base.checkbox(label="Новинка", expect_checked=True)
    with allure.step("7 - Listda bekor qilingan kod yo'qligini tekshirish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=cancelled["code"])
        base.grid(state="empty")


@allure.title("REG-PROD-CANCEL: ТМЦ yaratishni bekor qilish")
def test_cancel_product_creation(page, code):
    authorization(page, who="user", code=code)
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_cancel_product_creation(page, code)


@allure.title("REG-PROD-LIFECYCLE: ТМЦ edit-save va edit-cancel")
def test_edit_product(page, code):
    authorization(page, who="user", code=code)
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_edit_product(page, code)
