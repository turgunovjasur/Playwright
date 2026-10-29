import os
import re
from contextlib import contextmanager
from uuid import uuid4

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_report_grup.flow_report.report_helpers import generate_and_verify_download, open_report
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [
    pytest.mark.smoke_group("Report", independent=True),
    allure.epic("Report Group"),
    allure.feature("Integration Report"),
    allure.story("Integration Two"),
]

# The mock stops the two server proxy calls before they can reach an external service.
@contextmanager
def _monolith_transport(page):
    if os.getenv("INTEGRATION_TWO_DEMO", "0") != "1":
        yield
        return

    pattern = re.compile(r"/b/trade/rep/integration/integration_two:(get_request|post_request)(?:\?|$)")
    calls = []

    def respond(route):
        operation = pattern.search(route.request.url).group(1)
        calls.append(operation)
        route.fulfill(
            status=200,
            content_type="application/xml; charset=utf-8",
            body='<?xml version="1.0" encoding="UTF-8"?><extdata/>',
        )

    allure.dynamic.parameter("Monolith transport", "local demo mock")
    page.route(pattern, respond)
    try:
        yield
        if "get_request" not in calls or "post_request" not in calls:
            raise AssertionError("Demo mock: Monolith GET va POST oqimlari bajarilmadi")
    finally:
        page.unroute(pattern, respond)
        allure.attach("\n".join(calls), name="Monolith local mock calls", attachment_type=allure.attachment_type.TEXT)


# ----------------------------------------------------------------------------------------------------------------------

def run_report_integration_two_check(page):
    """Testcase: Monolith settings va oltita exchange mode XML faylini tekshirish.

    1. Administration filialida Integration Two reportini ochish.
    2. Konfiguratsiyadagi XML endpointini qo'llab, user va report filterlarini saqlash.
    3. Import order XML downloadini tekshirish.
    4. Export order XML downloadini tekshirish.
    5. Export status XML downloadini tekshirish.
    6. Export balance XML downloadini tekshirish.
    7. Export input XML downloadini tekshirish.
    8. Export internal movement XML downloadini tekshirish.
    """
    with _monolith_transport(page):
        base = AutoBasePage(page)
        run_suffix = uuid4().hex[:8]
        xml_url = os.getenv("INTEGRATION_TWO_XML_URL", "").strip()

        authorization(page, who="admin")

        with allure.step("1 - Administration filialida Integration Two reportini ochish"):
            base.switch_filial(name="Администрирование")
            open_report(base, "integration_two", timeout=120_000)
            base.expect_page(heading="Интеграция с системой монолит", url="integration_two")

        with allure.step("2 - Monolith endpoint preconditioni va report filterlarini saqlash"):
            base.click(name="Настройки", exact=True)
            base.input(label="User", expect_value=re.compile(r"\S"))
            if xml_url:
                base.input(label="URL", value=xml_url, expect_value=xml_url)
            base.input(label="URL", expect_value=re.compile(r"^https?://\S+$"))
            if not base.b_input(label="Тип цены", return_value=True):
                base.b_input(label="Тип цены", select_first=True)
            base.b_input(label="Тип цены", expect_value=re.compile(r"\S"))
            base.input(label="Ед. измерения (количество)", expect_value="шт", value="шт")
            base.input(label="Ед. измерения (блок)", expect_value="шт", value="шт")

            base.checkbox(label="Редактирование контрагента", checked=True)
            base.checkbox(label="Отправлять данные по всем заказам", checked=True)
            base.checkbox(label="Игнорировать обновление существующих заказов", checked=True)
            base.checkbox(label="Отображать код владельца", checked=True)

            base.b_input(label="Характеристика ТМЦ", value="Группа", clear=True)
            base.checkbox(label="Подтипы характеристик ТМЦ", expect_checked=True)
            base.b_input(label="Характеристики юридических лиц", value="Группа", clear=True)
            if not base.b_input(label="Подтипы характеристик", return_value=True):
                base.b_input(label="Подтипы характеристик", select_first=True)
            base.b_input(label="Подтипы характеристик", expect_value=re.compile(r"\S"))
            base.click(name="Сохранить", exact=True)
            base.click(name="Закрыть", exact=True)
            base.expect_page(heading="Интеграция с системой монолит", url="integration_two")

        with allure.step("3 - Import order XML downloadini tekshirish"):
            base.radio(label="Импорт заказа", click=True, expect_checked=True)
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_import_order_pw{run_suffix}.xml", expected_suffix=".xml")

        with allure.step("4 - Export order XML downloadini tekshirish"):
            base.radio(label="Экспорт заказа", click=True, expect_checked=True)
            base.date_picker(label="Начало периода", date="today")
            base.date_picker(label="Конец периода", date="today")
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_order_pw{run_suffix}.xml", expected_suffix=".xml")

        with allure.step("5 - Export status XML downloadini tekshirish"):
            base.radio(label="Экспорт статусов", click=True, expect_checked=True)
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_status_pw{run_suffix}.xml", expected_suffix=".xml")

        with allure.step("6 - Export balance XML downloadini tekshirish"):
            base.radio(label="Экспорт остатков", click=True, expect_checked=True)
            base.date_picker(label="Начало периода", date="today")
            base.date_picker(label="Конец периода", date="today")
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_balance_pw{run_suffix}.xml", expected_suffix=".xml")

        with allure.step("7 - Export input XML downloadini tekshirish"):
            base.radio(label="Экспорт приходов", click=True, expect_checked=True)
            base.date_picker(label="Начало периода", date="today")
            base.date_picker(label="Конец периода", date="today")
            base.multiselect(label="Исключение по организациям (только для экспорта приходов)", select_first=True)
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_input_pw{run_suffix}.xml", expected_suffix=".xml")

        with allure.step("8 - Export internal movement XML downloadini tekshirish"):
            base.radio(label="Экспорт внутренних перемещений", click=True, expect_checked=True)
            base.date_picker(label="Начало периода", date="today")
            base.date_picker(label="Конец периода", date="today")
            generate_and_verify_download(base, "Генерировать", None, f"integration_two_export_movement_pw{run_suffix}.xml", expected_suffix=".xml")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-06 - Integration Two settings va oltita XML")
def test_report_integration_two(page):
    run_report_integration_two_check(page)
