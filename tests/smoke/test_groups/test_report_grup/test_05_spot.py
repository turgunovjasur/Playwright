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
    allure.story("Spot 2D"),
]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_spot_check(page):
    """Testcase: Spot2D period/settings contracti va yangi template bilan ZIP downloadini tekshirish.

    1. Birinchi operatsion filialda Spot2D reportini ochib period defaultlarini tekshirish.
    2. Settings modalida VAT va optional flag defaultlarini tekshirish.
    3. Har bir run uchun yangi template required maydon va fayl kontrakti bilan yaratish.
    4. Template tanlanganini va Spot2D ZIP downloadini tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]
    template_name = f"Spot2D-pw{run_suffix}"

    authorization(page, who="admin")
    base.switch_filial(first_filial=True)

    with allure.step("1 - Spot2D reporti va period defaultlarini tekshirish"):
        open_report(base, "spot", re.compile(r"^\s*Spot2D\(\d+\)\s*$"))
        base.radio("Последние 45 дней", expect_checked=True)
        base.radio("Пользовательский период", expect_checked=False)
        base.date_picker(label="Дата окончания периода", date="yesterday")

    with allure.step("2 - Settings VAT va optional flag defaultlarini tekshirish"):
        base.click(name="Настройки", exact=True)
        base.checkbox(label="Разделить по дням (файл receive)", expect_checked=False)
        base.checkbox(label="Дублировать Код клиента ERP (ID#ID)", expect_checked=False)
        base.radio("Системный ввод НДС(%)", expect_checked=True)
        base.radio("Ручной ввод НДС(%)", expect_checked=False)
        base.text("Сброс настроек")
        base.click(name="Закрыть", exact=True)

    with allure.step("3 - Har bir run uchun yangi Spot2D templateini yaratish"):
        base.click(name="Шаблоны", exact=True)
        base.expect_page(heading="Шаблоны Spot2D", url="spot_template_list")
        base.click(name="Добавить", exact=True)
        base.expect_page(heading="Шаблон Spot2D (создание)", url="spot_template+add")
        base.input(label="Название", value=template_name)
        base.b_input(label="Продуктовое направление", value="Группа")
        base.checkbox(label="Подтипы характеристик", expect_checked=True)
        base.checkbox(label="Активный", expect_checked=True)
        base.text("Файл : delivery", "Файл : stocks", "Файл : clients", "Файл : receive", "Файл : warehouse", root="b-page:visible")
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading=re.compile(r"^\s*Spot2D\(\d+\)\s*$"), url="spot")

    with allure.step("4 - Template tanlovi va Spot2D ZIP downloadini tekshirish"):
        base.b_input(label="Шаблон", expect_value=template_name)
        generate_and_verify_download(base, "Сформировать", "Spot2D", f"Spot2D_pw{run_suffix}.zip", expected_suffix=".zip")


# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-05 - Spot2D settings, template va ZIP eksporti")
def test_report_spot(page):
    run_report_spot_check(page)
