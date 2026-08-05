"""Bitta composite menu identity uchun legacy/A2 FormMonitor lifecycle'i."""

from __future__ import annotations

import allure

from tests.smoke.flows.flow_authorization import authorization, company_url
from tests.smoke.test_forms.flow import (
    first_operational_filial,
    run_form_cases,
    switch_forms_filial,
)
from tests.smoke.test_forms.form_cases import (
    build_form_case_inventory,
    form_test_identity,
)
from tests.smoke.test_forms.form_monitor import FormMonitor
from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


OPERATIONAL_PLACEHOLDER = "<operatsion filial>"


def _build_monitor_inventory(
    buckets,
    *,
    shell,
    navbar_tab,
    menu_column,
):
    planned_cases = []
    skipped_cases = []
    expected_identity = form_test_identity(
        shell=shell,
        navbar_tab=navbar_tab,
        menu_column=menu_column,
    )
    number = 1
    for bucket in buckets:
        definitions = list(bucket["forms"] or [])
        if not definitions:
            continue
        inventory = build_form_case_inventory(
            definitions,
            start_number=number,
            filial=bucket["filial"],
            navbar_tab=navbar_tab,
            shell=shell,
            section=bucket["section"],
        )
        mixed_cases = [
            case
            for case in inventory["planned"] + inventory["skipped"]
            if case["test_identity"] != expected_identity
        ]
        if mixed_cases:
            actual = sorted({case["test_identity"] for case in mixed_cases})
            raise ValueError(
                f"Bitta pytest testida boshqa menu identity aralashgan: {actual}; "
                f"kutilgan={expected_identity}"
            )
        planned_cases.extend(inventory["planned"])
        skipped_cases.extend(inventory["skipped"])
        number += len(inventory["planned"])

    if not planned_cases:
        raise ValueError(f"{expected_identity} uchun aktiv forma topilmadi")
    return planned_cases, skipped_cases


def _new_monitor(
    page,
    *,
    suite_name,
    planned_cases,
    skipped_cases,
    terminal_reporter,
    progress_test_id,
    checks,
    diagnostics,
):
    return FormMonitor(
        page,
        suite_name=suite_name,
        planned_cases=planned_cases,
        skipped_cases=skipped_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id=progress_test_id,
        checks=checks,
        diagnostics=diagnostics,
    )


def run_legacy_menu_column_forms(
    page,
    *,
    suite_name,
    navbar_tab,
    menu_column,
    operational_forms=None,
    admin_forms=None,
    terminal_reporter=None,
    progress_test_id,
    checks=None,
    diagnostics=None,
):
    """Bitta legacy menu-column testini deklarativ forma listlaridan bajaradi."""
    planned_cases, skipped_cases = _build_monitor_inventory(
        (
            {
                "forms": operational_forms,
                "filial": OPERATIONAL_PLACEHOLDER,
                "section": "operational",
            },
            {
                "forms": admin_forms,
                "filial": "Администрирование",
                "section": "admin",
            },
        ),
        shell="legacy",
        navbar_tab=navbar_tab,
        menu_column=menu_column,
    )
    monitor = _new_monitor(
        page,
        suite_name=suite_name,
        planned_cases=planned_cases,
        skipped_cases=skipped_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id=progress_test_id,
        checks=checks,
        diagnostics=diagnostics,
    )

    try:
        first_number = planned_cases[0]["number"]
        monitor.precondition(
            "Admin avtorizatsiyasi",
            lambda: authorization(page, who="admin"),
            affected_case_number=first_number,
        )
        if monitor.blocked:
            return

        operational_cases = monitor.cases(section="operational")
        if operational_cases:
            operational_filial = monitor.precondition(
                "Operatsion filialni aniqlash",
                lambda: first_operational_filial(page),
                affected_case_number=operational_cases[0]["number"],
            )
            if monitor.blocked:
                return
            monitor.update_filial(OPERATIONAL_PLACEHOLDER, operational_filial)
            operational_cases = monitor.cases(section="operational")
            with allure.step(f"'{operational_filial}' filialidagi formalar"):
                monitor.precondition(
                    f"'{operational_filial}' filialiga o'tish",
                    lambda: switch_forms_filial(page, operational_filial),
                    affected_case_number=operational_cases[0]["number"],
                )
                if monitor.blocked:
                    return
                run_form_cases(page, operational_cases, monitor=monitor)

        admin_cases = monitor.cases(section="admin")
        if admin_cases:
            with allure.step("'Администрирование' filialidagi formalar"):
                monitor.precondition(
                    "'Администрирование' filialiga o'tish",
                    lambda: switch_forms_filial(page, "Администрирование"),
                    affected_case_number=admin_cases[0]["number"],
                )
                if monitor.blocked:
                    return
                run_form_cases(page, admin_cases, monitor=monitor)
    finally:
        with allure.step(f"{len(planned_cases)} ta forma natijasini jamlash"):
            monitor.finish()


