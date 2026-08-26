import allure
import pytest

from tests.smoke.test_groups.test_report_grup.test_01_cislink import run_report_cislink_check
from tests.smoke.test_groups.test_report_grup.test_02_integration_three import run_report_integration_three_check
from tests.smoke.test_groups.test_report_grup.test_03_saleswork import run_report_saleswork_check
from tests.smoke.test_groups.test_report_grup.test_04_optimum import run_report_optimum_check
from tests.smoke.test_groups.test_report_grup.test_05_spot import run_report_spot_check
from tests.smoke.test_groups.test_report_grup.test_06_integration_two import run_report_integration_two_check

pytestmark = [
    pytest.mark.smoke_group("Report", independent=True),
    allure.epic("Report Group"),
    allure.feature("Report Group Runner"),
    allure.story("Integration Reports"),
]

@allure.title("Report-01 - CisLink template va ZIP eksporti")
def test_report_01_cislink(group_session_page):
    run_report_cislink_check(group_session_page)


@allure.title("Report-02 - Integration №3 HTML preview va XLSX eksporti")
def test_report_02_integration_three(group_session_page):
    run_report_integration_three_check(group_session_page)


@allure.title("Report-03 - SalesWork template va ZIP eksporti")
def test_report_03_saleswork(group_session_page):
    run_report_saleswork_check(group_session_page)


@allure.title("Report-04 - Optimum sozlamalari va ZIP eksporti")
def test_report_04_optimum(group_session_page):
    run_report_optimum_check(group_session_page)


@allure.title("Report-05 - Spot2D settings, template va ZIP eksporti")
def test_report_05_spot(group_session_page):
    run_report_spot_check(group_session_page)


@allure.title("Report-06 - Integration Two settings, beshta XML va Export order errori")
def test_report_06_integration_two(group_session_page):
    run_report_integration_two_check(group_session_page)
