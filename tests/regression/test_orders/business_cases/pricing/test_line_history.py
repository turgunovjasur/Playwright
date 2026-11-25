"""Abgular 1555–1556. Saqlangan KG qatorining tahrir tarixi."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.discounts import parse_amount
from tests.regression.test_orders.helpers.flows.mixed_units import open_saved


def run_line_history(case):
    """1. Aynan guruh orderini ochish. 2. Yangilangan KG qatorining oldingi va yangi qiymatlarini solishtirish."""
    page = case.page
    with allure.step("Guruh buyurtmasini ochish va o‘zgarishlar tarixiga o‘tish"):
        base = open_saved(case, case.workflow["fractional_order"])
        history = "История изменений"
        if page.get_by_role("tab", name=history, exact=True).is_visible():
            base.tab(name=history)
        else:
            base.click(role="tab", name="Ещё", exact=True)
            base.click(role="menuitem", name=history, exact=True)
        base.tab(name="ТМЦ")
    with allure.step("Aynan KG mahsulotining yangilanish tafsilotlarini ochish"):
        rows = page.locator(".smt-data-row:visible").filter(has=page.get_by_text(case.product, exact=True))
        updated = rows.filter(has=page.get_by_text("Обновлен", exact=True))
        expect(updated).to_have_count(1)
        base.click(locator=updated)
        base.click(name="Детали истории изменений", exact=True)
        base.expect_page(heading="История изменений заказа", root=page.locator("body"))  # navigation: same-url - read-only history dialog
        detail = page.locator("main:visible").last
        base.tab(name="ТМЦ", root=detail)
    with allure.step("Miqdor, chegirma va qator summasining eski va yangi qiymatlarini tekshirish"):
        grid = detail.locator("smt-data-table:visible")
        for field, old, new in (
            ("Количество заказа", "1.25", "2.5"), ("Количество продажи", "1.25", "2.5"),
            ("Сумма переоценки", "-125", "-250"), ("Общая сумма", "1125", "2250"),
        ):
            row = grid.locator(".smt-data-row").filter(has=page.get_by_text(field, exact=True))
            expect(row).to_have_count(1)
            base.grid_cell(row, 0, expect_value=field)
            for index, value in ((1, old), (2, new)):
                actual = base.grid_cell(row, index, return_value=True)
                case.check(field + (" · eski" if index == 1 else " · yangi"), Decimal(value), parse_amount(actual))
