import allure
import pytest

from tests.smoke.test_forms.test_01_spravochniki_menu_forms import (
    SPRAVOCHNIKI_MENU_TESTS,
    run_spravochniki_menu_column_forms,
)
from tests.smoke.test_forms.test_02_a2_admin_menu_forms import (
    A2_MENU_TESTS,
    run_a2_menu_identity_forms,
)
from tests.smoke.test_forms.test_03_prodaja_menu_forms import (
    PRODAJA_MENU_TESTS,
    run_prodaja_menu_column_forms,
)


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


def _terminal_reporter(pytestconfig):
    return pytestconfig.pluginmanager.get_plugin("terminalreporter")


@pytest.mark.parametrize(
    "menu_test",
    SPRAVOCHNIKI_MENU_TESTS,
    ids=[item["test_identity"] for item in SPRAVOCHNIKI_MENU_TESTS],
)
def test_forms_01_spravochniki(group_session_page, pytestconfig, menu_test):
    allure.dynamic.title(f"Forms-01 — {menu_test['test_identity']}")
    run_spravochniki_menu_column_forms(
        group_session_page,
        menu_test=menu_test,
        terminal_reporter=_terminal_reporter(pytestconfig),
    )


@pytest.mark.parametrize(
    "menu_test",
    A2_MENU_TESTS,
    ids=[item["test_identity"] for item in A2_MENU_TESTS],
)
def test_forms_02_a2_admin(group_session_page, pytestconfig, menu_test):
    allure.dynamic.title(f"Forms-02 — {menu_test['test_identity']}")
    run_a2_menu_identity_forms(
        group_session_page,
        menu_test=menu_test,
        terminal_reporter=_terminal_reporter(pytestconfig),
    )


@pytest.mark.parametrize(
    "menu_test",
    PRODAJA_MENU_TESTS,
    ids=[item["test_identity"] for item in PRODAJA_MENU_TESTS],
)
def test_forms_03_prodaja(group_session_page, pytestconfig, menu_test):
    allure.dynamic.title(f"Forms-03 — {menu_test['test_identity']}")
    run_prodaja_menu_column_forms(
        group_session_page,
        menu_test=menu_test,
        terminal_reporter=_terminal_reporter(pytestconfig),
    )
