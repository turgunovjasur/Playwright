import re

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import flow_order_prepare_with_contract, auto_filled_order_dates
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("Order"),
    allure.story("Contract Limit"),
]

# ----------------------------------------------------------------------------------------------------------------------

def run_base_order(page, code):
    """
    Testcase:
    1. Order yaratish formasini ochish.
    2. Asosiy qadamdagi auto-fill sana, ishchi zona, shtat, vakil va klientni tekshirish.
    3. Product va miqdorni tanlash.
    4. To'lov turini tanlab, status va final summary qiymatlarini tekshirish.
    """
    base = BasePage(page)

    with allure.step("1 - Order yaratish formasini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        flow_order_list(page, add=True)

    with allure.step("2 - Asosiy qadam auto-fill qiymatlarini tekshirish"):
        base.expect_page(heading="Заказ (создание)", url="order+add")

        deal_time, delivery_date = auto_filled_order_dates(page)
        base.b_input(label="Рабочая зона", expect_value=f"room-pw{code}")
        base.b_input(label="Штат", expect_value=f"robot-pw{code}")
        base.form_view(label="Торговый представитель", expect_value=f"natural_person-pw{code}")
        base.b_input(label="Клиент", expect_value=f"natural_client-pw{code}")
        page.get_by_role("button", name="Далее").click()

    with allure.step("3 - Product va miqdorni tanlash"):
        product_grid = page.locator('b-pg-grid[name="goods_items"]')

        base.b_input(label="Название", value=f"product-pw{code}", root=product_grid)
        base.input(label="Кол-во", value="1", root=product_grid)
        page.get_by_role("button", name="Далее").click()

    with allure.step("4 - Final qadam qiymatlarini tekshirish"):
        base.b_input(label="Тип оплаты", value="Наличные деньги")
        base.ui_select(label="Статус", expect_value="Новый")

        base.form_view(label="ИТОГО", expect_value="7000", remove_spaces=True)
        base.form_view(label="Клиент", expect_value=f"natural_client-pw{code}")
        base.form_view(label="Рабочая зона", expect_value=f"room-pw{code}")
        base.form_view(label="Штат", expect_value=f"robot-pw{code}")

        base.form_view(label="Дата заказа", expect_value=deal_time)
        base.form_view(label="Дата отгрузки", expect_value=delivery_date)

        page.get_by_role("button", name="Сохранить", exact=False).first.click()
        base.confirm_biruni("Сохранить?")

    with allure.step("5 - Final qadam qiymatlarini tekshirish"):
        flow_order_list(page, find_row=f"room-pw{code}", search=False, view=True)

    with allure.step("5 - Final qadam qiymatlarini tekshirish"):
        base.expect_page(heading="Заказ / Просмотр", url="order_view")

        i = base.form_view(label="ИД заказа", return_value=True)
        print(f"order_view: {i}")


def run_contract_limit_validation_and_valid_order(page, code, load_data, save_data):
    """
    Testcase:
    1. Contract name qiymatini data_store.json dan olish.
    2. Oldingi orderlarni Отменен statusga o'tkazib, product bookingni tozalash.
    3. Contract bilan 700000 summali order tayyorlash.
    4. Contract limit errorini va order saqlanmaganini tekshirish.
    5. Shu contract bilan 7000 summali order tayyorlash.
    6. Limit ichidagi orderni muvaffaqiyatli saqlash.
    7. Order list va view oynasidagi asosiy qiymatlarni tekshirish.
    8. Order id qiymatini saqlab, order listga qaytish.
    """
    base = BasePage(page)

    with allure.step("1 - Contract name data_store.json dan olinadi"):
        contract_name = load_data("a_group_contract_name")
        if not contract_name:
            raise AssertionError("Contract name topilmadi. Avval runnerdagi A-01 testni run qiling.")

    with allure.step("2 - Oldingi orderlar bekor qilinib, product booking tozalanadi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        for _ in range(10):
            if not base.grid(f"natural_client-pw{code}", is_visible=True):
                break
            flow_order_list(page, find_row=f"natural_client-pw{code}", status="Отменен")
            base.navigate_to(tab="Продажа", name="Заказы")
            base.expect_page(heading="Заказы", url="order_list")

    with allure.step("3 - Contract bilan 700000 summali order tayyorlanadi"):
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="100",
            payment_type="Наличные деньги",
            status="Черновик",
            contract_balance_text="500 000",
        )
        base.text(
            "ИТОГО",
            "700 000",
            contract_name,
            "Наличные деньги",
            "Черновик",
            root="#kt_content",
        )

    with allure.step("4 - Contract limit errori va order saqlanmagani tekshiriladi"):
        page.get_by_role("button", name="Сохранить", exact=False).first.click()
        base.confirm_biruni("Сохранить?")
        base.text(
            "Сумма заказа превышает сумму остатка по договору",
            re.compile(r"Сумма остатка по договору: \d+"),
            "сумма заказа = 700000",
            root="body",
        )
        base.expect_page(heading="Заказ (создание)", url="order+add", root="#kt_content")
        base.close_biruni_alert()

    with allure.step("5 - Contract bilan 7000 summali order tayyorlanadi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="1",
            payment_type="Наличные деньги",
            status="Черновик",
            contract_balance_text="500 000",
        )
        base.text("ИТОГО", "7 000", contract_name, root="#kt_content")

    with allure.step("6 - Limit ichidagi order muvaffaqiyatli saqlanadi"):
        base.save_and_expect_heading(
            "Заказы",
            confirm_text="Сохранить?",
            exact_button=False,
            location_hint="A-03 contract limit order final page",
        )
        base.expect_page(url="order_list")

    with allure.step("7 - Order list va view oynasidagi qiymatlar tekshiriladi"):
        base.grid(f"natural_client-pw{code}", "7 000")
        flow_order_list(page, find_row=f"natural_client-pw{code}", view=True)
        base.expect_page(url="order_view")
        base.text(
            f"natural_client-pw{code}",
            contract_name,
            "Наличные деньги",
            "Черновик",
            f"product-pw{code}",
            "7 000",
            root="#kt_content",
        )

    with allure.step("8 - Order id saqlanadi va order listga qaytiladi"):
        save_data("a_group_order_id", base.form_view(label="ИД заказа", return_value=True))
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="Заказы", url="order_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Contract limit tekshiruvi va limit ichida order yaratish")
def test_base_order(page, code):
    authorization(page, who="user", code=code)
    run_base_order(page, code)

@allure.title("Contract limit tekshiruvi va limit ichida order yaratish")
def test_contract_limit_validation_and_valid_order(page, code, load_data, save_data):
    authorization(page, who="user", code=code)
    run_contract_limit_validation_and_valid_order(page, code, load_data, save_data)
