"""Order caselari uchun umumiy, har testcase'ga alohida UI setup va cleanup.

Bu yerda order yoki aksiya yaratilmaydi: biznes qadamlar leaf testda qoladi.
Katalog yozuvlari diagnostika uchun saqlanadi; stock hujjati bekor qilinadi.
"""

import json
import re
from dataclasses import asdict

import allure
from playwright.sync_api import expect

from tests.smoke.test_setup.flow_setup.flow_natural_person import (
    create_natural_person,
    open_natural_person_create,
    open_natural_person_list,
)
from utils.base_pages.auto_base_page import AutoBasePage
from utils.helper_utils import query_int_from_url


def prepare_order_environment(page, case, code):
    """Unique mijoz, paid/bonus mahsulot va har biriga 50 dona qoldiq."""
    base = AutoBasePage(page)
    with allure.step("Order setup: test filialini tanlash"):
        base.switch_filial(name=f"filial-pw{code}")

    open_natural_person_list(page, step_name="Order setup: mijozlar katalogini ochish")
    open_natural_person_create(page, step_name="Order setup: alohida mijoz formasini ochish")
    create_natural_person(page, case.client, f"oc-{case.key}", step_name="Order setup: faqat shu testcase mijozini saqlash", client=True)

    with allure.step("Order setup: ish zonalari ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны", url="room_list")
    with allure.step("Order setup: ish zonasining biriktirish formasini ochish"):
        base.grid_controller(search=case.room)
        base.grid(case.room, click=True)
        base.click(name="Прикрепление", exact=True)
        base.expect_page(heading=f"Рабочая зона (прикрепление): {case.room}", url="room_attachment")
        base.tab(name="Физические лица", section=True)
        base.tab(name="Доступные")
        base.grid_controller(search=case.client)
        base.grid(case.client, click=True)
        base.click(name="Прикрепить", exact=True)
        base.confirm_biruni(f"Прикрепить {case.client}?")
        case.client_attached = True
        base.tab(name="Прикрепленные")
        base.grid_controller(search=case.client)
        base.grid(case.client)

    for name, product_code, price, id_field in (
        (case.product, case.product_code, "100", "product_id"),
        (case.bonus_product, case.bonus_code, "1", "bonus_id"),
    ):
        with allure.step(f"Order setup: ТМЦ ro'yxati — {product_code}"):
            base.navigate_to(tab="Справочники", name="ТМЦ")
            base.expect_page(heading="ТМЦ", url="inventory_list")
            base.grid_controller(search=product_code)
            base.grid(state="empty")
        with allure.step(f"Order setup: {name} yaratish"):
            base.click(name="Создать", exact=True)
            base.expect_page(heading="ТМЦ (создание)", url=re.compile(r"inventory(?:\+|%2[bB])add"))
            base.input(label="Название", value=name)
            base.input(label="Код", value=product_code)
            base.b_input(label="Ед. изм.", value="шт", search_text="")
            base.checkbox(label="Активный", checked=True)
            base.checkbox(label="Товар", checked=True)
            base.checkbox(label="Продукция", checked=False)
            base.checkbox(label="Сырье", checked=False)
            base.multiselect(label="Наборы ТМЦ", clear=True, value=f"sector-pw{code}")
        with allure.step(f"Order setup: {name} saqlash"):
            base.click(name="Сохранить", exact=True)
            base.expect_page(heading="ТМЦ", url="inventory_list")
            base.grid_controller(search=product_code)
            base.grid(product_code, name, click=True)
        with allure.step(f"Order setup: {name} ID sini view'dan olish"):
            base.click(name="Просмотреть", exact=True)
            base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")
            setattr(case, id_field, query_int_from_url(page.url, "product_id"))
            base.form_view(label="Код", expect_value=product_code)
        with allure.step("Order setup: ТМЦ ro'yxatiga qaytish"):
            base.click(name="Закрыть", exact=True)
            base.expect_page(heading="ТМЦ", url="inventory_list")
            base.grid_controller(search=product_code)
            base.grid(product_code, name, click=True)
        with allure.step(f"Order setup: {name} uchun {price} USD narx"):
            base.click(name="Установить цены", exact=True)
            base.expect_page(heading="ТМЦ (установка цен)", url="product_set_price")
            base.input(label=case.price_type, value=price, press_tab=True)
        with allure.step("Order setup: narxni saqlash"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni("Сохранить?")
            base.expect_page(heading="ТМЦ", url="inventory_list")

    with allure.step("Order setup: boshlang'ich qoldiq ro'yxati"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
    with allure.step("Order setup: faqat ikki own mahsulot uchun kirim yaratish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)", url=re.compile(r"init_inventory_balance(?:\+|%2[bB])add"))
        base.input(ng_model="d.balance_number", value=case.reference)
        base.b_input(ng_model="d.warehouse_name", value=case.warehouse, clear=True)
        base.b_input(label="Валюта", value=case.currency, clear=True)
        for index, name in enumerate((case.product, case.bonus_product)):
            base.b_input(ng_model="item.product_name", value=name, index=index)
            base.input(ng_model="item.quantity", value="50", index=index, press_tab=True)
            base.input(ng_model="item.price", value="1", index=index, press_tab=True)
    with allure.step("Order setup: kirimni saqlash"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        case.receipt_number = case.reference
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid_controller(search=case.receipt_number)
        base.grid(case.receipt_number, click=True)
    with allure.step("Order setup: kirimni o'tkazish"):
        base.click(name="Провести", exact=True)
        base.confirm_biruni(f"Провести документ № {case.receipt_number}?")
        case.receipt_posted = True
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
        base.grid(case.receipt_number, "Да")
    allure.attach(json.dumps(asdict(case), ensure_ascii=False, indent=2, default=str), "Order testcase data", allure.attachment_type.JSON)


def cleanup_order_environment(page, case):
    """Faqat ro'yxatdan o'tkazilgan own IDlar; cleanup xatosi yashirilmaydi."""
    from tests.smoke.test_life_cycle.flow_order.order_regression import (
        ORDER_LISTS,
        change_order_status,
        open_order,
        open_saved_order,
    )
    from tests.smoke.test_life_cycle.flow_order.order_import import restore_order_import
    from tests.regression.test_orders.order_finance import cleanup_order_finance

    base = AutoBasePage(page)
    errors = []
    alert = page.locator('#biruniAlertExtended:visible, #biruniAlert:visible, [role="dialog"]:visible').filter(has_text=re.compile(r"ошибка|error", re.IGNORECASE))
    if alert.count():
        base.close_biruni_alert()
    if case.import_settings is not None:
        try:
            open_order(page, room=case.room, staff=case.staff, client=case.client)
            with allure.step("Cleanup: import mappingini tiklash formasini ochish"):
                base.click(name="Импорт", exact=True)
                base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
            restore_order_import(page, case.import_settings)
            case.import_settings = None
        except Exception as error:
            errors.append(f"Import settings: {type(error).__name__}: {error}")
    finance_clean = True
    try:
        cleanup_order_finance(page, case)
    except Exception as error:
        finance_clean = False
        errors.append(f"Finance: {type(error).__name__}: {error}")
    # Save muvaffaqiyatli bo'lib keyingi readback yiqilsa ham unikal own klient
    # orqali ID tiklanadi. Boshqa testcase klienti/hujjati tanlanmaydi.
    owned_orders = {}
    orders_clean = finance_clean
    if case.client_attached and finance_clean:
        for listing, (heading, route) in ORDER_LISTS.items():
            try:
                with allure.step(f"Cleanup: {heading} ichida faqat own klient orderlarini topish"):
                    base.navigate_to(tab="Продажа", name=heading)
                    base.expect_page(heading=heading, url=route)
                    id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД заказа", search_name="Клиент")
                    base.grid_controller(search=case.client)
                    if not base.grid(case.client, return_bool=True):
                        base.grid(state="empty")
                        continue
                    rows = page.locator("b-grid:visible .tbl-row").filter(has=page.get_by_text(case.client, exact=True))
                    expect(rows.first).to_be_visible()
                    for row in rows.all():
                        order_id = base.grid_cell(row, id_column, return_value=True, remove_spaces=True)
                        expect(base.grid_cell(row, id_column)).to_have_text(re.compile(r"^\d+$"))
                        owned_orders[order_id] = listing
            except Exception as error:
                orders_clean = False
                errors.append(f"Order discovery {listing}: {type(error).__name__}: {error}")
        missing = set(case.orders) - set(owned_orders)
        if missing:
            orders_clean = False
            errors.append(f"Ro'yxatdan o'tgan own order topilmadi: {sorted(missing)}")
        for order_id, listing in owned_orders.items():
            try:
                if order_id not in case.orders:
                    case.orders.append(order_id)
                if listing == "canceled":
                    open_saved_order(page, order_id, listing=listing)
                else:
                    if listing == "archive":
                        change_order_status(page, order_id, "Восстановить", listing="archive")
                    change_order_status(page, order_id, "Отменен")
                base.form_view(label="Статус", expect_value="Отменен")
            except Exception as error:
                orders_clean = False
                errors.append(f"Order {order_id}: {type(error).__name__}: {error}")

    for action_name in dict.fromkeys(case.action_names):
        try:
            with allure.step(f"Cleanup: own aksiya {action_name} ni nofaol qilish"):
                base.navigate_to(tab="Справочники", name="Акции")
                base.expect_page(heading="Акции", url="action_list")
            with allure.step("Cleanup: faol va nofaol aksiyalarni birga ko'rsatish"):
                base.grid_controller(open_filter=True)
                base.expect_page(heading="Фильтр", url="action_list")
                base.checkbox(label="Активный", checked=True)
                base.checkbox(label="Неактивный", checked=True)
                base.checkbox(label="Черновик", checked=True)
                base.click(name="Применить", exact=True)
                base.expect_page(heading="Акции", url="action_list")
            with allure.step(f"Cleanup: own aksiya {action_name} ID va statusini tiklash"):
                id_column = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="Название")
                status_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Статус")
                base.grid_controller(search=action_name)
                if not base.grid(action_name, return_bool=True):
                    base.grid(state="empty")
                    if case.actions:
                        raise AssertionError(f"Ro'yxatdan o'tgan own aksiya topilmadi: {action_name}, IDs={case.actions}")
                    continue
                expect(page.locator("b-grid:visible").get_by_text(action_name, exact=True)).to_have_count(1)
                row = base.grid(action_name, click=True)
                action_id = base.grid_cell(row, id_column, return_value=True, remove_spaces=True)
                expect(base.grid_cell(row, id_column)).to_have_text(re.compile(r"^\d+$"))
                if action_id not in case.actions:
                    case.actions.append(action_id)
                if base.grid_cell(row, status_column, return_value=True).strip() == "Неактивный":
                    continue
                base.action(name="Неактивный", menu="Изменить статус на")
                base.confirm_biruni()
                base.wait_for_loader()
                expect(base.grid_cell(base.grid(action_id), status_column)).to_have_text("Неактивный")
        except Exception as error:
            errors.append(f"Action {action_name}: {type(error).__name__}: {error}")

    if case.receipt_posted and orders_clean:
        try:
            with allure.step("Cleanup: own kirim hujjatini bekor qilish"):
                base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
                base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
                base.grid_controller(search=case.receipt_number)
                base.grid(case.receipt_number, click=True)
                base.click(name="Отменить", exact=True)
                base.confirm_biruni(f"Отменить документ № {case.receipt_number}?")
                base.wait_for_loader()
                base.grid(case.receipt_number, "Нет")
                case.receipt_posted = False
        except Exception as error:
            errors.append(f"Receipt {case.receipt_number}: {type(error).__name__}: {error}")

    if case.client_attached:
        try:
            with allure.step("Cleanup: ish zonalari ro'yxatini ochish"):
                base.navigate_to(tab="Справочники", name="Рабочие зоны")
                base.expect_page(heading="Рабочие зоны", url="room_list")
                base.grid_controller(search=case.room)
                base.grid(case.room, click=True)
            with allure.step("Cleanup: faqat own mijoz room birikmasini olib tashlash"):
                base.click(name="Прикрепление", exact=True)
                base.expect_page(heading=f"Рабочая зона (прикрепление): {case.room}", url="room_attachment")
                base.tab(name="Физические лица", section=True)
                base.tab(name="Прикрепленные")
                base.grid_controller(search=case.client)
                base.grid(case.client, click=True)
                base.click(name="Открепить", exact=True)
                base.confirm_biruni()
                base.wait_for_loader()
                base.grid_controller(search=case.client)
                base.grid(state="empty")
                case.client_attached = False
        except Exception as error:
            errors.append(f"Client attachment {case.client}: {type(error).__name__}: {error}")

    allure.attach(json.dumps({"retained": asdict(case), "cleanup_errors": errors}, ensure_ascii=False, indent=2, default=str), "Order cleanup", allure.attachment_type.JSON)
    if errors:
        raise AssertionError("Order cleanup yakunlanmadi:\n" + "\n".join(errors))
