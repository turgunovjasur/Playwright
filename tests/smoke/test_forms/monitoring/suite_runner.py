"""Legacy navbar monitoring façade'i va umumiy inventory helperlari."""

from __future__ import annotations

import time

import allure
from playwright.sync_api import Error as PlaywrightError

from tests.smoke.test_forms.inventory import OPERATIONAL_PLACEHOLDER
from tests.smoke.test_forms.monitoring.cases import build_form_case_inventory
from tests.smoke.test_forms.monitoring.monitor import FormMonitor
from tests.smoke.test_forms.monitoring.navigation import first_operational_filial, run_form_cases, switch_forms_filial


def build_suite_inventory(buckets, *, shell, navbar_tab=None):
    """Leaf suite'ning barcha active va intentional-skip caselarini normalizatsiya qiladi."""
    normalized_buckets = [{**bucket, "forms": list(bucket.get("forms") or [])} for bucket in buckets]
    group_keys = []
    for bucket in normalized_buckets:
        for definition in bucket["forms"]:
            key = (definition.get("navbar_tab") or navbar_tab, definition.get("menu_column"))
            if key not in group_keys:
                group_keys.append(key)

    planned_cases = []
    skipped_cases = []
    number = 1
    for group_tab, group_column in group_keys:
        for bucket in normalized_buckets:
            definitions = [definition for definition in bucket["forms"] if (definition.get("navbar_tab") or navbar_tab, definition.get("menu_column")) == (group_tab, group_column)]
            if not definitions:
                continue
            inventory = build_form_case_inventory(definitions, start_number=number, filial=bucket["filial"], navbar_tab=navbar_tab, shell=shell, section=bucket["section"])
            planned_cases.extend(inventory["planned"])
            skipped_cases.extend(inventory["skipped"])
            number += len(inventory["planned"])

    all_cases = planned_cases + skipped_cases
    if not all_cases:
        suite_label = navbar_tab or shell
        raise ValueError(f"{suite_label} uchun forma inventari bo'sh")

    if navbar_tab is not None:
        mixed_tabs = sorted({case["navbar_tab"] for case in all_cases if case["navbar_tab"] != navbar_tab})
        if mixed_tabs:
            raise ValueError(f"{navbar_tab} suite ichida boshqa navbar formalari bor: {mixed_tabs}")

    return planned_cases, skipped_cases


def _run_precondition(monitor, *, operation, affected_case_number, action):
    """Suite preconditionini bajaradi va xatoni monitor blockeriga aylantiradi."""
    started_at = time.monotonic()
    try:
        with allure.step(f"Suite precondition | {operation}"):
            return True, action()
    except (AssertionError, PlaywrightError) as exc:
        monitor.record_precondition_failure(operation, exc, affected_case_number=affected_case_number, started_at=started_at)
        return False, None


def run_legacy_form_monitoring(page, *, suite_name, progress_test_id, navbar_tab, form_buckets, terminal_reporter=None, checks=None, diagnostics=None):
    """Login qilingan page'da legacy navbar inventorysini filiallar bo'yicha bajaradi."""
    planned_cases, skipped_cases = build_suite_inventory(form_buckets, shell="legacy", navbar_tab=navbar_tab)
    monitor = FormMonitor(page, suite_name=suite_name, planned_cases=planned_cases, skipped_cases=skipped_cases, terminal_reporter=terminal_reporter, progress_test_id=progress_test_id, checks=checks, diagnostics=diagnostics)
    try:
        planned = monitor.cases()
        operational_filial = None
        if planned:
            operational_cases = monitor.cases(section="operational")
            if operational_cases:
                filial_resolved, operational_filial = _run_precondition(monitor, operation="Operatsion filialni aniqlash", affected_case_number=operational_cases[0]["number"], action=lambda: first_operational_filial(page))
                if not filial_resolved:
                    return
                monitor.update_filial(OPERATIONAL_PLACEHOLDER, operational_filial)

        menu_columns = []
        for case in monitor.planned_cases + monitor.skipped_cases:
            menu_column = case.get("menu_column")
            if menu_column not in menu_columns:
                menu_columns.append(menu_column)

        current_filial = None
        for menu_column in menu_columns:
            with allure.step(f"Menu column | {menu_column or '<ustunsiz>'}"):
                for section, target_filial in (("operational", operational_filial), ("admin", "Администрирование")):
                    cases = [case for case in monitor.cases(section=section) if case.get("menu_column") == menu_column]
                    if not cases:
                        continue
                    if current_filial != target_filial:
                        switched, _ = _run_precondition(monitor, operation=f"'{target_filial}' filialiga o'tish", affected_case_number=cases[0]["number"], action=lambda filial=target_filial: switch_forms_filial(page, filial))
                        if not switched:
                            return
                        current_filial = target_filial
                    run_form_cases(page, cases, monitor=monitor)

                skipped = [case for case in monitor.skipped_cases if case.get("menu_column") == menu_column]
                if skipped:
                    with allure.step("Ataylab skip qilingan menu itemlar"):
                        for case in skipped:
                            with allure.step(f"Menu item | {case['label']} | SKIPPED"):
                                allure.attach(case["reason"], name="Skip sababi", attachment_type=allure.attachment_type.TEXT)
    finally:
        with allure.step(f"{len(planned_cases)} ta forma natijasini jamlash"):
            results = monitor.finish()
    return results
