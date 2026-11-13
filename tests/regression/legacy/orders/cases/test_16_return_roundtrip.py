"""Own Archive orderdan to'liq Return va uning takroriy iqtisodiy qaytishi."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.test_life_cycle.flow_order.order_regression import (
    change_order_status,
    open_order,
    open_saved_order,
    read_settlement,
    read_stock,
    save_order,
)
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, allure.epic("Regression"), allure.feature("Order"), allure.story("To'lov, qaytarish va report")]


def run_return_roundtrip(page, order_case):
    """1. Faqat shu case uchun faol qaytarish sababini yaratish.
    2. O'z mahsulotidan 100 USD order yaratib Archivega o'tkazish.
    3. Shu orderdan 1 dona to'liq Return Draft yaratish va IDlarini tekshirish.
    4. Draft qoldiq yoki qarzga ta'sir qilmasligini tekshirish.
    5. Sent: qoldiq o'zgarmaydi, -100 ochiq qaytarish krediti paydo bo'ladi.
    6. Archive: 1 dona qoldiq va 100 predoplata, source qarzi esa saqlanadi.
    7. Draftga qaytarish, qayta Archive va yana Draft: ta'sir takrorlanmaydi.

    Return narxining tarkibi filial sozlamasiga bog'liq; net summa aynan source
    orderdagi 100 USD bo'lishi kerak. Sabab katalog yozuvi audit uchun qoladi.
    """
    base = AutoBasePage(page)
    case = order_case
    amount = Decimal("100")
    reason = f"Order Return {case.key}"

    with allure.step("1 - Qaytarishlar ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Возвраты")
        base.expect_page(heading="Возвраты", url="anor/mdeal/return/return_list")
    with allure.step("2 - Qaytarish sabablari katalogini ochish"):
        base.page_link(name="Причины возврата")
        base.expect_page(heading="Причины возврата", url="anor/mdeal/return/return_reason_list")
    with allure.step("3 - Faqat shu case uchun qaytarish sababini yaratish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Причина возврата (создание)", url=re.compile(r"return_reason(?:\+|%2[bB])add"))
        base.input(label="Название", value=reason)
        base.input(label="Код", value=f"R{case.key[-8:]}")
        base.checkbox(label="Активный", checked=True)
    with allure.step("4 - Own qaytarish sababini saqlash"):
        base.click(name="Сохранить", exact=True)
        saved_list = page.get_by_role("heading", name="Причины возврата").filter(visible=True)
        confirmation = page.get_by_role("heading", name="Сохранить?", exact=True).filter(visible=True)
        expect(saved_list.or_(confirmation)).to_be_visible()
        if confirmation.is_visible():
            base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Причины возврата", url="return_reason_list")
        base.grid_controller(search=reason)
        base.grid(reason)
        allure.attach(reason, "Own Return reason", allure.attachment_type.TEXT)

    baseline = read_settlement(page, case.client, case.currency, allow_empty=True)
    open_order(page, room=case.room, staff=case.staff, client=case.client)
    with allure.step("5 - Qaytarish uchun 100 USD source order tayyorlash"):
        goods = 'b-pg-grid[name="goods_items"]'
        base.b_input(label="Название", value=case.product, root=goods)
        base.input(ng_model="item.quantity", value="1", root=goods, press_tab=True)
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.input(label="Номер ТТН", value=case.reference)
        base.ui_select(label="Статус", value="Черновик")
        base.form_view(label="ИТОГО", expect_value=str(amount), remove_spaces=True)
    order_id = save_order(page, client=case.client)
    case.orders.append(order_id)
    for status in ("Новый", "В обработке", "В ожидании", "Отгружен", "Доставлен", "Архив"):
        change_order_status(page, order_id, status)
    archived_stock = read_stock(page, case.product_code, warehouse=case.warehouse)
    archived_balance = read_settlement(page, case.client, case.currency)
    expected_archive = {**baseline, "debt": baseline["debt"] + amount, "balance": baseline["balance"] - amount}
    if archived_balance != expected_archive:
        raise AssertionError(f"Source Archive saldo: expected={expected_archive}; actual={archived_balance}")

    open_saved_order(page, order_id, listing="archive")
    with allure.step("6 - Exact source orderning Archive qatoriga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Архив заказов", url="order_history_list")
        row = base.grid(order_id, case.client, click=True)
    with allure.step("7 - Source orderdan Return formasini ochish"):
        base.click(name="Возврат", exact=True, root=row)
        base.expect_page(heading="Возврат (создание)", url=re.compile(r"return(?:\+|%2[bB])add"))
        base.b_input(label="ИД заказа", expect_value=re.compile(rf"^{order_id}\s*/"))
        base.b_input(label="Клиент", expect_value=case.client)
        base.b_input(label="Валюта", expect_value=case.currency)
        base.b_input(label="Склад", value=case.warehouse, clear=True)
        base.input(ng_model="d.delivery_date", value=base.date("today"), press_tab=True)
        base.checkbox(label="Частичный возврат", checked=False)
    with allure.step("8 - To'liq qaytarishning bir dona mahsulotini tekshirish"):
        base.click(name="Далее")
        return_goods = 'b-pg-grid[name="items"]'
        base.text(case.product, root=return_goods)
        base.input(ng_model="item.quantity", expect_value="1", root=return_goods)
        expect(page.locator(return_goods).locator('input[ng-model="item.quantity"]')).not_to_be_editable()
    with allure.step("9 - To'lov turi va own qaytarish sababini tanlash"):
        base.click(name="Далее")
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.b_input(label="Причина возврата", value=reason)
        base.input(label="Номер товарно-транспортной накладной", value=f"R{case.key[-8:]}")
        base.input(ng_model="d.note", value=f"Order regression: full Return of {order_id}")
    with allure.step("10 - Return Draftning source net summasini tekshirish"):
        base.click(name="Далее")
        base.ui_select(label="Статус", value="Черновик")
        base.form_view(label="Итоговая сумма возврата с учетом общей скидки/наценки к заказу", expect_value=str(amount), remove_spaces=True)
    with allure.step("11 - Own Return Draftni saqlash"):
        case.return_pending = True
        base.click(name="Сохранить")
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Архив заказов", url="order_history_list")
    with allure.step("12 - Saqlangan own Return qatorini topish"):
        base.navigate_to(tab="Продажа", name="Возвраты")
        base.expect_page(heading="Возвраты", url="anor/mdeal/return/return_list")
        base.grid_controller(search=case.client)
        expect(page.locator("b-grid:visible").get_by_text(case.client, exact=True)).to_have_count(1)
        row = base.grid(case.client, "Черновик", click=True)
    with allure.step("13 - Return ID, source ID va net summani fresh viewda tekshirish"):
        base.click(name="Просмотреть", exact=True, root=row)
        base.expect_page(heading="Возврат (просмотр)", url="return_view")
        return_id = base.form_view(label="ИД возврата", expect_value=re.compile(r"^\d+$"), return_value=True).strip()
        case.returns.append(return_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Валюта", expect_value=case.currency)
        base.form_view(label="Статус", expect_value="Черновик")
        saved_goods = 'b-pg-grid[name="items0"]'
        product_row = base.grid(case.product, root=saved_goods)
        headers = page.locator(saved_goods).locator(".tbl-header-cell")
        expect(headers.first).to_be_visible()
        columns = [re.sub(r"[\s\uf000-\uf8ff]+", " ", text).strip() for text in headers.all_text_contents()]
        expect(base.grid_cell(product_row, columns.index("Кол-во"))).to_have_text(re.compile(r"^\s*1(?:\.0+)?\s*$"))
        expect(base.grid_cell(product_row, columns.index("Сумма с переоценкой"))).to_have_text(re.compile(r"^\s*100(?:\.0+)?\s*$"))

    draft_stock = read_stock(page, case.product_code, warehouse=case.warehouse)
    draft_balance = read_settlement(page, case.client, case.currency)
    if draft_stock != archived_stock or draft_balance != archived_balance:
        raise AssertionError(f"Return Draft iqtisodiy ta'siri: expected stock={archived_stock}, saldo={archived_balance}; actual stock={draft_stock}, saldo={draft_balance}")

    returned_stock = {**archived_stock, "physical": archived_stock["physical"] + 1, "available": archived_stock["available"] + 1}
    sent_balance = {**archived_balance, "open_order": archived_balance["open_order"] - amount, "balance": archived_balance["balance"] + amount}
    returned_balance = {**archived_balance, "prepayment": archived_balance["prepayment"] + amount, "balance": archived_balance["balance"] + amount}
    # Bir hujjat qayta o'tkazilganda +1/+100 ikkinchi marta jamlanmasligi kerak.
    status_checks = (
        ("Отправлено", archived_stock, sent_balance),
        ("Архив", returned_stock, returned_balance),
        ("Черновик", archived_stock, archived_balance),
        ("Архив", returned_stock, returned_balance),
        ("Черновик", archived_stock, archived_balance),
    )
    for index, (status, expected_stock, expected_balance) in enumerate(status_checks, start=1):
        with allure.step(f"14.{index} - Own Return {return_id}: {status} uchun ro'yxatni ochish"):
            base.navigate_to(tab="Продажа", name="Возвраты")
            base.expect_page(heading="Возвраты", url="anor/mdeal/return/return_list")
            base.grid_controller(search=case.client)
            expect(page.locator("b-grid:visible").get_by_text(case.client, exact=True)).to_have_count(1)
        with allure.step(f"15.{index} - Own Return statusini {status} ga o'tkazish"):
            if status == "Черновик":
                row = base.grid(case.client, click=True)
                base.click(name="Статус", exact=True, root=row)
                coach = page.get_by_role("dialog", name="Статус", exact=True)
                if coach.is_visible():
                    base.click(name="Больше не показывать", exact=True, root=coach)
                base.click(name="Черновик", role="link", root=row)
            else:
                status_button = page.locator(f"#status-btn-{return_id}")
                base.click(locator=status_button)
                base.click(name=status, root=status_button)
            base.confirm_biruni(f"Изменить на {status}?")
            base.wait_for_loader()
            row = base.grid(case.client, status, click=True)
        with allure.step(f"16.{index} - Returnning exact IDsi va {status} saqlanganini tekshirish"):
            base.click(name="Просмотреть", exact=True, root=row)
            base.expect_page(heading="Возврат (просмотр)", url="return_view")
            base.form_view(label="ИД возврата", expect_value=return_id)
            base.form_view(label="ИД заказа", expect_value=order_id)
            base.form_view(label="Клиент", expect_value=case.client)
            base.form_view(label="Статус", expect_value=status)
        actual_stock = read_stock(page, case.product_code, warehouse=case.warehouse)
        actual_balance = read_settlement(page, case.client, case.currency)
        if actual_stock != expected_stock or actual_balance != expected_balance:
            raise AssertionError(f"Return {status} #{index}: expected stock={expected_stock}, saldo={expected_balance}; actual stock={actual_stock}, saldo={actual_balance}")


@allure.title("ORD-16: Orderdan Return, Archive va qaytarishni bekor qilish")
def test_16_return_roundtrip(page, order_case):
    run_return_roundtrip(page, order_case)
