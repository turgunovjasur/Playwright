"""ORD-13: optional summa aksiyasi, 10% chegirma va saqlangan total."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_action.flow_action.flow_action import fill_action_scope, open_action_form
from tests.smoke.test_life_cycle.flow_order.order_regression import open_order, save_order
from tests.smoke.test_life_cycle.flow_order.order_summary import summary_quantity_cell
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order aksiyalari")]


def run_amount_promotion(page, order_case):
    """1. Own optional 300–500 summa aksiyasini yaratish. 2. 200/300/500/600.

    3. Opt-indan keyin 10% va bonus yo'qligi. 4. Saqlangan 270 USD readback.
    """
    base = AutoBasePage(page)
    action_name = f"ORD13 {order_case.key} sum300-500 discount10"
    start_date, end_date = base.date(), base.date(days=1)

    open_action_form(page)
    with allure.step("1 - Own optional summa aksiyasining doirasini belgilash"):
        fill_action_scope(page, name=action_name, action_code=f"O13-{order_case.key}", room=order_case.room, price_type=order_case.price_type, start_date=start_date, end_date=end_date)
        base.ui_select(label="Тип акции", value="Сумма")

    with allure.step("2 - Aksiya shartlari formasini ochish"):
        base.click(name="Далее", exact=True)
        base.expect_page(heading="Условия", url=re.compile(r"action(?:\+|%2[bB])add"))

    with allure.step("3 - Faqat own mahsulotga 300–500 va shu mahsulotga 10% chegirma"):
        base.checkbox(label="Ассортимент", checked=False)
        base.ui_select(label="Тип условия", value="Обычный")
        base.b_input(ng_model="d['selected_rule_name_' + condition_index + rule_index]", value=order_case.product)
        base.input(ng_model="rule.main_value", value="300")
        base.input(ng_model="rule.extra_value", value="500")
        base.input(ng_model="rule.required_count", value="1")
        base.ui_select(label="Тип бонуса", value="Скидка")
        base.b_input(ng_model="d['selected_bonus_name_' + condition_index + bonus_index]", value=order_case.product)
        base.input(ng_model="product.value", value="10")

    with allure.step("4 - Aksiyani Active saqlash va cleanup ID sini ro'yxatga olish"):
        order_case.action_names.append(action_name)
        base.click(name="Завершить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Акции", url="action_list")
        id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="Название")
        base.grid_controller(search=action_name)
        row = base.grid(action_name, "Сумма", "Активный")
        action_id = base.grid_cell(row, id_column, return_value=True, remove_spaces=True)
        order_case.actions.append(action_id)
        expect(base.grid_cell(row, id_column)).to_have_text(re.compile(r"^\d+$"))

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    goods = page.locator('b-pg-grid[name="goods_items"]')
    with allure.step("5 - Own mahsulotning 100 USD narxini tekshirish"):
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(label="Цена", expect_value="100", root=goods)
        base.text(order_case.warehouse, order_case.price_type, root=goods)

    previous_eligible = False
    for index, (quantity, eligible) in enumerate(((2, False), (3, True), (5, True), (6, False), (3, True))):
        gross = Decimal(quantity) * Decimal("100")
        discount = gross * Decimal("0.10") if eligible else Decimal("0")
        payable = gross - discount
        with allure.step(f"6.{index + 1} - Gross {gross}: opt-in va chegirma {discount}, payable {payable}"):
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
            # Opt-in o'chirilgan holatda bir marta hisoblatib, so'ng karta tekshiriladi.
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
                base.grid(order_case.product, "10", root=card)
                base.checkbox(ng_model="condition.get", checked=True, root=card)
            else:
                expect(heading).to_have_count(0)
            base.click(locator="#anor279-button-next_step")
            base.form_view(label="ИТОГО", expect_value=format(payable.normalize(), "f"), remove_spaces=True)
            base.form_view(label="Сумма скидки/наценки", expect_value=format((-discount).normalize(), "f"), remove_spaces=True)
            expect(summary_quantity_cell(page, "Акция")).to_have_text(re.compile(r"^Кол-во\s*:\s*0$"))
            previous_eligible = eligible

    with allure.step("7 - 300 gross / minus 30 / USD 270 Draftni saqlash"):
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=order_case.reference)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)

    with allure.step("8 - Saqlangan qator miqdori, narxi, chegirmasi va payable"):
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="270", remove_spaces=True)
        base.form_view(label="Сумма скидки/наценки на заказ", expect_value="0", remove_spaces=True)
        grid = page.locator("b-grid:visible")
        row = base.grid(order_case.product, root=grid)
        headers = grid.locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        labels = [re.sub(r"[\s\uf000-\uf8ff]+", " ", value).strip() for value in headers.all_inner_texts()]
        for label, value in (("Количество продажи", "3"), ("Цена", "100"), ("Сумма скидки/наценки", "-30"), ("Итого", "270")):
            expect(base.grid_cell(row, labels.index(label))).to_have_text(re.compile(rf"^\s*{re.escape(value)}\s*$"))

    with allure.step("9 - Chegirma aksiyasi bepul bonus qatori yaratmaganini tekshirish"):
        expect(page.get_by_role("link", name="Акция", exact=True)).to_have_count(0)


@allure.title("ORD-13: Summa aksiyasi va chegirma chegaralari")
def test_amount_promotion(page, order_case):
    run_amount_promotion(page, order_case)
