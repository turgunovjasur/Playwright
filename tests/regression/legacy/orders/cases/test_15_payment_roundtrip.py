"""O'z Archive orderi uchun cashin va exact allocationning to'liq qaytishi."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import (
    change_order_status,
    open_order,
    read_settlement,
    read_stock,
    save_order,
)
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("To'lov, qaytarish va report")]


def run_payment_roundtrip(page, order_case):
    """1. O'z 100 USD orderini yaratib Archivega o'tkazish.
    2. Auto-offsetsiz 100 USD cashin Draft yaratish va qayta ochish.
    3. Cashinni o'tkazish: qarz saqlanib, alohida 100 USD predoplata hosil bo'ladi.
    4. Faqat shu orderga predoplatani ajratish va yangi tarix yozuvini tekshirish.
    5. Aynan shu allocationni bekor qilish: qarz va predoplata qaytadi.
    6. Cashinni Unpost qilish: Archive oldidagi qarz/stock holati qaytadi.

    Fixture teardown o'z orderini keyin bekor qiladi; sibling data ishlatilmaydi.
    """
    base = AutoBasePage(page)
    amount = Decimal("100")
    payment_number = order_case.reference
    baseline = read_settlement(page, order_case.client, order_case.currency, allow_empty=True)

    open_order(page, room=order_case.room, staff=order_case.staff, client=order_case.client)
    with allure.step("1 - O'z mahsulotidan 100 USD naqd order tayyorlash"):
        goods = page.locator('b-pg-grid[name="goods_items"]')
        base.b_input(label="Название", value=order_case.product, root=goods)
        base.input(ng_model="item.new_price", expect_value="100", root=goods)
        base.input(ng_model="item.quantity", value="1", root=goods, press_tab=True)
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(label="Номер ТТН", value=order_case.reference)
        base.ui_select(label="Статус", value="Черновик")
        base.form_view(label="ИТОГО", expect_value=str(amount), remove_spaces=True)
    order_id = save_order(page, client=order_case.client)
    order_case.orders.append(order_id)
    for status in ("Новый", "В обработке", "В ожидании", "Отгружен", "Доставлен", "Архив"):
        change_order_status(page, order_id, status)
    archived_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
    archived_balance = read_settlement(page, order_case.client, order_case.currency)
    expected_archive = {**baseline, "debt": baseline["debt"] + amount, "balance": baseline["balance"] - amount}
    if archived_balance != expected_archive:
        raise AssertionError(f"Archive saldo: expected={expected_archive}; actual={archived_balance}")

    with allure.step("2 - Klient to'lovlari ro'yxatini ochish"):
        base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
    with allure.step("3 - Alohida cashin yaratish formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Оплата от клиента / Создание", url=re.compile(r"cashin(?:\+|%2[bB])add"))
        base.input(label="Номер оплаты", value=payment_number)
        base.b_input(label="Валюта", value=order_case.currency, clear=True)
        base.b_input(label="Клиент", value=order_case.client)
        base.input(label="Сумма", value=str(amount), press_tab=True)
        base.b_input(label="Тип оплаты", value="Наличные деньги")
        base.b_input(label="Касса", value="Основная касса")
        base.checkbox(label="Провести взаимозачёт", checked=False)
        base.input(ng_model="d.note", value=f"Order regression {order_id}: exact payment roundtrip")
    with allure.step("4 - Cashin Draftni saqlash"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        order_case.cashins.append(payment_number)
        base.expect_page(heading="Оплата от клиента / Создание", url=re.compile(r"cashin(?:\+|%2[bB])add"))
    with allure.step("5 - Cashin ro'yxatida o'tkazilmagan hujjatni topish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
        posted_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Проведено", search_name="Номер оплаты")
        base.grid_controller(search=payment_number)
        row = base.grid(payment_number, order_case.client, click=True)
        base.grid_cell(row, posted_column, expect_value="Нет")
    with allure.step("6 - Saqlangan cashin klienti, valyutasi va summasini tekshirish"):
        base.click(name="Просмотр", exact=True, root=row)
        base.expect_page(heading="Оплата от клиента / Просмотр", url="cashin_view")
        base.form_view(label="Номер оплаты", expect_value=payment_number)
        base.form_view(label="Клиент", expect_value=order_case.client)
        base.form_view(label="Валюта", expect_value=order_case.currency)
        base.form_view(label="Сумма", expect_value=str(amount), remove_spaces=True)
    draft_balance = read_settlement(page, order_case.client, order_case.currency)
    if draft_balance != archived_balance:
        raise AssertionError(f"Draft cashin saldo o'zgartirdi: before={archived_balance}; after={draft_balance}")

    with allure.step("7 - Aynan own cashinni o'tkazish uchun listga qaytish"):
        base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
        base.grid_controller(search=payment_number)
        row = base.grid(payment_number, order_case.client, click=True)
    with allure.step("8 - Cashinni Post qilish"):
        base.click(name="Провести", exact=True, root=row)
        base.confirm_biruni(f"Провести {payment_number}?")
        base.wait_for_loader()
        row = base.grid(payment_number, order_case.client)
        base.grid_cell(row, posted_column, expect_value="Да")
    posted_balance = read_settlement(page, order_case.client, order_case.currency)
    expected_posted = {**archived_balance, "prepayment": archived_balance["prepayment"] + amount, "balance": archived_balance["balance"] + amount}
    if posted_balance != expected_posted:
        raise AssertionError(f"Post saldo: expected={expected_posted}; actual={posted_balance}")

    with allure.step("9 - Own klientning qarz detallarini ochish"):
        row = base.grid(order_case.client, order_case.currency, click=True)
        base.click(name="Детали", exact=True, root=row)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")
        base.grid_controller(search=order_id)
        row = base.grid(order_id, "Архив", click=True)
    with allure.step("10 - Faqat shu orderning predoplata hisob-kitobini ochish"):
        base.click(name="Перерасчет", exact=True, root=row)
        base.expect_page(heading="Взаиморасчет по предоплате", url=re.compile(r"/offset/offset(?:[?#]|$)"))
        base.text(order_case.client, order_id)
        expect(page.locator('input[ng-model="row.offset_amount"]:visible')).to_have_count(1)
        base.input(ng_model="row.offset_amount", value=str(amount), press_tab=True)
    with allure.step("11 - Exact allocationni o'tkazish va own qarz yo'qolishini tekshirish"):
        order_case.allocation_pending = True
        base.click(name="Провести", exact=True)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")
        base.grid_controller(search=order_id)
        base.grid(state="empty")
    with allure.step("12 - Shu allocationning yagona tarix yozuvini olish"):
        base.click(name="История взаиморасчетов", role="link", exact=True)
        base.expect_page(heading="История взаиморасчетов", url="offset_history_list")
        number_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Номер взаиморасчета", search_name="Клиент")
        amount_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Сумма")
        base.grid_controller(search=order_case.client)
        expect(page.locator("b-grid:visible").get_by_text(order_case.client, exact=True)).to_have_count(1)
        row = base.grid(order_case.client, order_case.currency)
        allocation_number = base.grid_cell(row, number_column, return_value=True).strip()
        order_case.allocations.append(allocation_number)
        base.grid_cell(row, amount_column, expect_value=str(amount), remove_spaces=True)
    allocated_balance = read_settlement(page, order_case.client, order_case.currency, allow_empty=True)
    if allocated_balance != baseline:
        raise AssertionError(f"To'liq allocationdan keyingi saldo: expected={baseline}; actual={allocated_balance}")

    with allure.step("13 - O'zaro hisob-kitob tarixini qayta ochish"):
        base.click(name="История взаиморасчетов", role="link", exact=True)
        base.expect_page(heading="История взаиморасчетов", url="offset_history_list")
        base.grid_controller(search=order_case.client)
    with allure.step("14 - Faqat yangi allocationni bekor qilish"):
        row = base.grid(allocation_number, order_case.client, click=True)
        base.click(name="Отменить взаиморасчет", exact=True, root=row)
        base.confirm_biruni("Отменить?")
        base.wait_for_loader()
        base.grid_controller(search=order_case.client)
        base.grid(state="empty")
        order_case.allocations.clear()
        order_case.allocation_pending = False
    restored_payment = read_settlement(page, order_case.client, order_case.currency)
    if restored_payment != posted_balance:
        raise AssertionError(f"Allocation reversal: expected={posted_balance}; actual={restored_payment}")

    with allure.step("15 - Own cashin ro'yxatini qayta ochish"):
        base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
        base.grid_controller(search=payment_number)
        row = base.grid(payment_number, order_case.client, click=True)
    with allure.step("16 - Cashinni Unpost qilish"):
        base.click(name="Отменить", exact=True, root=row)
        base.confirm_biruni(f"Отменить {payment_number}?")
        base.wait_for_loader()
        row = base.grid(payment_number, order_case.client)
        base.grid_cell(row, posted_column, expect_value="Нет")
        order_case.cashins.remove(payment_number)
    restored_balance = read_settlement(page, order_case.client, order_case.currency)
    restored_stock = read_stock(page, order_case.product_code, warehouse=order_case.warehouse)
    if restored_balance != archived_balance or restored_stock != archived_stock:
        raise AssertionError(f"Payment roundtrip: expected balance={archived_balance}, stock={archived_stock}; actual balance={restored_balance}, stock={restored_stock}")


@allure.title("ORD-15: To'lov, exact orderga ajratish va bekor qilish")
def test_15_payment_roundtrip(page, order_case):
    run_payment_roundtrip(page, order_case)
