from datetime import datetime
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
    allure.story("Integration Three"),
]

REPORT_RENDER_TIMEOUT = 60_000


# ----------------------------------------------------------------------------------------------------------------------

def run_report_integration_three_check(page):
    """Testcase: Integration №3 HTML preview va XLSX downloadini tekshirish.

    1. Birinchi operatsion filialda Integration №3 reportini ochish.
    2. Period va product filterlarining default qiymatlarini tekshirish.
    3. Settings rejimida Documents, Balances va Warehouses ustunlari defaultlarini tekshirish.
    4. HTML preview hosil qilib, uchta nomlangan sheetni ketma-ket ochish.
    5. EXCEL outputni generate qilib non-empty XLSX downloadni tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]
    month_start = datetime.now().replace(day=1)

    authorization(page, who="admin")
    base.switch_filial(first_filial=True)

    with allure.step("1 - Birinchi operatsion filialda Integration №3 reportini ochish"):
        open_report(base, "integration_three", "Интеграция №3 NEON")

    with allure.step("2 - Period va product filterlari defaultlarini tekshirish"):
        base.date_picker(label="Начало периода", date=month_start)
        base.date_picker(label="Конец периода", date="today")
        base.b_input(label="Характеристики ТМЦ", expect_value="Группа")
        base.checkbox(label="Подтипы характеристик", expect_checked=True)

    with allure.step("3 - Settings ustunlari va nomlash defaultlarini tekshirish"):
        base.click(name="Настройки", exact=True)
        base.checkbox(label="Отображать штрих-код", expect_checked=True, index=0)
        base.checkbox(label="Отображать артикул код", expect_checked=True, index=0)
        base.checkbox(label="Отображать единицу измерения", expect_checked=True, index=0)
        base.checkbox(label="Отображать цену реализации", expect_checked=True)
        base.checkbox(label="Отображать цену поставки", expect_checked=True)
        base.checkbox(label="Отображать идентификатор раздела Б", expect_checked=True, index=0)
        base.radio("Полное название", expect_checked=True)
        base.radio("Альтернативное название", expect_checked=False)
        base.checkbox(label="Отображать штрих-код", expect_checked=True, index=1)
        base.checkbox(label="Отображать артикул код", expect_checked=True, index=1)
        base.checkbox(label="Отображать единицу измерения", expect_checked=True, index=1)
        base.checkbox(label="Отображать сумму остатков на начало", expect_checked=True)
        base.checkbox(label="Отображать сумму остатков на конец", expect_checked=True)
        base.checkbox(label="Отображать идентификатор раздела Б", expect_checked=True, index=1)
        base.checkbox(label="Отображать кол-во прихода на склад", expect_checked=True)
        base.checkbox(label="Отображать кол-во ухода со склада", expect_checked=True)
        base.checkbox(label="Отображать название склада", expect_checked=True)
        base.checkbox(label="Отображать адрес склада", expect_checked=True)
        base.text("Настройки типов документов", "Заказ", "Инвентаризация расход")
        base.click(name="Параметры", exact=True)

    with allure.step("4 - HTML previewdagi Склады, Документы va Остатки sheetlarini tekshirish"):
        base.click(name="Сформировать", exact=True)
        base.wait_for_loader()
        report = page.frame_locator("iframe.report-frame")
        tabs = report.locator("a.nav-link")
        expect(tabs).to_have_count(3, timeout=REPORT_RENDER_TIMEOUT)
        expect(tabs).to_have_text(["Склады", "Документы", "Остатки"])
        expect(tabs.nth(0)).to_have_class("nav-link active")
        expect(report.locator("#sheet1")).to_be_visible(timeout=REPORT_RENDER_TIMEOUT)
        tabs.nth(1).click()
        expect(report.locator("#sheet2")).to_be_visible()
        tabs.nth(2).click()
        expect(report.locator("#sheet3")).to_be_visible()

    with allure.step("5 - Integration Three XLSX downloadini tekshirish"):
        generate_and_verify_download(base, "EXCEL", None, f"integration_three_pw{run_suffix}.xlsx", expected_suffix=".xlsx")


# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-02 - Integration №3 HTML preview va XLSX eksporti")
def test_report_integration_three(page):
    run_report_integration_three_check(page)
