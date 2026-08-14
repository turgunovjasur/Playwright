import re

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import auto_filled_order_dates
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("0"),
    allure.epic("0 Group"),
    allure.feature("Order"),
    allure.story("Base Order"),
]

# ----------------------------------------------------------------------------------------------------------------------


def run_create_base_order(page, code, save_data):
    """Testcase: setup baseline asosida oddiy order yaratib, IDni saqlash.

    1. Clientning boshlang'ich settlement summalarini saqlash.
    2. Order listdan yangi order yaratish formasini ochish.
    3. Setup yaratgan auto-fill sana, room, robot, vakil va klientni tekshirish.
    4. Setup mahsulotini tanlab, ombor, narx turi, narx, miqdor va summani tekshirish.
    5. To'lov turi, default status va final summaryni tekshirib orderni saqlash.
    6. Yaratilgan orderni listda tekshirib, view formasini ochish.
    7. Order IDni saqlab, asosiy order qiymatlarini view formasida tekshirish.
    """
    base = BasePage(page)
    client = f"natural_client-pw{code}"
    product = f"product-pw{code}"
    room = f"room-pw{code}"
    robot = f"robot-pw{code}"
    representative = f"natural_person-pw{code}"
    price_type = f"Price Type UZB-pw{code}"

    with allure.step("1 - Clientning boshlang'ich settlement summalarini saqlash"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        base.grid_controller(search=client)

        if base.grid(client, root="b-grid:visible", return_bool=True):
            row = base.grid(client, root="b-grid:visible")
            base.grid_cell(row, 1, expect_value=client)
            base.grid_cell(row, 2, expect_value="Узбекский сум")
            baseline = {
                "debt": int(base.grid_cell(row, 3, return_value=True, remove_spaces=True)),
                "prepayment": int(base.grid_cell(row, 4, return_value=True, remove_spaces=True)),
                "order": int(base.grid_cell(row, 5, return_value=True, remove_spaces=True)),
                "reserved_prepayment": int(base.grid_cell(row, 6, return_value=True, remove_spaces=True)),
                "balance": int(base.grid_cell(row, 7, return_value=True, remove_spaces=True)),
            }
        else:
            base.grid(root="b-grid:visible", state="empty")
            baseline = {
                "debt": 0,
                "prepayment": 0,
                "order": 0,
                "reserved_prepayment": 0,
                "balance": 0,
            }

        save_data("group_0_offset_baseline", baseline)

    with allure.step("2 - Order listdan yaratish formasini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        flow_order_list(page, add=True)
        base.expect_page(heading="Заказ (создание)", url="order+add")

    with allure.step("3 - Setup baseline auto-fill qiymatlarini tekshirish"):
        deal_time, delivery_date = auto_filled_order_dates(page)
        base.b_input(label="Рабочая зона", expect_value=room)
        base.b_input(label="Штат", expect_value=robot)
        base.form_view(label="Торговый представитель", expect_value=representative)
        base.b_input(label="Клиент", expect_value=client)
        base.click(name="Далее")

    with allure.step("4 - Setup mahsuloti va hisob qiymatlarini tekshirish"):
        product_grid = 'b-pg-grid[name="goods_items"]'
        base.b_input(label="Название", value=product, root=product_grid)
        base.text("Основной склад", price_type, "7 000", root=product_grid)
        base.input(label="Кол-во", value="1", expect_value="1", root=product_grid)
        base.text(product, "7 000", root=product_grid)
        base.click(name="Далее")

    with allure.step("5 - Final summaryni tekshirib orderni saqlash"):
        base.b_input(label="Тип оплаты", value="Наличные деньги")
        base.ui_select(label="Статус", expect_value="Новый")
        base.form_view(label="ИТОГО", expect_value="7000", remove_spaces=True)
        base.form_view(label="Клиент", expect_value=client)
        base.form_view(label="Рабочая зона", expect_value=room)
        base.form_view(label="Штат", expect_value=robot)
        base.form_view(label="Дата заказа", expect_value=deal_time)
        base.form_view(label="Дата отгрузки", expect_value=delivery_date)
        base.grid(product, "1", "7 000", root='b-pg-grid[name="goods_items_view"]')
        base.click(name="Сохранить")
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="Заказы", url="order_list")

    with allure.step("6 - Yaratilgan orderni listda tekshirib view formasini ochish"):
        base.grid_controller(search=client)
        base.grid(client, "7 000", "Новый")
        flow_order_list(page, find_row=client, search=False, view=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")

    with allure.step("7 - Order viewdagi asosiy qiymatlarni tekshirish"):
        order_id = base.form_view(label="ИД заказа", expect_value=re.compile(r"^\d+$"), return_value=True)
        base.form_view(label="Дата заказа", expect_value=deal_time.split(" ", 1)[0])
        base.form_view(label="Дата отгрузки", expect_value=delivery_date)
        base.form_view(label="Статус", expect_value="Новый")
        base.form_view(label="Рабочая зона", expect_value=room)
        base.form_view(label="Штат", expect_value=robot)
        base.form_view(label="Клиент", expect_value=client)
        base.form_view(label="Тип оплаты", expect_value="Наличные деньги")
        base.grid(product, "1", "7 000", root='b-pg-grid[name="goods_items_view"]')
        save_data("group_0_order_id", order_id)
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Заказы", url="order_list")

    return order_id


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Setup baseline asosida oddiy order yaratish va IDni saqlash")
def test_create_base_order(page, code, save_data):
    authorization(page, who="user", code=code)
    run_create_base_order(page, code, save_data)
