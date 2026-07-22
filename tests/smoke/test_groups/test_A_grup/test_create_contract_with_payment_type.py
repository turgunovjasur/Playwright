import random

import allure
import pytest
from faker import Faker

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("Contracts"),
    allure.story("Contract Payment Type"),
]

# ----------------------------------------------------------------------------------------------------------------------


def run_create_contract_with_payment_type(page, code, save_data):
    """
    Testcase:
    1. Finans > Договоры ro'yxatini ochish.
    2. Payment type sharti uchun yangi contract yaratish formasini ochish.
    3. Contract asosiy maydonlarini va Типы оплат = Перечисление qiymatini to'ldirish.
    4. Contractni saqlab ro'yxatga qaytish.
    5. Yaratilgan contractni code orqali topib, list qiymatlarini tekshirish.
    6. Contract view oynasida asosiy qiymatlar va Тип оплаты ni tekshirish.
    7. View oynasini yopib contract ro'yxatiga qaytish.
    8. Contract code, name va payment type qiymatlarini keyingi testlar uchun saqlash.
    """
    contract_code = f"contract_payment_type_{random.randint(1000, 9999)}"
    contract_name = f"{Faker('ru_RU').company()} payment type contract-pw{code}"
    amount = "500000"
    payment_type = "Перечисление"
    base = BasePage(page)

    with allure.step("1 - Finans > Договоры ro'yxati ochiladi"):
        base.navigate_to(tab="Финансы", name="Договоры")
        base.expect_page(heading="Договоры", url="anor/mkf/contract_list")

    with allure.step("2 - Payment type sharti uchun contract yaratish formasi ochiladi"):
        page.get_by_role("button", name="Создать", exact=True).click()
        base.expect_page(heading="Договор (создание)", url="anor/mkf/contract+add")

    with allure.step("3 - Contract va Типы оплат maydonlari to'ldiriladi"):
        base.input(label="Код", value=contract_code)
        base.input(label="Номер", value=code)
        base.input(label="Название", value=contract_name)
        page.get_by_text("Физическое лицо", exact=True).click()
        base.radio("Физическое лицо", expect_checked=True)
        base.b_input(label="Физическое лицо", value=f"natural_client-pw{code}")
        base.b_input(label="Валюта", value="Узбекский сум")
        base.input(label="Сумма договора", value=amount)
        base.b_input(label="Типы оплат", value=payment_type)

    with allure.step("4 - Contract saqlanadi va ro'yxatga qaytiladi"):
        base.save_and_expect_heading(
            "Договоры",
            location_hint="A-02 payment type contract add form",
        )
        base.expect_page(url="anor/mkf/contract_list")

    with allure.step("5 - Yaratilgan contract listda tekshiriladi"):
        base.grid_controller(search=contract_code)
        base.grid(
            contract_code,
            contract_name,
            f"natural_client-pw{code}",
            "Узбекский сум",
            f"{int(amount):,}".replace(",", " "),
            click=True,
        )

    with allure.step("6 - Contract view oynasida payment type va asosiy qiymatlar tekshiriladi"):
        page.get_by_role("button", name="Просмотр", exact=True).click()
        base.expect_page(heading="Договор (просмотр)", url="anor/mkf/contract_view")
        base.form_view(label="Название", expect_value=contract_name)
        base.form_view(label="Код", expect_value=contract_code)
        base.form_view(label="Контрагент", expect_value=f"natural_client-pw{code}")
        base.form_view(label="Валюта", expect_value="Узбекский сум")
        base.form_view(label="Сумма договора", expect_value=amount)
        base.form_view(label="Тип оплаты", expect_value=payment_type)

    with allure.step("7 - View oynasi yopiladi va contract ro'yxatiga qaytiladi"):
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="Договоры", url="anor/mkf/contract_list")

    with allure.step("8 - Payment type contract ma'lumotlari keyingi testlar uchun saqlanadi"):
        save_data("a_group_contract_payment_type_code", contract_code)
        save_data("a_group_contract_payment_type_name", contract_name)
        save_data("a_group_contract_payment_type", payment_type)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Tip oplati sharti bilan contract yaratish")
def test_create_contract_with_payment_type(page, code, save_data):
    authorization(page, who="user", code=code)
    run_create_contract_with_payment_type(page, code, save_data)
