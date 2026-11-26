"""Faqat xizmatli qoralamani jo‘natish va qayta qoralamaga o‘tkazish."""
from decimal import Decimal

import allure

from tests.regression.test_orders.helpers.flows.mixed_units import open_saved, save_draft
from tests.regression.test_orders.helpers.flows.order import select_order_client, existing_order, open_new_order
from tests.regression.test_orders.helpers.flows.order_services import add_order_services, check_saved_services
from tests.regression.test_orders.helpers.flows.settlement import change_order_status
from tests.regression.test_orders.helpers.flows.stock import read_stock
from utils.base_pages.auto_base_page import AutoBasePage


def check_service_order(case, status):
    order = case.workflow["service_order"]
    with allure.step(f"{status} holatidagi buyurtmaning ID, klient, TTN va summasi"):
        base = open_saved(case, order, status=status)
        base.form_view(label="Сумма заказа", expect_value="3600", remove_spaces=True)
    check_saved_services(case, service_lines(case))
    with allure.step("Nazorat mahsulotining fizik, rezerv va erkin qoldig‘ini solishtirish"):
        before = {k: Decimal(v) for k, v in case.workflow["control_stock"].items()}
        case.check("Nazorat tovarining qoldig‘i", before, read_stock(case, "Основной склад"))


def service_lines(case):
    first, second = case.workflow["services"]
    return [(first, 1), (second, 2)]


def run_service_draft(case):
    """1. Klient. 2. Faqat ikkita xizmat. 3. Qoralamani qayta ochish va qoldiqni tekshirish."""
    oid = existing_order(case)
    if not oid:
        open_new_order(case.page)
        base = AutoBasePage(case.page)
        with allure.step("Guruh klientini tanlab mahsulotlar bosqichiga o‘tish"):
            select_order_client(case.page, case.client, room=case.room, staff=case.staff)
            base.click(name="Далее", exact=True)
        add_order_services(case.page, case.price_type, service_lines(case))
        oid = save_draft(case, 3600)
    case.remember_order(oid)
    case.workflow["service_order"] = {"id": oid, "reference": case.reference}
    case.checkpoint()
    check_service_order(case, "Черновик")


def run_service_status(case, current, target):
    """1. Shu buyurtma statusini o‘zgartirish. 2. Xizmatlar, summa va qoldiqni qayta o‘qish."""
    change_order_status(case.page, case.workflow["service_order"]["id"], current=current, target=target)
    check_service_order(case, target)
