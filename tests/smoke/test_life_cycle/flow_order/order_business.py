"""Uch A2 biznes testcase uchun order list/create/save/reopen gatewaylari."""
import re
import allure
from playwright.sync_api import expect
from utils.base_pages.auto_base_page import AutoBasePage


def promotion_card(page, name):
    """02.11.2026 live A2 DOM: aksiya nomi va switch bitta article ichida."""
    card = page.locator("article").filter(has=page.get_by_text(name, exact=True))
    expect(card).to_have_count(1)
    expect(card).to_be_visible()
    return card


def open_new_order(page):
    base = AutoBasePage(page)
    with allure.step("Order ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="/a2/trade/tdeal/order/order_list")
    with allure.step("Oddiy order yaratish formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"/a2/.*/order(?:%2[Bb]|\+)add"))


def save_order_by_reference(page, reference):
    base = AutoBasePage(page)
    with allure.step("Orderni saqlab ro'yxatga qaytish"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Заказы", url="order_list")
    with allure.step("Unique TTN bo'yicha aynan yangi orderni topish"):
        column = base.grid_setting(menu_name="Настройка таблицы", field_name="Номер ТТН", search_name="Номер ТТН")
        base.grid_controller(search=reference)
        row = base.grid(reference, click=True)
        expect(page.locator("smt-data-table:visible .smt-data-row")).to_have_count(1)
        expect(base.grid_cell(row, column)).to_have_text(reference)
    with allure.step("Saqlangan order viewini ochish"):
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="Номер ТТН", expect_value=reference)
        return base.form_view(label="ИД заказа", expect_value=re.compile(r"^\d+$"), return_value=True).strip()


def reopen_order_goods(page):
    base = AutoBasePage(page)
    with allure.step("Saqlangan orderni tahrirga qayta ochish"):
        base.click(name="Редактировать", exact=True)
        base.expect_page(heading="Заказ (изменение)", url=re.compile(r"order(?:%2[Bb]|\+)edit"))
    with allure.step("Saqlangan mahsulotlar bosqichini ochish"):
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")
