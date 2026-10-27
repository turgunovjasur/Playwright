"""ORD-14: optional siklik bonus va paid/bonus rezervining qaytarilishi."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_action.flow_action.flow_action import fill_action_scope, open_action_form
from tests.smoke.test_life_cycle.flow_order.order_regression import change_order_status, open_order, read_stock, save_order
from tests.smoke.test_life_cycle.flow_order.order_summary import summary_quantity_cell
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order aksiyalari")]


def run_cyclic_promotion(page, order_case):
    """1. Own har 3 donaga 1 bonus aksiyasi. 2. 2/3/5/6 va optional qayta opt-in.

    3. Qty 6 / bonus 2 ni saqlash. 4. New/Cancel/Restore paid va bonus qoldig'i.
    """
    base = AutoBasePage(page)
    action_name = f"ORD14 {order_case.key} cyclic3 bonus1"
    start_date, end_date = base.date(), base.date(days=1)

    open_action_form(page)
    with allure.step("1 - Own optional siklik aksiyaning doirasini belgilash"):
        fill_action_scope(page, name=action_name, action_code=f"O14-{order_case.key}", room=order_case.room, price_type=order_case.price_type, start_date=start_date, end_date=end_date)
        base.ui_select(label="Тип акции", value="Кол-во")

    with allure.step("2 - Aksiya shartlari formasini ochish"):
        base.click(name="Далее", exact=True)
        base.expect_page(heading="Условия", url=re.compile(r"action(?:\+|%2[bB])add"))

    with allure.step("3 - Own mahsulotning har 3 donasi uchun 1 dona own bonus"):
        base.checkbox(label="Ассортимент", checked=False)
        base.ui_select(label="Тип условия", value="Циклично")
        base.b_input(ng_model="d['selected_rule_name_' + condition_index + rule_index]", value=order_case.product)
        base.input(ng_model="rule.main_value", value="3")
        base.input(ng_model="rule.required_count", value="1")
        base.ui_select(label="Тип бонуса", value="Кол-во")
        base.b_input(ng_model="d['selected_bonus_name_' + condition_index + bonus_index]", value=order_case.bonus_product)
        base.input(ng_model="product.value", value="1")

    with allure.step("4 - Aksiyani Active saqlash va cleanup ID sini ro'yxatga olish"):
        order_case.action_names.append(action_name)
        base.click(name="Завершить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Акции", url="action_list")
        id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="Название")
        base.grid_controller(search=action_name)
        row = base.grid(action_name, "Кол-во", "Активный")
        action_id = base.grid_cell(row, id_column, return_value=True, remove_spaces=True)
        order_case.actions.append(action_id)
        expect(base.grid_cell(row, id_column)).to_have_text(re.compile(r"^\d+$"))

    baseline = {"physical": Decimal("50"), "booked": Decimal("0"), "available": Decimal("50")}
    for code in (order_case.product_code, order_case.bonus_code):
        actual = read_stock(page, code, warehouse=order_case.warehouse)
        if actual != baseline:
            pytest.fail(f"Own {code} boshlang'ich qoldig'i: expected={baseline}, actual={actual}")

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    goods = page.locator('b-pg-grid[name="goods_items"]')
    with allure.step("5 - Own paid mahsulotning 100 USD narxini tekshirish"):
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(label="Цена", expect_value="100", root=goods)
        base.text(order_case.warehouse, order_case.price_type, root=goods)

    previous_eligible = False
    for index, (quantity, bonus_quantity) in enumerate(((2, 0), (3, 1), (5, 1), (6, 2), (2, 0), (3, 1), (6, 2))):
        eligible = quantity >= 3
        gross = Decimal(quantity) * Decimal("100")
        with allure.step(f"6.{index + 1} - Qty {quantity}: har 3 donaga 1, bepul qty {bonus_quantity}"):
            if index:
                base.click(locator="#anor279-button-prev_step")
                base.click(name="Товар", role="link", exact=True)
                expect(goods).to_be_visible()
            if previous_eligible:
                base.click(name=re.compile(r"^Акции"), role="link")
                card = page.get_by_role("heading", name=action_name, exact=True).locator("xpath=ancestor::*[.//input[@ng-model='condition.get']][1]")
                base.checkbox(ng_model="condition.get", checked=False, root=card)
                base.click(name="Товар", role="link", exact=True)
            base.input(label="Кол-во", value=str(quantity), root=goods, press_tab=True)
            base.click(locator="#anor279-button-next_step")
            base.form_view(label="ИТОГО", expect_value=str(gross), remove_spaces=True)
            base.click(locator="#anor279-button-prev_step")
            expect(goods).to_be_visible()
            base.click(name=re.compile(r"^Акции"), role="link")
            heading = page.get_by_role("heading", name=action_name, exact=True)
            if eligible:
                expect(heading).to_be_visible()
                card = heading.locator("xpath=ancestor::*[.//input[@ng-model='condition.get']][1]")
                base.checkbox(ng_model="condition.get", expect_checked=False, root=card)
                base.grid(order_case.bonus_product, "1", root=card)
                base.checkbox(ng_model="condition.get", checked=True, root=card)
            else:
                expect(heading).to_have_count(0)
            base.click(locator="#anor279-button-next_step")
            base.form_view(label="ИТОГО", expect_value=str(gross), remove_spaces=True)
            expect(summary_quantity_cell(page, "Акция")).to_have_text(re.compile(rf"^Кол-во\s*:\s*{bonus_quantity}$"))
            previous_eligible = eligible

    with allure.step("7 - Qty 6 / USD 600 / bonus 2 Draftni saqlash"):
        base.ui_select(label="Статус", value="Черновик")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(ng_model="d.delivery_number", value=order_case.reference)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)

    with allure.step("8 - Saqlangan paid qatori va 600 USD summani tekshirish"):
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="600", remove_spaces=True)
        base.form_view(label="Сумма скидки/наценки на заказ", expect_value="0", remove_spaces=True)
        grid = page.locator("b-grid:visible")
        row = base.grid(order_case.product, root=grid)
        headers = grid.locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        labels = [re.sub(r"[\s\uf000-\uf8ff]+", " ", value).strip() for value in headers.all_inner_texts()]
        for label, value in (("Количество продажи", "6"), ("Цена", "100"), ("Итого", "600")):
            expect(base.grid_cell(row, labels.index(label))).to_have_text(re.compile(rf"^\s*{re.escape(value)}\s*$"))

    with allure.step("9 - Saqlangan bonus manbasi, qty 2 va zero charge"):
        base.click(name="Акция", role="link", exact=True)
        grid = page.locator("b-grid:visible")
        row = base.grid(order_case.bonus_product, action_name, order_case.warehouse, root=grid)
        headers = grid.locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        labels = [re.sub(r"[\s\uf000-\uf8ff]+", " ", value).strip() for value in headers.all_inner_texts()]
        for label, value in (("Количество продажи", "2"), ("Цена", "0"), ("Итого", "0")):
            expect(base.grid_cell(row, labels.index(label))).to_have_text(re.compile(rf"^\s*{re.escape(value)}\s*$"))

    change_order_status(page, order_id, "Новый")
    with allure.step("10 - New paid 6 va bonus 2 ni bir marta rezerv qiladi, physical o'zgarmaydi"):
        for code, quantity in ((order_case.product_code, Decimal("6")), (order_case.bonus_code, Decimal("2"))):
            expected = {"physical": Decimal("50"), "booked": quantity, "available": Decimal("50") - quantity}
            actual = read_stock(page, code, warehouse=order_case.warehouse)
            if actual != expected:
                pytest.fail(f"New {code}: expected={expected}, actual={actual}")

    change_order_status(page, order_id, "Отменен")
    with allure.step("11 - Cancel ikkala rezervni baseline'ga qaytaradi"):
        for code in (order_case.product_code, order_case.bonus_code):
            actual = read_stock(page, code, warehouse=order_case.warehouse)
            if actual != baseline:
                pytest.fail(f"Canceled {code}: expected={baseline}, actual={actual}")

    change_order_status(page, order_id, "Восстановить", listing="canceled")
    with allure.step("12 - Restore Draft 600 USD bo'ladi va qayta rezerv qilmaydi"):
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="600", remove_spaces=True)
        for code in (order_case.product_code, order_case.bonus_code):
            actual = read_stock(page, code, warehouse=order_case.warehouse)
            if actual != baseline:
                pytest.fail(f"Restored Draft {code}: expected={baseline}, actual={actual}")


@allure.title("ORD-14: Siklik bonus, rezerv va bekor qilish")
def test_cyclic_promotion(page, order_case):
    run_cyclic_promotion(page, order_case)
