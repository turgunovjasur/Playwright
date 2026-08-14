"""``Склад`` navbaridagi legacy va A2 forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: operatsion filialda 38 direct menu forma va 38 page-link —
jami 76 ta navigatsiya. ``Администрирование``dagi ayni 7 forma operatsion
filialda ham borligi sabab takroran tekshirilmaydi.
``Инвентаризация КМ`` dostup yo'qligi sabab umumiy skip registry orqali
qamrovdan chiqariladi.
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
    allure.feature("Navbar Forms"),
    allure.story("Склад menu formalarini ochish"),
]

NAVBAR_TAB = "Склад"

# ----------------------------------------------------------------------------------------------------------------------


def run_sklad_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """Testcase: ``Склад`` navbaridagi legacy va A2 formalarni tekshirish.

    1. Company admini bilan authorization qilish.
    2. ``Склад`` markaziy forma inventorysini olish.
    3. Inventoryni filiallar bo'yicha monitoring qilib, to'liq natijani qaytarish.
    """
    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")

    with allure.step("2 - Склад forma inventorysini olish"):
        form_buckets = get_legacy_form_buckets(NAVBAR_TAB)

    with allure.step("3 - Склад formalarini markaziy monitoring qilish"):
        return run_legacy_form_monitoring(page, suite_name="Forms-03 — Склад", progress_test_id=progress_test_id, navbar_tab=NAVBAR_TAB, form_buckets=form_buckets, terminal_reporter=terminal_reporter, checks=checks, diagnostics=diagnostics)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Склад")
def test_sklad_forms(page, pytestconfig, request):
    run_sklad_forms(page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
