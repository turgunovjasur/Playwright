"""``Продажа`` tabidagi user-visible forma yo'llarini ochish smoke testi.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov: 26 direct menu forma va 12 ta rekursiv page-link — jami 38 ta
navigatsiya. ``+add`` ikonka-linklar tekshirilmaydi.
``Дашборд по продажам (БЕТА)`` umumiy skip registry orqali test rejasidan
chiqariladi.
"""

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.flow import (
    first_operational_filial,
    run_form_cases,
    switch_forms_filial,
)
from tests.smoke.test_forms.form_monitor import FormMonitor, build_form_case_plan


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


def run_prodaja_menu_forms(page, *, terminal_reporter=None):
    """Testcase: ``Продажа`` tabidagi barcha aktiv forma yo'llarini ochish.

    1. Birinchi operatsion filialni topib, 26 ta aktiv direct menu formani tekshirish.
    2. Shu filialdagi 12 ta page-link va canonical cycle yo'lini tekshirish.
    3. Jami 38 ta navigatsiya natijasini terminal va Allurega biriktirish.

    ``Дашборд по продажам (БЕТА)`` Qlik litsenziyasi yo'qligi sabab umumiy
    ``SKIPPED_FORMS`` registry orqali test rejasiga qo'shilmaydi.
    """
    operational_placeholder = "<operatsion filial>"
    planned_cases = []
    number = 1
    for cases, section in (
        (OPERATIONAL_DIRECT_FORMS, "operational-direct"),
        (OPERATIONAL_PAGE_LINK_FORMS, "operational-page-link"),
    ):
        planned = build_form_case_plan(
            cases,
            navbar_tab=NAVBAR_TAB,
            start_number=number,
            filial=operational_placeholder,
            section=section,
        )
        planned_cases.extend(planned)
        number += len(planned)
    expected_count = len(planned_cases)

    monitor = FormMonitor(
        page,
        suite_name="Forms-03 — Продажа",
        planned_cases=planned_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id="test_forms_03_prodaja",
    )
    try:
        monitor.precondition(
            "Admin avtorizatsiyasi",
            lambda: authorization(page, who="admin"),
            affected_case_number=1,
        )
        if monitor.blocked:
            return

        operational_filial = monitor.precondition(
            "Operatsion filialni aniqlash",
            lambda: first_operational_filial(page),
            affected_case_number=1,
        )
        if monitor.blocked:
            return
        monitor.update_filial(operational_placeholder, operational_filial)

        with allure.step(f"1 - '{operational_filial}' filialidagi direct menu formalar"):
            direct_cases = monitor.cases(section="operational-direct")
            monitor.precondition(
                f"'{operational_filial}' filialiga o'tish",
                lambda: switch_forms_filial(page, operational_filial),
                affected_case_number=(
                    direct_cases[0]["number"] if direct_cases else None
                ),
            )
            if monitor.blocked:
                return
            run_form_cases(page, direct_cases, monitor=monitor)

        with allure.step(f"2 - '{operational_filial}' filialidagi page-link formalar"):
            run_form_cases(
                page,
                monitor.cases(section="operational-page-link"),
                monitor=monitor,
            )
    finally:
        with allure.step(f"3 - {expected_count} ta navigatsiya natijasini tekshirish"):
            monitor.finish()


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Продажа — menu va page-link formalarni ochish smoke")
def test_prodaja_menu_forms(page, pytestconfig):
    run_prodaja_menu_forms(
        page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
