"""``Главное`` navbaridagi legacy va A2 forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: operatsion filialda 11 direct menu forma va 17 page-link,
``Администрирование``da esa 4 admin-only direct forma va 1 page-link — jami
33 ta navigatsiya. Admin menyusidagi qolgan 10 direct forma operatsion
filialda ham borligi sabab takroran tekshirilmaydi.
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
    allure.story("Главное menu formalarini ochish"),
]

NAVBAR_TAB = "Главное"

# ----------------------------------------------------------------------------------------------------------------------


def run_glavnoe_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """Testcase: ``Главное`` navbaridagi legacy va A2 formalarni tekshirish.

    1. Company admini bilan authorization qilish.
    2. ``Главное`` markaziy forma inventorysini olish.
    3. Inventoryni filiallar bo'yicha monitoring qilib, to'liq natijani qaytarish.
    """
    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")

    with allure.step("2 - Главное forma inventorysini olish"):
        form_buckets = get_legacy_form_buckets(NAVBAR_TAB)

    with allure.step("3 - Главное formalarini markaziy monitoring qilish"):
        return run_legacy_form_monitoring(
            page,
            suite_name="Forms-01 — Главное",
            progress_test_id=progress_test_id,
            navbar_tab=NAVBAR_TAB,
            form_buckets=form_buckets,
            terminal_reporter=terminal_reporter,
            checks=checks,
            diagnostics=diagnostics,
        )


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Главное")
def test_glavnoe_forms(page, pytestconfig, request):
    run_glavnoe_forms(
        page,
        progress_test_id=request.node.name,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"),
    )
