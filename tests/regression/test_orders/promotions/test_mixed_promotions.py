"""Majburiy bonus va ixtiyoriy chegirma bir orderda: UI hisob va persistence."""
from decimal import Decimal
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.flows.order import (existing_order,
    open_new_order, promotion_card, reopen_order_goods, save_edited_order,
    save_order_by_reference, select_order_product,
)
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.feature("Majburiy va ixtiyoriy aksiyalar birga")]


def _completion(case, quantity, discount_on):
    """Shu faylning pul oracle’i: caller miqdor va tanlovni ochiq beradi."""
    base = AutoBasePage(case.page)
    gross = Decimal(quantity) * Decimal("7000")
    discount = gross * Decimal("0.10") if discount_on else Decimal("0")
    expected = gross - discount
    expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1)
    base.input(label="ИТОГО", expect_value=format(expected.normalize(), "f"))
    base.input(label="Сумма скидки/наценки", expect_value=format((-discount).normalize(), "f"))
    case.check("Yakunlashdagi jami (so‘m)", expected,
               Decimal(re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True))))
    case.check("Mahsulot chegirmasi (so‘m)", -discount,
               Decimal(re.sub(r"\s+", "", base.input(label="Сумма скидки/наценки", return_value=True))))
    base.b_input(label="Тип оплаты", expect_value=case.promotions["payments"]["bank"]["name"])


def _saved_result(case, quantity, discount_on, bonus_count):
    """Saved order, mahsulot va bonus tarkibini alohida UI qiymatlari bilan tekshiradi."""
    page, base = case.page, AutoBasePage(case.page)
    gross = Decimal(quantity) * Decimal("7000")
    discount = gross * Decimal("0.10") if discount_on else Decimal("0")
    base.form_view(label="ИД заказа", expect_value=case.orders[-1])
    base.form_view(label="Клиент", expect_value=case.client)
    base.form_view(label="Статус", expect_value="Черновик")
    base.form_view(label="Валюта", expect_value="Узбекский сум")
    base.form_view(label="Тип оплаты", expect_value=case.promotions["payments"]["bank"]["name"])
    case.check("Saqlangan order jami (so‘m)", gross - discount,
               Decimal(base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)))
    goods = page.locator("smt-table:visible").last
    expect(goods.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, root=goods)
    labels = [" ".join(text.split()) for text in goods.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество продажи", Decimal(quantity)), ("Цена", Decimal("7000")),
                            ("Сумма скидки/наценки", -discount), ("Итого", gross - discount)):
        case.check(f"Saqlangan mahsulot: {label}", expected,
                   Decimal(base.grid_cell(row, labels.index(label), return_value=True, remove_spaces=True)))
    if bonus_count == 0:
        expect(page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)
        case.check("Chegaradan pastda bonus bo‘limi", 0, page.get_by_role("tab", name="Акция", exact=True).count())
        return
    base.tab(name="Акция")
    bonus = page.locator("smt-table:visible").last
    expect(bonus.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=bonus)
    labels = [" ".join(text.split()) for text in bonus.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество продажи", Decimal(bonus_count)), ("Цена", Decimal("0")), ("Итого", Decimal("0"))):
        case.check(f"Majburiy bonus: {label}", expected,
                   Decimal(base.grid_cell(row, labels.index(label), return_value=True, remove_spaces=True)))


def run_toggle_discount(case):
    """1. A10, bank to‘lovi va own narx bilan order ochish.
    2. Majburiy B1ni bosmasdan ixtiyoriy 10%ni yoqish: 63 000, B1.
    3. Save/view/reopen; ixtiyoriy skidkani o‘chirish: 70 000, B1.
    4. Save/view/reopen; skidkani qayta yoqish: 63 000, B1, o‘sha order ID.
    """
    page, base = case.page, AutoBasePage(case.page)
    saved_order_id = existing_order(case)
    if not saved_order_id:
        require_available(case, 10, bonus_quantity=1)
        open_new_order(page)
        with allure.step("1 - Setup klienti va alohida narxda 10 dona mahsulot"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            base.text("Название", "Кол-во")
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="10", press_tab=True)
        with allure.step("2 - Bank to‘lovi, Draft va unique TTNni belgilash"):
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value=case.promotions["payments"]["bank"]["name"], clear=True)
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        with allure.step("3 - Majburiy bonusga tegmasdan ixtiyoriy 10%ni yoqish"):
            base.click(name="Назад", exact=True)
            base.tab(name=re.compile(r"^Акции"))
            promotion_card(page, case.promotions["bonus"]["name"])
            toggle = promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch")
            base.checkbox(locator=toggle, expect_checked=False)
            base.checkbox(locator=toggle, checked=True)
            base.click(name="Далее", exact=True)
            _completion(case, 10, True)
        saved_order_id = save_order_by_reference(page, case.reference)
    case.remember_order(saved_order_id)
    order_id = case.orders[-1]
    with allure.step("4 - Saqlangan 63 000 va bitta bepul majburiy bonus"):
        _saved_result(case, 10, True, 1)
    for desired in (False, True):
        reopen_order_goods(page)
        with allure.step(f"5 - Qayta ochilgan ixtiyoriy skidkani {'yoqish' if desired else 'o‘chirish'}"):
            base.input(label="Кол-во", expect_value="10")
            base.tab(name=re.compile(r"^Акции"))
            promotion_card(page, case.promotions["bonus"]["name"])
            toggle = promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch")
            base.checkbox(locator=toggle, expect_checked=not desired)
            base.checkbox(locator=toggle, checked=desired)
            base.click(name="Далее", exact=True)
            _completion(case, 10, desired)
        saved = save_edited_order(page, order_id, case.reference)
        case.check("Skidka tanlovi o‘zgarganda order ID", order_id, saved)
        with allure.step("6 - Save’dan keyin summa va majburiy B1 saqlangan"):
            _saved_result(case, 10, desired, 1)
    reopen_order_goods(page)
    with allure.step("7 - Yakuniy reopen: ixtiyoriy tanlov saqlangan, jami 63 000"):
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch"), expect_checked=True)
        base.click(name="Далее", exact=True)
        _completion(case, 10, True)


