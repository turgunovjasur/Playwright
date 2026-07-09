import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    flow_order_final_page,
    flow_order_main_page,
    flow_order_product_page,
    flow_order_prepare_with_contract,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_open_order_list, flow_order_list
from tests.smoke.flows.flow_order.flow_order_view import flow_order_view
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("A"),
    allure.epic("A Group"),
    allure.feature("Order"),
    allure.story("Order With Contract"),
]


def _close_extended_alert(page):
    alert = page.locator("#biruniAlertExtended")
    expect(alert).to_be_visible()
    alert.locator("button.close").click()
    alert.wait_for(state="hidden")


def run_a_group_contract_limit_validation_and_valid_order(
    page,
    code,
    load_data,
    save_data,
    login=True,
):
    """
    Testcase:
    1. User sifatida tizimga kirish.
    2. A-group contract testida yaratilgan contract name qiymatini data_store.json dan olish.
    3. Order listdagi oldin yaratilgan orderlarni Отменен statusga o'tkazib, product bookingni tozalash.
    4. Contract bilan 700000 summali zakaz yaratib, limit error xabarini tekshirish.
    5. Limitdan oshgan zakaz saqlanmay, order add formasida qolganini tekshirish.
    6. Order listga qaytib, shu contract bilan 1 ta mahsulotli zakaz yaratish.
    7. 7000 summali zakaz muvaffaqiyatli saqlanishini tekshirish.
    8. Zakaz listda ko'rinishini va view oynasida contract, client, summa, product ko'ringanini tekshirish.
    9. Order id qiymatini keyingi A-group testlari uchun data_store.json ga saqlash.
    """
    base = BasePage(page)

    if login:
        with allure.step("1 - User tizimga muvaffaqiyatli kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - A-group contract name data_store.json dan olinadi"):
        contract_name = load_data("a_group_contract_name") or load_data("contract_name")
        if not contract_name:
            raise AssertionError("A-group contract name topilmadi. Avval A-01 testni run qiling.")

    with allure.step("3 - Eski orderlar Отменен statusga o'tkazilib, product booking tozalanadi"):
        flow_open_order_list(page)
        expect(page.locator("b-grid")).to_contain_text("Статус")
        for _ in range(10):
            if page.locator("b-grid .tbl-row").filter(has_text=f"natural_client-pw{code}").count() == 0:
                break
            flow_order_list(page, find_row=f"natural_client-pw{code}", status="Отменен")
            flow_open_order_list(page)
            expect(page.locator("b-grid")).to_contain_text("Статус")

    with allure.step("4 - Contract bilan 700000 summali zakaz tayyorlanadi"):
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="100",
            payment_type="Наличные деньги",
            status="Черновик",
            contract_balance_text="500 000",
        )
        expect(page.locator("#kt_content")).to_contain_text("ИТОГО")
        expect(page.locator("#kt_content")).to_contain_text("700 000")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        expect(page.locator("#kt_content")).to_contain_text("Наличные деньги")
        expect(page.locator("#kt_content")).to_contain_text("Черновик")

    with allure.step("5 - Contract limitidan oshgani uchun save xabari chiqadi"):
        page.get_by_role("button", name="Сохранить").click()
        base.confirm_biruni("Сохранить?")
        expect(page.locator("body")).to_contain_text("Сумма заказа превышает сумму остатка по договору")
        expect(page.locator("body")).to_contain_text(re.compile(r"Сумма остатка по договору: \d+"))
        expect(page.locator("body")).to_contain_text("сумма заказа = 700000")
        expect(page).to_have_url(re.compile(r".*/order\+add"))
        expect(page.locator("#kt_content")).to_contain_text("Заказ (создание)")
        _close_extended_alert(page)

    with allure.step("6 - Order listga qaytib, contract bilan 1 ta mahsulotli zakaz tayyorlanadi"):
        flow_open_order_list(page)
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="1",
            payment_type="Наличные деньги",
            status="Черновик",
            contract_balance_text="500 000",
        )
        expect(page.locator("#kt_content")).to_contain_text("ИТОГО")
        expect(page.locator("#kt_content")).to_contain_text("7 000")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)

    with allure.step("7 - 7000 summali zakaz muvaffaqiyatli saqlanadi"):
        # Order wizard save tugmasi ikonkali: exact accessible name mos kelmaydi -> exact=False
        page.get_by_role("button", name="Сохранить", exact=False).first.click()
        base.confirm_biruni("Сохранить?")
        base.wait_for_loader()
        base.expect_page(heading="Заказы")
        expect(page).to_have_url(re.compile(r".*/order_list"))

    with allure.step("8 - Zakaz list va view oynasida contract bilan tekshiriladi"):
        expect(page.locator("b-grid")).to_contain_text("7 000")
        page.locator("b-grid").get_by_text("7 000").first.click()
        expect(page.get_by_role("button", name="Просмотреть", exact=True)).to_be_visible()
        page.get_by_role("button", name="Просмотреть", exact=True).click()
        expect(page).to_have_url(re.compile(r".*/order_view"))
        base.wait_for_loader()
        expect(page.locator("#kt_content")).to_contain_text(f"natural_client-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        expect(page.locator("#kt_content")).to_contain_text("Наличные деньги")
        expect(page.locator("#kt_content")).to_contain_text("Черновик")
        expect(page.locator("#kt_content")).to_contain_text(f"product-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text("7 000")

    with allure.step("9 - Order id keyingi A-group testlari uchun saqlanadi"):
        save_data("a_group_order_id", page.locator('//t[contains(text(),"ИД заказа")]/../../span').inner_text().strip())
        page.get_by_role("button", name="Закрыть").click()
        expect(page).to_have_url(re.compile(r".*/order_list"))


def run_a_group_order_uses_contract_payment_type(
    page,
    code,
    load_data,
    save_data,
    login=True,
):
    """
    Testcase:
    1. User sifatida tizimga kirish.
    2. Типы оплат = Перечисление bilan yaratilgan contract ma'lumotlarini data_store.json dan olish.
    3. Order listdagi oldin yaratilgan orderlarni Отменен statusga o'tkazib, product bookingni tozalash.
    4. Shu contract bilan 700000 summali zakaz yaratib, contract limit error xabarini tekshirish.
    5. Shu contract bilan 1 ta mahsulotli zakaz yaratib, Тип оплаты avtomatik Перечисление bo'lib kelganini tekshirish.
    6. User Тип оплаты qiymatini Наличные деньги ga o'zgartira olishini va order saqlanishini tekshirish.
    7. Zakaz view oynasida contract, o'zgartirilgan payment type, client, product va summa ko'ringanini tekshirish.
    8. Order id qiymatini keyingi A-group testlari uchun data_store.json ga saqlash.
    """
    base = BasePage(page)

    if login:
        with allure.step("1 - User tizimga muvaffaqiyatli kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - Tip oplati contract ma'lumotlari data_store.json dan olinadi"):
        contract_name = load_data("a_group_contract_payment_type_name") or load_data("contract_payment_type_name")
        contract_payment_type = load_data("a_group_contract_payment_type") or load_data("contract_payment_type")
        if not contract_name or not contract_payment_type:
            raise AssertionError(
                "Tip oplati contract ma'lumotlari topilmadi. Avval "
                "A-02 testni run qiling."
            )

    with allure.step("3 - Eski orderlar Отменен statusga o'tkazilib, product booking tozalanadi"):
        flow_open_order_list(page)
        expect(page.locator("b-grid")).to_contain_text("Статус")
        for _ in range(10):
            if page.locator("b-grid .tbl-row").filter(has_text=f"natural_client-pw{code}").count() == 0:
                break
            flow_order_list(page, find_row=f"natural_client-pw{code}", status="Отменен")
            flow_open_order_list(page)
            expect(page.locator("b-grid")).to_contain_text("Статус")

    with allure.step("4 - Tip oplati contract bilan 700000 summali zakaz error beradi"):
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="100",
            contract_balance_text="500 000",
        )
        expect(page.locator("#kt_content")).to_contain_text("ИТОГО")
        expect(page.locator("#kt_content")).to_contain_text("700 000")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        base.b_input(label="Тип оплаты", expect_value=contract_payment_type)

        page.get_by_role("button", name="Сохранить").click()
        base.confirm_biruni("Сохранить?")
        expect(page.locator("body")).to_contain_text("Сумма заказа превышает сумму остатка по договору")
        expect(page.locator("body")).to_contain_text(re.compile(r"Сумма остатка по договору: \d+"))
        expect(page.locator("body")).to_contain_text("сумма заказа = 700000")
        expect(page).to_have_url(re.compile(r".*/order\+add"))
        _close_extended_alert(page)

    with allure.step("5 - Tip oplati contract bilan 1 ta mahsulotli zakaz tayyorlanadi"):
        flow_open_order_list(page)
        flow_order_prepare_with_contract(
            page,
            code,
            contract_name,
            quantity="1",
            contract_balance_text="500 000",
        )
        expect(page.locator("#kt_content")).to_contain_text("ИТОГО")
        expect(page.locator("#kt_content")).to_contain_text("7 000")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)

    with allure.step("6 - Contractdagi Типы оплат auto-fill bo'ladi va user uni o'zgartira oladi"):
        base.b_input(label="Тип оплаты", expect_value=contract_payment_type)
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.b_input(label="Тип оплаты", expect_value="Наличные деньги")

    with allure.step("7 - O'zgartirilgan tip oplati bilan zakaz muvaffaqiyatli saqlanadi"):
        flow_order_final_page(
            page,
            status="Черновик",
            save=True,
        )
        expect(page).to_have_url(re.compile(r".*/order_list"))
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

    with allure.step("8 - Zakaz view oynasida contract va o'zgartirilgan tip oplati tekshiriladi"):
        expect(page.locator("b-grid")).to_contain_text("7 000")
        page.locator("b-grid").get_by_text("7 000").first.click()
        expect(page.get_by_role("button", name="Просмотреть", exact=True)).to_be_visible()
        page.get_by_role("button", name="Просмотреть", exact=True).click()
        expect(page).to_have_url(re.compile(r".*/order_view"))
        base.wait_for_loader()
        expect(page.locator("#kt_content")).to_contain_text(f"natural_client-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        expect(page.locator("#kt_content")).to_contain_text("Наличные деньги")
        expect(page.locator("#kt_content")).to_contain_text("Черновик")
        expect(page.locator("#kt_content")).to_contain_text(f"product-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text("7 000")

    with allure.step("9 - Tip oplati order id keyingi A-group testlari uchun saqlanadi"):
        save_data("a_group_payment_type_order_id", page.locator('//t[contains(text(),"ИД заказа")]/../../span').inner_text().strip())
        page.get_by_role("button", name="Закрыть").click()
        expect(page).to_have_url(re.compile(r".*/order_list"))


def run_a_group_edit_order_and_save_as_new(
    page,
    code,
    load_data,
    login=True,
):
    """
    Testcase:
    1. User sifatida tizimga kirish.
    2. A-04 testida yaratilgan order id va contract name qiymatlarini data_store.json dan olish.
    3. Order listda yaratilgan orderni edit qilish uchun ochish.
    4. Edit asosiy sahifasidagi mavjud qiymatlar to'g'ri ko'rinishini tekshirib, hech narsa o'zgartirmasdan keyingi sahifaga o'tish.
    5. Product sahifasidagi product, sklad, price type va quantity qiymatlari o'zgarmaganini tekshirib, keyingi sahifaga o'tish.
    6. Final sahifada client, room, robot, contract, payment type, status va summa tekshiriladi.
    7. Order statusi Новый qilib saqlanadi.
    8. Saqlangandan keyin view oynasida order id va asosiy qiymatlar to'g'riligi tekshiriladi.
    """

    if login:
        with allure.step("1 - User tizimga muvaffaqiyatli kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - A-04 yaratgan order ma'lumotlari data_store.json dan olinadi"):
        order_id = load_data("a_group_payment_type_order_id")
        contract_name = load_data("a_group_contract_payment_type_name")
        if not order_id or not contract_name:
            raise AssertionError(
                "A-04 order ma'lumotlari topilmadi. Avval A-group runnerni A-01 dan boshlab run qiling."
            )

    with allure.step("3 - Yaratilgan order edit qilish uchun ochiladi"):
        flow_open_order_list(page)
        expect(page.locator("b-grid")).to_contain_text(f"natural_client-pw{code}")
        flow_order_list(page, find_row=f"natural_client-pw{code}", edit=True)
        expect(page).to_have_url(re.compile(rf".*/order\+edit.*deal_id={re.escape(order_id)}"))

    with allure.step("4 - Edit asosiy sahifasida qiymatlar tekshiriladi va hech narsa o'zgartirilmaydi"):
        deal_time_input = page.locator("#anor279-input-deal_time")
        delivery_date_input = page.locator("#anor279-input-delivery_date")
        expect(deal_time_input).to_have_value(re.compile(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"))
        expect(delivery_date_input).to_have_value(re.compile(r"\d{2}\.\d{2}\.\d{4}"))
        deal_time = deal_time_input.input_value().strip()
        delivery_date = delivery_date_input.input_value().strip()

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

    with allure.step("5 - Product sahifasida qiymatlar tekshiriladi va hech narsa o'zgartirilmaydi"):
        flow_order_product_page(
            page,
            check_form=True,
            product=f"product-pw{code}",
            quantity="1",
            warehouse="Основной склад",
            price_type=f"Price Type UZB-pw{code}",
            next_page=True,
        )

    with allure.step("6 - Final sahifada qiymatlar tekshiriladi"):
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        expect(page.locator("#kt_content")).to_contain_text(f"product-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text("7 000")
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

    with allure.step("7 - Order statusi Новый qilib saqlanadi"):
        flow_order_final_page(
            page,
            status="Новый",
            save=True,
        )
        expect(page).to_have_url(re.compile(r".*/order_list"))
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

    with allure.step("8 - View oynasida editdan keyin qiymatlar tekshiriladi"):
        flow_order_list(page, find_row=f"natural_client-pw{code}", view=True)
        expect(page.locator("#kt_content")).to_contain_text(contract_name)
        expect(page.locator("#kt_content")).to_contain_text(f"product-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text("7 000")
        order_data = flow_order_view(
            page,
            get_value=[
                "ИД заказа",
                "Дата заказа",
                "Дата отгрузки",
                "Статус",
                "Рабочая зона",
                "Штат",
                "Клиент",
                "Тип оплаты",
            ],
        )
        expected_values = {
            "ИД заказа": order_id,
            "Дата заказа": delivery_date,
            "Дата отгрузки": delivery_date,
            "Статус": "Новый",
            "Рабочая зона": f"room-pw{code}",
            "Штат": f"robot-pw{code}",
            "Клиент": f"natural_client-pw{code}",
            "Тип оплаты": "Наличные деньги",
        }
        for key, expected in expected_values.items():
            actual = order_data.get(key)
            if actual != expected:
                raise AssertionError(f"{key} o'zgargan. Expected: {expected!r}, actual: {actual!r}")


@allure.title("A Group: Contract limit tekshiruvi va limit ichida zakaz yaratish")
def test_a_group_contract_limit_validation_and_valid_order(page, code, load_data, save_data):
    run_a_group_contract_limit_validation_and_valid_order(page, code, load_data, save_data)


@allure.title("A Group: Contract tip oplati auto-fill va limit tekshiruvi")
def test_a_group_order_uses_contract_payment_type(page, code, load_data, save_data):
    run_a_group_order_uses_contract_payment_type(page, code, load_data, save_data)


@allure.title("A Group: Order editda statusni Новый qilib saqlash")
def test_a_group_edit_order_and_save_as_new(page, code, load_data):
    run_a_group_edit_order_and_save_as_new(page, code, load_data)
