"""Dona va KG qatorlariga bitta foizli chegirma. Abgular 1686–1691."""
import re

import allure
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.flows.mixed_units import check_line, open_saved, save_draft
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, reopen_order_goods, select_client_product, select_order_product,
)
from utils.base_pages.auto_base_page import AutoBasePage


def run_apply_all(case, catalog):
    """1. Birinchi qatorga −17%. 2. Tarqatishni rad etish. 3. Tasdiqlash va saqlash."""
    page, base = case.page, AutoBasePage(case.page)
    piece_type = catalog["mixed_prices"]["piece"]["name"]
    order_id = existing_order(case)
    if not order_id:
        open_new_order(page)
        with allure.step("1 dona va 2,5 kg qo‘shib, faqat dona qatoriga 17% chegirma tanlash"):
            piece = select_client_product(page, case.client, case.bonus_product, piece_type)
            base.input(locator=piece.locator("[data-smt-col-key=quantity] input"), value="1", press_tab=True)
            kg = select_order_product(page, case.product, case.price_type, index=1)
            base.input(locator=kg.locator("[data-smt-col-key=quantity] input"), value="2.5", press_tab=True)
            base.ui_select(label="Скидка/наценка", value="-17")
            percent = "[data-smt-col-key=margin] input"
            expect(piece.locator(percent)).to_have_value("-17")
            expect(kg.locator(percent)).to_have_value("")
            total = page.locator("article:visible").filter(has_text="ИТОГО")
            expect(total).to_contain_text(re.compile(r"ИТОГО:\s*3\s*745\s*$"))
        with allure.step("Нет — KG chegirmasi bo‘sh va jami 3 745 so‘m qolishi"):
            base.click(name="Применить ко всем ?", exact=True, root=piece)
            base.confirm_biruni("Применить ко всем ?", button_name="Нет")
            expect(kg.locator(percent)).to_have_value("")
            expect(total).to_contain_text(re.compile(r"ИТОГО:\s*3\s*745\s*$"))
        with allure.step("Да — har ikkala qatorga 17% qo‘llash va qoralamani saqlash"):
            base.click(name="Применить ко всем ?", exact=True, root=piece)
            base.confirm_biruni("Применить ко всем ?")
            expect(kg.locator(percent)).to_have_value("-17")
            order_id = save_draft(case, 3320)
    case.remember_order(order_id)
    case.workflow["apply_all_order"] = {"id": order_id, "reference": case.reference}
    case.checkpoint()


def run_check_saved_discount(case, catalog):
    """1. Har bir saqlangan qatorni o‘qish. 2. Tahrirda ikkala foizni tekshirish."""
    base = open_saved(case, case.workflow["apply_all_order"])
    base.form_view(label="Сумма заказа", expect_value="3320", remove_spaces=True)
    check_line(case, case.bonus_product, catalog["mixed_prices"]["piece"]["name"],
               quantity=1, price=1500, discount=-255, net=1245)
    check_line(case, case.product, case.price_type, quantity="2.5", price=1000, discount=-425, net=2075)
    reopen_order_goods(case.page)
    percentages = case.page.locator(".smt-data-row:visible [data-smt-col-key=margin] input:visible")
    expect(percentages).to_have_count(2)
    for field in percentages.all():
        expect(field).to_have_value("-17")
