"""Positive regression uchun run/case dalillari; smoke reporting o'zgarmaydi."""
import hashlib
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import allure

from tests.shared.browser import browser_context, browser_page
from tests.shared.reporting import (
    auth_diagnostic_for_item, browser_state, reporting_warning, safe_page_screenshot,
)
from utils.report_safety import safe_payload, safe_text, safe_url

ROOT = Path(__file__).resolve().parents[2]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write_json(path, value):
    path.write_text(json.dumps(safe_payload(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def new_run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def prepare_run(run_id, *, environment=None):
    """CLI va pytest bitta run papkasini ishlatadi; retention startupda bajariladi."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", run_id):
        raise ValueError("REGRESSION_RUN_ID faqat xavfsiz papka nomi bo'lishi kerak")
    environment = os.environ if environment is None else environment
    directory = ROOT / "test-results/runs" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory / "run.json").exists():
        _write_json(directory / "run.json", {
            "run_id": run_id, "status": "process", "started_at_utc": _now(),
            "server": safe_url(environment.get("COMPANY_URL", "")),
            "company": environment.get("COMPANY_CODE", ""),
        })
    return directory


def run_directory(config):
    """Har pytest sessiyasi o'z papkasiga ega; oldingi trace almashmaydi."""
    directory = getattr(config, "_regression_run_dir", None)
    if directory is None:
        run_id = os.environ.get("REGRESSION_RUN_ID") or new_run_id()
        directory = prepare_run(run_id)
        config._regression_run_dir = directory
    return directory


def finalize_run(directory, exit_code, *, stop_signal=None):
    """Child tugagach qolgan process caselarni interrupted deb belgilash."""
    completed = _now()
    counts = {}
    attempts = {}
    attempt_counts = {}
    unfinished = []
    errors = []
    for path in sorted(directory.glob("*/attempt-*/result.json")):
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
            if result.get("status") == "process":
                result.update(status="interrupted", updated_at_utc=completed,
                              interruption_reason="Pytest yakunlandi; case barcha fazalarini tugatmadi")
                result["trace"] = "trace.zip" if (path.parent / "trace.zip").is_file() else None
                _write_json(path, result)
                unfinished.append(str(path.relative_to(directory)))
            status = result.get("status", "unknown")
            attempt_counts[status] = attempt_counts.get(status, 0) + 1
            attempts.setdefault(result["nodeid"], []).append((path, result))
        except (OSError, ValueError, TypeError) as error:
            errors.append({"path": str(path.relative_to(directory)), "error_type": type(error).__name__})
    from tests.regression.retry.planning import final_result
    for entries in attempts.values():
        entries.sort(key=lambda entry: entry[1].get("attempt", 1))
        _, result = final_result(entries)
        status = result.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    interrupted = bool(stop_signal or unfinished or counts.get("interrupted") or exit_code in (-2, -15, 130, 143))
    status = ("interrupted" if interrupted else
              "failed" if exit_code or counts.get("failed") or errors else
              "blocked" if counts.get("skipped") else "passed")
    path = directory / "run.json"
    run = json.loads(path.read_text(encoding="utf-8"))
    run.update(status=status, exit_code=exit_code, completed_at_utc=completed,
               case_status_counts=counts, attempt_status_counts=attempt_counts,
               interrupted_cases=unfinished)
    if stop_signal:
        run["stop_signal"] = stop_signal
    if errors:
        run["artifact_errors"] = errors
    _write_json(path, run)
    return run


def begin_case(item):
    """Pytest retry bo'lsa ham yangi attempt papkasini ochish."""
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", safe_text(item.name))[:80].strip("_") or "case"
    digest = hashlib.sha256(item.nodeid.encode()).hexdigest()[:8]
    parent = run_directory(item.config) / f"{slug}-{digest}"
    attempt = getattr(item, "_regression_attempt", 0) + 1
    directory = parent / f"attempt-{attempt:02d}"
    directory.mkdir(parents=True, exist_ok=False)
    item._regression_attempt = attempt
    item.regression_case_dir = directory
    item.regression_reports = {}
    item._regression_trace_attached = False
    item._regression_trace_reference_attached = False
    item._regression_runtime_page = None
    item._regression_interrupted = False
    item._regression_started_at = _now()
    _write_json(directory / "result.json", {
        "nodeid": item.nodeid, "status": "process", "attempt": attempt,
        "started_at_utc": item._regression_started_at, "phases": {},
    })
    return directory


def case_directory(item):
    return getattr(item, "regression_case_dir", None) or begin_case(item)


def attach_trace(item):
    """Faqat haqiqatan saqlangan shu attempt trace'iga link va fayl berish."""
    failed = any(phase["outcome"] == "failed" for phase in item.regression_reports.values())
    if not failed and not getattr(item, "_regression_interrupted", False):
        return
    trace = case_directory(item) / "trace.zip"
    if not trace.is_file():
        return
    reference = {"path": str(trace.relative_to(ROOT)), "scope": "test", "attempt": item._regression_attempt}
    if not item._regression_trace_reference_attached:
        allure.attach(json.dumps(reference), "trace-reference", allure.attachment_type.JSON)
        item._regression_trace_reference_attached = True
    if not item._regression_trace_attached:
        allure.attach.file(str(trace), name="03 - Playwright Trace", attachment_type="application/zip", extension="zip")
        item._regression_trace_attached = True


@contextmanager
def order_page_context(browser, item, *, storage_state=None):
    directory = case_directory(item)
    trace = directory / "trace.zip"
    try:
        with browser_context(browser, trace, storage_state=storage_state) as context:
            from tests.regression.retry.state import ACTIVE
            from tests.regression.retry.reconcile import bind_browser
            journal = ACTIVE.get()
            if journal:
                bind_browser(context, journal)
            with browser_page(context) as page:
                item._regression_runtime_page = page
                yield page
    except (KeyboardInterrupt, SystemExit):
        item._regression_interrupted = True
        raise
    finally:
        # Save the original Playwright ZIP once. Keep it pending until the last
        # teardown report, so a later fixture failure still has its trace.
        try:
            attach_trace(item)
        except Exception as error:
            _write_json(directory / "artifact-error.json", {
                "error_type": type(error).__name__, "message": safe_text(str(error)),
            })
            reporting_warning(item.nodeid, "Order trace dalilini biriktirish", safe_text(str(error)))


def record_phase(item, report, call):
    """Setup/call/teardown natijasi ledgerga ham, Allurega ham ochiq."""
    directory = case_directory(item)
    setattr(item, "rep_" + report.when, report)
    phase = {"outcome": report.outcome, "duration_seconds": report.duration}
    journal = getattr(item, "_retry_journal", None)
    if journal and getattr(journal, "blocked_reason", None):
        phase["retry_safety_reason"] = journal.blocked_reason
    if call.excinfo:
        phase.update(error_type=call.excinfo.typename, message=safe_text(str(call.excinfo.value)))
        if journal and getattr(journal, "blocked_reason", None):
            phase["message"] = journal.blocked_reason + "; " + phase["message"]
    if report.failed:
        exception = safe_text(str(report.longrepr))
        path = directory / f"{report.when}-exception.txt"
        path.write_text(exception, encoding="utf-8")
        allure.attach.file(str(path), f"Order {report.when} xatosi", allure.attachment_type.TEXT)
        page = item.funcargs.get("order_page") or getattr(item, "_regression_runtime_page", None)
        if page is not None and not page.is_closed():
            try:
                state = browser_state(page)
                diagnostic = auth_diagnostic_for_item(SimpleNamespace(funcargs={"page": page}))
                try:
                    if page.locator("app-session-lock").first.is_visible():
                        state["session_lock_visible"] = True
                        if diagnostic is not None:
                            diagnostic["ui_state"] = "session_lock"
                            diagnostic["summary"] = diagnostic["summary"].rsplit("; UI=", 1)[0] + "; UI=A2 qayta login oynasi"
                except Exception as error:
                    state.setdefault("observation_errors", []).append(
                        "A2 sessiya oynasi holatini aniqlab bo'lmadi: " + type(error).__name__
                    )
                state["auth_diagnostic"] = diagnostic
                _write_json(directory / "browser-state.json", state)
                (directory / "current-url.txt").write_text(safe_url(page.url), encoding="utf-8")
                image = safe_page_screenshot(page, full_page=True)
                (directory / "failure.png").write_bytes(image)
                allure.attach(image, "Order failure — maxfiy qiymatlar yashirilgan", allure.attachment_type.PNG)
                allure.attach.file(str(directory / "browser-state.json"), "Order browser holati", allure.attachment_type.JSON)
            except Exception as error:
                reporting_warning(item.nodeid, "Order failure screenshot", safe_text(str(error)))
    item.regression_reports[report.when] = phase
    phases = item.regression_reports
    status = "failed" if any(row["outcome"] == "failed" for row in phases.values()) else "skipped" if any(row["outcome"] == "skipped" for row in phases.values()) else "interrupted" if getattr(item, "_regression_interrupted", False) else "passed" if report.when == "teardown" else "process"
    if report.when == "teardown" and status in {"passed", "skipped"}:
        try:
            (directory / "trace.zip").unlink(missing_ok=True)
        except OSError as error:
            reporting_warning(item.nodeid, "PASS/SKIP trace faylini o'chirish", safe_text(str(error)))
            _write_json(directory / "artifact-error.json", {
                "error_type": type(error).__name__, "message": safe_text(str(error)),
            })
    _write_json(directory / "result.json", {
        "nodeid": item.nodeid, "status": status, "attempt": item._regression_attempt,
        "started_at_utc": item._regression_started_at,
        "updated_at_utc": _now(), "blocked_by": getattr(item, "_smartup_blocked_by", ""),
        "environment_failure": (getattr(item.config, "_order_environment_block", None) or [None])[0] == item.nodeid,
        "phases": phases, "trace": "trace.zip" if (directory / "trace.zip").is_file() else None,
    })
    attach_trace(item)
    if report.when == "teardown":
        allure.attach.file(str(directory / "result.json"), "Order fazalari natijasi", allure.attachment_type.JSON)
