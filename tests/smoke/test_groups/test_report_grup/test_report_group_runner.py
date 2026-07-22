import allure
import pytest

from tests.smoke.test_groups.test_report_grup.test_cislink import run_report_cislink_check
from tests.smoke.test_groups.test_report_grup.test_integration_three import run_report_integration_three_check
from tests.smoke.test_groups.test_report_grup.test_saleswork import run_report_saleswork_check
from tests.smoke.test_groups.test_report_grup.test_optimum import run_report_optimum_check
from tests.smoke.test_groups.test_report_grup.test_spot import run_report_spot_check
from tests.smoke.test_groups.test_report_grup.test_integration_two import run_report_integration_two_check

pytestmark = [
    pytest.mark.smoke_group("Report", independent=True),
    allure.epic("Report Group"),
    allure.feature("Report Group Runner"),
    allure.story("Integration Reports"),
]

# CisLink integration report sahifasi Smartup deploymentlar bo'ylab o'zgarmoqda
# (xtrade'da "Настройки" tugmasi yo'q, filtrlar inline) — barqarorlashguncha
# BARCHA serverda skip. Qayta yoqish uchun quyidagi testdagi
# @pytest.mark.skip ni olib tashlang.
CISLINK_SKIP_REASON = (
    "CisLink sahifasi Smartup deploymentlar bo'ylab o'zgarmoqda "
    "(xtrade'da Настройки tugmasi yo'q) — barqarorlashguncha barcha serverda skip"
)


@pytest.mark.skip(reason=CISLINK_SKIP_REASON)
@allure.title("Report-01 - CisLink integration report")
def test_report_01_cislink(group_session_page, code):
    run_report_cislink_check(group_session_page, code)


@allure.title("Report-02 - Integration №3 report")
def test_report_02_integration_three(group_session_page, code):
    run_report_integration_three_check(group_session_page, code)


@allure.title("Report-03 - SalesWork report")
def test_report_03_saleswork(group_session_page, code):
    run_report_saleswork_check(group_session_page, code)


@allure.title("Report-04 - Optimum report")
def test_report_04_optimum(group_session_page, code):
    run_report_optimum_check(group_session_page, code)


@allure.title("Report-05 - Spot 2d report")
def test_report_05_spot(group_session_page, code):
    run_report_spot_check(group_session_page, code)


@allure.title("Report-06 - Integration Two report")
def test_report_06_integration_two(group_session_page, code, load_data):
    run_report_integration_two_check(group_session_page, code, load_data)
