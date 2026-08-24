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
    allure.story("Optimum"),
]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_optimum_check(page):
    """Testcase: Optimum periodi, integration sozlamalari va ZIP downloadini tekshirish.

    1. Birinchi operatsion filialda Optimum reportini ochib period defaultlarini tekshirish.
    2. Product group va sakkizta operation prefiksini real label orqali sozlash.
    3. Sozlamani saqlab main formaga qaytishni tekshirish.
    4. Optimum ZIP download nomi va fayl bo'sh emasligini tekshirish.
    """
    base = BasePage(page)
    run_suffix = uuid4().hex[:8]
    month_start = datetime.now().replace(day=1)

    authorization(page, who="admin")
    base.switch_filial(first_filial=True)

    with allure.step("1 - Optimum reporti va period defaultlarini tekshirish"):
        open_report(base, "optimum", "Интеграция OPTIMUM")
        base.date_picker(label="Дата начала", date=month_start)
        base.date_picker(label="Конец периода", date="today")
        base.text("Выбранный период не должен превышать 3 месяца")

    with allure.step("2 - Product group va sakkizta operation prefiksini sozlash"):
        base.click(name="Настройки", exact=True)
        base.b_input(label="Продуктовое группа", value="Группа", clear=True)
        base.checkbox(label="Подтипы характеристик", expect_checked=True)
        base.input(label='Префикс для "Перемещение между складами (отгрузка)"', value="1")
        base.input(label='Префикс для "Перемещение между складами (приход)"', value="2")
        base.input(label='Префикс для "Инвентаризации: списание со склада"', value="3")
        base.input(label='Префикс для "Инвентаризации: приход на склад"', value="4")
        base.input(label='Префикс для "Перемещение между площадками дистрибутора (расход)"', value="5")
        base.input(label='Префикс для "Перемещение между площадками дистрибутора (приход)"', value="6")
        base.input(label='Префикс для "Списание со склада (производство, фасовка)"', value="7")
        base.input(label='Префикс для "Приход на склад (производство, фасовка)"', value="8")

    with allure.step("3 - Sozlamani saqlab main formaga qaytishni tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Интеграция OPTIMUM", url="optimum")
        base.click(name="Настройки", exact=True)
        base.input(label='Префикс для "Перемещение между складами (отгрузка)"', expect_value="1")
        base.input(label='Префикс для "Приход на склад (производство, фасовка)"', expect_value="8")
        base.click(name="Закрыть", exact=True)

    with allure.step("4 - Optimum ZIP downloadini tekshirish"):
        generate_and_verify_download(base, "Сформировать", "optimum", f"optimum_pw{run_suffix}.zip", expected_suffix=".zip")


# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Report-04 - Optimum sozlamalari va ZIP eksporti")
def test_report_optimum(page):
    run_report_optimum_check(page)
