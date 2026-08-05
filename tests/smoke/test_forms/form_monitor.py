"""Barcha forma runnerlari uchun markaziy kuzatuv, tahlil va hisobot xizmati."""

from __future__ import annotations

import json
import re
import time
from collections import Counter

import allure
from playwright.sync_api import Error as PlaywrightError

from tests.smoke.progress import emit_progress_event
from tests.smoke.smoke_reporting import safe_page_screenshot
from tests.smoke.test_forms.form_cases import (
    build_form_case_inventory,
    build_form_case_plan,
    form_case,
    form_case_key,
)
from tests.smoke.test_forms.form_checks import (
    CHECK_NAMES,
    NOT_CHECKED,
    NOT_OPENED,
    OBSERVED_ONLY,
    OPENED_WITH_DEFECT,
    PASSED,
    TEST_BLOCKED,
    allowed_warning_text as _allowed_warning_text,
    assert_healthy_form_state as _assert_healthy_form_state,
    classify_form_failure,
    clean_text as _clean_text,
    evaluate_checks,
    normalize_enabled_names,
    reason_description,
    title_verified as _title_verified,
)
from tests.smoke.test_forms.form_diagnostics import (
    ALERT_SELECTORS,
    ALERT_WAIT_MS,
    CAPTURE_JS_ERROR_SCRIPT,
    CAPTURE_READ_SCRIPT,
    CAPTURE_RESET_SCRIPT,
    DIAGNOSTIC_NAMES,
    EMPTY_CAPTURE_SIGNALS,
    MAX_PAGE_EVENTS,
    capture_form_state,
    evaluate_diagnostics,
    failed_request_label as _failed_request_label,
    js_error_label as _js_error_label,
    reset_capture_signals as _reset_capture_signals,
    safe_locator_visible as _safe_locator_visible,
)
from tests.smoke.test_forms.flow import settle_form_open
from tests.smoke.test_forms.form_reporting import (
    build_monitor_payload,
    build_form_result,
    form_step_title,
    format_form_result,
    render_monitor_summary,
    write_terminal_report,
)


def _shell_from_url(url, fallback=None):
    if "/a2/" in (url or ""):
        return "a2"
    if url:
        return "legacy"
    return fallback


