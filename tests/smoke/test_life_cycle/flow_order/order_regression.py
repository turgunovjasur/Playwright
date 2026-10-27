"""Order regression uchun takrorlanadigan UI o'tishlari va iqtisodiy readbacklar.

Biznes ssenariy, test data va expected summalar leaf testcase ichida qoladi.
Bu flowlar yaratgan yoki o'zgartirgan hujjatni aniq ID orqali qayta ochadi.
"""

import re
from decimal import Decimal

import allure
from playwright.sync_api import Page, expect

from utils.base_pages.auto_base_page import AutoBasePage


ORDER_LISTS = {
    "active": ("Заказы", "order_list"),
    "archive": ("Архив заказов", "order_history_list"),
    "canceled": ("Отмененные заказы", "order_cancelled_list"),
}


def open_order(page: Page, *, room: str, staff: str, client: str) -> None:
    """Yangi orderni berilgan room/staff/client bilan goods bosqichigacha ochish."""
    base = AutoBasePage(page)
    with allure.step("Order — yangi hujjat uchun ro'yxatni ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")

    with allure.step("Order — yaratish formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Заказ (создание)", url=re.compile(r"order(?:\+|%2[bB])add(?:[?#]|$)"))

    with allure.step("Order — testcase klienti, ish zonasi va shtatini tanlash"):
        base.b_input(label="Рабочая зона", value=room, clear=True)
        base.b_input(label="Штат", value=staff, clear=True)
        base.b_input(label="Клиент", value=client, clear=True)
        base.click(name="Далее")
        expect(page.locator('b-pg-grid[name="goods_items"]')).to_be_visible()


def save_order(page: Page, *, client: str, order_id: str | None = None) -> str:
    """Final stepni saqlab exact order viewdan ID qaytarish.

    Yangi order uchun testcase o'zining unikal klientini beradi: shu klientda
    aynan bitta order bo'lishi tekshiriladi. Edit/copy hujjati IDsi allaqachon
    ma'lum bo'lsa ``order_id`` majburiy; birinchi yoki eng yangi row olinmaydi.
    """
    base = AutoBasePage(page)
    with allure.step("Order — final qadamdagi hujjatni saqlash"):
        base.click(name="Сохранить")
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(url=re.compile(r"/(?:order_list|order_view)(?:[?#]|$)"))

    if order_id is not None:
        open_saved_order(page, order_id)
        return base.form_view(label="ИД заказа", return_value=True).strip()

    with allure.step("Order — unikal klientning saqlangan orderini topish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Клиент", search_name="Клиент")
        base.grid_controller(search=client)
        expect(page.locator("b-grid:visible").get_by_text(client, exact=True)).to_have_count(1)
        row = base.grid(client, click=True)

    with allure.step("Order — yangi hujjat viewini ochib IDni o'qish"):
        base.click(name="Просмотр", exact=True, root=row)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="Клиент", expect_value=client)
        return base.form_view(label="ИД заказа", expect_value=re.compile(r"^\d+$"), return_value=True).strip()


def open_saved_order(page: Page, order_id: str, *, listing: str = "active") -> None:
    """Active/archive/canceled ro'yxatidan aniq IDli order viewini ochish."""
    if listing not in ORDER_LISTS:
        raise ValueError(f"Noma'lum order ro'yxati: {listing!r}")
    order_id = str(order_id)
    if not order_id.isdigit():
        raise ValueError("order_id faqat raqamlardan iborat bo'lishi kerak")
    heading, route = ORDER_LISTS[listing]
    base = AutoBasePage(page)
    with allure.step(f"Order {order_id} — {heading} ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name=heading)
        base.expect_page(heading=heading, url=route)

    with allure.step(f"Order {order_id} — ID bo'yicha exact rowni topish"):
        id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД заказа", search_name="ИД заказа")
        base.grid_controller(search=order_id)
        row = base.grid(re.compile(rf"(?<!\d){re.escape(order_id)}(?!\d)"), click=True)
        expect(base.grid_cell(row, id_column)).to_have_text(order_id)

    with allure.step(f"Order {order_id} — viewni ochish"):
        base.click(name="Просмотр", exact=True, root=row)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="ИД заказа", expect_value=order_id)


def edit_saved_order(page: Page, order_id: str, *, listing: str = "active") -> None:
    """Exact orderni tahrirga ochib goods bosqichida qoldirish."""
    open_saved_order(page, order_id, listing=listing)
    base = AutoBasePage(page)
    with allure.step(f"Order {order_id} — tahrirlash formasini ochish"):
        base.click(name="Редактировать", exact=True)
        base.expect_page(heading="Заказ (изменение)", url=re.compile(r"order(?:\+|%2[bB])edit(?:[?#]|$)"))

    with allure.step(f"Order {order_id} — saqlangan mahsulotlar bosqichini ochish"):
        base.click(name="Далее")
        expect(page.locator('b-pg-grid[name="goods_items"]')).to_be_visible()


