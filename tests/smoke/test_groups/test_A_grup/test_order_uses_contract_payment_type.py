import re

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    flow_order_final_page,
    flow_order_prepare_with_contract,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("Order"),
    allure.story("Contract Payment Type"),
]

# ----------------------------------------------------------------------------------------------------------------------


def run_order_uses_contract_payment_type(page, code, load_data, save_data):
    """
    Testcase:
    1. Payment type contract ma'lumotlarini data_store.json dan olish.
    2. Oldingi orderlarni Отменен statusga o'tkazib, product bookingni tozalash.
    3. Contract bilan 700000 summali orderda limit errorini tekshirish.
    4. Shu contract bilan 7000 summali order tayyorlash.
    5. Тип оплаты auto-fill qiymatini tekshirib, uni o'zgartirish.
    6. O'zgartirilgan payment type bilan orderni saqlash.
    7. Order list va view oynasidagi asosiy qiymatlarni tekshirish.
    8. Order id qiymatini saqlab, order listga qaytish.
    """
    base = BasePage(page)

    with allure.step("1 - Payment type contract ma'lumotlari data_store.json dan olinadi"):
        contract_name = load_data("a_group_contract_payment_type_name")
        contract_payment_type = load_data("a_group_contract_payment_type")
        if not contract_name or not contract_payment_type:
            raise AssertionError("Payment type contract topilmadi. Avval runnerdagi A-02 testni run qiling.")

    with allure.step("2 - Oldingi orderlar bekor qilinib, product booking tozalanadi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        for _ in range(10):
            if not base.grid(f"natural_client-pw{code}", is_visible=True):
                break
            flow_order_list(page, find_row=f"natural_client-pw{code}", status="Отменен")
            base.navigate_to(tab="Продажа", name="Заказы")
            base.expect_page(heading="Заказы", url="order_list")

    with allure.step("3 - Contract bilan 700000 summali orderda limit errori tekshiriladi"):
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="100",
            contract_balance_text="500 000",
        )
        base.text("ИТОГО", "700 000", contract_name, root="#kt_content")
        base.b_input(label="Тип оплаты", expect_value=contract_payment_type)

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

    with allure.step("4 - Contract bilan 7000 summali order tayyorlanadi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="1",
            contract_balance_text="500 000",
        )
        base.text("ИТОГО", "7 000", contract_name, root="#kt_content")

    with allure.step("5 - Тип оплаты auto-fill qiymati tekshiriladi va o'zgartiriladi"):
        base.b_input(label="Тип оплаты", expect_value=contract_payment_type)
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.b_input(label="Тип оплаты", expect_value="Наличные деньги")

    with allure.step("6 - O'zgartirilgan payment type bilan order saqlanadi"):
        flow_order_final_page(page, status="Черновик", save=True)
        base.expect_page(heading="Заказы", url="order_list")

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
        save_data("a_group_payment_type_order_id", base.form_view(label="ИД заказа", return_value=True))
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="Заказы", url="order_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Contract payment type auto-fill va limit tekshiruvi")
def test_order_uses_contract_payment_type(page, code, load_data, save_data):
    authorization(page, who="user", code=code)
    run_order_uses_contract_payment_type(page, code, load_data, save_data)
