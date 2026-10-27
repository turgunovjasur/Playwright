"""ORD-07: faylsiz, bo'sh, unknown ID va manfiy import validatsiyasi."""

import re

import allure
import pytest
from openpyxl import Workbook
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_import import apply_order_import, read_order_import_settings, restore_order_import
from tests.smoke.test_life_cycle.flow_order.order_regression import open_order
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("Podbor va Excel import")]


def run_import_invalid(page, order_case):
    """1. Faylsiz/bo'sh fayl guardi. 2. Unknown IDning qator raqami.

    3. Valid qatorlar previewsi. 4. Manfiy sotuv miqdori saqlanmasligi.
    """
    base = AutoBasePage(page)
    empty_path = order_case.directory / "empty.xlsx"
    mixed_path = order_case.directory / "invalid-rows.xlsx"
    workbook = Workbook()
    workbook.save(empty_path)
    workbook.active.append([order_case.product_id, 2, "Y"])
    workbook.active.append([999999999999, 1, "Y"])
    workbook.active.append([order_case.product_id, -1, "Y"])
    workbook.save(mixed_path)
    workbook.close()
    allure.attach.file(str(mixed_path), name="ORD-07 input", extension="xlsx")

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - Import formasini ochish"):
        base.click(name="Импорт", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
    order_case.import_settings = read_order_import_settings(page)
    apply_order_import(page)
    with allure.step("2 - Faylsiz import rad qilinadi"):
        base.b_input(ng_model="q.warehouse_name", value=order_case.warehouse, clear=True)
        base.b_input(ng_model="q.price_type_name", value=order_case.price_type, clear=True)
        base.click(name="Загрузить файл", exact=True)
        base.close_biruni_alert("H02-ANOR677-001")
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
    with allure.step("3 - Bo'sh XLSX qabul qilinmaydi"):
        page.locator('input[type="file"]').set_input_files(empty_path)
        base.click(name="Загрузить файл", exact=True)
        base.confirm_biruni()
        base.close_biruni_alert("A02-01-072")
    with allure.step("4 - Aralash faylda unknown ID aynan ikkinchi qator xatosi"):
        page.locator('input[type="file"]').set_input_files(mixed_path)
        base.click(name="Загрузить файл", exact=True)
        base.confirm_biruni()
        errors = page.locator('b-pg-grid[name="error_messages"]')
        base.grid("ТМЦ с данным ИД не найдено", "999999999999", root=errors)
        error_row = base.grid("999999999999", root=errors)
        expect(base.grid_cell(error_row, 0)).to_have_text("2")
        quantities = page.locator('b-pg-grid[name="products"] input[ng-model="row.quantity"]:visible')
        expect(quantities).to_have_count(2)
        expect(quantities.nth(0)).to_have_value("2")
        expect(quantities.nth(1)).to_have_value("-1")
    restore_order_import(page, order_case.import_settings)
    order_case.import_settings = None
    with allure.step("5 - Parsed qatorlarni orderga o'tkazish"):
        base.click(name="Добавить выбранные поля", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add"))
        base.input(ng_model="item.quantity", index=0, expect_value="2")
        base.input(ng_model="item.quantity", index=1, expect_value="-1")
        base.click(locator="#anor279-button-next_step")
        base.form_view(label="ИТОГО", expect_value="100", remove_spaces=True)
        base.ui_select(label="Статус", value="Черновик")
    with allure.step("6 - Manfiy miqdor serverda ham saqlanmaydi"):
        base.click(name="Сохранить")
        base.confirm_biruni("Сохранить?")
        base.close_biruni_alert('Неверно указано значение "Кол-во заказов"', "-1")
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add"))
    with allure.step("7 - Own klient uchun noqonuniy order yaratilmaganini tekshirish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Клиент", search_name="Клиент")
        base.grid_controller(search=order_case.client)
        base.grid(state="empty")


@allure.title("ORD-07: Import validatsiyasi va manfiy miqdorni rad etish")
def test_import_invalid(page, order_case):
    run_import_invalid(page, order_case)