def change_order_status(page: Page, order_id: str, status: str, *, listing: str = "active") -> None:
    """Exact order statusini UI orqali almashtirish yoki arxiv/cancelni tiklash.

    ``status='Восстановить'`` archive/canceled listda ishlatiladi. Qoldiq va
    saldo kutilmalari bu helperda emas, chaqiruvchi testcase ichida tekshiriladi.
    """
    allowed_statuses = {
        "Черновик", "Новый", "В обработке", "В ожидании", "Отгружен",
        "Доставлен", "Архив", "Отменен", "Восстановить",
    }
    if status not in allowed_statuses:
        raise ValueError(f"Noma'lum order statusi: {status!r}")
    if (status == "Восстановить") != (listing in {"archive", "canceled"}):
        raise ValueError("Arxiv/canceled ro'yxatida faqat Восстановить ishlatiladi")
    order_id = str(order_id)
    open_saved_order(page, order_id, listing=listing)
    base = AutoBasePage(page)
    heading, route = ORDER_LISTS[listing]

    with allure.step(f"Order {order_id} — tekshirilgan viewdan ro'yxatga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading=heading, url=route)

    with allure.step(f"Order {order_id} — {status} amalini tasdiqlash"):
        if status == "Восстановить":
            row = base.grid(re.compile(rf"(?<!\d){re.escape(order_id)}(?!\d)"), click=True)
            base.click(name="Восстановить", exact=True, root=row)
            base.confirm_biruni(expected_text="Восстановить заказ?")
            destination = "active"
        else:
            status_button = page.locator(f"#status-btn-{order_id}")
            base.click(locator=status_button)
            base.click(name=status, exact=True, root=".dropdown-menu.show")
            base.confirm_biruni(expected_text=f"Изменить статус на {status}?")
            destination = {"Архив": "archive", "Отменен": "canceled"}.get(status, "active")
        base.expect_page(heading=heading, url=route)

    open_saved_order(page, order_id, listing=destination)
    if status != "Восстановить":
        base.form_view(label="Статус", expect_value=status)


def read_stock(page: Page, product_code: str, *, warehouse: str = "Основной склад") -> dict[str, Decimal]:
    """Mahsulot/ombor rowidan physical, booked, available qiymatlarini o'qish."""
    base = AutoBasePage(page)
    with allure.step(f"Qoldiq — {product_code} uchun ombor ro'yxatini ochish"):
        base.navigate_to(tab="Склад", name="Остатки ТМЦ")
        base.expect_page(heading="Остатки ТМЦ", url="balance_list")

    with allure.step(f"Qoldiq — {warehouse} / {product_code} qiymatlarini o'qish"):
        columns = {}
        for key, label in (
            ("warehouse", "Склад"), ("code", "Код"), ("physical", "В наличии"),
            ("booked", "Забронировано"), ("available", "Доступно"),
        ):
            columns[key] = base.grid_setting(menu_name="Настройка таблицы", field_name=label, search_name="Код" if key == "code" else None)
        base.grid_controller(search=product_code)
        row = base.grid(re.compile(rf"(?s)(?=.*{re.escape(warehouse)})(?=.*{re.escape(product_code)}).*"))
        expect(base.grid_cell(row, columns["warehouse"])).to_have_text(warehouse)
        expect(base.grid_cell(row, columns["code"])).to_have_text(product_code)
        values = {}
        for key in ("physical", "booked", "available"):
            text = base.grid_cell(row, columns[key], return_value=True, remove_spaces=True)
            values[key] = Decimal(text.replace(",", "."))
        return values


def read_settlement(page: Page, client: str, currency: str, *, allow_empty: bool = False) -> dict[str, Decimal]:
    """Exact client/currency rowidagi besh settlement summasini o'qish.

    ``allow_empty=True`` faqat testcase own klient uchun nolni asoslaganda:
    yangi baseline yoki exact allocation/reversal dalilidan keyin ishlatiladi.
    Empty UI tasdiqlanadi; mavjud boshqa valyuta rowi nol deb olinmaydi.
    """
    base = AutoBasePage(page)
    fields = {
        "debt": "Задолженность", "prepayment": "Предоплата", "open_order": "Заказ",
        "booked_prepayment": "Забронированная предоплата", "balance": "Баланс",
    }
    with allure.step(f"Settlement — {client} uchun o'zaro hisob-kitobni ochish"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")

    with allure.step(f"Settlement — {client} / {currency} qiymatlarini o'qish"):
        columns = {}
        for key, label in {"client": "Клиент", "currency": "Валюта", **fields}.items():
            columns[key] = base.grid_setting(menu_name="Настройка таблицы", field_name=label, search_name="Клиент" if key == "client" else None)
        base.grid_controller(search=client)
        if allow_empty and not base.grid(client, return_bool=True):
            base.grid(state="empty")
            return {key: Decimal("0") for key in fields}

        row = base.grid(re.compile(rf"(?s)(?=.*{re.escape(client)})(?=.*{re.escape(currency)}).*"))
        expect(base.grid_cell(row, columns["client"])).to_have_text(client)
        expect(base.grid_cell(row, columns["currency"])).to_have_text(currency)
        values = {}
        for key in fields:
            text = base.grid_cell(row, columns[key], return_value=True, remove_spaces=True)
            values[key] = Decimal(text.replace(",", ".") or "0")
        return values
