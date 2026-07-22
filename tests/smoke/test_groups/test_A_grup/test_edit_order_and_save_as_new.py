import re

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    flow_order_final_page,
    flow_order_main_page,
    flow_order_product_page,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_order_list
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("Order"),
    allure.story("Edit Order"),
]

# ----------------------------------------------------------------------------------------------------------------------


def run_edit_order_and_save_as_new(page, code, load_data):
    """
    Testcase:
    1. Oldingi test yaratgan order id va contract name qiymatlarini data_store.json dan olish.
    2. Orderni edit qilish uchun listdan ochish.
    3. Main sahifadagi qiymatlarni tekshirib, keyingi sahifaga o'tish.
    4. Product sahifasidagi qiymatlarni tekshirib, keyingi sahifaga o'tish.
    5. Final sahifadagi asosiy qiymatlarni tekshirish.
    6. Order statusini Новый qilib saqlash.
    7. View oynasida order id, status va asosiy qiymatlarni tekshirish.
    """
    base = BasePage(page)

    with allure.step("1 - Order ma'lumotlari data_store.json dan olinadi"):
        order_id = load_data("a_group_payment_type_order_id")
        contract_name = load_data("a_group_contract_payment_type_name")
        if not order_id or not contract_name:
            raise AssertionError("Order ma'lumotlari topilmadi. Avval runnerdagi A-04 testni run qiling.")

    with allure.step("2 - Order edit qilish uchun listdan ochiladi"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.grid(f"natural_client-pw{code}")
        flow_order_list(page, find_row=f"natural_client-pw{code}", edit=True)
        base.expect_page(url=re.compile(rf".*/order\+edit.*deal_id={re.escape(order_id)}"))

    with allure.step("3 - Main sahifadagi qiymatlar tekshiriladi"):
        deal_time = base.input(
            locator="#anor279-input-deal_time",
            expect_value=re.compile(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"),
            return_value=True,
        )
        delivery_date = base.input(
            locator="#anor279-input-delivery_date",
            expect_value=re.compile(r"\d{2}\.\d{2}\.\d{4}"),
            return_value=True,
        )
        flow_order_main_page(
            page,
            check_form=True,
            deal_time=deal_time,
            delivery_date=delivery_date,
            room=f"room-pw{code}",
            robot=f"robot-pw{code}",
            natural_client=f"natural_client-pw{code}",
            contract=contract_name,
            next_page=True,
        )

    with allure.step("4 - Product sahifasidagi qiymatlar tekshiriladi"):
        flow_order_product_page(
            page,
            check_form=True,
            product=f"product-pw{code}",
            quantity="1",
            warehouse="Основной склад",
            price_type=f"Price Type UZB-pw{code}",
            next_page=True,
        )

    with allure.step("5 - Final sahifadagi qiymatlar tekshiriladi"):
        base.text(contract_name, f"product-pw{code}", "7 000", root="#kt_content")
        flow_order_final_page(
            page,
            check_form=True,
            payment_type="Наличные деньги",
            natural_client=f"natural_client-pw{code}",
            room=f"room-pw{code}",
            robot=f"robot-pw{code}",
            status="Черновик",
            save=False,
        )

    with allure.step("6 - Order statusi Новый qilib saqlanadi"):
        flow_order_final_page(page, status="Новый", save=True)
        base.expect_page(heading="Заказы", url="order_list")

    with allure.step("7 - View oynasidagi qiymatlar tekshiriladi"):
        flow_order_list(page, find_row=f"natural_client-pw{code}", view=True)
        base.expect_page(url="order_view")
        base.text(contract_name, f"product-pw{code}", "7 000", root="#kt_content")
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Дата заказа", expect_value=delivery_date)
        base.form_view(label="Дата отгрузки", expect_value=delivery_date)
        base.form_view(label="Статус", expect_value="Новый")
        base.form_view(label="Рабочая зона", expect_value=f"room-pw{code}")
        base.form_view(label="Штат", expect_value=f"robot-pw{code}")
        base.form_view(label="Клиент", expect_value=f"natural_client-pw{code}")
        base.form_view(label="Тип оплаты", expect_value="Наличные деньги")
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="Заказы", url="order_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Order editda statusni Новый qilib saqlash")
def test_edit_order_and_save_as_new(page, code, load_data):
    authorization(page, who="user", code=code)
    run_edit_order_and_save_as_new(page, code, load_data)
