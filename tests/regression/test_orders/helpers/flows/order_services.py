"""Orderdagi xizmatlar bo‘limini to‘ldirish va saqlangan qatorlarni o‘qish."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.discounts import parse_amount
from utils.base_pages.auto_base_page import AutoBasePage


def add_order_services(page, price_type, lines):
    base = AutoBasePage(page)
    with allure.step("Buyurtmaning xizmatlar bo‘limini ochish"):
        base.tab(name="Услуга")
    table = page.locator("smt-table:visible").first
    for index, (service, quantity) in enumerate(lines):
        with allure.step(f"{service['name']} xizmatidan {quantity} dona tanlash"):
            field = base.b_input(placeholder="Выберите...", index=index, root=table,
                                 value=service["name"], option_contains=(price_type,), stop_after_select=True)
            expect(field).to_have_value(service["name"])
            row = table.locator(".smt-data-row").nth(index)
            expect(row.get_by_text(price_type, exact=True)).to_be_visible()
            base.input(locator=row.locator("[data-smt-col-key=quantity] input"),
                       value=str(quantity), press_tab=True)


def check_saved_services(case, lines):
    base = AutoBasePage(case.page)
    with allure.step("Saqlangan xizmatlarning soni, miqdori, narxi va summasi"):
        base.tab(name="Услуга")
        first = base.grid(lines[0][0]["name"])
        table = first.locator("xpath=ancestor::*[self::smt-table or self::smt-data-table][1]")
        expect(table.locator(".smt-data-row")).to_have_count(len(lines))
        columns = [" ".join(v.split()) for v in table.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for service, quantity in lines:
            row = base.grid(service["name"], root=table)
            for label, expected in (("Количество продажи", quantity), ("Цена", 1200), ("Итого", 1200 * quantity)):
                cell = base.grid_cell(row, columns.index(label), return_value=True)
                case.check(f"{service['name']} · {label}", Decimal(expected), parse_amount(cell))
