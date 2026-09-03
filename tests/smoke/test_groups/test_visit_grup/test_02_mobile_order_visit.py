"""Orderli Visitni API orqali yaratib Web'da tekshirish testcase'i."""

import allure

from tests.smoke.clients.visit_sync import build_order_visit
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_mobile_authorization import authorize_mobile
from tests.smoke.flows.flow_navigate import navigate_to_a2
from tests.smoke.flows.flow_visit_sync import sync_visit
from utils.angular_base_page import AngularBasePage
from utils.helper_utils import query_int_from_url


def api_create_order_visit(load_data, save_data):
    """Mobile API orqali orderli Visit yaratib ``OrderVisit`` qaytaradi.

    1. Mobile API orqali login qilish va target filialni tekshirish.
    2. Sync endpoint orqali orderli Visit yaratish.
    """
    with allure.step("1 - Mobile API orqali login qilish"):
        mobile_authorization = authorize_mobile(load_data, save_data)

    with allure.step("2 - API orqali orderli Visit yaratish"):
        client_person_id = load_data("client_person_id")
        sales_manager_id = load_data("user_person_id")
        price_type_id = load_data("price_type_id_uzb")
        warehouse_id = load_data("warehouse_id")
        product_id = load_data("product_id")
        visit = build_order_visit(filial_id=load_data("filial_id"), room_id=load_data("room_id"), robot_id=load_data("robot_id"), client_person_id=client_person_id, sales_manager_id=sales_manager_id, currency_id=load_data("currency_id_uzb"), payment_type_id=load_data("payment_type_id"), price_type_id=price_type_id, warehouse_id=warehouse_id, product_id=product_id, price="7000", quantity="1", vat_percent=0, deal_recom_calculation_method="")
        order = visit.envelope["entries"][0]["value"]["orders"][0]
        item = order["items"][0]
        if order["person_id"] != int(client_person_id):
            raise AssertionError("Order person_id client_person_id bilan mos emas")
        if order["sales_manager_id"] != int(sales_manager_id):
            raise AssertionError("Order sales_manager_id user_person_id bilan mos emas")
        if (
            order["source_table"] != "MVTM_VISIT_HEADERS"
            or order["source_id"] != visit.entry_id
        ):
            raise AssertionError("Order parent Visit source invariantiga mos emas")
        if (
            item["price_type_id"] != int(price_type_id)
            or item["warehouse_id"] != int(warehouse_id)
            or item["product_id"] != int(product_id)
        ):
            raise AssertionError("Order item setup price type, warehouse yoki product ID bilan mos emas")

        sync_result = sync_visit(mobile_authorization, visit)
        if sync_result.entry_id != visit.entry_id:
            raise AssertionError("Sync response entry_id yuborilgan orderli Visit bilan mos emas")
        save_data("mobile_order_visit_id", visit.entry_id)
        save_data("mobile_order_visit_note", visit.visit_note)
        save_data("mobile_order_note", visit.order_note)
        save_data("mobile_order_visit_begun_on", visit.begun_on)
        save_data("mobile_order_visit_ended_on", visit.ended_on)
        save_data("mobile_order_deal_time", visit.deal_time)
        save_data("mobile_order_delivery_date", visit.delivery_date)
        save_data("mobile_order_price", visit.price)
        save_data("mobile_order_quantity", visit.quantity)
        save_data("mobile_order_vat_percent", visit.vat_percent)

    return visit


def web_verify_order_visit(page, visit, load_data, save_data):
    """Orderli Visit va linked orderni Web'da tekshirib order IDni qaytaradi.

    3. Web user sifatida login qilish.
    4. Visit listdan orderli Visitni topish.
    5. Visit viewdagi asosiy qiymatlarni tekshirish.
    6. Linked order grididagi product va summalarni tekshirish.
    7. Linked order viewdagi asosiy qiymatlarni tekshirish.
    """
    with allure.step("3 - Web user sifatida login qilish"):
        code = load_data("code")
        authorization(page, who="user", code=code)

    base = AngularBasePage(page)
    client_name = f"natural_client-pw{code}"
    user_person_name = f"natural_person-pw{code}"
    room_name = f"room-pw{code}"
    robot_name = f"robot-pw{code}"
    product_name = f"product-pw{code}"
    price_type_name = f"Price Type UZB-pw{code}"

    with allure.step("4 - Visit listda orderli Visitni unique note orqali topish"):
        navigate_to_a2(page, tab="Продажа", path="trade/tvt/visit_list")
        base.expect_page(heading="Визиты", url="trade/tvt/visit_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Примечание к визиту")
        visit_id_index = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД")
        base.grid_controller(search=client_name)
        visit_row = base.grid(visit.visit_note, client_name, room_name, user_person_name, "Новый")
        server_visit_id = int(base.grid_cell(visit_row, visit_id_index, return_value=True))
        if server_visit_id <= 0:
            raise AssertionError("Orderli Web Visit ID musbat integer emas")
        save_data("mobile_order_server_visit_id", server_visit_id)

    with allure.step("5 - Orderli Visit viewdagi asosiy qiymatlarni tekshirish"):
        visit_row.click()
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="Визит (просмотр)", url="trade/tvt/visit_view")
        if query_int_from_url(page.url, "visit_id") != server_visit_id:
            raise AssertionError("Orderli Visit row ID va view URL ID bir xil emas")
        base.input(label="ID визита", expect_value=str(server_visit_id))
        base.input(label="Статус", expect_value="Новый")
        base.input(label="Рабочая зона", expect_value=room_name)
        base.input(label="Пользователь", expect_value=user_person_name)
        base.input(label="Клиент", expect_value=client_name)

    with allure.step("6 - Linked order grididagi product va summalarni tekshirish"):
        base.click(name="Заказы", exact=True)
        base.wait_for_loader()
        order_row = base.grid(product_name, price_type_name, room_name, client_name, "Новый")
        base.grid_cell(order_row, 0, expect_value=price_type_name)
        base.grid_cell(order_row, 1, expect_value=visit.quantity)
        base.grid_cell(order_row, 2, expect_value=visit.price)
        base.grid_cell(order_row, 3, expect_value="0")
        base.grid_cell(order_row, 4, expect_value="0")
        base.grid_cell(order_row, 5, expect_value=visit.price)
        base.grid_cell(order_row, 6, expect_value=room_name)
        base.grid_cell(order_row, 7, expect_value=client_name)
        base.grid_cell(order_row, 8, expect_value="Новый")

    with allure.step("7 - Linked order viewdagi asosiy qiymatlarni tekshirish"):
        base.click(name="Действия", exact=True, root=order_row)
        base.expect_page(heading="Заказ / Просмотр", url="trade/tdeal/order/order_view")
        server_order_id = query_int_from_url(page.url, "deal_id")
        base.text(f"ИД заказа: {server_order_id}", "Статус: Новый", f"Рабочая зона: {room_name}", f"Штат: {robot_name}", f"Торговый представитель: {user_person_name}", f"Клиент: {client_name}", "Тип оплаты: Наличные деньги", "Валюта: Узбекский сум", f"Сумма заказа: {visit.price}")
        save_data("mobile_order_id", server_order_id)

    return server_order_id


def run_mobile_order_visit_check(page, load_data, save_data):
    """API yaratgan orderli Visit va linked orderni Web orqali tekshiradi."""
    visit = api_create_order_visit(load_data, save_data)
    return web_verify_order_visit(page, visit, load_data, save_data)
