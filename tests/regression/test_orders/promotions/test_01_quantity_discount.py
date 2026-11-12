"""ORD-BIZ-03: to'g'ri miqdor chegirmasi, saqlangan qiymat va tanlov."""
from decimal import Decimal
import re
import allure
import pytest
from playwright.sync_api import expect
from tests.regression.test_orders.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference, promotion_card, reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Order biznes flowlari"), allure.story("Miqdor chegirmasi")]


def run_quantity_discount(case):
    """1. Setup klienti uchun 10 dona mahsulotli order ochish.
    2. Faqat 10% chegirmani tanlab 70 000 − 7 000 = 63 000 ni tekshirish.
    3. Draftni saqlash, TTN orqali aynan shu orderni topish va ID olish.
    4. View va qayta ochilgan editda summa, miqdor va aksiya tanlovini tekshirish.
    """
    page, base = case.page, AutoBasePage(case.page)
    gross = Decimal("10") * Decimal(case.promotions["unit_price"])
    discount = gross * Decimal("0.10")
    expected = format((gross - discount).normalize(), "f")
    order_id = existing_order(case)
    if not order_id:
        require_available(case, 10, bonus_quantity=0)
        open_new_order(page)
        with allure.step("1 - Setup klienti, xona va shtatni tekshirib mahsulotga o'tish"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            base.text("Название", "Кол-во")
        with allure.step("2 - Setup mahsulotidan 10 dona, narxi 7 000 so'm"):
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="10", press_tab=True)
            base.tab(name=re.compile(r"^Акции"))
            card = promotion_card(page, case.promotions["discount"]["name"])
            base.checkbox(locator=card.get_by_role("switch"), expect_checked=False)
            base.checkbox(locator=card.get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
        with allure.step("3 - Yakunda chegirma 7 000 va to'lov 63 000 bo'lishi"):
            base.click(name="Далее", exact=True)
            base.input(label="Сумма скидки/наценки", expect_value=format((-discount).normalize(), "f"))
            case.check("Order chegirmasi (so'm)", format((-discount).normalize(), "f"), re.sub(r"\s+", "", base.input(label="Сумма скидки/наценки", return_value=True)))
            base.input(label="ИТОГО", expect_value=expected)
            case.check("Saqlashdan oldingi order jami (so'm)", expected, re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    with allure.step("4 - Saqlangan ID, klient, valyuta va order summasi"):
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Валюта", expect_value="Узбекский сум")
        base.form_view(label="Сумма заказа", expect_value=expected, remove_spaces=True)
        case.check("Saqlangan order jami (so'm)", expected, base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        paid_grid = page.locator("smt-table:visible").last
        expect(paid_grid.locator(".smt-data-row")).to_have_count(1)
        paid_row = base.grid(case.product, root=paid_grid)
        paid_labels = [text.strip() for text in paid_grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество заказа", r"10"), ("Цена", r"7\s*000"), ("Итого", r"63\s*000")):
            expect(base.grid_cell(paid_row, paid_labels.index(label))).to_have_text(re.compile(r"^\s*" + value + r"\s*$"))
            expected_cells = {"Количество заказа": ("Mahsulot miqdori (dona)", "10"), "Цена": ("Mahsulot narxi (so'm)", "7000"), "Итого": ("Chegirmadan keyingi mahsulot summasi (so'm)", "63000")}
            caption, expected_cell = expected_cells[label]
            case.check(caption, expected_cell, base.grid_cell(paid_row, paid_labels.index(label), return_value=True, remove_spaces=True))
        # Bonus yo‘q bo‘lsa viewda bonus tabining o‘zi ko‘rsatilmaydi.
        expect(page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)
        case.check("Faqat chegirmali orderda bonus bo'limi soni", 0, page.get_by_role("tab", name="Акция", exact=True).count())
    reopen_order_goods(page)
    with allure.step("5 - Qayta ochilganda 10 dona va tanlangan chegirma saqlanadi"):
        base.input(label="Кол-во", expect_value="10")
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch"), expect_checked=True)
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
        base.click(name="Далее", exact=True)
        base.input(label="ИТОГО", expect_value=expected)
        case.check("Qayta ochilgan order jami (so'm)", expected, re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))


@allure.title("OB-01: 10 dona mahsulotga 10% chegirma")
def test_quantity_discount(promoted_order):
    run_quantity_discount(promoted_order)
