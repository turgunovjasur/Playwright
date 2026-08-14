"""``Продажа`` navbaridagi user-visible forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: 26 direct menu forma va 12 ta rekursiv page-link — jami 38 ta
navigatsiya. ``+add`` ikonka-linklar tekshirilmaydi.
``Дашборд по продажам (БЕТА)`` umumiy skip registry orqali test rejasidan
chiqariladi.
"""

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.inventory import get_legacy_form_buckets
from tests.smoke.test_forms.monitoring.suite_runner import run_legacy_form_monitoring


pytestmark = [
    pytest.mark.smoke_group(
        "Forms",
        independent=True,
        setup_independent=True,
    ),
    allure.epic("Smoke"),
    allure.feature("Legacy Forms"),
    allure.story("Продажа menu formalarini ochish"),
]

NAVBAR_TAB = "Продажа"

# ----------------------------------------------------------------------------------------------------------------------


def run_prodaja_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """Testcase: ``Продажа`` navbaridagi legacy formalarni tekshirish.

    1. Company admini bilan authorization qilish.
    2. ``Продажа`` markaziy forma inventorysini olish.
    3. Inventoryni operatsion filial bo'yicha monitoring qilib, to'liq natijani qaytarish.
    """
    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")

    with allure.step("2 - Продажа forma inventorysini olish"):
        form_buckets = get_legacy_form_buckets(NAVBAR_TAB)

    with allure.step("3 - Продажа formalarini markaziy monitoring qilish"):
        return run_legacy_form_monitoring(page, suite_name="Forms-02 — Продажа", progress_test_id=progress_test_id, navbar_tab=NAVBAR_TAB, form_buckets=form_buckets, terminal_reporter=terminal_reporter, checks=checks, diagnostics=diagnostics)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Продажа")
def test_prodaja_forms(page, pytestconfig, request):
    run_prodaja_forms(page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
