"""Qo'lda summali skidka: har dona, butun order va ixtiyoriy bonus.

Oracle: manual order-full-20261026/1111–1112, 1248–1251; goods per-unit,
header bir martalik. A2 margin DOM: 20261103T032209Z-a32cf727 trace.
Faqat UI amallari; katalog/aksiya tayyorlovi runnerdagi alohida testda.
"""
from decimal import Decimal
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.discounts import (
    check_saved_amounts, open_discount_goods, parse_amount, save_discount_draft,
    set_line_discount_amount, set_order_discount_amount,
)
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_order_summary, promotion_card, reopen_order_goods,
)
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Qo'lda chegirma"), allure.story("Summali chegirma")]


def run_line_amount(case):
    """1. 2 × 7 000 mahsulotli order.
    2. Har donaga −100: qator chegirmasi −200, jami 13 800.
    3. Save/viewda line −200 va header 0; editda har dona −100 saqlangan.
    """
    base = AutoBasePage(case.page)
    saved_order_id = existing_order(case)
    if saved_order_id:
        case.remember_order(saved_order_id)
    else:
        row = open_discount_goods(case, 2)
        with allure.step("1 - Har dona uchun 100 so'm chegirma; 2 dona uchun jami 200"):
            set_line_discount_amount(case, row, -100)
        with allure.step("2 - Order yakunlash bosqichida jami 13 800"):
            open_order_summary(case.page, expected_total="13800")
        save_discount_draft(case, 13800)
    with allure.step('3 - Saqlangan orderda mahsulot chegirmasi −200, umumiy order chegirmasi 0, jami 13 800 so‘m'):
        check_saved_amounts(case, 2, -200, 13800, 0, 13800)
    reopen_order_goods(case.page)
    with allure.step("4 - Qayta ochilgan mahsulot miqdori 2, har dona chegirmasi −100"):
        base.input(label="Кол-во", expect_value="2")
        base.input(label="Скидка/наценка", expect_value="-100")
        case.check("Qayta ochilgan har dona chegirmasi", Decimal("-100"), parse_amount(base.input(label="Скидка/наценка", return_value=True)))
    with allure.step("5 - Qayta ochilgan order jami 13 800"):
        open_order_summary(case.page, expected_total="13800")
        case.check("Qayta ochilgan jami (so'm)", Decimal("13800"), parse_amount(base.input(label="ИТОГО", return_value=True)))


def run_order_amount(case):
    """1. 2 × 7 000 mahsulotli order, qator chegirmasi yo'q.
    2. Butun orderga bir martalik −200: jami 13 800 (13 600 emas).
    3. Save/viewda qator 14 000, header −200; editda −200 saqlangan.
    """
    base = AutoBasePage(case.page)
    saved_order_id = existing_order(case)
    if saved_order_id:
        case.remember_order(saved_order_id)
    else:
        open_discount_goods(case, 2)
        with allure.step("1 - Chegirmasiz 14 000 so'm bilan yakunlash bosqichini ochish"):
            open_order_summary(case.page, expected_total="14000")
        with allure.step("2 - Butun orderga bir martalik 200 so'm chegirma"):
            set_order_discount_amount(case, -200)
            base.input(label="ИТОГО", expect_value="13800")
        save_discount_draft(case, 13800)
    with allure.step('3 - Saqlangan mahsulot summasi 14 000, umumiy order chegirmasi −200, jami 13 800 so‘m'):
        check_saved_amounts(case, 2, 0, 14000, -200, 13800)
    reopen_order_goods(case.page)
    with allure.step("4 - Qayta ochilgan mahsulot miqdori 2"):
        base.input(label="Кол-во", expect_value="2")
    with allure.step('5 - Qayta ochilgan orderga umumiy chegirma −200, jami 13 800 so‘m'):
        open_order_summary(case.page, expected_total="13800")
        base.input(label="Скидка/наценка к заказу", expect_value="-200")
        case.check("Qayta ochilgan order chegirmasi", Decimal("-200"), parse_amount(base.input(label="Скидка/наценка к заказу", return_value=True)))
        case.check("Qayta ochilgan jami (so'm)", Decimal("13800"), parse_amount(base.input(label="ИТОГО", return_value=True)))


def run_amounts_with_bonus(case):
    """1. 10 × 7 000, har donaga −100: qator 69 000.
    2. Faqat ixtiyoriy A10→B1 bonusini tanlash; aksiya skidkasi OFF.
    3. Headerga bir martalik −200: jami 68 800 + bepul B1.
    4. Save/view/reopen bilan har ikki skidka, jami va bonusni tasdiqlash.
    """
    page, base = case.page, AutoBasePage(case.page)
    saved_order_id = existing_order(case)
    if saved_order_id:
        case.remember_order(saved_order_id)
    else:
        row = open_discount_goods(case, 10)
        with allure.step("1 - 10 donaning har biriga −100: mahsulotlar jami 69 000"):
            set_line_discount_amount(case, row, -100)
        with allure.step('2 - Aksiyalarni ochib faqat test uchun tayyorlangan bepul bonusni yoqish'):
            base.tab(name=re.compile(r"^Акции"))
            bonus = promotion_card(page, case.promotions["bonus"]["name"])
            base.checkbox(locator=bonus.get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
        with allure.step('3 - Bonus bilan yakunlash: orderga umumiy chegirma berishdan oldin jami 69 000 so‘m'):
            open_order_summary(case.page, expected_total="69000")
        with allure.step("4 - Butun orderga qo'shimcha −200: yakuniy jami 68 800"):
            set_order_discount_amount(case, -200)
            base.input(label="ИТОГО", expect_value="68800")
        save_discount_draft(case, 68800)
    with allure.step('5 - Saqlangan qator chegirmasi −1 000, umumiy order chegirmasi −200, jami 68 800 so‘m va 1 dona bepul bonus'):
        check_saved_amounts(case, 10, -1000, 69000, -200, 68800, bonus=True)
    reopen_order_goods(page)
    with allure.step("6 - Qayta ochilgan 10 dona va har dona −100"):
        base.input(label="Кол-во", expect_value="10")
        base.input(label="Скидка/наценка", expect_value="-100")
        case.check("Qayta ochilgan har dona chegirmasi", Decimal("-100"), parse_amount(base.input(label="Скидка/наценка", return_value=True)))
    with allure.step('7 - Qayta ochilganda faqat test uchun tayyorlangan bonus tanlovi saqlangan'):
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["bonus"]["name"]).get_by_role("switch"), expect_checked=True)
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
    with allure.step('8 - Qayta ochilgan orderga umumiy chegirma −200, jami 68 800 so‘m'):
        open_order_summary(case.page, expected_total="68800")
        base.input(label="Скидка/наценка к заказу", expect_value="-200")
        case.check("Qayta ochilgan order chegirmasi", Decimal("-200"), parse_amount(base.input(label="Скидка/наценка к заказу", return_value=True)))
        case.check("Qayta ochilgan jami (so'm)", Decimal("68800"), parse_amount(base.input(label="ИТОГО", return_value=True)))
