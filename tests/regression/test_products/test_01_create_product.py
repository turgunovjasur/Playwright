"""REG-PROD-CREATE: oltita kengaytirilgan ТМЦ kartasi va saqlanish tekshiruvi."""

import os
import re

import allure
import pytest

from tests.regression.test_products.flow_product.product_form import fill_product_card
from tests.regression.test_products.product_cases import MANUAL_PRODUCT_KEYS, product_case
from tests.shared.authorization import authorization, current_company_code
from utils.base_pages.auto_base_page import AutoBasePage
from utils.data_store import save_data
from utils.helper_utils import query_int_from_url

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("ТМЦ"), allure.story("Kengaytirilgan yaratish")]


def check_product_card(page, product):
    """Qayta ochilgan kartani mustaqil expected qiymatlar bilan solishtiradi."""
    base = AutoBasePage(page)
    for label, key in (("Название", "name"), ("Альтернативное название", "short_name"), ("Код", "code"), ("Артикул код", "article_code"), ("Порядковый номер", "order_no")):
        base.input(label=label, expect_value=product[key])
    base.b_input(label="Ед. изм.", expect_value=product["measure"])
    base.multiselect(label="Наборы ТМЦ", expect_value=product["sector"])
    base.checkbox(label="Активный", expect_checked=True)
    base.checkbox(label="Товар", expect_checked=True)
    base.checkbox(label="Продукция", expect_checked=product["production"])
    base.checkbox(label="Сырье", expect_checked=product["material"])
    for level, name_key, qty_key in ((1, "box", "box_qty"), (2, "pallet", "pallet_qty")):
        base.b_input(label=f"Тип кейса ({level} уровень)", expect_value=product[name_key])
        if product[qty_key]:
            base.input(label=f"Кол-во в кейсе ({level} уровень)", expect_value=re.compile(rf"^\s*{re.escape(product[qty_key])}(?:[.,]0+)?\s*$"))
    page.locator("#kt_content a").filter(has=page.get_by_text("Вес", exact=True)).click()
    for label, key in (("Вес нетто (кг)", "weight_netto"), ("Вес брутто (кг)", "weight_brutto"), ("Литр/Дециметр куб.", "volume")):
        parts = product[key].split(".")
        number = re.escape(parts[0]) + (r"[.,]" + re.escape(parts[1]) + "0*" if len(parts) == 2 else r"(?:[.,]0+)?")
        base.input(label=label, expect_value=re.compile(rf"^\s*{number}\s*$"))


def run_create_product(page, code, key, *, prefix="reg", save_baseline=False):
    """Testcase: ТМЦ yaratish, view va edit orqali kartaning saqlanishini tekshirish.

    1. ТМЦ listini ochish va noyob kod mavjud emasligini tekshirish.
    2. Create formasida nom/kod/birlik, tur, qadoq, og'irlik/hajmni kiritish.
    3. Saqlab listda kod, nom, birlik va faol holatni tekshirish.
    4. View orqali yaratilgan mahsulot IDsi va asosiy qiymatlarni tekshirish.
    5. Edit orqali kiritilgan barcha qiymatlarni qayta solishtirish.
    6. O'zgartirmasdan viewga qaytish.
    7. Listga qaytish va ixtiyoriy setup natijasini saqlash.
    """
    product = product_case(code, key, prefix=prefix)
    base = AutoBasePage(page)
    baseline_key = f"regression_product_{key.lower().replace('-', '_')}"
    if save_baseline:
        # Oldingi muvaffaqiyatli run qiymati yangi muvaffaqiyatsiz attemptni yashirmaydi.
        save_data(baseline_key, None)

    with allure.step(f"1 - {key}: ТМЦ listida noyob kodni tekshirish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product["code"])
        base.grid(state="empty")

    with allure.step(f"2 - {key}: kengaytirilgan ТМЦ yaratish formasini to'ldirish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="ТМЦ (создание)")
        fill_product_card(page, product)

    with allure.step(f"3 - {key}: saqlash va list natijasini tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product["code"])
        base.grid(product["code"], product["name"], product["short_name"], product["measure"], "Активный")

    with allure.step(f"4 - {key}: ТМЦ view va yaratilgan IDni tekshirish"):
        base.grid(product["code"], click=True)
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")
        base.text(product["name"], product["code"], product["short_name"])
        product_id = query_int_from_url(page.url, "product_id")

    with allure.step(f"5 - {key}: editda saqlangan kartani solishtirish"):
        base.click(name="Изменить", exact=True)
        base.expect_page(heading="ТМЦ (изменение)")
        check_product_card(page, product)

    with allure.step(f"6 - {key}: editni o'zgartirmasdan yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ (просмотр)")

    with allure.step(f"7 - {key}: ТМЦ listiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid(product["code"], product["name"], "Активный")

    if save_baseline:
        save_data(baseline_key, {"run_code": str(code), "server": os.environ["COMPANY_URL"].rstrip("/"), "company": current_company_code(), "product_id": product_id, "card_verified": True, "price_verified": False, "stock_verified": False, **product})
    return product


@pytest.mark.parametrize("key", MANUAL_PRODUCT_KEYS, ids=MANUAL_PRODUCT_KEYS)
@allure.title("REG-PROD-CREATE-{key}: kengaytirilgan ТМЦ yaratish")
def test_create_product(page, code, key):
    authorization(page, who="user", code=code)
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_create_product(page, code, key, save_baseline=True)
