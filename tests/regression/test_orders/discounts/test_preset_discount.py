"""Katalogda tayyorlangan foizli skidka: aksiya tanlamasdan order round-trip."""
from decimal import Decimal
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.discounts.test_manual_discount import _number, _open_goods, _save_draft, _saved_amounts
from tests.regression.test_orders.flows.order import reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Tayyor va qo'lda skidka"),
              allure.story("Tayyor foizli skidka")]


def run_preset_discount(case):
    """1. Xonaga biriktirilgan own 10% skidka tayyorligini tekshirish.
    2. 2 × 7 000 mahsulotli orderda tayyor −10 foiz variantini tanlash.
    3. 14 000 − 1 400 = 12 600; order-level skidka va bonus yo'q.
    4. Save/viewda ID, miqdor, narx, chegirma va jami tekshiriladi.
    5. Editni qayta ochib aynan −10% tanlovi va 12 600 jami saqlangani tekshiriladi.
    """
    margin = case.workflow.get("margin", {})
    if margin.get("status") != "passed":
        pytest.skip("BLOCKED: own 10% skidka yaratilib filial va xonaga biriktirilmagan")
    if margin.get("percent_type") != "D" or Decimal(margin["percent"]) != Decimal("10"):
        raise AssertionError("Tayyorlov aynan 10% Скидка yaratishi kerak")
    quantity, unit_price, percent = Decimal("2"), Decimal("7000"), Decimal("10")
    gross = quantity * unit_price
    discount = gross * percent / Decimal("100")
    total = gross - discount
    base = AutoBasePage(case.page)
    row = _open_goods(case, quantity)
    with allure.step('1 - Foiz rejimida katalogdagi tayyor −10% chegirmani tanlash'):
        toggle = row.locator('[data-smt-col-key="margin"]').get_by_role("button", name="Скидка/наценка", exact=True)
        expect(toggle.locator('svg-icon[aria-label="percent-01-icon"]')).to_be_visible()
        base.ui_select(label="Скидка/наценка", value="-10")
        case.check('Mahsulot uchun tanlangan tayyor chegirma (%)', -percent,
                   _number(base.ui_select(label="Скидка/наценка", return_value=True)))
    with allure.step("2 - Yakunlash bosqichida chegirma 1 400 va jami 12 600"):
        base.click(name="Далее", exact=True)
        # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
        expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
        base.input(label="Сумма скидки/наценки", expect_value=str(-discount))
        base.input(label="ИТОГО", expect_value=str(total))
        case.check("Mahsulotlar chegirmasi (so'm)", -discount,
                   _number(base.input(label="Сумма скидки/наценки", return_value=True)))
    _save_draft(case, total)
    with allure.step('3 - Saqlangan order: 2 dona, narx 7 000, mahsulot chegirmasi −1 400, umumiy order chegirmasi 0 va jami 12 600 so‘m'):
        _saved_amounts(case, quantity, -discount, total, 0, total)
    reopen_order_goods(case.page)
    with allure.step("4 - Qayta ochilgan orderda 2 dona va tayyor −10% tanlovi saqlangan"):
        base.input(label="Кол-во", expect_value=str(quantity))
        base.ui_select(label="Скидка/наценка", expect_value="-10")
        case.check('Qayta ochilgan tayyor chegirma (%)', -percent,
                   _number(base.ui_select(label="Скидка/наценка", return_value=True)))
    with allure.step("5 - Qayta ochilgan yakuniy summa 12 600 va chegirma −1 400"):
        base.click(name="Далее", exact=True)
        # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
        expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
        base.input(label="Сумма скидки/наценки", expect_value=str(-discount))
        base.input(label="ИТОГО", expect_value=str(total))
        case.check("Qayta ochilgan chegirma (so'm)", -discount,
                   _number(base.input(label="Сумма скидки/наценки", return_value=True)))
        case.check("Qayta ochilgan jami (so'm)", total,
                   _number(base.input(label="ИТОГО", return_value=True)))


@allure.title("OD-03: Tayyor −10% skidka — 12 600 so'm")
def test_preset_discount(workflow_order):
    run_preset_discount(workflow_order)
