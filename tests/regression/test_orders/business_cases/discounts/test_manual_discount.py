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

from tests.regression.test_orders.helpers.flows.order import existing_order, open_new_order, select_order_product, save_order_by_reference, reopen_order_goods, promotion_card
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Qo'lda chegirma"), allure.story("Summali chegirma")]


def _number(value):
    return Decimal(re.sub(r"\s+", "", value).replace(",", "."))


def _open_goods(case, quantity):
    """Uch case uchun bir xil create → klient → mahsulot choreography."""
    base = AutoBasePage(case.page)
    require_available(case, quantity, bonus_quantity=0)
    open_new_order(case.page)
    with allure.step('Tayyorlangan test klienti bilan mahsulotlar bosqichini ochish'):
        base.b_input(label="Рабочая зона", expect_value=case.room)
        base.b_input(label="Штат", expect_value=case.staff)
        base.b_input(label="Клиент", value=case.client, clear=True)
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")
    with allure.step(f"Tayyorlangan narxda {quantity} dona mahsulotni tanlash"):
        row = select_order_product(case.page, case.product, case.price_type)
        base.input(label="Кол-во", value=str(quantity), press_tab=True)
        expect(row.locator("[data-smt-col-key=price]")).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
    return row


def _line_amount(case, row, amount):
    """Foiz rejimidan qo'lda summaga; barcha amallar mavjud base API bilan."""
    base = AutoBasePage(case.page)
    margin = row.locator('[data-smt-col-key="margin"]')
    toggle = margin.get_by_role("button", name="Скидка/наценка", exact=True)
    # Fresh addning standart rejimini tasdiqlash; tasodifan teskari toggle yo'q.
    expect(toggle.locator('svg-icon[aria-label="percent-01-icon"]')).to_be_visible()
    base.click(name="Скидка/наценка", exact=True, root=margin)
    base.input(label="Скидка/наценка", value=str(amount), press_tab=True)
    case.check("Bir dona uchun kiritilgan summali chegirma", Decimal(amount), _number(base.input(label="Скидка/наценка", return_value=True)))


def _header_amount(case, amount):
    base = AutoBasePage(case.page)
    toggle = case.page.get_by_role("button", name="Скидка/наценка", exact=True)
    expect(toggle).to_have_count(1)
    expect(toggle.locator('svg-icon[aria-label="percent-01-icon"]')).to_be_visible()
    base.click(name="Скидка/наценка", exact=True)
    base.input(label="Скидка/наценка к заказу", value=str(amount), press_tab=True)
    case.check("Butun orderga kiritilgan summali chegirma", Decimal(amount), _number(base.input(label="Скидка/наценка к заказу", return_value=True)))


def _save_draft(case, total):
    base = AutoBasePage(case.page)
    with allure.step(f"{total} so'mlik orderga alohida TTN raqami berib saqlashga tayyorlash"):
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(label="ИТОГО", expect_value=str(total))
        case.check("Saqlashdan oldingi jami (so'm)", Decimal(total), _number(base.input(label="ИТОГО", return_value=True)))
        base.input(label="Номер товарно-транспортной накладной", value=case.reference)
        base.ui_select(label="Статус", value="Черновик")
    case.remember_order(save_order_by_reference(case.page, case.reference))


