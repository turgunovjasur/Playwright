import allure
import re
from playwright.sync_api import expect

from tests.smoke.flows import flow_modal
from tests.smoke.flows.flow_navigate import navigate_to
from utils.base_page import BasePage

ORDER_VIEW_BUTTON_NAME = re.compile(r"^Просмотр(?:еть)?$")

# ----------------------------------------------------------------------------------------------------------------------


def _order_grid_row(page, row_text):
    row = page.locator("b-grid .tbl-row").filter(has_text=row_text).first
    expect(row).to_be_visible()
    return row


def _ensure_order_grid_row_open(page, row_text):
    row = _order_grid_row(page, row_text)
    if "open" not in (row.get_attribute("class") or "").split():
        row.click()
    expect(row.locator(".tbl-row-menu")).to_be_visible()
    return row


def flow_open_order_list(page):
    navigate_to(page, tab="Продажа", name="Заказы")
    expect(page).to_have_url(re.compile(r".*/order_list"))
    expect(page.get_by_role("heading")).to_contain_text("Заказы")
    expect(page.get_by_role("button", name="Создать", exact=True)).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_list(page, add=False, find_row=None, view=False, edit=False, status=None):
    page.wait_for_url("**/order_list")
    expect(page.get_by_role("heading")).to_contain_text("Заказы")

    if add:
        with allure.step("Order List: 'Создать' button click"):
            page.get_by_role("button", name="Создать", exact=True).click()
            return

    if find_row:
        with allure.step(f"Order List: find_row -> '{find_row}'"):
            row = _ensure_order_grid_row_open(page, find_row)
    else:
        row = None

    if view:
        with allure.step("Order List: 'Просмотр' button click"):
            button_scope = row or page
            button_scope.get_by_role("button", name=ORDER_VIEW_BUTTON_NAME).click()

    if edit:
        with allure.step("Order List: 'Изменить' button click"):
            button_scope = row or page
            button_scope.get_by_role("button", name="Изменить", exact=True).click()

    if status:
        with allure.step("Order List: 'Изменить статус' button click"):
            button_scope = row or page
            button_scope.get_by_role("button", name="Изменить статус", exact=True).click()

            flow_modal.dialog_status(page)

            page.get_by_role("link", name=status).click()
            # Smartup confirm matni: "Изменить статус на {status}?" (ilgari "Изменить на ...").
            BasePage(page).confirm_biruni(f"Изменить статус на {status}?")
            BasePage(page).wait_for_loader()

            if page.locator("#dropdown").count() > 0:
                expect(page.locator("#dropdown").first).to_contain_text(status)
            else:
                expect(page.get_by_role("heading")).to_contain_text("Заказы")

def flow_order_list_grid_setting(page, colum_name, search_name):
    page.wait_for_url("**/order_list")
    expect(page.get_by_role("heading")).to_contain_text("Заказы")
    page.locator(".btn.btn-default.dropdown-toggle.no-after").first.click()
    page.get_by_role("link", name="Настройка таблицы").click()

    expect(page.locator("#kt_content")).to_contain_text("Настройка таблицы: Заказы")
    page.locator("#deal_id").get_by_text(colum_name).click()
    page.locator("label").filter(has_text=search_name).click()
    expect(page.locator("#deal_id")).to_contain_text(colum_name)
    page.get_by_role("button", name="Сохранить").click()

    page.wait_for_url("**/order_list")
    expect(page.get_by_role("heading")).to_contain_text("Заказы")

# ----------------------------------------------------------------------------------------------------------------------
