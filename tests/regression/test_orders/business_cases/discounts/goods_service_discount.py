"""Tovar va xizmatga buyurtma darajasidagi 17% chegirma. Abgular 1376–1378."""
import allure
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.discounts import save_discount_draft
from tests.regression.test_orders.helpers.flows.mixed_units import open_saved, start_goods
from tests.regression.test_orders.helpers.flows.order import existing_order, open_order_summary, reopen_order_goods
from tests.regression.test_orders.helpers.flows.order_services import add_order_services
from utils.base_pages.auto_base_page import AutoBasePage


def run_mixed_discount(case):
    """1. Tovar va xizmat. 2. Umumiy 17% chegirma. 3. Buyurtmani saqlash."""
    base = AutoBasePage(case.page)
    oid = existing_order(case)
    if not oid:
        with allure.step("2 dona tovar va 1 dona xizmatni qo‘shish"):
            row = start_goods(case)
            base.input(locator=row.locator("[data-smt-col-key=quantity] input"), value="2", press_tab=True)
            add_order_services(case.page, case.price_type, [(case.workflow["services"][0], 1)])
        open_order_summary(case.page, expected_total="4200")
        with allure.step("Butun buyurtmaga 17% chegirma tanlash va 3 486 so‘mlik qoralamani saqlash"):
            base.ui_select(label="Скидка/наценка к заказу", value="-17")
            save_discount_draft(case, 3486, payment_type="Перечисление")
        oid = case.orders[-1]
    case.remember_order(oid)
    case.workflow["discount_order"] = {"id": oid, "reference": case.reference}
    case.checkpoint()


def run_reopen_mixed_discount(case):
    """1. Saqlangan chegirma va jami. 2. Tahrirda tarkib. 3. Yakuniy foiz va summa."""
    base = open_saved(case, case.workflow["discount_order"])
    base.form_view(label="Сумма заказа", expect_value="3486", remove_spaces=True)
    base.form_view(label="Сумма скидки/наценки на заказ", expect_value="-714", remove_spaces=True)
    reopen_order_goods(case.page)
    table = case.page.locator("smt-table:visible").first
    with allure.step("Tahrirga qayta kirib tovar va xizmat miqdorlarini tekshirish"):
        base.b_input(placeholder="Выберите...", root=table, expect_value=case.product)
        base.input(label="Кол-во", expect_value="2")
        base.tab(name="Услуга")
        base.b_input(placeholder="Выберите...", root=table, expect_value=case.workflow["services"][0]["name"])
        expect(table.locator(".smt-data-row").first.locator("[data-smt-col-key=quantity] input")).to_have_value("1")
    open_order_summary(case.page, expected_total="3486")
    base.ui_select(label="Скидка/наценка к заказу", expect_value="-17")
