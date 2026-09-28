import re

import allure

from tests.smoke.test_life_cycle.flow_order.flow_status_dialog import dialog_status
from utils.base_pages.auto_base_page import AutoBasePage

ORDER_VIEW_BUTTON_NAME = re.compile(r"^Просмотр(?:еть)?$")

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_list(page, add=False, find_row=None, search=True, view=False, edit=False, status=None):
    base = AutoBasePage(page)
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
        with allure.step("Order List: open view"):
            row.dblclick()

    if edit:
        with allure.step("Order List: 'Редактировать' button click"):
            row.hover()
            row.get_by_role("button", name="Редактировать", exact=True).click()

    if status:
        with allure.step("Order List: 'Изменить статус' button click"):
            row.hover()
            change_status = row.get_by_role("button", name="Изменить статус", exact=True)
            if change_status.count() > 0:
                change_status.first.click()
            else:
                row.locator("app-status-dropdown .dropdown-toggle, app-status-dropdown button").first.click()

            dialog_status(page)

            overlay = page.locator("[cdkmenu], [role='menu']").filter(visible=True)
            overlay.get_by_role("menuitem", name=status).or_(
                page.get_by_role("link", name=status)
            ).first.click()
            # Smartup confirm matni: "Изменить статус на {status}?" (ilgari "Изменить на ...").
            base.confirm_biruni(f"Изменить статус на {status}?")
            base.wait_for_loader()

            if page.locator("#dropdown").count() > 0:
                base.text(status, root=page.locator("#dropdown").first)
            else:
                base.expect_page(heading="Заказы", url="order_list")

def flow_order_list_grid_setting(page, colum_name, search_name):
    base = AutoBasePage(page)
    base.expect_page(heading="Заказы", url="order_list")
    base.grid_setting(menu_name="Настройка таблицы", field_name=colum_name, search_name=search_name)

# ----------------------------------------------------------------------------------------------------------------------
