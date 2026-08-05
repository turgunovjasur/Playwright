"""``Продажа`` tabidagi user-visible forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: 26 direct menu forma va 12 ta rekursiv page-link — jami 38 ta
navigatsiya. ``+add`` ikonka-linklar tekshirilmaydi.
``Дашборд по продажам (БЕТА)`` umumiy skip registry orqali test rejasidan
chiqariladi.
"""

import allure
import pytest

from tests.smoke.test_forms.form_cases import (
    form_test_identity,
    select_form_definitions,
    validate_menu_test_coverage,
)
from tests.smoke.test_forms.menu_column_runner import run_legacy_menu_column_forms


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


OPERATIONAL_DIRECT_FORMS = [
    {
        "menu_column": "Визиты",
        "menu_item": "Визиты",
        "path": "trade/tvt/visit_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Архив визитов",
        "path": "trade/tvt/visit_history_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание пользователей",
        "path": "trade/tvt/user_locations",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание мобильных представителей",
        "path": "trade/tph/user_tracking",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Планирование визитов",
        "path": "trade/tvt/plan/room_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Планы",
        "path": "trade/tvt/plan/plan_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Автоформирование плана визитов",
        "path": "trade/tvt/auto_gen_visit_plan",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "path": "trade/tvt/equipment_review_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Фото- и видеоотчеты",
        "path": "trade/tvt/photo_video_gallery",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "path": "trade/tdeal/order/order_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Архив заказов",
        "path": "trade/tdeal/order/order_history_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Отмененные заказы",
        "path": "trade/tdeal/order/order_cancelled_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Возвраты",
        "path": "anor/mdeal/return/return_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "path": "anor/mdeal/order/offset/offset_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Лиды",
        "path": "anor/mdeal/order/lead_list",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд",
        "path": "trade/tdeal/sales_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "path": "trade/tdeal/sales_dashboard_two",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам (БЕТА)",
        "title": "Дашборд по продажам (БЕТА)(GWS_QLIK_001)",
        "path": "trade/tdeal/qlik_sales_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Конструктор отчётов по продажам",
        "path": "trade/rep/mbi/tdeal/order",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Общий отчет по продажам (организации)",
        "path": "trade/rep/tdeal/sales",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Задолженность покупателей по срокам задолженности",
        "title": "Задолженность покупателей по срокам задолженности(FIN00001)",
        "path": "anor/rep/analytics/debtor_clients",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Расчет бонуса за оплату долга",
        "path": "trade/rep/tdeal/sales_discount",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Коммерческий дашборд",
        "path": "trade/tdeal/commercial_dashboard",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Конструктор отчётов по визитам",
        "path": "trade/rep/mbi/tvt/visit",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Отчет по визитам",
        "path": "trade/rep/tvt/visits",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Анализ маршрута",
        "path": "trade/rep/route_analysis",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Отчёт о маршруте пользователей",
        "path": "trade/rep/path_visit_user",
    },
]


OPERATIONAL_PAGE_LINK_FORMS = [
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "page_links": ["Архив"],
        "path": "trade/tvt/equipment_review_history_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "page_links": ["Архив", "Отслеживание оборудования"],
        "path": "trade/tvt/equipment_review_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Отказы"],
        "path": "anor/mdeal/order/sales_return_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Детали задолженности"],
        "path": "anor/mdeal/order/offset/offset_detail_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Детали задолженности", "История взаиморасчетов"],
        "path": "anor/mdeal/order/offset/offset_history_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": [
            "Детали задолженности",
            "История взаиморасчетов",
            "Детали задолженности",
        ],
        "path": "anor/mdeal/order/offset/offset_detail_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Возвраты",
        "page_links": ["Причины возврата"],
        "path": "anor/mdeal/return/return_reason_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты"],
        "path": "anor/mku/offset/offset_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты", "Парные счета"],
        "path": "anor/mku/coa_twin_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты", "Парные счета", "Взаиморасчеты"],
        "path": "anor/mku/offset/offset_list",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "page_links": ["Дашборд команды продаж"],
        "path": "trade/tdeal/sales_team_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "page_links": ["Дашборд команды продаж", "Дашборд по продажам"],
        "path": "trade/tdeal/sales_dashboard_two",
    },
]


PRODAJA_MENU_TESTS = [
    {
        "shell": "legacy",
        "navbar_tab": NAVBAR_TAB,
        "menu_column": "Визиты",
        "progress_test_id": "forms_03_prodaja_visits",
    },
    {
        "shell": "legacy",
        "navbar_tab": NAVBAR_TAB,
        "menu_column": "Продажа",
        "progress_test_id": "forms_03_prodaja_sales",
    },
    {
        "shell": "legacy",
        "navbar_tab": NAVBAR_TAB,
        "menu_column": "Отчеты по визитам",
        "progress_test_id": "forms_03_prodaja_visit_reports",
    },
    {
        "shell": "legacy",
        "navbar_tab": NAVBAR_TAB,
        "menu_column": "Отчеты по продажам",
        "progress_test_id": "forms_03_prodaja_sales_reports",
    },
]

for _menu_test in PRODAJA_MENU_TESTS:
    _menu_test["test_identity"] = form_test_identity(
        shell=_menu_test["shell"],
        navbar_tab=_menu_test["navbar_tab"],
        menu_column=_menu_test["menu_column"],
    )

validate_menu_test_coverage(
    PRODAJA_MENU_TESTS,
    OPERATIONAL_DIRECT_FORMS,
    OPERATIONAL_PAGE_LINK_FORMS,
    default_shell="legacy",
    default_navbar_tab=NAVBAR_TAB,
)


def run_prodaja_menu_column_forms(
    page,
    *,
    menu_test,
    terminal_reporter=None,
    checks=None,
    diagnostics=None,
):
    """Bitta ``Продажа`` menu column formasini markaziy monitor bilan ochadi."""
    navbar_tab = menu_test["navbar_tab"]
    menu_column = menu_test["menu_column"]
    operational_forms = select_form_definitions(
        OPERATIONAL_DIRECT_FORMS,
        OPERATIONAL_PAGE_LINK_FORMS,
        navbar_tab=navbar_tab,
        menu_column=menu_column,
    )
    return run_legacy_menu_column_forms(
        page,
        suite_name=f"Forms-03 — {menu_test['test_identity']}",
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        operational_forms=operational_forms,
        terminal_reporter=terminal_reporter,
        progress_test_id=menu_test["progress_test_id"],
        checks=checks,
        diagnostics=diagnostics,
    )


@pytest.mark.parametrize(
    "menu_test",
    PRODAJA_MENU_TESTS,
    ids=[item["test_identity"] for item in PRODAJA_MENU_TESTS],
)
def test_prodaja_menu_column_forms(page, pytestconfig, menu_test):
    allure.dynamic.title(f"{menu_test['test_identity']} formalarini ochish")
    run_prodaja_menu_column_forms(
        page,
        menu_test=menu_test,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
