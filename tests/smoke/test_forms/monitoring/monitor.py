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
from tests.smoke.test_forms.monitoring.cases import (
    build_form_case_inventory as _build_form_case_inventory,
    build_form_case_plan as _build_form_case_plan,
    form_case as _form_case,
    form_case_key,
)
from tests.smoke.test_forms.monitoring.checks import (
    CHECK_NAMES,
    DEFAULT_APPLICATION_ERROR_TIMEOUT,
    DEFAULT_CONTENT_READY_TIMEOUT,
    DEFAULT_LOADER_TIMEOUT,
    DEFAULT_TITLE_TIMEOUT,
    DEFAULT_URL_TIMEOUT,
    HARD_ERROR_SELECTORS,
    NOT_CHECKED,
    NOT_OPENED,
    OBSERVED_ONLY,
    OPENED_WITH_DEFECT,
    PASSED,
    TEST_BLOCKED,
    canonical_form_path,
    check_application_error,
    check_content_ready,
    check_loader,
    check_title,
    check_url,
    classify_form_failure,
    clean_text as _clean_text,
    detect_shell,
    dismiss_application_error,
    evaluate_checks,
    normalize_enabled_names,
    primary_check_failure,
    reason_description,
)
from tests.smoke.test_forms.monitoring.diagnostics import (
    DIAGNOSTIC_NAMES,
    FormDiagnostics,
    MAX_PAGE_EVENTS,
    capture_form_state,
)
from tests.smoke.test_forms.monitoring.reporting import (
    build_monitor_payload,
    build_form_result,
    form_step_title,
    format_form_result,
    format_form_result_row,
    render_monitor_summary,
    status_counts,
    write_terminal_report,
)


# Modulga ajratishdan oldingi public/test consumer importlari buzilmasin.
ALERT_SELECTORS = HARD_ERROR_SELECTORS
ALERT_WAIT_MS = DEFAULT_APPLICATION_ERROR_TIMEOUT
build_form_case_inventory = _build_form_case_inventory
build_form_case_plan = _build_form_case_plan
form_case = _form_case