def _open_a2_dashboard_shell(page):
    page.goto(
        f"{company_url()}/a2/trade/intro/dashboard",
        wait_until="domcontentloaded",
        timeout=30_000,
    )
    AngularBasePage(page).wait_for_loader(timeout=30_000)


def run_a2_menu_column_forms(
    page,
    *,
    suite_name,
    navbar_tab,
    menu_column,
    admin_forms=None,
    operational_forms=None,
    terminal_reporter=None,
    progress_test_id,
    checks=None,
    diagnostics=None,
):
    """Bitta A2 menu-column testini shell/filial sync bilan bajaradi."""
    planned_cases, skipped_cases = _build_monitor_inventory(
        (
            {
                "forms": admin_forms,
                "filial": "Администрирование",
                "section": "admin",
            },
            {
                "forms": operational_forms,
                "filial": OPERATIONAL_PLACEHOLDER,
                "section": "operational",
            },
        ),
        shell="a2",
        navbar_tab=navbar_tab,
        menu_column=menu_column,
    )
    monitor = _new_monitor(
        page,
        suite_name=suite_name,
        planned_cases=planned_cases,
        skipped_cases=skipped_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id=progress_test_id,
        checks=checks,
        diagnostics=diagnostics,
    )

    try:
        first_number = planned_cases[0]["number"]
        monitor.precondition(
            "Admin avtorizatsiyasi",
            lambda: authorization(page, who="admin"),
            affected_case_number=first_number,
        )
        if monitor.blocked:
            return

        monitor.precondition(
            "Legacy shellni 'Администрирование' filialiga o'tkazish",
            lambda: BasePage(page).switch_filial(name="Администрирование"),
            affected_case_number=first_number,
        )
        if monitor.blocked:
            return

        operational_cases = monitor.cases(section="operational")
        operational_filial = None
        if operational_cases:
            operational_filial = monitor.precondition(
                "Operatsion filialni aniqlash",
                lambda: first_operational_filial(page),
                affected_case_number=operational_cases[0]["number"],
            )
            if monitor.blocked:
                return
            monitor.update_filial(OPERATIONAL_PLACEHOLDER, operational_filial)

        monitor.precondition(
            "A2 dashboard shellga kirish",
            lambda: _open_a2_dashboard_shell(page),
            affected_case_number=first_number,
        )
        if monitor.blocked:
            return

        angular = AngularBasePage(page)
        admin_cases = monitor.cases(section="admin")
        if admin_cases:
            with allure.step("'Администрирование' filialidagi A2 formalar"):
                monitor.precondition(
                    "A2 filialini 'Администрирование' bilan sinxronlash",
                    lambda: angular.switch_filial(name="Администрирование"),
                    affected_case_number=admin_cases[0]["number"],
                )
                if monitor.blocked:
                    return
                run_form_cases(page, admin_cases, monitor=monitor)

        operational_cases = monitor.cases(section="operational")
        if operational_cases:
            with allure.step(f"'{operational_filial}' filialidagi A2 formalar"):
                monitor.precondition(
                    f"A2 shellni '{operational_filial}' filialiga o'tkazish",
                    lambda: angular.switch_filial(name=operational_filial),
                    affected_case_number=operational_cases[0]["number"],
                )
                if monitor.blocked:
                    return
                run_form_cases(page, operational_cases, monitor=monitor)
    finally:
        with allure.step(f"{len(planned_cases)} ta A2 forma natijasini jamlash"):
            monitor.finish()
