"""SCN-018. Ikki to‘lov sanasida Cancel, Save va qayta ochish."""
import re

import allure
from playwright.sync_api import expect

from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.helpers.retry.checkpoints import reuse, verified
from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.discounts import parse_amount
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, open_order_summary, reopen_order_goods,
    save_edited_order, save_order_by_reference, select_order_product,
)
from utils.base_pages.auto_base_page import AutoBasePage
from utils.date_utils import format_date

DUE_DATE = "Дата оплаты по консигнации"
INSTALLMENT = "Сумма консигнации"
BASELINE = (1000, 1000)
EDITED = (750, 1250)


def _view(case, order_id, dates):
    base = AutoBasePage(case.page)
    base.form_view(label="ИД заказа", expect_value=order_id)
    base.form_view(label="Номер ТТН", expect_value=case.reference)
    base.form_view(label="Клиент", expect_value=case.client)
    base.form_view(label="Сумма заказа", expect_value="2000", remove_spaces=True)
    base.tab("Консигнация")
    grid = case.page.locator("main:visible smt-table:visible").filter(
        has=case.page.get_by_text("Дата", exact=True)).filter(has=case.page.get_by_text("Сумма", exact=True))
    expect(grid).to_have_count(1)
    expect(grid.locator(".smt-data-row")).to_have_count(2)
    amounts = []
    for day in dates:
        row = grid.locator(".smt-data-row").filter(has=case.page.get_by_text(day, exact=True))
        expect(row).to_have_count(1)
        amounts.append(parse_amount(base.grid_cell(row, 1, return_value=True)))
    return tuple(amounts)


def _check_editor(case, dates, amounts):
    base = AutoBasePage(case.page)
    for index, (day, amount) in enumerate(zip(dates, amounts, strict=True)):
        # In A2 auto_fill=True is a read-only assertion on the persisted date.
        base.date_picker(DUE_DATE, day, index=index, auto_fill=True)
        actual = parse_amount(base.input(label=INSTALLMENT, index=index, return_value=True))
        case.check(f"{day} konsignatsiya summasi", amount, actual)


def _open_editor(case, dates, amounts):
    reopen_order_goods(case.page)
    open_order_summary(case.page, expected_total=2000)
    _check_editor(case, dates, amounts)


def _set_amounts(case, dates, amounts):
    base = AutoBasePage(case.page)
    # First decrease the larger payment so the running total never exceeds the order.
    indexes = (0, 1) if amounts == EDITED else (1, 0)
    for index in indexes:
        base.input(label=INSTALLMENT, index=index, value=str(amounts[index]), press_tab=True)
    _check_editor(case, dates, amounts)


def _save_edit(case, order_id, operation):
    if is_retry():
        allow_absent_ui_write(
            "anor/mdeal/order/order+edit$save", identity={"deal_id": order_id, "delivery_number": case.reference},
            operation=operation + ":" + order_id,
        )
    save_edited_order(case.page, order_id, case.reference)


def _create_order(case, dates):
    page = case.page
    base = AutoBasePage(page)
    require_available(case, 2)
    open_new_order(page)
    with allure.step("Xona, klient, loyiha va shartnomani tanlash"):
        base.b_input(label="Рабочая зона", expect_value=case.room)
        base.b_input(label="Штат", expect_value=case.staff)
        base.b_input(label="Клиент", value=case.client, clear=True)
        base.b_input(label="Проект", value=case.workflow["consignment_project"], clear=True)
        base.b_input(label="Договор", value=case.workflow["consignment_contract"], clear=True)
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")
    with allure.step("2 dona mahsulotni 1 000 so‘mdan tanlash"):
        select_order_product(page, case.product, case.price_type)
        base.input(label="Кол-во", value="2", press_tab=True)
    open_order_summary(page, expected_total=2000)
    with allure.step("Ikki kelajak sanasi uchun 1 000 so‘mdan muddat belgilash"):
        base.b_input(label="Тип оплаты", value="Перечисление", clear=True)
        base.input(label="Номер товарно-транспортной накладной", value=case.reference)
        base.ui_select(label="Статус", value="Черновик")
        for index, day in enumerate(dates):
            if index:
                base.click(name="Создать", exact=True)
                base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:%2[Bb]|\+)add"))
            base.date_picker(DUE_DATE, day, index=index)
            base.input(label=INSTALLMENT, index=index, value="1000", press_tab=True)
        _check_editor(case, dates, BASELINE)
    return save_order_by_reference(page, case.reference)


def run_consignment_dates(case):
    """1. Ikki muddatga qoralama yaratish. 2. Cancelni tekshirish.
    3. Summalarni saqlash va qayta ochish. 4. Dastlabki taqsimotni tiklash.
    """
    dates = case.workflow.setdefault("consignment_dates", [format_date(days=1), format_date(days=2)])
    case.checkpoint()
    order_id = existing_order(case) or _create_order(case, dates)
    case.remember_order(order_id)
    case.workflow["consignment_order"] = {"id": order_id, "reference": case.reference}
    case.checkpoint()
    base = AutoBasePage(case.page)
    with allure.step("1 - Saqlangan ikki muddat va summalarni ko‘rish"):
        actual = _view(case, order_id, dates)
    if not reuse("cancel_kept_dates"):
        case.check("Dastlabki konsignatsiya", BASELINE, actual)
        _open_editor(case, dates, BASELINE)
        _set_amounts(case, dates, EDITED)
        with allure.step("2 - 750 va 1 250 so‘mlik o‘zgarishni bekor qilish"):
            base.click(name="Go back", exact=True)
            base.confirm_biruni(re.compile("Все не сохраненные данные.*Продолжить", re.I | re.S))
            base.expect_page(heading="Заказ / Просмотр", url="order_view")
            actual = _view(case, order_id, dates)
            case.check("Bekor qilingandan keyingi summalar", BASELINE, actual)
        verified("cancel_kept_dates")
    restored_already = False
    if not reuse("saved_edited_dates"):
        if actual == BASELINE:
            _open_editor(case, dates, BASELINE)
            _set_amounts(case, dates, EDITED)
            _save_edit(case, order_id, "save_edit")
        case.check("Saqlangan 750 va 1 250", EDITED, _view(case, order_id, dates))
        _open_editor(case, dates, EDITED)
        verified("saved_edited_dates")
    elif actual == EDITED:
        _open_editor(case, dates, EDITED)
    else:
        case.check("Qayta ishga tushirilgan orderda tiklangan taqsimot", BASELINE, actual)
        restored_already = True
    if not restored_already:
        with allure.step("4 - Dastlabki 1 000 va 1 000 so‘m taqsimotni tiklash"):
            _set_amounts(case, dates, BASELINE)
            _save_edit(case, order_id, "restore_edit")
    case.check("Yakuniy qoralama muddatlari", BASELINE, _view(case, order_id, dates))
    _open_editor(case, dates, BASELINE)