def _saved_amounts(case, quantity, line_discount, line_total, order_discount, total, bonus=False):
    """Viewdagi signed chegirmalar va ikki alohida hisoblash bazasini tekshirish."""
    page, base = case.page, AutoBasePage(case.page)
    base.form_view(label="ИД заказа", expect_value=case.orders[-1])
    base.form_view(label="Клиент", expect_value=case.client)
    base.form_view(label="Статус", expect_value="Черновик")
    base.form_view(label="Валюта", expect_value="Узбекский сум")
    for label, expected in (("Сумма заказа", total), ("Сумма скидки/наценки на заказ", order_discount)):
        base.form_view(label=label, expect_value=str(expected), remove_spaces=True)
        case.check(f"Saqlangan order: {label}", Decimal(expected), _number(base.form_view(label=label, return_value=True, remove_spaces=True)))
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, root=grid)
    labels = [" ".join(value.split()) for value in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество заказа", quantity), ("Цена", 7000), ("Сумма скидки/наценки", line_discount), ("Итого", line_total)):
        if labels.count(label) != 1:
            raise AssertionError(f"View goods ustuni topilmadi yoki takrorlangan: {label}")
        cell = base.grid_cell(row, labels.index(label))
        expect(cell).to_have_text(re.compile(r"^\s*" + r"\s*".join(re.escape(c) for c in str(expected)) + r"\s*$"))
        case.check(f"Saqlangan mahsulot: {label}", Decimal(expected), _number(base.grid_cell(row, labels.index(label), return_value=True)))
    if not bonus:
        expect(page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)
        case.check("Saqlangan orderda bonus bo'limi soni", 0, page.get_by_role("tab", name="Акция", exact=True).count())
        return
    with allure.step("Saqlangan bepul bonus bo'limini ochish"):
        base.tab(name="Акция")
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=grid)
    with allure.step("Aynan tayyorlangan aksiya: boshqa mahsulotdan 1 dona, narxi va summasi 0"):
        labels = [" ".join(value.split()) for value in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, expected in (("Количество продажи", 1), ("Цена", 0), ("Итого", 0)):
            if labels.count(label) != 1:
                raise AssertionError(f"Bonus view ustuni topilmadi yoki takrorlangan: {label}")
            expect(base.grid_cell(row, labels.index(label))).to_have_text(str(expected))
            case.check(f"Saqlangan bonus: {label}", Decimal(expected), _number(base.grid_cell(row, labels.index(label), return_value=True)))


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
        row = _open_goods(case, 2)
        with allure.step("1 - Har dona uchun 100 so'm chegirma; 2 dona uchun jami 200"):
            _line_amount(case, row, -100)
        with allure.step("2 - Order yakunlash bosqichida jami 13 800"):
            base.click(name="Далее", exact=True)
            # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
            expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
            base.input(label="ИТОГО", expect_value="13800")
        _save_draft(case, 13800)
    with allure.step('3 - Saqlangan orderda mahsulot chegirmasi −200, umumiy order chegirmasi 0, jami 13 800 so‘m'):
        _saved_amounts(case, 2, -200, 13800, 0, 13800)
    reopen_order_goods(case.page)
    with allure.step("4 - Qayta ochilgan mahsulot miqdori 2, har dona chegirmasi −100"):
        base.input(label="Кол-во", expect_value="2")
        base.input(label="Скидка/наценка", expect_value="-100")
        case.check("Qayta ochilgan har dona chegirmasi", Decimal("-100"), _number(base.input(label="Скидка/наценка", return_value=True)))
    with allure.step("5 - Qayta ochilgan order jami 13 800"):
        base.click(name="Далее", exact=True)
        # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
        expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
        base.input(label="ИТОГО", expect_value="13800")
        case.check("Qayta ochilgan jami (so'm)", Decimal("13800"), _number(base.input(label="ИТОГО", return_value=True)))


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
        _open_goods(case, 2)
        with allure.step("1 - Chegirmasiz 14 000 so'm bilan yakunlash bosqichini ochish"):
            base.click(name="Далее", exact=True)
            # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
            expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
            base.input(label="ИТОГО", expect_value="14000")
        with allure.step("2 - Butun orderga bir martalik 200 so'm chegirma"):
            _header_amount(case, -200)
            base.input(label="ИТОГО", expect_value="13800")
        _save_draft(case, 13800)
    with allure.step('3 - Saqlangan mahsulot summasi 14 000, umumiy order chegirmasi −200, jami 13 800 so‘m'):
        _saved_amounts(case, 2, 0, 14000, -200, 13800)
    reopen_order_goods(case.page)
    with allure.step("4 - Qayta ochilgan mahsulot miqdori 2"):
        base.input(label="Кол-во", expect_value="2")
    with allure.step('5 - Qayta ochilgan orderga umumiy chegirma −200, jami 13 800 so‘m'):
        base.click(name="Далее", exact=True)
        # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
        expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
        base.input(label="Скидка/наценка к заказу", expect_value="-200")
        base.input(label="ИТОГО", expect_value="13800")
        case.check("Qayta ochilgan order chegirmasi", Decimal("-200"), _number(base.input(label="Скидка/наценка к заказу", return_value=True)))
        case.check("Qayta ochilgan jami (so'm)", Decimal("13800"), _number(base.input(label="ИТОГО", return_value=True)))


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
        row = _open_goods(case, 10)
        with allure.step("1 - 10 donaning har biriga −100: mahsulotlar jami 69 000"):
            _line_amount(case, row, -100)
        with allure.step('2 - Aksiyalarni ochib faqat test uchun tayyorlangan bepul bonusni yoqish'):
            base.tab(name=re.compile(r"^Акции"))
            bonus = promotion_card(page, case.promotions["bonus"]["name"])
            base.checkbox(locator=bonus.get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
        with allure.step('3 - Bonus bilan yakunlash: orderga umumiy chegirma berishdan oldin jami 69 000 so‘m'):
            base.click(name="Далее", exact=True)
            # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
            expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
            base.input(label="ИТОГО", expect_value="69000")
        with allure.step("4 - Butun orderga qo'shimcha −200: yakuniy jami 68 800"):
            _header_amount(case, -200)
            base.input(label="ИТОГО", expect_value="68800")
        _save_draft(case, 68800)
    with allure.step('5 - Saqlangan qator chegirmasi −1 000, umumiy order chegirmasi −200, jami 68 800 so‘m va 1 dona bepul bonus'):
        _saved_amounts(case, 10, -1000, 69000, -200, 68800, bonus=True)
    reopen_order_goods(page)
    with allure.step("6 - Qayta ochilgan 10 dona va har dona −100"):
        base.input(label="Кол-во", expect_value="10")
        base.input(label="Скидка/наценка", expect_value="-100")
        case.check("Qayta ochilgan har dona chegirmasi", Decimal("-100"), _number(base.input(label="Скидка/наценка", return_value=True)))
    with allure.step('7 - Qayta ochilganda faqat test uchun tayyorlangan bonus tanlovi saqlangan'):
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["bonus"]["name"]).get_by_role("switch"), expect_checked=True)
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
    with allure.step('8 - Qayta ochilgan orderga umumiy chegirma −200, jami 68 800 so‘m'):
        base.click(name="Далее", exact=True)
        # Bosqich almashib bo‘lmaguncha eski grid maydonlarini qidirmaymiz.
        expect(case.page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$")).filter(visible=True)).to_have_count(1, timeout=60_000)
        base.input(label="Скидка/наценка к заказу", expect_value="-200")
        base.input(label="ИТОГО", expect_value="68800")
        case.check("Qayta ochilgan order chegirmasi", Decimal("-200"), _number(base.input(label="Скидка/наценка к заказу", return_value=True)))
        case.check("Qayta ochilgan jami (so'm)", Decimal("68800"), _number(base.input(label="ИТОГО", return_value=True)))
