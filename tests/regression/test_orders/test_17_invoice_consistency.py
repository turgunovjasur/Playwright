"""Saqlangan order va standart HTML nakladnoy bir xil miqdor/summani ko'rsatadi."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import open_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("To'lov, qaytarish va report")]


def run_invoice_consistency(page, order_case):
    """1. O'z mahsulotidan ikki dona Draft order yaratish.
    2. Saqlangan view'da klient, valyuta, miqdor va summani tekshirish.
    3. Shu orderning Накладная № 4 (2012) HTML reportini ochish.
    4. Report identifikatori, mahsulot qatori va footer summasini solishtirish.

    QQS siyosati va Excel fayli bu testcase scope'iga kirmaydi.
    """
    base = AutoBasePage(page)
    quantity = Decimal("2")
    unit_price = Decimal("100")
    total = quantity * unit_price

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Ikki dona own mahsulotning 200 USD orderini tayyorlash"):
        goods = page.locator('b-pg-grid[name="goods_items"]')
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value=str(unit_price), root=goods)
        base.input(ng_model="item.quantity", value=str(quantity), root=goods, press_tab=True)
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(label="Номер ТТН", value=order_case.reference)
        base.ui_select(label="Статус", value="Черновик")
        base.form_view(label="ИТОГО", expect_value=str(total), remove_spaces=True)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)

    with allure.step("2 - Saqlangan orderning identifikatori va summasi"):
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=order_case.client)
        base.form_view(label="Валюта", expect_value=order_case.currency)
        base.form_view(label="Сумма заказа", expect_value=str(total), remove_spaces=True)
        saved_goods = "b-grid:visible"
        saved_row = base.grid(order_case.product, order_case.warehouse, order_case.price_type, root=saved_goods)
        saved_headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(saved_headers.first).to_be_visible()
        saved_columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in saved_headers.all_text_contents()]
        expect(base.grid_cell(saved_row, saved_columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*2(?:\.0+)?\s*$"))
        expect(base.grid_cell(saved_row, saved_columns.index("Итого"))).to_have_text(re.compile(r"^\s*200(?:\.0+)?\s*$"))

    with allure.step("3 - Aynan shu orderning ro'yxat qatoriga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_controller(search=order_case.client)
        expect(page.locator("b-grid:visible").get_by_text(order_case.client, exact=True)).to_have_count(1)
        row = base.grid(order_case.client, click=True)

    with allure.step("4 - Standart nakladnoy HTML oynasini ochish"):
        base.click(name="Накладные", exact=True, root=row)
        with page.expect_popup() as popup:
            base.click(locator=page.get_by_text("Накладная № 4 (2012)", exact=True).filter(visible=True))
        report_page = popup.value
        report_base = AutoBasePage(report_page)
        report_base.expect_page(url="invoice_four:run")

    try:
        with allure.step("5 - Report headeri, mahsulot qatori va umumiy summa"):
            report_base.text(order_case.reference, order_case.client, order_case.currency, root="body")
            header = report_page.get_by_role("row").filter(has=report_page.get_by_role("cell", name="Наименование ТМЦ", exact=True))
            expect(header).to_have_count(1)
            labels = [" ".join(text.split()) for text in header.get_by_role("cell").all_text_contents()]
            required = ("Код ТМЦ", "Наименование ТМЦ", "Количество", "Цена", "Сумма")
            missing = [label for label in required if label not in labels]
            if missing:
                raise AssertionError(f"Nakladnoy ustunlari yetishmaydi: {missing}; mavjud: {labels}")

            product_row = report_page.get_by_role("row").filter(has=report_page.get_by_role("cell", name=order_case.product, exact=True))
            expect(product_row).to_have_count(1)
            cells = product_row.get_by_role("cell")
            expect(cells.nth(labels.index("Код ТМЦ"))).to_have_text(order_case.product_code)
            for label, expected in (("Количество", quantity), ("Цена", unit_price), ("Сумма", total)):
                expect(cells.nth(labels.index(label))).to_have_text(re.compile(rf"^\s*{expected}(?:\.0+)?\s*$"))
            footer = report_page.get_by_role("row").filter(has=report_page.get_by_role("cell", name="Сумма со скидкой/наценкой", exact=True))
            expect(footer).to_have_count(1)
            expect(footer.get_by_role("cell").last).to_have_text(re.compile(rf"^\s*{total}(?:\.0+)?\s*$"))
            allure.attach(report_page.screenshot(full_page=True), "Order invoice HTML", allure.attachment_type.PNG)
    finally:
        report_page.close()


@allure.title("ORD-17: Invoice va saqlangan order summalari izchilligi")
def test_17_invoice_consistency(page, order_case):
    run_invoice_consistency(page, order_case)
