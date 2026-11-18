"""Order chegirmalari uchun umumiy ssenariy qadamlari va hisob tekshiruvlari."""
from decimal import Decimal
import re

import allure
from playwright.sync_api import expect

from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.test_orders.helpers.flows.order import (
    open_new_order, save_order_by_reference, select_client_product,
)
from utils.base_pages.auto_base_page import AutoBasePage


def parse_amount(value):
    return Decimal(re.sub(r"\s+", "", value).replace(",", "."))


def open_discount_goods(case, quantity):
    """Uch case uchun bir xil create → klient → mahsulot choreography."""
    base = AutoBasePage(case.page)
    require_available(case, quantity, bonus_quantity=0)
    open_new_order(case.page)
    with allure.step('Tayyorlangan test klienti bilan mahsulotlar bosqichini ochish'):
        base.b_input(label="Рабочая зона", expect_value=case.room)
        base.b_input(label="Штат", expect_value=case.staff)
        row = select_client_product(case.page, case.client, case.product, case.price_type)
    with allure.step(f"Tanlangan mahsulot miqdorini {quantity} qilib narxini tekshirish"):
        base.input(label="Кол-во", value=str(quantity), press_tab=True)
        expect(row.locator("[data-smt-col-key=price]")).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
    return row


def save_discount_draft(case, total):
    base = AutoBasePage(case.page)
    with allure.step(f"{total} so'mlik orderga alohida TTN raqami berib saqlashga tayyorlash"):
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(label="ИТОГО", expect_value=str(total))
        case.check("Saqlashdan oldingi jami (so'm)", Decimal(total), parse_amount(base.input(label="ИТОГО", return_value=True)))
        base.input(label="Номер товарно-транспортной накладной", value=case.reference)
        base.ui_select(label="Статус", value="Черновик")
    case.remember_order(save_order_by_reference(case.page, case.reference))


def check_saved_amounts(case, quantity, line_discount, line_total, order_discount, total, bonus=False):
    """Viewdagi signed chegirmalar va ikki alohida hisoblash bazasini tekshirish."""
    page, base = case.page, AutoBasePage(case.page)
    base.form_view(label="ИД заказа", expect_value=case.orders[-1])
    base.form_view(label="Клиент", expect_value=case.client)
    base.form_view(label="Статус", expect_value="Черновик")
    base.form_view(label="Валюта", expect_value="Узбекский сум")
    for label, expected in (("Сумма заказа", total), ("Сумма скидки/наценки на заказ", order_discount)):
        base.form_view(label=label, expect_value=str(expected), remove_spaces=True)
        case.check(f"Saqlangan order: {label}", Decimal(expected), parse_amount(base.form_view(label=label, return_value=True, remove_spaces=True)))
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, root=grid)
    labels = [" ".join(value.split()) for value in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество заказа", quantity), ("Цена", 7000), ("Сумма скидки/наценки", line_discount), ("Итого", line_total)):
        if labels.count(label) != 1:
            raise AssertionError(f"View goods ustuni topilmadi yoki takrorlangan: {label}")
        cell = base.grid_cell(row, labels.index(label))
        expect(cell).to_have_text(re.compile(r"^\s*" + r"\s*".join(re.escape(c) for c in str(expected)) + r"\s*$"))
        case.check(f"Saqlangan mahsulot: {label}", Decimal(expected), parse_amount(base.grid_cell(row, labels.index(label), return_value=True)))
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
            case.check(f"Saqlangan bonus: {label}", Decimal(expected), parse_amount(base.grid_cell(row, labels.index(label), return_value=True)))
