import re
from datetime import datetime
from uuid import uuid4

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, open_report
from utils.base_page import BasePage

pytestmark = [
    pytest.mark.smoke_group("Report", independent=True),
    allure.epic("Report Group"),
    allure.feature("Integration Report"),
    allure.story("SalesWork"),
]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_saleswork_check(page):
    """Testcase: yangi SalesWork templatei bilan ZIP eksportini tekshirish.

    1. Birinchi operatsion filialda SalesWork reportini ochib period defaultlarini tekshirish.
    2. Har bir run uchun yangi template required maydon va defaultlari bilan yaratish.
    3. Template main formada tanlanganini tekshirish.
    4. Export download nomi va fayl bo'sh emasligini tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]
    template_name = f"SalesWork-pw{run_suffix}"
    month_start = datetime.now().replace(day=1)

    authorization(page, who="admin")
    base.switch_filial(first_filial=True)

    with allure.step("1 - SalesWork reporti va period defaultlarini tekshirish"):
        open_report(base, "saleswork", "Saleswork")
        base.date_picker(label="Дата начала периода", date=month_start)
        base.date_picker(label="Дата окончания периода", date="today")

    with allure.step("2 - Har bir run uchun yangi SalesWork templateini yaratish"):
        base.click(name="Шаблоны", exact=True)
        base.expect_page(heading="Шаблоны SalesWorks", url="saleswork_template_list")
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Шаблон Saleswork (Создание)", url="saleswork_template+add")
        base.input(label="Название", value=template_name)
        base.b_input(label="Продуктовое направление", value="Группа")
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Подтипы характеристик", expect_checked=True)
        base.radio(label="MarevenFoodCentral", expect_checked=True)
        base.radio(label="Kimberly-Clark", expect_checked=False)
        base.checkbox(label="ParentCompanies", expect_checked=True)
        base.checkbox(label="Outlets", expect_checked=True)
        base.checkbox(label="ArchivedStocks", expect_checked=True)
        base.checkbox(label="LocalProducts", expect_checked=True)
        base.checkbox(label="OutletDebts", expect_checked=False)
        base.checkbox(label="SalOuts", expect_checked=True)
        base.checkbox(label="SalIns", expect_checked=True)
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading=re.compile(r"^\s*Saleswork\s*$"), url=re.compile(r"/trade/rep/integration/saleswork$"))

    with allure.step("3 - Template main formada tanlanganini tekshirish"):
        base.b_input(label="Шаблон", expect_value=template_name)

    with allure.step("4 - SalesWork ZIP downloadini tekshirish"):
        generate_and_verify_download(base, "Экспорт", "sales_work", f"sales_work_pw{run_suffix}.zip", expected_suffix=".zip")


# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-03 - SalesWork template va ZIP eksporti")
def test_report_saleswork(page):
    run_report_saleswork_check(page)
