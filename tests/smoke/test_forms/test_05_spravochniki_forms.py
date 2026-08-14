"""``Справочники`` tabidagi legacy formalarni user-visible yo'llar orqali tekshirish.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov — jami 88 ta navigatsiya: operatsion filialda 33 direct menu
forma, 35 page-link/sub-page-link va 14 ``Создать`` dropdown forma;
``Администрирование`` filialida 1 direct, 2 page-link va 3 ``Создать``
dropdown forma. ``Продавцы`` (8 yo'l) va ``Публикация в бот`` (4 yo'l)
parentlariga tegishli 12 ta yo'l vaqtincha qamrovdan chiqarilgan. Har bir
aktiv forma Allure va terminalda filial, tab, menu, forma, kutilgan URL va
haqiqiy URL bilan hisobot qilinadi.
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
    allure.story("Справочники menu formalarini ochish"),
]

NAVBAR_TAB = "Справочники"

# ----------------------------------------------------------------------------------------------------------------------


def run_spravochniki_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """Testcase: ``Справочники`` navbaridagi legacy formalarni tekshirish.

    1. Company admini bilan authorization qilish.
    2. ``Справочники`` markaziy forma inventorysini olish.
    3. Inventoryni filiallar bo'yicha monitoring qilib, to'liq natijani qaytarish.
    """
    with allure.step("1 - Company admini bilan authorization"):
        authorization(page, who="admin")

    with allure.step("2 - Справочники forma inventorysini olish"):
        form_buckets = get_legacy_form_buckets(NAVBAR_TAB)

    with allure.step("3 - Справочники formalarini markaziy monitoring qilish"):
        return run_legacy_form_monitoring(page, suite_name="Forms-05 — Справочники", progress_test_id=progress_test_id, navbar_tab=NAVBAR_TAB, form_buckets=form_buckets, terminal_reporter=terminal_reporter, checks=checks, diagnostics=diagnostics)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Справочники")
def test_spravochniki_forms(page, pytestconfig, request):
    run_spravochniki_forms(page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
