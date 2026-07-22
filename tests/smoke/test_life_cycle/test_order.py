import allure
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    auto_filled_order_dates,
    flow_order_main_page,
    flow_order_product_page,
    flow_order_final_page,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list, flow_order_list_grid_setting
from tests.smoke.flows.flow_order.flow_order_view import flow_order_view
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Life Cycle"), allure.story("Order")]

# ----------------------------------------------------------------------------------------------------------------------

def run_order_basic(page, code, save_data):
    base = BasePage(page)
    authorization(page, who="user", code=code)

    with allure.step("Navigate To: Order Page"):
        base.navigate_to(tab="Продажа",
                    name="Заказы")

    with allure.step("Order List: Add Button"):
        flow_order_list(page, add=True)

    with allure.step("Order Add: Main Page"):
        deal_time, delivery_date = auto_filled_order_dates(page)
        flow_order_main_page(page,
                             check_form=True,
                             deal_time=deal_time,
                             delivery_date=delivery_date,
                             room=f"room-pw{code}",
                             robot=f"robot-pw{code}",
                             natural_client=f"natural_client-pw{code}",
                             next_page=True)

    with allure.step("Order Add: Product Page"):
        flow_order_product_page(page,
                                product=f"product-pw{code}",
                                quantity="1",
                                next_page=True)

    with allure.step("Order Add: Final Page"):
        flow_order_final_page(page,
                              payment_type="Наличные деньги",
                              status="Черновик",
                              save=True)

    with allure.step("Order List: View Button"):
        flow_order_list(page,
                        find_row=f"room-pw{code}",
                        view=True)

    with allure.step("Order View: Get Value"):
        order_data = flow_order_view(page,
                                     get_value=[
                                         "ИД заказа",
                                         "Дата заказа",
                                         "Дата отгрузки",
                                         "Статус",
                                         "Рабочая зона",
                                         "Штат",
                                         "Клиент",
                                         "Тип оплаты"
                                     ])
        save_data("order_id", order_data["ИД заказа"])

    with allure.step("Order View: Assert Values"):
        expected_view_data = {
            "Дата заказа": deal_time,
            "Дата отгрузки": delivery_date,
            "Статус": "Черновик",
            "Рабочая зона": f"room-pw{code}",
            "Штат": f"robot-pw{code}",
            "Клиент": f"natural_client-pw{code}",
            "Тип оплаты": "Наличные деньги",
        }
        actual_view_data = {key: order_data.get(key) for key in expected_view_data}
        assert actual_view_data == expected_view_data, (
            f"Order view qiymatlari mos kelmadi.\nExpected: {expected_view_data}\nActual: {actual_view_data}"
        )

    with allure.step("Order List: Edit Button"):
        flow_order_list(page, find_row=f"room-pw{code}", edit=True)

    with allure.step("Order Edit: Main Page"):
        flow_order_main_page(page,
                             check_form=True,
                             deal_time=deal_time,
                             delivery_date=delivery_date,
                             room=f"room-pw{code}",
                             robot=f"robot-pw{code}",
                             natural_client=f"natural_client-pw{code}",
                             next_page=True)

    with allure.step("Order Edit: Product Page"):
        flow_order_product_page(page,
                                check_form=True,
                                product=f"product-pw{code}",
                                quantity="1",
                                warehouse="Основной склад",
                                price_type=f"Price Type UZB-pw{code}",
                                next_page=True)

    with allure.step("Order Edit: Final Page"):
        flow_order_final_page(page,
                              check_form=True,
                              payment_type="Наличные деньги",
                              natural_client=f"natural_client-pw{code}",
                              room=f"room-pw{code}",
                              robot=f"robot-pw{code}",
                              status="Черновик",
                              save=True)

    with allure.step("Order List: Status Button"):
        flow_order_list(page, find_row=f"room-pw{code}", status="Новый")
        flow_order_list(page, find_row=f"room-pw{code}", status="В обработке")
        flow_order_list(page, find_row=f"room-pw{code}", status="В ожидании")
        flow_order_list(page, find_row=f"room-pw{code}", status="Отгружен")
        flow_order_list(page, find_row=f"room-pw{code}", status="Доставлен")
        # flow_order_list(page, find_row=f"room-pw{code}", status="Архив")
        # flow_order_list(page, find_row=f"room-pw{code}", status="Отменен")
        run_order_add_column_order_id(page, code)

# ----------------------------------------------------------------------------------------------------------------------

def run_order_add_column_order_id(page, code):

    with allure.step("Order List: Grid Setting"):
        flow_order_list_grid_setting(page, colum_name="ИД заказа", search_name="ИД заказа")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Order Basic")
def test_order_basic(page, code, save_data):
    run_order_basic(page, code, save_data)


@allure.title("Order Add Column -> Order Id")
def test_order_add_column_order_id(page, code):
    run_order_add_column_order_id(page, code)
