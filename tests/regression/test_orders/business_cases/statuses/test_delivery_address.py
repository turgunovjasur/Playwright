"""Buyurtmada klientning yetkazish manzili. Abgular 1570–1578."""
import allure

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.flows.mixed_units import open_saved, start_goods
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_order_summary, reopen_order_goods, save_edited_order, save_order_by_reference,
)
from utils.base_pages.auto_base_page import AutoBasePage

FIELD = "Адрес доставки клиента"


def _check_fields(base, address):
    short = address["address_short"] if address else ""
    full = address["address_full"] if address else ""
    base.b_input(label=FIELD, expect_value=short)
    base.input(label="Ориентир", expect_value=short)
    base.input(label="Адрес", expect_value=full)


def _open_summary(case, order):
    base = open_saved(case, order)
    base.form_view(label="Сумма заказа", expect_value="1000", remove_spaces=True)
    reopen_order_goods(case.page)
    open_order_summary(case.page, expected_total="1000")
    return base


def run_save_first_address(case):
    """1. Bitta mahsulotli orderga A manzilini tanlash. 2. Saqlab uchala maydonni qayta o‘qish."""
    page, base = case.page, AutoBasePage(case.page)
    first = case.workflow["client"]["addresses"][0]
    identity = existing_order(case)
    if not identity:
        start_goods(case)
        base.input(label="Кол-во", value="1", press_tab=True)
        open_order_summary(page, expected_total="1000")
        with allure.step("Klientning A manzilini tanlash va 1 000 so‘mlik qoralamani saqlash"):
            base.b_input(label=FIELD, value=first["address_short"], lookup_route=":person_addresses")
            _check_fields(base, first)
            base.b_input(label="Тип оплаты", value="Перечисление")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
            identity = save_order_by_reference(page, case.reference)
    case.remember_order(identity)
    case.workflow["address_order"] = order = {"id": identity, "reference": case.reference}
    case.checkpoint()
    _check_fields(_open_summary(case, order), first)


def run_change_address(case, *, clear):
    """1. Oldingi manzilni tekshirish. 2. Almashtirish yoki tozalash. 3. Xuddi shu buyurtmani qayta o‘qish."""
    order = case.workflow["address_order"]
    first, second = case.workflow["client"]["addresses"]
    previous, target = (second, None) if clear else (first, second)
    base = _open_summary(case, order)
    current = base.b_input(label=FIELD, return_value=True)
    if not (is_retry() and current == (target["address_short"] if target else "")):
        _check_fields(base, previous)
        with allure.step("Yetkazish manzilini tozalash" if clear else "A manzilini B ga almashtirish"):
            if clear:
                base.b_input(label=FIELD, clear=True)
            else:
                base.b_input(label=FIELD, value=target["address_short"], lookup_route=":person_addresses")
                _check_fields(base, target)
            if is_retry():
                allow_absent_ui_write("anor/mdeal/order/order+edit$save", identity={"deal_id": order["id"]})
            save_edited_order(case.page, order["id"], order["reference"])
    with allure.step("Saqlangan tanlov, mo‘ljal va to‘liq manzilni qayta ochib tekshirish"):
        _check_fields(_open_summary(case, order), target)
