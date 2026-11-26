"""KG qatori: abgular 1537–1542, saqlangan sotuv miqdori va summali chegirma."""
from decimal import Decimal

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.discounts import parse_amount, set_line_discount_amount
from tests.regression.test_orders.helpers.flows.mixed_units import check_line, open_saved, save_draft, start_goods
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_order_summary, product_loaded, reopen_order_goods, save_edited_order,
)
from utils.base_pages.auto_base_page import AutoBasePage


def run_fractional_draft(case):
    order_id = existing_order(case)
    if not order_id:
        with product_loaded(case.page, case.baseline["product_id"], case.baseline["price_type_id_uzb"]):
            row = start_goods(case)
        AutoBasePage(case.page).input(locator=row.locator("[data-smt-col-key=quantity] input"),
                                      value="1.25", press_tab=True)
        set_line_discount_amount(case, row, -100)
        order_id = save_draft(case, 1125)
    case.remember_order(order_id)
    order = {"id": order_id, "reference": case.reference}
    case.workflow["fractional_order"] = order
    case.checkpoint()
    base = open_saved(case, order)
    base.form_view(label="Сумма заказа", expect_value="1125", remove_spaces=True)
    check_line(case, case.product, case.price_type, quantity="1.25", price=1000, discount=-125, net=1125)


def run_rescale(case):
    order = case.workflow["fractional_order"]
    base = open_saved(case, order)
    saved = parse_amount(base.form_view(label="Сумма заказа", return_value=True))
    if saved != 2250:
        case.check("Tahrirlashdan oldingi summa", Decimal(1125), saved)
        reopen_order_goods(case.page)
        base.input(label="Кол-во", expect_value="1.25")
        base.input(label="Скидка/наценка", expect_value="-100")
        base.input(label="Кол-во", value="2.5", press_tab=True)
        open_order_summary(case.page, expected_total="2250")
        if is_retry():
            allow_absent_ui_write("anor/mdeal/order/order+edit$save", identity={"deal_id": order["id"]})
        save_edited_order(case.page, order["id"], order["reference"])
    open_saved(case, order)
    base.form_view(label="Сумма заказа", expect_value="2250", remove_spaces=True)
    check_line(case, case.product, case.price_type, quantity="2.5", price=1000, discount=-250, net=2250)
    reopen_order_goods(case.page)
    base.input(label="Кол-во", expect_value="2.5")
    base.input(label="Скидка/наценка", expect_value="-100")