class FormMonitor:
    """Forma suite'ini boshidan oxirigacha kuzatuvchi markaziy xizmat."""

    def __init__(
        self,
        page,
        *,
        suite_name,
        planned_cases,
        terminal_reporter=None,
        progress_runner="test_0_forms_runner.py",
        progress_test_id="forms",
        skipped_cases=None,
        checks=None,
        diagnostics=None,
    ):
        self.page = page
        self.suite_name = suite_name
        self.planned_cases = [dict(case) for case in planned_cases]
        self.skipped_cases = [dict(case) for case in (skipped_cases or [])]
        self.terminal_reporter = terminal_reporter
        self.progress_runner = progress_runner
        self.progress_test_id = progress_test_id
        self.enabled_checks = normalize_enabled_names(checks)
        self.enabled_diagnostics = normalize_enabled_names(
            diagnostics,
            available=DIAGNOSTIC_NAMES,
            option_name="diagnostics",
        )
        self.results = []
        self.blockers = []
        self.blocked = False
        self._results_by_number = {}
        self.js_errors = []
        self.failed_requests = []
        self.js_error_count = 0
        self.failed_request_count = 0

        numbers = [case["number"] for case in self.planned_cases]
        duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
        if duplicates:
            raise ValueError(f"Takrorlangan forma raqami bor: {duplicates}")

        case_keys = [form_case_key(case) for case in self.planned_cases]
        duplicate_keys = sorted(
            key for key, count in Counter(case_keys).items() if count > 1
        )
        if duplicate_keys:
            raise ValueError(
                "Bitta form testida takrorlangan forma definition bor: "
                f"{duplicate_keys}"
            )

        self._install_page_listeners()

    def _install_page_listeners(self):
        """``pageerror`` va 4xx/5xx javoblarni yig'ishni yoqadi.

        JS xatosi formani ``JS_ERROR`` nuqsoni qiladi; network signallari esa
        raw payload uchun qayd qilinadi va human hisobotda agregatsiya qilinadi.

        Diqqat: ``pageerror`` **faqat legacy shell'da** ishlaydi. A2 ilovasi
        global ``error`` eventida ``preventDefault()`` chaqiradi, shuning uchun
        A2 formalarida bu kanal ko'r — batafsil `ui-patterns.md`.
        """
        self._pageerror_listener_installed = False
        self._response_listener_installed = False
        try:
            if "javascript" in self.enabled_checks:
                self.page.on("pageerror", self._record_js_error)
                self._pageerror_listener_installed = True
            if "failed_requests" in self.enabled_diagnostics:
                self.page.on("response", self._record_failed_request)
                self._response_listener_installed = True
        except (AttributeError, TypeError):
            self._listeners_installed = False
            return
        self._listeners_installed = (
            self._pageerror_listener_installed
            or self._response_listener_installed
        )
        if (
            "javascript" in self.enabled_checks
            or "resource_errors" in self.enabled_diagnostics
            or "promise_rejections" in self.enabled_diagnostics
        ):
            self._install_capture_js_error_script()

    def _install_capture_js_error_script(self):
        """A2 uchun canonical capture-fazali JS xato kuzatuvini yoqadi.

        ``add_init_script`` ni olib tashlashning Playwright'da yo'li yo'q, va
        uch suite bitta ``page`` fixture'ni bo'lishadi — shuning uchun har
        ``FormMonitor.__init__`` bu funksiyani qayta chaqiradi. Takroriy
        listener ro'yxatga olinishining oldini skriptning o'zidagi
        ``__formMonitorCaptureInstalled`` bayrog'i oladi: har document yangi
        ``window`` bilan boshlanadi, birinchi qo'shilgan skript bayroqni
        o'rnatadi, qolganlari jim chiqib ketadi.
        """
        try:
            self.page.add_init_script(CAPTURE_JS_ERROR_SCRIPT)
        except (PlaywrightError, AttributeError, TypeError):
            pass

    def _remove_page_listeners(self):
        if not getattr(self, "_listeners_installed", False):
            return
        try:
            if self._pageerror_listener_installed:
                self.page.remove_listener("pageerror", self._record_js_error)
            if self._response_listener_installed:
                self.page.remove_listener("response", self._record_failed_request)
        except (AttributeError, TypeError, ValueError, KeyError):
            pass
        self._listeners_installed = False

    def _record_js_error(self, error):
        label = _js_error_label(error)
        if not label:
            return
        self.js_error_count += 1
        if len(self.js_errors) < MAX_PAGE_EVENTS:
            self.js_errors.append(label)

    def _record_failed_request(self, response):
        label = _failed_request_label(response)
        if not label:
            return
        self.failed_request_count += 1
        if len(self.failed_requests) < MAX_PAGE_EVENTS:
            self.failed_requests.append(label)

    def _reset_page_events(self):
        """Har case/precondition o'z oynasini oladi — signal qo'shnisiga o'tmaydi."""
        self.js_errors = []
        self.failed_requests = []
        self.js_error_count = 0
        self.failed_request_count = 0
        if (
            "javascript" in self.enabled_checks
            or "resource_errors" in self.enabled_diagnostics
            or "promise_rejections" in self.enabled_diagnostics
        ):
            _reset_capture_signals(self.page)

    def update_filial(self, placeholder, actual_name):
        for case in self.planned_cases + self.skipped_cases:
            if case.get("filial") == placeholder:
                case["filial"] = actual_name

    def _planned_case(self, number):
        return next(
            (case for case in self.planned_cases if case["number"] == number),
            None,
        )

    def planned_case(self, number):
        """Runtime'da actual filial bilan yangilangan planned case'ni qaytaradi."""
        case = self._planned_case(number)
        if case is None:
            raise KeyError(f"Planned forma topilmadi: {number}")
        return case

    def cases(self, *, section=None):
        """Monitor ichidagi aktual case'larni raqam tartibida qaytaradi."""
        cases = self.planned_cases
        if section is not None:
            cases = [case for case in cases if case.get("section") == section]
        return sorted(cases, key=lambda case: case["number"])

    def _write_live_line(self, line):
        if self.terminal_reporter is not None:
            self.terminal_reporter.write_line(line)
        else:
            print(line, flush=True)

    def _append_result(self, result):
        number = result["number"]
        if number in self._results_by_number:
            raise RuntimeError(f"Forma natijasi ikki marta yozilmoqda: {number:03d}")
        self._results_by_number[number] = result
        self.results.append(result)
        reason = result.get("reason_summary") or result.get("reason_code")
        reason_part = f" | Sabab: {reason}" if reason else ""
        line = (
            f"[FORM MONITOR] {number:03d}/{len(self.planned_cases):03d} "
            f"{result.get('status_icon', '•')} {result.get('status')} | "
            f"Forma: {result['title']} | Filial: {result['filial']}"
            f"{reason_part}"
        )
        self._write_live_line(line)
        emit_progress_event(
            event="form_result",
            group="Forms group",
            runner=self.progress_runner,
            test_id=self.progress_test_id,
            title=self.suite_name,
            display=(
                f"{self.suite_name}: {number:03d}/{len(self.planned_cases):03d} "
                f"{result['title']} — {result['status']}"
            ),
            error_type=result.get("reason_code") or None,
            message=reason or None,
            writer=(
                self.terminal_reporter.write_line
                if self.terminal_reporter is not None
                else None
            ),
            form_number=number,
            form_total=len(self.planned_cases),
            form_status=result["status"],
        )
        return result

    def _attach_case_evidence(self, result, *, case=None):
        safe_title = re.sub(r"[^\w.-]+", "-", result["title"], flags=re.UNICODE).strip("-")
        screenshot_name = (
            f"{result['number']:03d}-{safe_title}-{result['status']}-"
            f"{result.get('reason_code') or 'UNKNOWN'}-evidence"
        )
        try:
            allure.attach(
                safe_page_screenshot(
                    self.page,
                    full_page=True,
                    mask_profile=(case or {}).get("screenshot_mask"),
                ),
                name=screenshot_name,
                attachment_type=allure.attachment_type.PNG,
            )
            result["screenshot"] = screenshot_name
            result["screenshot_redacted"] = True
        except (PlaywrightError, OSError, ValueError, AttributeError, TypeError) as exc:
            result["screenshot_error"] = _clean_text(exc)
        allure.attach(
            format_form_result(result),
            name=f"{result['number']:03d} | {result['title']} | monitoring tafsilotlari",
            attachment_type=allure.attachment_type.TEXT,
        )

    @staticmethod
    def _checks(
        case,
        state,
        *,
        enabled_checks=None,
        enabled_diagnostics=None,
        page_events=None,
    ):
        hard_checks = evaluate_checks(
            case,
            state,
            enabled_names=enabled_checks,
        )
        diagnostics = evaluate_diagnostics(
            state,
            page_events or {},
            enabled_names=enabled_diagnostics,
        )
        path_matches = hard_checks["url"]["passed"]
        allowed_warning = _allowed_warning_text(case, state)
        visible_error = hard_checks["application_error"]["actual"]
        js_errors = (
            list(state.get("js_errors") or [])
            if hard_checks["javascript"]["enabled"]
            else []
        )
        capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
        resources = diagnostics["resource_errors"]
        promises = diagnostics["promise_rejections"]
        busy = diagnostics["busy"]
        failed_requests = diagnostics["failed_requests"]
        usability_names = (
            "url",
            "application_error",
            "javascript",
            "loader",
            "content_ready",
        )
        enabled_usability_checks = [
            hard_checks[name]
            for name in usability_names
            if hard_checks[name]["enabled"]
        ]
        usable = bool(enabled_usability_checks) and all(
            result["passed"] for result in enabled_usability_checks
        )
        return {
            "js_errors": js_errors,
            "js_error_count": (
                int(state.get("js_error_count") or 0)
                if hard_checks["javascript"]["enabled"]
                else 0
            ),
            "js_error_source": (
                state.get("js_error_source") or ""
                if hard_checks["javascript"]["enabled"]
                else ""
            ),
            "capture_js_errors": (
                list(capture.get("js_errors") or [])[:MAX_PAGE_EVENTS]
                if hard_checks["javascript"]["enabled"]
                else []
            ),
            "capture_js_error_count": (
                int(capture.get("js_error_count") or 0)
                if hard_checks["javascript"]["enabled"]
                else 0
            ),
            "capture_resource_errors": resources.get("samples", []),
            "capture_resource_error_count": resources.get("count", 0),
            "promise_rejections": promises.get("samples", []),
            "promise_rejection_count": promises.get("count", 0),
            "failed_requests": failed_requests.get("samples", []),
            "failed_request_count": failed_requests.get("count", 0),
            "url_matches": path_matches,
            "title_matches": hard_checks["title"]["passed"],
            "title_verified": (
                _title_verified(case, state)
                if hard_checks["title"]["enabled"]
                else False
            ),
            "title_source": state.get("title_source") or "",
            "document_title": state.get("document_title") or "",
            "content_ready": hard_checks["content_ready"]["passed"],
            "ready_required": bool(state.get("ready_required")),
            "ready_visible": bool(state.get("ready_visible")),
            "loader_visible": (
                not hard_checks["loader"]["passed"]
                if hard_checks["loader"]["enabled"]
                else False
            ),
            "busy_visible": busy.get("visible", False),
            "busy_visible_count": busy.get("count", 0),
            "visible_error": visible_error,
            "allowed_warning": allowed_warning,
            "usable": usable,
            "hard_checks": hard_checks,
            "diagnostics": diagnostics,
            "enabled_checks": [
                name for name in CHECK_NAMES if hard_checks[name]["enabled"]
            ],
            "enabled_diagnostics": [
                name
                for name in DIAGNOSTIC_NAMES
                if diagnostics[name]["enabled"]
            ],
        }

    def _capture_state(self, case=None):
        """Shellga mos yagona effective JS kanalini sahifa holatiga qo'shadi."""
        state = capture_form_state(self.page, ready=(case or {}).get("ready"))
        capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
        if "javascript" not in self.enabled_checks:
            state["js_errors"] = []
            state["js_error_count"] = 0
            state["js_error_source"] = "disabled"
        elif "/a2/" in state.get("actual_url", ""):
            state["js_errors"] = list(capture["js_errors"])
            state["js_error_count"] = capture["js_error_count"]
            state["js_error_source"] = "capture"
        else:
            state["js_errors"] = list(self.js_errors)
            state["js_error_count"] = self.js_error_count
            state["js_error_source"] = "pageerror"
        return state

    def _case_checks(self, case, state):
        """Sof holat tekshiruvlariga cheklanmagan hisoblar va network signalini qo'shadi.

        JS xatolari ``state`` orqali ``_checks`` ga yetib boradi va statusga
        ta'sir qiladi; network signallari esa hozir faqat qayd qilinadi.
        """
        checks = self._checks(
            case,
            state,
            enabled_checks=list(self.enabled_checks),
            enabled_diagnostics=list(self.enabled_diagnostics),
            page_events={
                "failed_requests": self.failed_requests,
                "failed_request_count": self.failed_request_count,
            },
        )
        return checks

    def _failure_result(
        self,
        *,
        case,
        stage,
        exc,
        started_at,
        test_started,
        test_completed,
        state=None,
    ):
        state = state or self._capture_state(case)
        detail = _clean_text(exc)
        checks = self._case_checks(case, state)
        analysis = classify_form_failure(
            case=case,
            stage=stage,
            detail=detail,
            state=state,
            enabled_names=list(self.enabled_checks),
            check_results=checks["hard_checks"],
        )
        result = build_form_result(
            number=case["number"],
            filial=case["filial"],
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            menu_item=case["menu_item"],
            title=case["title"],
            expected_path=case.get("expected_path"),
            actual_url=state["actual_url"],
            page_links=case.get("page_links"),
            action=case.get("action"),
            add_icon=case.get("add_icon", False),
            detail=detail,
            status=analysis["status"],
            reason_code=analysis["reason_code"],
            reason_summary=analysis["reason_summary"],
            failed_stage=stage,
            expected_title=case["title"],
            actual_title=state["actual_title"],
            opened=analysis["opened"],
            page_reached=(
                stage == "validation"
                and test_started
                and (
                    checks["url_matches"]
                    if "url" in self.enabled_checks
                    else True
                )
            ),
            test_started=test_started,
            test_completed=test_completed,
            validation_completed=(stage == "validation" and test_started),
            validation_passed=False,
            usable=(checks["usable"] if test_started else False),
            checks=checks,
            shell=_shell_from_url(state["actual_url"], case.get("shell")),
            suite=self.suite_name,
            duration_ms=int((time.monotonic() - started_at) * 1000),
            label=case.get("label"),
            test_identity=case.get("test_identity"),
        )
        return self._append_result(result)

    def run_case(self, case, *, navigate):
        """Bitta formani kuzatadi; kutilgan UI xatosidan keyin davom etadi."""
        if self.blocked:
            return None
        case = dict(self.planned_case(case["number"]))
        self._reset_page_events()
        started_at = time.monotonic()
        stage = "navigation"
        failure_result = None
        state = None
        previous_url = getattr(self.page, "url", "") or ""
        step_title = form_step_title(
            number=case["number"],
            filial=case["filial"],
            navbar_tab=case["navbar_tab"],
            menu_column=case.get("menu_column"),
            title=case["title"],
        )

        try:
            with allure.step(step_title):
                try:
                    navigate()
                    stage = "validation"
                    with allure.step(
                        f"Tekshiruv | Forma: {case['title']} | "
                        f"Kutilgan URL: {case.get('expected_path') or '—'}"
                    ):
                        settle_detail = settle_form_open(
                            self.page,
                            case=case,
                            enabled_checks=self.enabled_checks,
                            previous_url=previous_url,
                        )
                        state = self._capture_state(case)
                        _assert_healthy_form_state(
                            case,
                            state,
                            enabled_names=list(self.enabled_checks),
                        )
                except (AssertionError, PlaywrightError) as exc:
                    failure_result = self._failure_result(
                        case=case,
                        stage=stage,
                        exc=exc,
                        started_at=started_at,
                        test_started=True,
                        test_completed=True,
                        state=state,
                    )
                    self._attach_case_evidence(failure_result, case=case)
                    raise

                checks = self._case_checks(case, state)
                checks["settle_detail"] = _clean_text(settle_detail)
                observed_only = not self.enabled_checks
                status = OBSERVED_ONLY if observed_only else PASSED
                result = build_form_result(
                    number=case["number"],
                    filial=case["filial"],
                    navbar_tab=case["navbar_tab"],
                    menu_column=case.get("menu_column"),
                    menu_item=case["menu_item"],
                    title=case["title"],
                    expected_path=case.get("expected_path"),
                    actual_url=state["actual_url"],
                    page_links=case.get("page_links"),
                    action=case.get("action"),
                    add_icon=case.get("add_icon", False),
                    status=status,
                    reason_code="",
                    failed_stage="",
                    expected_title=case["title"],
                    actual_title=state["actual_title"],
                    opened=True,
                    page_reached=True,
                    test_started=True,
                    test_completed=True,
                    validation_completed=not observed_only,
                    validation_passed=not observed_only,
                    usable=checks["usable"],
                    checks=checks,
                    shell=_shell_from_url(state["actual_url"], case.get("shell")),
                    suite=self.suite_name,
                    duration_ms=int((time.monotonic() - started_at) * 1000),
                    label=case.get("label"),
                    test_identity=case.get("test_identity"),
                )
                self._append_result(result)
                result_label = "KUZATILDI" if observed_only else "OCHILDI"
                with allure.step(
                    f"Natija: {result_label} | Haqiqiy URL: {state['actual_url']}"
                ):
                    pass
        except (AssertionError, PlaywrightError):
            return failure_result

        return result

    def precondition(self, operation, action, *, affected_case_number=None):
        """Login/filial/shell kabi suite amallarini forma xatosidan ajratadi."""
        if self.blocked:
            return None
        self._reset_page_events()
        started_at = time.monotonic()
        value = None
        try:
            with allure.step(f"Suite precondition | {operation}"):
                try:
                    value = action()
                except (AssertionError, PlaywrightError) as exc:
                    self._block_suite(
                        operation=operation,
                        exc=exc,
                        affected_case_number=affected_case_number,
                        started_at=started_at,
                    )
                    raise
        except (AssertionError, PlaywrightError):
            return None
        return value

    def _block_suite(self, *, operation, exc, affected_case_number, started_at):
        self.blocked = True
        case = self._planned_case(affected_case_number) if affected_case_number else None
        if case is None:
            case = next(
                (
                    planned
                    for planned in self.planned_cases
                    if planned["number"] not in self._results_by_number
                ),
                None,
            )
            if case is not None:
                affected_case_number = case["number"]
        state = self._capture_state(case)
        analysis_case = dict(case or {})
        analysis_case["failed_operation"] = operation
        analysis = classify_form_failure(
            case=analysis_case,
            stage="suite_precondition",
            detail=exc,
            state=state,
        )
        blocker = {
            "operation": operation,
            "reason_code": analysis["reason_code"],
            "detail": _clean_text(exc),
            "actual_url": state["actual_url"],
            "actual_title": state["actual_title"],
            "affected_case_number": affected_case_number,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
        }
        self.blockers.append(blocker)

        if case is not None:
            blocked_case = dict(case)
            blocked_case["failed_operation"] = operation
            result = self._failure_result(
                case=blocked_case,
                stage="suite_precondition",
                exc=exc,
                started_at=started_at,
                test_started=False,
                test_completed=False,
                state=state,
            )
            self._attach_case_evidence(result, case=blocked_case)
        else:
            allure.attach(
                json.dumps(blocker, ensure_ascii=False, indent=2),
                name=f"Suite blocker | {operation}",
                attachment_type=allure.attachment_type.JSON,
            )
            try:
                allure.attach(
                    safe_page_screenshot(self.page, full_page=True),
                    name=f"Suite blocker | {operation} | redacted screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except (PlaywrightError, OSError, ValueError, AttributeError, TypeError):
                pass

    def _append_not_checked(self):
        blocker_reason = "BLOCKED_BY_PRECONDITION" if self.blockers else "NOT_EXECUTED"
        for case in self.planned_cases:
            if case["number"] in self._results_by_number:
                continue
            result = build_form_result(
                number=case["number"],
                filial=case["filial"],
                navbar_tab=case["navbar_tab"],
                menu_column=case.get("menu_column"),
                menu_item=case["menu_item"],
                title=case["title"],
                expected_path=case.get("expected_path"),
                actual_url="",
                page_links=case.get("page_links"),
                action=case.get("action"),
                add_icon=case.get("add_icon", False),
                detail="",
                status=NOT_CHECKED,
                reason_code=blocker_reason,
                reason_summary=reason_description(blocker_reason),
                failed_stage="not_started",
                expected_title=case["title"],
                actual_title="",
                opened=False,
                page_reached=False,
                test_started=False,
                test_completed=False,
                validation_completed=False,
                validation_passed=False,
                usable=False,
                checks={},
                shell=case.get("shell"),
                suite=self.suite_name,
                duration_ms=None,
                label=case.get("label"),
                test_identity=case.get("test_identity"),
            )
            self._append_result(result)

    def complete_results(self):
        """Planned, ammo ishlamagan formalarni NOT_CHECKED bilan to'ldiradi."""
        self._append_not_checked()
        return sorted(self.results, key=lambda result: result["number"])

    def finish(self):
        """Har qanday yakunda to'liq planned coverage va yagona hisobot chiqaradi."""
        self._remove_page_listeners()
        ordered_results = self.complete_results()
        summary = render_monitor_summary(
            suite_name=self.suite_name,
            planned_count=len(self.planned_cases),
            results=ordered_results,
            blockers=self.blockers,
            skipped_cases=self.skipped_cases,
        )
        write_terminal_report(summary, terminal_reporter=self.terminal_reporter)
        allure.attach(
            summary,
            name=f"{self.suite_name} | markaziy forma monitoring hisoboti",
            attachment_type=allure.attachment_type.TEXT,
        )
        payload = build_monitor_payload(
            suite_name=self.suite_name,
            planned_count=len(self.planned_cases),
            results=ordered_results,
            blockers=self.blockers,
            skipped_cases=self.skipped_cases,
            enabled_checks=self.enabled_checks,
            enabled_diagnostics=self.enabled_diagnostics,
        )
        allure.attach(
            json.dumps(payload, ensure_ascii=False, indent=2),
            name=f"{self.suite_name} | form-monitor.json",
            attachment_type=allure.attachment_type.JSON,
        )

        counts = _status_counts(ordered_results)
        actionable = [
            result
            for result in ordered_results
            if result["status"] not in {PASSED, OBSERVED_ONLY, NOT_CHECKED}
        ]
        if actionable or counts[NOT_CHECKED]:
            failures = "\n".join(
                f"{result['number']:03d} | {result['title']} | "
                f"{result['status']} | {result.get('reason_code') or '—'} | "
                f"{result.get('detail') or '—'}"
                for result in actionable
            )
            raise AssertionError(
                f"{self.suite_name}: reja={len(ordered_results)}, "
                f"muvaffaqiyatli={counts[PASSED]}, "
                f"faqat_kuzatildi={counts[OBSERVED_ONLY]}, "
                f"nuqsonli={counts[OPENED_WITH_DEFECT]}, "
                f"ochilmadi={counts[NOT_OPENED]}, "
                f"bloklandi={counts[TEST_BLOCKED]}, "
                f"tekshirilmadi={counts[NOT_CHECKED]}.\n"
                f"Asosiy muammolar:\n{failures or 'Suite yakunlanmadi.'}"
            )
        return ordered_results
