import re

import allure
from playwright.sync_api import expect
from utils.base_page import BasePage

from tests.smoke.flows.flow_order.flow_order_list import flow_order_list

# ----------------------------------------------------------------------------------------------------------------------

def auto_filled_order_dates(page):
    deal_time_input = page.locator("#anor279-input-deal_time")
    delivery_date_input = page.locator("#anor279-input-delivery_date")
    expect(deal_time_input).to_have_value(re.compile(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"))
    expect(delivery_date_input).to_have_value(re.compile(r"\d{2}\.\d{2}\.\d{4}"))
    return deal_time_input.input_value().strip(), delivery_date_input.input_value().strip()

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
    page.wait_for_url(re.compile(r".*/order\+(add|edit)"))
    expect(page.locator("#kt_content")).to_have_text(re.compile(r"Заказ \((создание|изменение)\)"))

    if check_form:
        with allure.step("Main Page: Auto fill bo'lganini tekshirish"):
            expect(page.locator("#anor279-input-deal_time")).to_have_value(deal_time)
            expect(page.locator("#anor279-input-delivery_date")).to_have_value(delivery_date)
            expect(page.locator("#anor279-input-b_input-room_name").get_by_role("textbox", name="Поиск")).to_have_value(room)
            expect(page.locator("#anor279-input-b_input-robot_name").get_by_role("textbox", name="Поиск")).to_have_value(robot)
            expect(page.locator("#anor279-input-b_input-person_name").get_by_role("textbox", name="Поиск")).to_have_value(natural_client)

            if contract:
                expect(page.locator("b-page")).to_contain_text(contract)

    if contract and not check_form:
        with allure.step(f"Main Page: contract -> '{contract}' tanlash"):
            base.b_input(label="Договор", value=contract, exact=False)
            if contract_balance_text:
                expect(page.locator("#kt_content")).to_contain_text(contract_balance_text)

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
    expect(page.locator("#kt_content")).to_have_text(re.compile(r"Заказ \((создание|изменение)\)"))

    if product and not check_form:
        with allure.step(f"Product Page: product -> '{product}' tanlash"):
            # Product b-input dropdownidagi option matni kombinatsiyalangan
            # ("product-pw{code}  <ombor>  <price type>  <narx>"), shuning uchun
            # page-wide get_by_text(product) bir nechta elementga tushib flaky bo'ladi.
            # Dropdownni shu b-inputga scope qilib, hint-item ko'rinishini kutib bosamiz.
            product_input = page.locator("#anor279_input-b_input-product_name_goods0")
            search = product_input.get_by_role("textbox", name="Поиск")
            search.click()
            search.fill(product)
            option = product_input.locator(".hint-item").filter(has_text=product).first
            expect(option).to_be_visible()
            option.click()
            expect(product_input.locator("input").first).to_have_value(product)

    if quantity and not check_form:
        with allure.step(f"Product Page: quantity -> '{quantity}' kiritish"):
            page.locator("#anor279_input-b_pg_col-quantity_0").fill(quantity)

    if check_form:
        with allure.step(f"Product Page: "
                         f"Check product -> '{product}', "
                         f"Check warehouse -> '{warehouse}', "
                         f"Check price_type -> '{price_type}', "
                         f"Check quantity -> '{quantity}'"
                         ):
            expect(page.locator("#anor279_input-b_input-product_name_goods0").get_by_role("textbox", name="Поиск")).to_have_value(product)
            expect(page.locator("#anor279_input-b_pg_grid-goods_items")).to_contain_text(warehouse)
            expect(page.locator("#anor279_input-b_pg_grid-goods_items")).to_contain_text(price_type)
            expect(page.locator("#anor279_input-b_pg_col-quantity_0")).to_have_value(quantity)

    if next_page:
        with allure.step("Product Page: Keyingi page ga o'tish"):
            page.get_by_role("button", name="Далее").click()

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_final_page(page, check_form=False, payment_type=None, natural_client=None, room=None, robot=None, status=None, save=True):
    base = BasePage(page)
    expect(page.locator("#kt_content")).to_have_text(re.compile(r"Заказ \((создание|изменение)\)"))

    if status and not check_form:
        with allure.step(f"Final Page: Order status -> '{status}' tanlash"):
            page.locator("#anor279-ui_select-status:visible").get_by_label("Select box activate").click()
            option = page.locator(".ui-select-choices-row-inner").get_by_text(status, exact=True)
            expect(option).to_be_visible()
            option.click()

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
            expect(page.locator("#anor279-ui_select-status:visible")).to_contain_text(status)
            expect(page.locator("form[name=\"step2\"]")).to_contain_text(natural_client)
            expect(page.locator("form[name=\"step2\"]")).to_contain_text(room)
            expect(page.locator("form[name=\"step2\"]")).to_contain_text(robot)

    if save:
        with allure.step("Final Page: Order save qilish"):
            # Order wizard tugmasida fa-save ikonka bor: ::before glyph accessible name'ga
            # qo'shilib exact match buziladi, shuning uchun exact=False
            page.get_by_role("button", name="Сохранить", exact=False).first.click()
            base.confirm_biruni("Сохранить?")
            base.wait_for_loader()
            base.expect_page(heading="Заказы")

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
