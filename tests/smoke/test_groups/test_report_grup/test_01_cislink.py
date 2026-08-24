import re
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
    allure.story("CisLink"),
]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_cislink_check(page):
    """Testcase: yangi CisLink templatei bilan report ZIP downloadini tekshirish.

    1. Birinchi operatsion filialda CisLink reportini ochish.
    2. Har bir run uchun yangi template required konfiguratsiya bilan yaratish.
    3. Main formada template tanlab, period va `До` sanasini sozlash.
    4. CisLink reportini generate qilib non-empty ZIP downloadni tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]
    template_name = f"CisLink-pw{run_suffix}"

    authorization(page, who="admin")
    base.switch_filial(first_filial=True)

    with allure.step("1 - Birinchi operatsion filialda CisLink reportini ochish"):
        open_report(base, "cislink", re.compile(r"^\s*CisLink\(7008\)\s*$"))
        base.radio("Последние 45 дней", expect_checked=True)
        base.radio("Пользовательский период", expect_checked=False)
        base.text("Сформировать", "Сформировать(MQ)", "Шаблоны")

    with allure.step("2 - Har bir run uchun yangi CisLink templateini yaratish"):
        base.click(name="Шаблоны", exact=True)
        base.expect_page(heading="Шаблоны CisLink(7008)", url="cislink_template_list")
        base.click(name="Добавить", exact=True)
        base.expect_page(heading="Шаблоны CisLink(7008) (создание)", url="cislink_template+add")
        base.input(label="Название", value=template_name)
        base.input(label='Значение поля "manfid"', value="test")
        base.checkbox(label="Активный", expect_checked=True)
        base.radio("Табуляция", expect_checked=True)
        base.radio("ANSI", expect_checked=True)
        base.b_input(label="Характеристики", value="Группа")
        base.b_input(label="Продуктовое направление", value="Группа")
        base.checkbox(label="Подтипы характеристик", expect_checked=True)
        base.b_input(label="Тип цены", select_first=True)
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Шаблоны CisLink(7008)", url="cislink_template_list")
        base.grid(template_name, "Активный")
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading=re.compile(r"^\s*CisLink\(7008\)\s*$"), url=re.compile(r"/trade/rep/integration/cislink$"))

    with allure.step("3 - Template, period va report sanasini sozlash"):
        base.b_input(label="Шаблон", value=template_name, clear=True)
        base.radio("Последние 45 дней", expect_checked=True)
        base.date_picker(label="До", date="today", auto_fill=True)
        base.b_input(label="Шаблон", expect_value=template_name)

    with allure.step("4 - CisLink ZIP downloadini tekshirish"):
        generate_and_verify_download(base, "Сформировать", "cislink", f"cislink_pw{run_suffix}.zip", expected_suffix=".zip")


# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-01 - CisLink template va ZIP eksporti")
def test_report_cislink(page):
    run_report_cislink_check(page)
