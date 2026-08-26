import re
from uuid import uuid4

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, open_report
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("Report", independent=True),
    allure.epic("Report Group"),
    allure.feature("Integration Report"),
    allure.story("Integration Two"),
]

# ----------------------------------------------------------------------------------------------------------------------

def run_report_integration_two_check(page):
    """Testcase: Monolith settings, beshta XML va Export order errorini tekshirish.

    1. Administration filialida Integration Two reportini ochish.
    2. Mavjud Monolith endpoint/user sozlamalarini tekshirib report filterlarini saqlash.
    3. Saqlangan price type va o'lchov birliklarini qayta tekshirish.
    4. Import order XML downloadini tekshirish.
    5. Export order error modalini yopib davom etish.
    6. Export status XML downloadini tekshirish.
    7. Export balance XML downloadini tekshirish.
    8. Export input XML downloadini tekshirish.
    9. Export internal movement XML downloadini tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]

    authorization(page, who="admin")

    with allure.step("1 - Administration filialida Integration Two reportini ochish"):
        base.switch_filial(name="Администрирование")
        open_report(base, "integration_two", timeout=60_000)
        base.expect_page(heading="Интеграция с системой монолит", url="integration_two")

    with allure.step("2 - Monolith endpoint preconditioni va report filterlarini saqlash"):
        base.click(name="Настройки", exact=True)
        base.input(label="User", value=123)
        base.input(label="URL", value="https://qa-assistant.uz/")
        base.b_input(label="Тип цены", clear=True, select_first=True)
        base.input(label="Ед. измерения (количество)", expect_value="шт", value="шт")
        base.input(label="Ед. измерения (блок)", expect_value="шт", value="шт")

        base.checkbox(label="Редактирование контрагента", checked=True)
        base.checkbox(label="Отправлять данные по всем заказам", checked=True)
        base.checkbox(label="Игнорировать обновление существующих заказов", checked=True)
        base.checkbox(label="Отображать код владельца", checked=True)

        base.b_input(label="Характеристика ТМЦ", value="Группа", clear=True)
        base.checkbox(label="Подтипы характеристик ТМЦ", expect_checked=True)
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Интеграция с системой монолит", url="integration_two")

    with allure.step("4 - Import order XML downloadini tekshirish"):
        base.radio(label="Импорт заказа", click=True, expect_checked=True)
        generate_and_verify_download(base, "Генерировать", None, f"integration_two_import_order_pw{run_suffix}.xml", expected_suffix=".xml")

    with allure.step("close_biruni_alert"):
        base.close_biruni_alert()

    with allure.step("5 - Export order error modalini yopib davom etish"):
        base.radio(label="Экспорт заказа", click=True, expect_checked=True)
        base.date_picker(label="Начало периода", date="today")
        base.date_picker(label="Конец периода", date="today")
        base.click(name="Генерировать", exact=True)

    with allure.step("6 - Export status XML downloadini tekshirish"):
        base.radio(label="Экспорт статусов", click=True, expect_checked=True)
        generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_status_pw{run_suffix}.xml", expected_suffix=".xml")

    with allure.step("7 - Export balance XML downloadini tekshirish"):
        base.radio(label="Экспорт остатков", click=True, expect_checked=True)
        base.date_picker(label="Начало периода", date="today")
        base.date_picker(label="Конец периода", date="today")
        generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_balance_pw{run_suffix}.xml", expected_suffix=".xml")

    with allure.step("8 - Export input XML downloadini tekshirish"):
        base.radio(label="Экспорт приходов", click=True, expect_checked=True)
        base.date_picker(label="Начало периода", date="today")
        base.date_picker(label="Конец периода", date="today")
        base.b_input(label="Исключение по организациям (только для экспорта приходов)", select_first=True)
        generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_input_pw{run_suffix}.xml", expected_suffix=".xml")

    with allure.step("9 - Export internal movement XML downloadini tekshirish"):
        base.radio(label="Экспорт внутренних перемещений", click=True, expect_checked=True)
        base.date_picker(label="Начало периода", date="today")
        base.date_picker(label="Конец периода", date="today")
        generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_movement_pw{run_suffix}.xml", expected_suffix=".xml")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-06 - Integration Two settings, beshta XML va Export order errori")
def test_report_integration_two(page):
    run_report_integration_two_check(page)
