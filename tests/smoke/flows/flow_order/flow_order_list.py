import re

import allure

from tests.smoke.flows import flow_modal
from utils.base_page import BasePage

ORDER_VIEW_BUTTON_NAME = re.compile(r"^Просмотр(?:еть)?$")

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_list(page, add=False, find_row=None, search=True, view=False, edit=False, status=None):
    base = BasePage(page)
    base.expect_page(heading="Заказы", url="order_list")
    row = None

    if (view or edit or status) and not find_row:
        raise ValueError("flow_order_list(): view/edit/status uchun find_row berilishi kerak")

    if add:
        with allure.step("Order List: 'Создать' button click"):
            page.get_by_role("button", name="Создать", exact=True).click()

    if find_row:
        with allure.step(f"Order List: find_row -> '{find_row}'"):
            if search:
                base.grid_controller(search=find_row)
            row = base.grid(find_row, click=True)

    if view:
        with allure.step("Order List: 'Просмотр' button click"):
            row.get_by_role("button", name=ORDER_VIEW_BUTTON_NAME).click()

    if edit:
        with allure.step("Order List: 'Редактировать' button click"):
            row.get_by_role("button", name="Редактировать", exact=True).click()

    if status:
        with allure.step("Order List: 'Изменить статус' button click"):
            row.get_by_role("button", name="Изменить статус", exact=True).click()

            flow_modal.dialog_status(page)

            page.get_by_role("link", name=status).click()
            # Smartup confirm matni: "Изменить статус на {status}?" (ilgari "Изменить на ...").
            base.confirm_biruni(f"Изменить статус на {status}?")
            base.wait_for_loader()

            if page.locator("#dropdown").count() > 0:
                base.text(status, root=page.locator("#dropdown").first)
            else:
                base.expect_page(heading="Заказы", url="order_list")

def flow_order_list_grid_setting(page, colum_name, search_name):
    base = BasePage(page)
    base.expect_page(heading="Заказы", url="order_list")
    base.grid_controller(open_setting=True)
    page.get_by_role("link", name="Настройка таблицы").click()

    base.text("Настройка таблицы: Заказы", root="#kt_content")
    page.locator("#deal_id").get_by_text(colum_name).click()
    page.locator("label").filter(has_text=search_name).click()
    base.text(colum_name, root="#deal_id")
    base.save_and_expect_heading("Заказы", location_hint="order list grid setting")
    base.expect_page(url="order_list")

# ----------------------------------------------------------------------------------------------------------------------
