"""Ro‘yxatdan narxni almashtirish va tahrirda aksiyani qayta hisoblash."""
import re

import allure
from playwright.sync_api import expect

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.helpers.flows.mixed_units import (
    check_line, open_saved, save_draft, select_saved_order, start_goods,
)
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_order_summary, promotion_card, reopen_order_goods, save_edited_order,
)
from utils.base_pages.auto_base_page import AutoBasePage


def _saved_bonus(case):
    base = AutoBasePage(case.page)
    base.tab(name="Акция")
    table = case.page.locator("smt-table:visible").last
    expect(table.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=table)
    labels = [s.strip() for s in table.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, value in (("Количество продажи", "1"), ("Цена", "0"), ("Итого", "0")):
        expect(base.grid_cell(row, labels.index(label))).to_have_text(value)


def run_bonus_draft(case, key):
    """1. Beshta tovar va 17% chegirma. 2. Bitta bonusni tanlash. 3. Saqlangan qoralama."""
    base = AutoBasePage(case.page)
    oid = existing_order(case)
    if not oid:
        row = start_goods(case)
        with allure.step("5 × 1 000 so‘mlik qatorga 17% chegirma berish"):
            base.input(label="Кол-во", value="5", press_tab=True)
            base.ui_select(label="Скидка/наценка", value="-17")
            expect(row.locator("[data-smt-col-key=margin] input")).to_have_value("-17")
        with allure.step("Eski narx turiga tegishli aksiyadan bir dona bonusni tanlash"):
            base.tab(name=re.compile(r"^Акции"))
            card = promotion_card(case.page, case.promotions["bonus"]["name"])
            base.grid(case.bonus_product, "1", root=card)
            base.checkbox(locator=card.get_by_role("switch"), checked=True)
        oid = save_draft(case, 4150)
    case.remember_order(oid)
    order = {"id": oid, "reference": case.reference}
    case.workflow[key] = order
    case.checkpoint()
    base = open_saved(case, order)
    base.form_view(label="Сумма заказа", expect_value="4150", remove_spaces=True)
    check_line(case, case.product, case.price_type, quantity=5, price=1000, discount=-850, net=4150)
    _saved_bonus(case)


def _choose_target_price(case, order, target):
    page, base = case.page, AutoBasePage(case.page)
    select_saved_order(case, order, "Заказы")
    with allure.step("Ro‘yxatdagi «Изменить тип цены» formasini ochish"):
        menu = page.get_by_role("button", name="Редактировать", exact=True).and_(page.locator("[aria-haspopup]"))
        base.click(locator=menu)
        base.click(role="menuitem", name="Изменить тип цены", exact=True)
        base.expect_page(url="change_price_type")
    row = base.grid(case.price_type)
    expect(row.get_by_role("radio", name="Все ТМЦ", exact=True)).to_be_checked()
    base.b_input(placeholder="Выберите...", root=row, value=target)
    base.click(name="Сохранить", exact=True)


def run_list_price_change(case, key):
    """1. Almashtirishni rad etish. 2. Yangi narxni tasdiqlash. 3. Eski bonusni tekshirish."""
    page, order = case.page, case.workflow[key]
    target = case.workflow["target_price"]
    base = open_saved(case, order)
    base.tab(name="Товар")
    paid = base.grid(case.product, root=page.locator("smt-table:visible").last)
    if not (is_retry() and paid.get_by_text(target, exact=True).is_visible()):
        with allure.step("Narxni almashtirishni rad etganda eski summa va bonus saqlanadi"):
            _choose_target_price(case, order, target)
            base.confirm_biruni("Изменить типы цен?", button_name="Нет")
            base.click(name="Закрыть", exact=True)
            base.expect_page(heading="Заказы", url="order_list")
            open_saved(case, order)
            base.form_view(label="Сумма заказа", expect_value="4150", remove_spaces=True)
            check_line(case, case.product, case.price_type, quantity=5, price=1000, discount=-850, net=4150)
            _saved_bonus(case)
        with allure.step("Barcha TMZ uchun yangi narx turini tasdiqlash"):
            _choose_target_price(case, order, target)
            if is_retry():
                allow_absent_ui_write("anor/mdeal/order/change_price_type:save", identity={"deal_id": order["id"]})
            base.confirm_biruni("Изменить типы цен?")
            base.expect_page(heading="Заказы", url="order_list")
    with allure.step("Tahrirga kirmasdan qoralamada yangi summa va avvalgi bonusni tekshirish"):
        open_saved(case, order)
        base.form_view(label="Сумма заказа", expect_value="6225", remove_spaces=True)
        check_line(case, case.product, target, quantity=5, price=1500, discount=-1275, net=6225)
        _saved_bonus(case)


def run_recalculation(case, *, trigger):
    """1. Saqlangan bonus. 2. Tanlangan qayta hisoblash amali. 3. Qayta ochib bonus yo‘qligini tekshirish."""
    page, order = case.page, case.workflow[trigger]
    base = open_saved(case, order)
    target = case.workflow["target_price"]
    if trigger == "picker":
        quantity, discount, total = 5, -1275, 6225
    elif trigger == "quantity":
        quantity, discount, total = 6, -1530, 7470
    else:
        raise ValueError(trigger)
    bonus_tab = page.get_by_role("tab", name="Акция", exact=True)
    base.tab(name="Товар")
    base.grid(case.product, target, root=page.locator("smt-table:visible").last)
    if not (is_retry() and bonus_tab.count() == 0):
        _saved_bonus(case)
        reopen_order_goods(page)
        base.input(label="Кол-во", expect_value="5")
        if trigger == "picker":
            with allure.step("«Подбор»ni ochish"):
                base.click(name="Подбор", exact=True)
                heading = page.get_by_role("heading", name="Заказ (подбор)", exact=True)
                expect(heading).to_be_visible()
            with allure.step("Tanlovni o‘zgartirmasdan «Подбор»dan chiqish"):
                picker = page.locator("main:visible").filter(has=heading)
                base.click(name="Закрыть", exact=True, root=picker)
                expect(heading).to_be_hidden()
        else:
            with allure.step("«Подбор»ni ochmasdan miqdorni 5 dan 6 donaga o‘zgartirish"):
                base.input(label="Кол-во", value=str(quantity), press_tab=True)
        with allure.step("Saqlashdan oldin «Акции» tabidagi bonus soni yo‘qolganini tekshirish"):
            expect(page.get_by_role("tab", name="Акции", exact=True)).to_be_visible()
        open_order_summary(page, expected_total=total)
        if is_retry():
            allow_absent_ui_write("anor/mdeal/order/order+edit$save", identity={"deal_id": order["id"]})
        save_edited_order(page, order["id"], order["reference"])
    with allure.step("Qayta ochilgan qoralamada tovar, yangi narx, jami va bonus olib tashlanganini tekshirish"):
        open_saved(case, order)
        base.form_view(label="Сумма заказа", expect_value=str(total), remove_spaces=True)
        check_line(case, case.product, target, quantity=quantity, price=1500, discount=discount, net=total)
        expect(bonus_tab).to_have_count(0)
