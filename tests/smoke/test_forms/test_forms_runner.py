import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.test_a2_admin_menu_forms import (
    run_a2_admin_menu_forms,
)
from tests.smoke.test_forms.test_spravochniki_menu_forms import (
    run_spravochniki_menu_forms,
)


pytestmark = [
    pytest.mark.smoke_group("Forms", independent=True),
    allure.epic("Smoke"),
    allure.feature("Forms Runner"),
    allure.story("Menu orqali formalarni ochish"),
]


@pytest.fixture(scope="module")
def forms_admin_page(group_session_page):
    authorization(group_session_page, who="admin")
    return group_session_page


@allure.title("Forms-01 - Справочники menu formalarini ochish")
def test_forms_01_spravochniki(forms_admin_page, pytestconfig):
    run_spravochniki_menu_forms(
        forms_admin_page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )


@allure.title("Forms-02 - A2 admin menu formalarini ochish")
def test_forms_02_a2_admin(forms_admin_page, pytestconfig):
    run_a2_admin_menu_forms(
        forms_admin_page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