def run_quantity_boundary(case):
    """1. A9: 9 × 7 000 = 63 000, skidka 0 va bonus 0 bilan saqlash.
    2. Reopen va A10: majburiy B1 avtomatik, ixtiyoriy 10%ni tanlash.
    3. O‘sha orderni 63 000, skidka 7 000 va B1 bilan saqlash/reopen.

    Ikki holatda jami bir xil; miqdor, skidka va bonus alohida oracle bo‘ladi.
    """
    page, base = case.page, AutoBasePage(case.page)
    saved_order_id = existing_order(case)
    if not saved_order_id:
        require_available(case, 9, bonus_quantity=0)
        open_new_order(page)
        with allure.step("1 - Aksiya chegarasidan bir dona kam: 9 dona"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            base.text("Название", "Кол-во")
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="9", press_tab=True)
        with allure.step("2 - Bank to‘lovi bilan A9: 63 000, skidka 0"):
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value=case.promotions["payments"]["bank"]["name"], clear=True)
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
            _completion(case, 9, False)
        saved_order_id = save_order_by_reference(page, case.reference)
    case.remember_order(saved_order_id)
    order_id = case.orders[-1]
    with allure.step("3 - A9 saved: tovar 9, skidka 0, bonus 0"):
        _saved_result(case, 9, False, 0)
    reopen_order_goods(page)
    with allure.step("4 - 9 dona qayta ochilgan; 10 donaga oshirib ixtiyoriy skidkani tanlash"):
        base.input(label="Кол-во", expect_value="9")
        base.input(label="Кол-во", value="10", press_tab=True)
        base.tab(name=re.compile(r"^Акции"))
        promotion_card(page, case.promotions["bonus"]["name"])
        toggle = promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch")
        base.checkbox(locator=toggle, expect_checked=False)
        base.checkbox(locator=toggle, checked=True)
        base.click(name="Далее", exact=True)
        _completion(case, 10, True)
    saved = save_edited_order(page, order_id, case.reference)
    case.check("9 donadan 10 donaga o‘tganda order ID", order_id, saved)
    with allure.step("5 - A10 saved: skidka 7 000, jami 63 000 va majburiy B1"):
        _saved_result(case, 10, True, 1)
    reopen_order_goods(page)
    with allure.step("6 - 10 dona va ixtiyoriy tanlov qayta ochilganda saqlangan"):
        base.input(label="Кол-во", expect_value="10")
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch"), expect_checked=True)
        base.click(name="Далее", exact=True)
        _completion(case, 10, True)
