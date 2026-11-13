"""ORD-02: nusxa manbadan mustaqil; discard saqlangan qiymatni buzmaydi."""

import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import edit_saved_order, open_order, open_saved_order, save_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Order yaratish va tahrirlash")]


def run_copy_discard_order(page, order_case):
    """Nusxani tahrirlash va manbadagi saqlanmagan o'zgarishni tashlash.

    1. Own klientga 1 dona / 100 USD manba Draft yaratish.
    2. Copy modal orqali bitta nusxa yaratib yangi IDni darhol ro'yxatga olish.
    3. Nusxani 2 dona / 200 USD qilib saqlash; manba 100 USD qolishi.
    4. Manbada 9 dona kiritib discard qilish; fresh viewda 1 dona / 100 USD qolishi.
    """
    base = AutoBasePage(page)
    case = order_case
    goods = 'b-pg-grid[name="goods_items"]'
    saved_goods = "b-grid:visible"

    with allure.step("1 - 1 dona / 100 USD manba Draft yaratish"):
        open_order(page, room=case.room, staff=case.staff, client=case.client)
        base.b_input(label="Название", value=case.product, root=goods)
        base.input(ng_model="item.quantity", value="1", press_tab=True, root=goods)
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        base.input(ng_model="d.delivery_number", value=case.reference)
        base.form_view(label="ИТОГО", expect_value="100", remove_spaces=True)
        source_id = save_order(page, client=case.client)
        case.orders.append(source_id)
        base.form_view(label="Сумма заказа", expect_value="100", remove_spaces=True)

    with allure.step("2 - Manba ro'yxatiga qaytib Copy modalini ochish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_controller(search=case.client)
        source_row = base.grid(case.client, click=True)
        base.click(name="Копировать", exact=True, root=source_row)
        copy_modal = page.locator(".modal:visible").filter(has=page.get_by_role("heading", name="Копировать заказ", exact=True))
        expect(copy_modal).to_be_visible()
        base.text(case.client, root=copy_modal)

    with allure.step("2 - Bitta nusxani yaratib uning yangi ID sini darhol olish"):
        base.click(name="Копировать", exact=True, root=copy_modal)
        expect(copy_modal).to_be_hidden()
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_controller(search=case.client)
        markers = page.locator('b-grid:visible [id^="status-btn-"]')
        expect(markers).to_have_count(2)
        copy_marker = page.locator(f'b-grid:visible [id^="status-btn-"]:not(#status-btn-{source_id})')
        expect(copy_marker).to_have_count(1)
        copy_id = copy_marker.get_attribute("id").removeprefix("status-btn-")
        case.orders.append(copy_id)
        open_saved_order(page, copy_id)
        base.form_view(label="ИД заказа", expect_value=copy_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="100", remove_spaces=True)

    with allure.step("3 - Nusxani 200 USDga o'zgartirib manba 100 USD qolishini tekshirish"):
        edit_saved_order(page, copy_id)
        base.input(ng_model="item.quantity", value="2", press_tab=True, root=goods)
        base.click(name="Далее")
        base.input(ng_model="d.delivery_number", value=f"{case.reference}C")
        base.form_view(label="ИТОГО", expect_value="200", remove_spaces=True)
        save_order(page, client=case.client, order_id=copy_id)
        base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)
        row = base.grid(case.product, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*2(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*200(?:\.0+)?\s*$"))
        open_saved_order(page, source_id)
        base.form_view(label="Сумма заказа", expect_value="100", remove_spaces=True)
        base.form_view(label="Номер ТТН", expect_value=case.reference)

    with allure.step("4 - Manbadagi 9 dona saqlanmagan o'zgarishni discard qilish"):
        edit_saved_order(page, source_id)
        base.input(ng_model="item.quantity", value="9", press_tab=True, root=goods)
        base.click(locator="#anor279-button-prev_step")
        base.b_input(label="Клиент", expect_value=case.client)
        base.click(locator='button[ng-click="close()"]:visible')
        base.confirm_biruni(expected_text="Все не сохраненные данные будут потеряны")
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        open_saved_order(page, source_id)
        base.form_view(label="ИД заказа", expect_value=source_id)
        base.form_view(label="Сумма заказа", expect_value="100", remove_spaces=True)
        row = base.grid(case.product, root=saved_goods)
        expect(base.grid_cell(row, columns.index("Количество продажи"))).to_have_text(re.compile(r"^\s*1(?:\.0+)?\s*$"))
        expect(base.grid_cell(row, columns.index("Итого"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))
        open_saved_order(page, copy_id)
        base.form_view(label="Сумма заказа", expect_value="200", remove_spaces=True)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("ORD-02: Order nusxasi va saqlanmagan o'zgarishlarni tashlash")
def test_copy_discard_order(page, order_case):
    run_copy_discard_order(page, order_case)