def _shell_from_url(url, fallback=None):
    detected = detect_shell(url)
    if detected is not None:
        return detected
    return fallback if not url else None


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
        url_timeout=DEFAULT_URL_TIMEOUT,
        loader_timeout=DEFAULT_LOADER_TIMEOUT,
        application_error_timeout=DEFAULT_APPLICATION_ERROR_TIMEOUT,
        content_ready_timeout=DEFAULT_CONTENT_READY_TIMEOUT,
        title_timeout=DEFAULT_TITLE_TIMEOUT,
        try_direct_url=True,
    ):
        self.page = page
        self.suite_name = suite_name
        self.planned_cases = [dict(case) for case in planned_cases]
        self.skipped_cases = [dict(case) for case in (skipped_cases or [])]
        self.terminal_reporter = terminal_reporter
        self.progress_runner = progress_runner
        self.progress_test_id = progress_test_id
        self.enabled_checks = normalize_enabled_names(checks)
        if not isinstance(url_timeout, int) or isinstance(url_timeout, bool) or url_timeout <= 0:
            raise ValueError("FormMonitor url_timeout musbat int bo'lishi kerak")
        if not isinstance(loader_timeout, int) or isinstance(loader_timeout, bool) or loader_timeout <= 0:
            raise ValueError("FormMonitor loader_timeout musbat int bo'lishi kerak")
        if (
            not isinstance(application_error_timeout, int)
            or isinstance(application_error_timeout, bool)
            or application_error_timeout <= 0
        ):
            raise ValueError("FormMonitor application_error_timeout musbat int bo'lishi kerak")
        if (
            not isinstance(content_ready_timeout, int)
            or isinstance(content_ready_timeout, bool)
            or content_ready_timeout <= 0
        ):
            raise ValueError("FormMonitor content_ready_timeout musbat int bo'lishi kerak")
        if (
            not isinstance(title_timeout, int)
            or isinstance(title_timeout, bool)
            or title_timeout <= 0
        ):
            raise ValueError("FormMonitor title_timeout musbat int bo'lishi kerak")
        if not isinstance(try_direct_url, bool):
            raise ValueError("FormMonitor try_direct_url bool bo'lishi kerak")
        self.url_timeout = url_timeout
        self.loader_timeout = loader_timeout
        self.application_error_timeout = application_error_timeout
        self.content_ready_timeout = content_ready_timeout
        self.title_timeout = title_timeout
        self.try_direct_url = try_direct_url
        self.results = []
        self.blockers = []
        self.blocked = False
        self._results_by_number = {}

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

        self.form_diagnostics = FormDiagnostics(
            self.page,
            enabled_names=diagnostics,
        )
        self.enabled_diagnostics = self.form_diagnostics.enabled_names

    def _reset_page_events(self):
        """Har case/precondition o'z oynasini oladi — signal qo'shnisiga o'tmaydi."""
        self.form_diagnostics.reset()

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
        line = (
            "[FORM MONITOR] "
            f"{format_form_result_row(result, total=len(self.planned_cases))}"
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

    def _capture_case_screenshot(self, result, *, case=None):
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

    def _attach_case_evidence(self, result, *, case=None):
        self._capture_case_screenshot(result, case=case)
        self._attach_case_details(result)

    @staticmethod
    def _attach_case_details(result):
        allure.attach(
            format_form_result(result),
            name=f"{result['number']:03d} | {result['title']} | monitoring tafsilotlari",
            attachment_type=allure.attachment_type.TEXT,
        )

    def _capture_url_check_evidence(self, case, stage, check_result):
        safe_title = re.sub(r"[^\w.-]+", "-", case["title"], flags=re.UNICODE).strip("-")
        reason_code = check_result.get("reason_code") or "EXPECTED_URL_NOT_REACHED"
        screenshot_name = f"{case['number']:03d}-{safe_title}-NOT_OPENED-{reason_code}-{stage}-evidence"
        try:
            allure.attach(safe_page_screenshot(self.page, full_page=True, mask_profile=case.get("screenshot_mask")), name=screenshot_name, attachment_type=allure.attachment_type.PNG)
            return {"stage": stage, "name": screenshot_name, "redacted": True}
        except (PlaywrightError, OSError, ValueError, AttributeError, TypeError) as exc:
            return {"stage": stage, "error": _clean_text(exc), "redacted": True}

    @staticmethod
    def _checks(
        case,
        state,
        *,
        enabled_checks=None,
        enabled_diagnostics=None,
        diagnostic_results=None,
        precomputed_checks=None,
        stop_after=None,
    ):
        hard_checks = evaluate_checks(
            case,
            state,
            enabled_names=enabled_checks,
            precomputed_results=precomputed_checks,
            stop_after=stop_after,
        )
        if diagnostic_results is None:
            run_diagnostics = not (
                stop_after == "url"
                and hard_checks["url"].get("passed") is False
            )
            enabled_names = set(
                normalize_enabled_names(
                    enabled_diagnostics,
                    available=DIAGNOSTIC_NAMES,
                    option_name="diagnostics",
                )
            )
            diagnostics = {
                "failed_requests": (
                    {
                        "enabled": True,
                        "execution_status": "COMPLETED",
                        "count": 0,
                        "samples": [],
                    }
                    if "failed_requests" in enabled_names and run_diagnostics
                    else (
                        {
                            "enabled": True,
                            "execution_status": "NOT_RUN",
                            "blocked_by": "url",
                        }
                        if "failed_requests" in enabled_names
                        else {
                            "enabled": False,
                            "execution_status": "DISABLED",
                        }
                    )
                )
            }
        else:
            diagnostics = dict(diagnostic_results)
        path_matches = hard_checks["url"]["passed"]
        visible_error = hard_checks["application_error"]["actual"]
        content_ready_check = hard_checks["content_ready"]
        title_check = hard_checks["title"]
        failed_requests = diagnostics["failed_requests"]
        usability_names = (
            "url",
            "loader",
            "application_error",
            "content_ready",
        )
        enabled_usability_checks = [
            hard_checks[name]
            for name in usability_names
            if hard_checks[name]["enabled"] and hard_checks[name]["passed"] is not None
        ]
        usable = bool(enabled_usability_checks) and all(
            result["passed"] for result in enabled_usability_checks
        )
        return {
            "failed_requests": failed_requests.get("samples", []),
            "failed_request_count": failed_requests.get("count", 0),
            "url_matches": path_matches,
            "title_matches": title_check["passed"],
            "title_verified": (
                title_check.get("execution_status") in {"PASSED", "FAILED"}
            ),
            "title_source": (
                title_check.get("title_source")
                or state.get("title_source")
                or ""
            ),
            "document_title": (
                title_check.get("document_title")
                or state.get("document_title")
                or ""
            ),
            "content_ready": content_ready_check["passed"],
            "ready_required": content_ready_check.get("ready_source") == "explicit",
            "ready_visible": (
                content_ready_check.get("ready_source") == "explicit"
                and content_ready_check.get("passed") is True
            ),
            "ready_source": content_ready_check.get("ready_source") or "",
            "expected_ready": content_ready_check.get("expected_ready") or "",
            "matched_ready_selector": (
                content_ready_check.get("matched_selector") or ""
            ),
            "content_observation": (
                content_ready_check.get("content_observation") or ""
            ),
            "loader_visible": (
                not hard_checks["loader"]["passed"]
                if hard_checks["loader"]["enabled"] and hard_checks["loader"]["passed"] is not None
                else False
            ),
            "visible_error": visible_error,
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
        """Hard check va observation diagnostikalari uchun browser holatini oladi."""
        del case
        return capture_form_state(self.page)

    def _case_checks(self, case, state, *, precomputed_checks=None, stop_after=None):
        """Hard check natijalariga observation-only browser signallarini qo'shadi."""
        run_diagnostics = not (
            stop_after == "url"
            and (precomputed_checks or {}).get("url", {}).get("passed") is False
        )
        checks = self._checks(
            case,
            state,
            enabled_checks=list(self.enabled_checks),
            enabled_diagnostics=list(self.enabled_diagnostics),
            diagnostic_results=self.form_diagnostics.evaluate(
                run=run_diagnostics,
            ),
            precomputed_checks=precomputed_checks,
            stop_after=stop_after,
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
        checks=None,
    ):
        state = state or self._capture_state(case)
        detail = _clean_text(exc)
        checks = checks or self._case_checks(case, state)
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
            actual_url=state.get("actual_url") or "",
            page_links=case.get("page_links"),
            action=case.get("action"),
            add_icon=case.get("add_icon", False),
            detail=detail,
            status=analysis["status"],
            reason_code=analysis["reason_code"],
            reason_summary=analysis["reason_summary"],
            failed_stage=stage,
            expected_title=case["title"],
            actual_title=state.get("actual_title") or "",
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
            shell=_shell_from_url(state.get("actual_url") or "", case.get("shell")),
            suite=self.suite_name,
            duration_ms=int((time.monotonic() - started_at) * 1000),
            label=case.get("label"),
            test_identity=case.get("test_identity"),
        )
        return self._append_result(result)

    def _url_failure_result(self, case, url_check, *, started_at):
        state = {
            "actual_url": url_check.get("actual_url") or "",
            "actual_title": "",
            "canonical_path": url_check.get("actual_path") or "",
            "title_candidates": [],
            "title_source": "",
            "document_title": "",
            "visible_error": "",
            "content_ready": False,
            "loader_visible": False,
            "ready_required": False,
            "ready_visible": False,
        }
        checks = self._case_checks(case, state, precomputed_checks={"url": url_check}, stop_after="url")
        result = self._failure_result(case=case, stage="validation", exc=url_check["detail"], started_at=started_at, test_started=True, test_completed=True, state=state, checks=checks)
        evidence = list(url_check.get("evidence") or [])
        result["evidence"] = evidence
        menu_evidence = next((item for item in evidence if item.get("stage") == "menu"), {})
        direct_evidence = next((item for item in evidence if item.get("stage") == "direct"), {})
        if menu_evidence.get("name"):
            result["screenshot"] = menu_evidence["name"]
            result["screenshot_redacted"] = True
        elif menu_evidence.get("error"):
            result["screenshot_error"] = menu_evidence["error"]
        if direct_evidence.get("name"):
            result["direct_screenshot"] = direct_evidence["name"]
            result["direct_screenshot_redacted"] = True
        elif direct_evidence.get("error"):
            result["direct_screenshot_error"] = direct_evidence["error"]
        self._attach_case_details(result)
        return result

    def _loader_failure_result(self, case, url_check, loader_check, *, started_at):
        actual_url = loader_check.get("actual_url") or str(getattr(self.page, "url", "") or "")
        state = {
            "actual_url": actual_url,
            "actual_title": "",
            "canonical_path": (
                url_check.get("actual_path")
                if url_check is not None
                else canonical_form_path(actual_url)
            ),
            "title_candidates": [],
            "title_source": "",
            "document_title": "",
            "visible_error": "",
            "content_ready": False,
            "loader_visible": True,
            "ready_required": False,
            "ready_visible": False,
        }
        precomputed_checks = {"loader": loader_check}
        if url_check is not None:
            precomputed_checks["url"] = url_check
        checks = self._case_checks(case, state, precomputed_checks=precomputed_checks, stop_after="loader")
        result = self._failure_result(case=case, stage="validation", exc=loader_check["detail"], started_at=started_at, test_started=True, test_completed=True, state=state, checks=checks)
        self._attach_case_evidence(result, case=case)
        return result

    def _application_error_failure_result(
        self,
        case,
        url_check,
        loader_check,
        application_error_check,
        *,
        started_at,
    ):
        actual_url = application_error_check.get("actual_url") or str(
            getattr(self.page, "url", "") or ""
        )
        state = {
            "actual_url": actual_url,
            "actual_title": "",
            "canonical_path": (
                url_check.get("actual_path")
                if url_check is not None
                else canonical_form_path(actual_url)
            ),
            "title_candidates": [],
            "title_source": "",
            "document_title": "",
            "visible_error": (
                application_error_check.get("error_text")
                or application_error_check.get("matched_selector")
                or ""
            ),
            "content_ready": False,
            "loader_visible": False,
            "ready_required": False,
            "ready_visible": False,
        }
        precomputed_checks = {"application_error": application_error_check}
        if url_check is not None:
            precomputed_checks["url"] = url_check
        if loader_check is not None:
            precomputed_checks["loader"] = loader_check
        checks = self._case_checks(
            case,
            state,
            precomputed_checks=precomputed_checks,
            stop_after="application_error",
        )
        result = self._failure_result(
            case=case,
            stage="validation",
            exc=application_error_check["detail"],
            started_at=started_at,
            test_started=True,
            test_completed=True,
            state=state,
            checks=checks,
        )

        self._capture_case_screenshot(result, case=case)
        cleanup = dismiss_application_error(self.page, application_error_check)
        result["hard_checks"]["application_error"].update(cleanup)
        result["checks"]["visible_error"] = (
            application_error_check.get("error_text")
            or application_error_check.get("matched_selector")
            or ""
        )
        result.update(cleanup)
        self._attach_case_details(result)
        return result

    def _content_ready_failure_result(
        self,
        case,
        url_check,
        loader_check,
        application_error_check,
        content_ready_check,
        *,
        started_at,
    ):
        actual_url = content_ready_check.get("actual_url") or str(
            getattr(self.page, "url", "") or ""
        )
        state = {
            "actual_url": actual_url,
            "actual_title": "",
            "canonical_path": (
                url_check.get("actual_path")
                if url_check is not None
                else canonical_form_path(actual_url)
            ),
            "title_candidates": [],
            "title_source": "",
            "document_title": "",
            "visible_error": "",
            "content_ready": False,
            "loader_visible": False,
        }
        precomputed_checks = {"content_ready": content_ready_check}
        if url_check is not None:
            precomputed_checks["url"] = url_check
        if loader_check is not None:
            precomputed_checks["loader"] = loader_check
        if application_error_check is not None:
            precomputed_checks["application_error"] = application_error_check
        checks = self._case_checks(
            case,
            state,
            precomputed_checks=precomputed_checks,
            stop_after="content_ready",
        )
        result = self._failure_result(
            case=case,
            stage="validation",
            exc=content_ready_check["detail"],
            started_at=started_at,
            test_started=True,
            test_completed=True,
            state=state,
            checks=checks,
        )
        self._attach_case_evidence(result, case=case)
        return result

    def _title_failure_result(
        self,
        case,
        url_check,
        loader_check,
        application_error_check,
        content_ready_check,
        title_check,
        *,
        started_at,
    ):
        actual_url = title_check.get("actual_url") or str(
            getattr(self.page, "url", "") or ""
        )
        state = {
            "actual_url": actual_url,
            "actual_title": title_check.get("actual_title") or "",
            "canonical_path": (
                url_check.get("actual_path")
                if url_check is not None
                else canonical_form_path(actual_url)
            ),
            "title_candidates": list(title_check.get("title_candidates") or []),
            "title_source": title_check.get("title_source") or "",
            "document_title": title_check.get("document_title") or "",
            "visible_error": "",
            "content_ready": True,
            "loader_visible": False,
        }
        precomputed_checks = {"title": title_check}
        if url_check is not None:
            precomputed_checks["url"] = url_check
        if loader_check is not None:
            precomputed_checks["loader"] = loader_check
        if application_error_check is not None:
            precomputed_checks["application_error"] = application_error_check
        if content_ready_check is not None:
            precomputed_checks["content_ready"] = content_ready_check
        checks = self._case_checks(
            case,
            state,
            precomputed_checks=precomputed_checks,
            stop_after="title",
        )
        result = self._failure_result(
            case=case,
            stage="validation",
            exc=title_check["detail"],
            started_at=started_at,
            test_started=True,
            test_completed=True,
            state=state,
            checks=checks,
        )
        self._attach_case_evidence(result, case=case)
        return result

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
        checks = None
        url_check_result = None
        loader_check_result = None
        application_error_check_result = None
        content_ready_check_result = None
        title_check_result = None
        detected_shell = None
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
                        if "url" in self.enabled_checks:
                            url_check_result, detected_shell = check_url(self.page, case.get("expected_path"), timeout=self.url_timeout, try_direct_url=self.try_direct_url, capture_evidence=lambda evidence_stage, check_result: self._capture_url_check_evidence(case, evidence_stage, check_result))
                            if url_check_result["passed"] is False:
                                failure_result = self._url_failure_result(
                                    case,
                                    url_check_result,
                                    started_at=started_at,
                                )
                                raise AssertionError(url_check_result["detail"])
                        else:
                            detected_shell = detect_shell(getattr(self.page, "url", ""))

                        if "loader" in self.enabled_checks:
                            loader_check_result = check_loader(self.page, shell=detected_shell, timeout=self.loader_timeout)
                            if loader_check_result["passed"] is False:
                                failure_result = self._loader_failure_result(
                                    case,
                                    url_check_result,
                                    loader_check_result,
                                    started_at=started_at,
                                )
                                raise AssertionError(loader_check_result["detail"])

                        if "application_error" in self.enabled_checks:
                            application_error_check_result = check_application_error(self.page, shell=detected_shell, timeout=self.application_error_timeout)
                            if application_error_check_result["passed"] is False:
                                failure_result = self._application_error_failure_result(
                                    case,
                                    url_check_result,
                                    loader_check_result,
                                    application_error_check_result,
                                    started_at=started_at,
                                )
                                raise AssertionError(
                                    application_error_check_result["detail"]
                                )

                        if "content_ready" in self.enabled_checks:
                            content_ready_check_result = check_content_ready(self.page, shell=detected_shell, ready=case.get("ready"), timeout=self.content_ready_timeout)
                            if content_ready_check_result["passed"] is False:
                                failure_result = self._content_ready_failure_result(
                                    case,
                                    url_check_result,
                                    loader_check_result,
                                    application_error_check_result,
                                    content_ready_check_result,
                                    started_at=started_at,
                                )
                                raise AssertionError(
                                    content_ready_check_result["detail"]
                                )

                        if "title" in self.enabled_checks:
                            title_check_result = check_title(self.page, expected_title=case.get("title"), shell=detected_shell, timeout=self.title_timeout)
                            if title_check_result["passed"] is False:
                                failure_result = self._title_failure_result(
                                    case,
                                    url_check_result,
                                    loader_check_result,
                                    application_error_check_result,
                                    content_ready_check_result,
                                    title_check_result,
                                    started_at=started_at,
                                )
                                raise AssertionError(title_check_result["detail"])

                        state = self._capture_state(case)
                        precomputed_checks = {}
                        if url_check_result is not None:
                            precomputed_checks["url"] = url_check_result
                        if loader_check_result is not None:
                            precomputed_checks["loader"] = loader_check_result
                        if application_error_check_result is not None:
                            precomputed_checks["application_error"] = application_error_check_result
                        if content_ready_check_result is not None:
                            precomputed_checks["content_ready"] = content_ready_check_result
                        if title_check_result is not None:
                            precomputed_checks["title"] = title_check_result
                        checks = self._case_checks(
                            case,
                            state,
                            precomputed_checks=precomputed_checks,
                        )
                        failure = primary_check_failure(checks["hard_checks"])
                        if failure:
                            raise AssertionError(failure["detail"])
                except (AssertionError, PlaywrightError) as exc:
                    if failure_result is None:
                        failure_result = self._failure_result(
                            case=case,
                            stage=stage,
                            exc=exc,
                            started_at=started_at,
                            test_started=True,
                            test_completed=True,
                            state=state,
                            checks=checks,
                        )
                        self._attach_case_evidence(failure_result, case=case)
                    raise

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
                    shell=detected_shell,
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

    def record_precondition_failure(
        self,
        operation,
        exc,
        *,
        affected_case_number=None,
        started_at=None,
    ):
        """Leaf test bajargan precondition xatosini suite natijasiga yozadi."""
        if self.blocked:
            return
        if started_at is None:
            started_at = time.monotonic()
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
        self.form_diagnostics.close()
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
            url_timeout=self.url_timeout,
            loader_timeout=self.loader_timeout,
            application_error_timeout=self.application_error_timeout,
            content_ready_timeout=self.content_ready_timeout,
            title_timeout=self.title_timeout,
            try_direct_url=self.try_direct_url,
        )
        allure.attach(
            json.dumps(payload, ensure_ascii=False, indent=2),
            name=f"{self.suite_name} | form-monitor.json",
            attachment_type=allure.attachment_type.JSON,
        )

        counts = status_counts(ordered_results)
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
