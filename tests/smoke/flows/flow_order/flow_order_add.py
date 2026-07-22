import re
from datetime import datetime
from zoneinfo import ZoneInfo

import allure
from utils.base_page import BasePage

from tests.smoke.flows.flow_order.flow_order_list import flow_order_list

# ----------------------------------------------------------------------------------------------------------------------

def auto_filled_order_dates(page):
    base = BasePage(page)

    today = datetime.now(
        ZoneInfo("Asia/Tashkent")
    ).strftime("%d.%m.%Y")

    deal_time = base.input(
        locator="#anor279-input-deal_time",
        expect_value=re.compile(
            rf"^{re.escape(today)} \d{{2}}:\d{{2}}$"
        ),
        return_value=True,
    )

    delivery_date = base.input(
        locator="#anor279-input-delivery_date",
        expect_value=re.compile(
            rf"^{re.escape(today)}$"
        ),
        return_value=True,
    )

    return deal_time.strip(), delivery_date.strip()

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_main_page(
    page,
    check_form=False,
    deal_time=None,
    delivery_date=None,
    room=None,
    robot=None,
    natural_client=None,
    contract=None,
    contract_balance_text=None,
    next_page=True,
):
    base = BasePage(page)
    base.expect_page(url=re.compile(r".*/order\+(add|edit)"))
    base.text(re.compile(r"Заказ \((создание|изменение)\)"), root="#kt_content")

    if check_form:
        with allure.step("Main Page: Auto fill bo'lganini tekshirish"):
            base.input(locator="#anor279-input-deal_time", expect_value=deal_time)
            base.input(locator="#anor279-input-delivery_date", expect_value=delivery_date)
            base.b_input(label="Рабочая зона", expect_value=room)
            base.b_input(label="Штат", expect_value=robot)
            base.b_input(label="Клиент", expect_value=natural_client)

            if contract:
                base.b_input(label="Договор", expect_value=contract)

    if contract and not check_form:
        with allure.step(f"Main Page: contract -> '{contract}' tanlash"):
            base.b_input(label="Договор", value=contract, exact=False)
            if contract_balance_text:
                base.text(contract_balance_text, root="#kt_content")

    if next_page:
        with allure.step("Main Page: Keyingi page ga o'tish"):
            page.get_by_role("button", name="Далее").click()

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_product_page(
    page,
    check_form=False,
    product=None,
    quantity=None,
    warehouse=None,
    price_type=None,
    next_page=True,
):
    base = BasePage(page)
    base.text(re.compile(r"Заказ \((создание|изменение)\)"), root="#kt_content")
    product_grid = page.locator('b-pg-grid[name="goods_items"]')

    if product and not check_form:
        with allure.step(f"Product Page: product -> '{product}' tanlash"):
            base.b_input(label="Название", value=product, root=product_grid)

    if quantity and not check_form:
        with allure.step(f"Product Page: quantity -> '{quantity}' kiritish"):
            base.input(label="Кол-во", value=quantity, root=product_grid)

    if check_form:
        with allure.step(f"Product Page: "
                         f"Check product -> '{product}', "
                         f"Check warehouse -> '{warehouse}', "
                         f"Check price_type -> '{price_type}', "
                         f"Check quantity -> '{quantity}'"
                         ):
            base.b_input(label="Название", expect_value=product, root=product_grid)
            base.text(warehouse, price_type, root=product_grid)
            base.input(label="Кол-во", expect_value=quantity, root=product_grid)

    if next_page:
        with allure.step("Product Page: Keyingi page ga o'tish"):
            page.get_by_role("button", name="Далее").click()

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_final_page(page, check_form=False, payment_type=None, natural_client=None, room=None, robot=None, status=None, save=True):
    base = BasePage(page)
    base.text(re.compile(r"Заказ \((создание|изменение)\)"), root="#kt_content")

    if status and not check_form:
        with allure.step(f"Final Page: Order status -> '{status}' tanlash"):
            base.ui_select(label="Статус", value=status)

    if payment_type and not check_form:
        with allure.step(f"Final Page: Payment Type -> '{payment_type}' tanlash"):
            base.b_input(label="Тип оплаты", value=payment_type, clear=True)

    if check_form:
        with allure.step(f"Final Page: "
                         f"Check payment_type -> '{payment_type}',  "
                         f"Check status -> '{status}'"
                         f"Check natural_client -> '{natural_client}'"
                         f"Check room -> '{room}'"
                         f"Check robot -> '{robot}'"
            ):
            base.b_input(label="Тип оплаты", expect_value=payment_type)
            if status:
                base.ui_select(label="Статус", expect_value=status)
            base.text(natural_client, room, robot, root='form[name="step2"]')

    if save:
        with allure.step("Final Page: Order save qilish"):
            base.save_and_expect_heading(
                "Заказы",
                confirm_text="Сохранить?",
                exact_button=False,
                location_hint="order final wizard",
            )
            base.expect_page(url="order_list")

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_prepare_with_contract(
    page,
    code,
    contract_name,
    quantity,
    payment_type=None,
    status=None,
    contract_balance_text=None,
    save=False,
):
    flow_order_list(page, add=True)
    deal_time, delivery_date = auto_filled_order_dates(page)
    flow_order_main_page(
        page,
        check_form=True,
        deal_time=deal_time,
        delivery_date=delivery_date,
        room=f"room-pw{code}",
        robot=f"robot-pw{code}",
        natural_client=f"natural_client-pw{code}",
        next_page=False,
    )
    flow_order_main_page(
        page,
        contract=contract_name,
        contract_balance_text=contract_balance_text,
        next_page=True,
    )
    flow_order_product_page(
        page,
        product=f"product-pw{code}",
        quantity=quantity,
        next_page=True,
    )
    flow_order_final_page(
        page,
        payment_type=payment_type,
        status=status,
        save=save,
    )

# ----------------------------------------------------------------------------------------------------------------------
