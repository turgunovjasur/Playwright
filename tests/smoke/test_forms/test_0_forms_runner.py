import allure
import pytest

from tests.smoke.test_forms.test_01_spravochniki_menu_forms import run_spravochniki_menu_forms
from tests.smoke.test_forms.test_02_a2_admin_menu_forms import run_a2_admin_menu_forms
from tests.smoke.test_forms.test_03_prodaja_menu_forms import run_prodaja_menu_forms


pytestmark = [
    pytest.mark.smoke_group(
        "Forms",
        independent=True,
        setup_independent=True,
    ),
    allure.epic("Smoke"),
    allure.feature("Forms Runner"),
    allure.story("Menu orqali formalarni ochish"),
]


@allure.title("Forms-01 - Справочники menu formalarini ochish")
def test_forms_01_spravochniki(group_session_page, pytestconfig):
    run_spravochniki_menu_forms(
        group_session_page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"),
    )


@allure.title("Forms-02 - A2 admin menu formalarini ochish")
def test_forms_02_a2_admin(group_session_page, pytestconfig):
    run_a2_admin_menu_forms(
        group_session_page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"),
    )


@allure.title("Forms-03 - Продажа menu formalarini ochish")
def test_forms_03_prodaja(group_session_page, pytestconfig):
    run_prodaja_menu_forms(
        group_session_page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"),
    )
