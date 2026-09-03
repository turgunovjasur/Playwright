import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Warehouse")]

# ----------------------------------------------------------------------------------------------------------------------


def run_warehouse(page, save_data):
    """Asosiy ombor view formasidan warehouse IDni olish va saqlash.

    1. Склад -> Склады ro'yxatini ochish.
    2. Основной склад view formasini ochish va tekshirish.
    3. View URLdan warehouse IDni olib, data_store ga saqlash.
    4. View formasini yopib, omborlar ro'yxatiga qaytish.
    """
    base = BasePage(page)

    with allure.step("1 - Omborlar ro'yxatini ochish"):
        base.navigate_to(tab="Склад", name="Склады")
        base.expect_page(heading="Склады", url="warehouse_list")

    with allure.step("2 - Asosiy ombor view formasini ochish va tekshirish"):
        base.grid("Основной склад", click=True)
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="Склад (просмотр)", url="warehouse_view?warehouse_id=")
        base.text("Основной склад", "Активный")

    with allure.step("3 - Warehouse IDni olish va saqlash"):
        save_data("warehouse_id", query_int_from_url(page.url, "warehouse_id"))

    with allure.step("4 - View formasini yopib, omborlar ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Склады", url="warehouse_list")


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Asosiy ombor ID sini olish")
def test_warehouse(page, code, save_data):
    authorization(page, who="user", code=code)
    run_warehouse(page, save_data)
