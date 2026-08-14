import allure
import pytest

from tests.smoke.test_forms.test_01_glavnoe_forms import run_glavnoe_forms
from tests.smoke.test_forms.test_02_prodaja_forms import run_prodaja_forms
from tests.smoke.test_forms.test_03_sklad_forms import run_sklad_forms
from tests.smoke.test_forms.test_04_finansy_forms import run_finansy_forms
from tests.smoke.test_forms.test_05_spravochniki_forms import run_spravochniki_forms


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


@allure.title("Главное")
def test_forms_01_glavnoe(group_session_page, pytestconfig, request):
    run_glavnoe_forms(group_session_page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))


@allure.title("Продажа")
def test_forms_02_prodaja(group_session_page, pytestconfig, request):
    run_prodaja_forms(group_session_page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))


@allure.title("Склад")
def test_forms_03_sklad(group_session_page, pytestconfig, request):
    run_sklad_forms(group_session_page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))


@allure.title("Финансы")
def test_forms_04_finansy(group_session_page, pytestconfig, request):
    run_finansy_forms(group_session_page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))


@allure.title("Справочники")
def test_forms_05_spravochniki(group_session_page, pytestconfig, request):
    run_spravochniki_forms(group_session_page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
