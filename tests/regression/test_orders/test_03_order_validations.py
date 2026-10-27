"""ORD-03: bo'sh order, nol miqdor va to'lov turisiz New validatsiyasi."""

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order yaratish va tahrirlash")]


def run_order_validations(page, order_case):
    """Invalid order holatlari saqlangan New hujjatga aylanmasligi.

    1. Tovarsiz Next H02-ANOR279-004 bilan bloklanishi.
    2. Tanlangan mahsulot miqdori 0 bo'lsa H02-ANOR279-005 chiqishi.
    3. Miqdorni 1 qilib to'lov turisiz Draft saqlash.
    4. New statusini tasdiqlash A02-16-047 bilan rad etilishi; fresh view Draft qolishi.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'

    with allure.step("1 - Tovarsiz order Next validatsiyasi"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)
        base.click(name="Далее")
        base.close_biruni_alert("H02-ANOR279-004")
        expect(page.locator(goods)).to_be_visible()

    with allure.step("2 - Nol miqdor keyingi bosqichga o'tmasligi"):
        base.b_input(label="Название", value=case.product, root=goods)
        base.input(ng_model="item.quantity", value="0", press_tab=True, root=goods)
        base.click(name="Далее")
        base.close_biruni_alert("H02-ANOR279-005")
        expect(page.locator(goods)).to_be_visible()

    with allure.step("3 - Valid 1 dona mahsulotni to'lov turisiz Draft saqlash"):
        base.input(ng_model="item.quantity", value="1", press_tab=True, root=goods)
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", clear=True, expect_value="")
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.form_view(label="ИТОГО", expect_value="100", remove_spaces=True)
        order_id = save_order(page, client=case.client)
        case.orders.append(order_id)
        base.form_view(label="Статус", expect_value="Черновик")

    with allure.step("4 - To'lov turisiz New rad etilib exact order Draft qolishi"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Заказы", url="order_list")
        base.click(locator=f"#status-btn-{order_id}")
        base.click(name="Новый", exact=True, root=".dropdown-menu.show")
        base.confirm_biruni(expected_text="Изменить статус на Новый?")
        base.close_biruni_alert("A02-16-047", "Выберите тип оплаты!")
        open_saved_order(page, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Сумма заказа", expect_value="100", remove_spaces=True)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-03: Bo'sh order, nol miqdor va to'lov turisiz New validatsiyasi")
def test_order_validations(page, order_case):
    run_order_validations(page, order_case)
