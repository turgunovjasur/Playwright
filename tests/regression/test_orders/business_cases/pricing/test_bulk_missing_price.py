"""Ikki narx turi xaritasi va narxi yo‘q KG qatori. Abgular 1543–1547."""
from playwright.sync_api import expect

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.flows.mixed_units import check_mixed_rows, open_saved, select_saved_order
from tests.regression.test_orders.helpers.flows.order import reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage


def run_change_price_types(case, catalog):
    page, base = case.page, AutoBasePage(case.page)
    order = case.workflow["mixed_order"]
    old, target = (catalog["mixed_prices"][k]["name"] for k in ("piece", "target"))
    open_saved(case, order)
    piece = base.grid(case.bonus_product, root=page.locator("smt-table:visible").last)
    already_applied = is_retry() and piece.get_by_text(target, exact=True).is_visible()
    if not already_applied:
        check_mixed_rows(case, old)
        select_saved_order(case, order, "Заказы")
        dropdown = page.get_by_role("button", name="Редактировать", exact=True).and_(page.locator("[aria-haspopup]"))
        base.click(locator=dropdown)
        base.click(role="menuitem", name="Изменить тип цены", exact=True)
        base.expect_page(url="change_price_type")
        expect(page.get_by_role("alert")).to_contain_text("тип цены продукции не будет изменен")
        for old_type in (case.price_type, old):
            row = base.grid(old_type)
            expect(row.get_by_role("radio", name="Все ТМЦ", exact=True)).to_be_checked()
            base.b_input(placeholder="Выберите...", root=row, value=target)
        if is_retry():
            allow_absent_ui_write("anor/mdeal/order/change_price_type:save", identity={"deal_id": order["id"]})
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Изменить типы цен?")
        base.expect_page(url="order_list")
    open_saved(case, order)
    check_mixed_rows(case, target)
    reopen_order_goods(page)
    for name, price_type in ((case.product, case.price_type), (case.bonus_product, target)):
        row = base.grid(price_type, "Основной склад")
        base.b_input(placeholder="Выберите...", root=row, expect_value=name)
