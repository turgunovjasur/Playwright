"""``Финансы`` navbaridagi legacy va A2 forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: operatsion filialda 42 direct menu forma va 67 recursive
page-link — jami 109 navigatsiya. ``Администрирование``dagi 8 direct forma va
2 child target operatsion graphda ham borligi sabab takroran tekshirilmaydi.
"""

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.inventory import get_legacy_form_buckets
from tests.smoke.test_forms.monitoring.suite_runner import run_legacy_form_monitoring


pytestmark = [
    pytest.mark.smoke_group("Forms", independent=True, setup_independent=True),
    allure.epic("Smoke"),
    allure.feature("Navbar Forms"),
    allure.story("Финансы menu formalarini ochish"),
]

NAVBAR_TAB = "Финансы"


def run_finansy_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """Testcase: ``Финансы`` navbaridagi legacy va A2 formalarni tekshirish.

    1. Company admini bilan authorization qilish.
    2. ``Финансы`` markaziy forma inventorysini olish.
    3. Inventoryni filiallar bo'yicha monitoring qilib, to'liq natijani qaytarish.
    """
    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")

    with allure.step("2 - Финансы forma inventorysini olish"):
        form_buckets = get_legacy_form_buckets(NAVBAR_TAB)

    with allure.step("3 - Финансы formalarini markaziy monitoring qilish"):
        return run_legacy_form_monitoring(page, suite_name="Forms-04 — Финансы", progress_test_id=progress_test_id, navbar_tab=NAVBAR_TAB, form_buckets=form_buckets, terminal_reporter=terminal_reporter, checks=checks, diagnostics=diagnostics)


@allure.title("Финансы")
def test_finansy_forms(page, pytestconfig, request):
    run_finansy_forms(page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
