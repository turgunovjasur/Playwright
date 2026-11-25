"""Arxivdan tiklash, bekor qilish va qoralamaga qaytarish. Abgular 1601–1617."""
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.flows.mixed_units import open_saved, select_saved_order
from tests.regression.test_orders.helpers.flows.order_status import cancel_order
from tests.regression.test_orders.helpers.flows.settlement import change_order_status, read_debts, read_settlement
from tests.regression.test_orders.helpers.flows.stock import read_stock
from utils.base_pages.auto_base_page import AutoBasePage


def check_stock(case, catalog, *, sold, reserved):
    for kind, quantity in (("goods", Decimal("2.5")), ("bonus", Decimal(1))):
        initial = catalog["opening_stock"][kind]
        physical = Decimal(initial["physical"]) - quantity * sold
        booked = Decimal(initial["booked"]) + quantity * reserved
        actual = read_stock(case, "Основной склад", product_id=catalog[kind]["id"])
        case.check(f"{catalog[kind]['name']} ombordagi qoldig‘i va rezervi",
                   {"physical": physical, "booked": booked, "available": physical - booked}, actual)


def run_forward(case, current, target):
    order = case.workflow["mixed_order"]
    change_order_status(case.page, order["id"], current=current, target=target)
    open_saved(case, order, status=target).form_view(label="Сумма заказа", expect_value="3750", remove_spaces=True)


def run_archive(case):
    run_forward(case, "Отгружен", "Архив")
    oid = case.workflow["mixed_order"]["id"]
    balances = read_settlement(case.page, case.client)
    case.check("Klientning arxivdan keyingi qarzi", Decimal(3750), balances["debt"])
    case.check("Qarz ro‘yxatida aynan shu order", {oid: Decimal(3750)},
               read_debts(case.page, case.client, settlement=balances))
    url = urlsplit(case.page.url)
    params = parse_qs(url.query)
    case.check("Qarz detalidagi klient va valyuta",
               ([str(case.workflow["client"]["person_id"])], [str(case.baseline["currency_id_uzb"])]),
               (params.get("person_id"), params.get("currency_id")))
    case.workflow["debt_detail_route"] = "anor/mdeal/order/offset/offset_detail_list?" + url.query
    case.checkpoint()


def run_restore(case, *, current, target, list_name, endpoint):
    order = case.workflow["mixed_order"]
    page, base = case.page, AutoBasePage(case.page)
    base.open_route("trade/tdeal/order/order_view?deal_id=" + order["id"], heading="Заказ / Просмотр")
    base.form_view(label="ИД заказа", expect_value=order["id"])
    base.form_view(label="Номер ТТН", expect_value=order["reference"])
    saved_status = base.form_view(label="Статус", return_value=True).strip()
    if not (is_retry() and saved_status == target):
        case.check("Tiklashdan oldingi status", current, saved_status)
        select_saved_order(case, order, list_name)
        if is_retry():
            allow_absent_ui_write(endpoint, identity={"deal_id": order["id"]})
        base.click(name="Восстановить", exact=True)
        base.confirm_biruni("Восстановить заказ?")
        base.grid(state="empty")
    open_saved(case, order, status=target).form_view(label="Сумма заказа", expect_value="3750", remove_spaces=True)


def check_no_debt(case):
    balances = read_settlement(case.page, case.client)
    case.check("Klientning qolgan qarzi", Decimal(0), balances["debt"])
    base = AutoBasePage(case.page)
    base.open_route(case.workflow["debt_detail_route"], heading="Детали задолженности")
    base.grid(state="empty")
    expect(case.page.locator("main:visible .smt-data-row")).to_have_count(0)


def run_cancel(case, catalog):
    order = case.workflow["mixed_order"]
    cancel_order(case.page, order_id=order["id"], client=case.client, amount="3750")
    open_saved(case, order, status="Отменен")
    check_no_debt(case)
    check_stock(case, catalog, sold=0, reserved=0)
