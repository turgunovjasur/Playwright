from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "test-results" / "allure-results"
LOG_DIR = ROOT / "test-results" / "logs"
SYSTEM_SUMMARY_MD = ROOT / "test-results" / "system-summary.md"
SYSTEM_SUMMARY_JSON = ROOT / "test-results" / "system-summary.json"
AI_SUMMARY_MD = ROOT / "test-results" / "ai-summary.md"
AI_SUMMARY_JSON = ROOT / "test-results" / "ai-summary.json"
DEFAULT_MODEL = "gemini-2.5-flash"
FAILED_STATUSES = {"failed", "broken"}
A2_ADMIN_FORMS_TEST = "test_a2_admin_menu_forms"
A2_ANGULAR_FORMS_TEST = "test_a2_angular_forms"
A2_FORM_STEP_PATTERN = re.compile(
    r"^(?:\d{2}\s+[—-]\s+|\d{3}\s+\|\s+Filial:)"
)
SPRAVOCHNIKI_FORM_STEP_PATTERN = re.compile(r"^\d{3}\s+\|\s+Filial:")
FORM_SUITE_LABELS = {
    "glavnoe": "Главное",
    "prodaja": "Продажа",
    "sklad": "Склад",
    "finansy": "Финансы",
    "spravochniki": "Справочники",
    "a2_admin": "A2Angular",
}
FORM_MONITOR_FAILURE_STATUSES = {
    "OPENED_WITH_DEFECT",
    "NOT_OPENED",
    "TEST_BLOCKED",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Pytest/Allure natijasidan system summary va ixtiyoriy AI xulosa yaratadi.")
    parser.add_argument("--exit-code", type=int, required=True, help="pytest exit code")
    parser.add_argument("--command", default="", help="Maskalangan pytest command")
    parser.add_argument("--started-at", type=float, default=0.0, help="Run boshlanish vaqti: time.time()")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--logs-dir", type=Path, default=LOG_DIR)
    parser.add_argument("--system-output-md", type=Path, default=SYSTEM_SUMMARY_MD)
    parser.add_argument("--system-output-json", type=Path, default=SYSTEM_SUMMARY_JSON)
    parser.add_argument("--ai-output-md", type=Path, default=AI_SUMMARY_MD)
    parser.add_argument("--ai-output-json", type=Path, default=AI_SUMMARY_JSON)
    return parser.parse_args()


def env_flag(name):
    return str(os.getenv(name, "0") or "0").strip() == "1"


def _read_json(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _auth_diagnostic_attachment(item, results_dir):
    attachments = item.get("attachments")
    if not isinstance(attachments, list):
        return {}

    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        if attachment.get("name") != "auth-diagnostic":
            continue
        source = Path(str(attachment.get("source") or "")).name
        if not source:
            return {}
        diagnostic = _read_json(results_dir / source)
        if not diagnostic:
            return {}
        return {
            "kind": str(diagnostic.get("kind") or ""),
            "error_type": str(diagnostic.get("error_type") or ""),
            "method": str(diagnostic.get("method") or ""),
            "path": str(diagnostic.get("path") or ""),
            "status": diagnostic.get("status") or "",
            "server_message": _truncate(
                _mask_sensitive(str(diagnostic.get("server_message") or "")),
                300,
            ),
            "ui_state": str(diagnostic.get("ui_state") or ""),
            "summary": _truncate(
                _mask_sensitive(str(diagnostic.get("summary") or "")),
                700,
            ),
        }
    return {}


def _json_attachment(item, results_dir, attachment_name):
    attachments = item.get("attachments")
    if not isinstance(attachments, list):
        return {}
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        if str(attachment.get("name") or "") != attachment_name:
            continue
        source = Path(str(attachment.get("source") or "")).name
        if not source:
            return {}
        return _read_json(results_dir / source) or {}
    return {}


def _form_monitor_attachment(item, results_dir):
    """Top-level yoki nested Allure stepdagi yagona form-monitor payloadini topadi."""

    def iter_attachments(node):
        if not isinstance(node, dict):
            return
        attachments = node.get("attachments")
        if isinstance(attachments, list):
            yield from attachments
        steps = node.get("steps")
        if isinstance(steps, list):
            for step in steps:
                yield from iter_attachments(step)

    for attachment in iter_attachments(item):
        if not isinstance(attachment, dict):
            continue
        name = str(attachment.get("name") or "").strip()
        if not name.endswith("| form-monitor.json"):
            continue
        source = Path(str(attachment.get("source") or "")).name
        if not source:
            continue
        payload = _read_json(results_dir / source)
        if not payload or not isinstance(payload.get("results"), list):
            continue
        return payload
    return {}


def _mask_sensitive(text):
    if not text:
        return text
    replacements = [
        (r"(--(?:company-password|head-password)\s+)(\S+)", r"\1***"),
        (r"((?:password|пароль)\s*[=:]\s*)(\S+)", r"\1***"),
        (r"(GEMINI_API_KEY\s*[=:]\s*)(\S+)", r"\1***"),
        (r"(AIza[0-9A-Za-z_\-]{20,})", "***"),
        (r"(sk-[0-9A-Za-z_\-]{20,})", "***"),
        (r"(#/)[^/\s\"']+", r"\1<session>"),
    ]
    masked = text
    for pattern, repl in replacements:
        masked = re.sub(pattern, repl, masked, flags=re.IGNORECASE)
    return masked


def _truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _first_non_empty_line(text):
    for line in text.splitlines():
        clean = line.strip()
        if clean:
            return clean
    return ""


def _timeout_text(message):
    match = re.search(r"Timeout\s+(\d+)ms", message)
    if not match:
        return "berilgan vaqt"
    milliseconds = int(match.group(1))
    seconds = milliseconds // 1000
    if seconds:
        return f"{seconds} sekund"
    return f"{milliseconds} ms"


def _waited_target(message):
    for pattern in (r"- waiting for (.+)", r"waiting for (.+)"):
        match = re.search(pattern, message)
        if match:
            return _truncate(match.group(1).strip(), 220)
    locator = re.search(r"(locator\(.+?\)(?:\.\w+\(.+?\))?)", message)
    if locator:
        return _truncate(locator.group(1).strip(), 220)
    return ""


def _element_state(message):
    lowered = message.lower()
    if "strict mode violation" in lowered:
        return "ambiguous"
    if "element is not visible" in lowered:
        return "hidden"
    if "element is not enabled" in lowered or "element is disabled" in lowered:
        return "disabled"
    if "element is not stable" in lowered:
        return "unstable"
    if "intercepts pointer events" in lowered:
        return "blocked"
    if "locator resolved to" in lowered:
        return "resolved"
    if "waiting for locator" in lowered or "waiting for get_by_" in lowered:
        return "not_found"
    return ""


def _target_text(target):
    return f" Maqsad: {target}." if target else ""


def _error_type(message):
    if "Smartup transition failed" in message:
        return "SmartupTransitionError"
    if "TimeoutError" in message:
        return "TimeoutError"
    if "AssertionError" in message:
        return "AssertionError"
    if "StrictModeViolation" in message:
        return "StrictModeViolation"
    if "Error:" in message:
        return _first_non_empty_line(message).split(":", 1)[0]
    return "unknown"


def _location(item):
    source = str(item.get("source") or "").strip()
    if source:
        return source
    full_name = str(item.get("fullName") or "").strip()
    return full_name or str(item.get("name") or "unknown")


def _runner_test(item):
    full_name = str(item.get("fullName") or "")
    match = re.search(r"(test_[A-Za-z0-9_]+)$", full_name)
    if match:
        return match.group(1)
    return ""


def _group_name(item, runner_test):
    full_name = str(item.get("fullName") or "").lower()
    name = str(item.get("name") or "").lower()
    source = str(item.get("source") or item.get("location") or "").lower()
    combined = " ".join([full_name, name, source, runner_test.lower()])

    if (
        "test_a2_admin_menu_forms" in combined
        or "test_a2_menu_identity_forms" in combined
        or "test_a2_admin_forms" in combined
        or "test_a2_angular_forms" in combined
        or A2_ANGULAR_FORMS_TEST in combined
        or "a2angular" in combined
        or "a2 admin menu forms" in combined
        or "a2 admin forms" in combined
    ):
        return "A2Angular Forms"
    if re.search(r"test_forms_\d+_[a-z0-9_]+", combined) or re.search(r"test_[a-z0-9_]+_forms", combined):
        return "Forms"
    if "report_group" in combined or "report group" in combined:
        return "Report group"
    if "c_group" in combined or "c group" in combined:
        return "C group"
    if "b_group" in combined or "b group" in combined:
        return "B group"
    if "a_group" in combined or "a group" in combined:
        return "A group"
    if "setup" in combined:
        return "Setup"
    return ""


def _trace_locations(trace):
    locations = []
    pattern = re.compile(
        r"(?P<path>(?:[A-Za-z]:)?[/\\]?.*?tests[/\\]smoke[/\\][^:\n]+?\.py):"
        r"(?P<line>\d+)(?::\s+in\s+(?P<func>[A-Za-z_]\w*))?"
    )
    for line in trace.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        path = match.group("path").replace("\\", "/")
        tests_index = path.find("tests/smoke/")
        if tests_index >= 0:
            path = path[tests_index:]
        locations.append(
            {
                "path": path,
                "line": match.group("line"),
                "function": match.group("func") or "",
                "source": f"{path}:{match.group('line')}",
            }
        )
    return locations


def _inner_source_from_trace(trace):
    locations = _trace_locations(trace)
    if not locations:
        return {}
    return locations[-1]


def _failed_step_entries(steps, parent=()):
    if not isinstance(steps, list):
        return []

    entries = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        name = str(step.get("name") or "").strip()
        path = parent + ((name or "unknown"),)
        child_entries = _failed_step_entries(step.get("steps"), path)
        if child_entries:
            entries.extend(child_entries)
            continue
        status = str(step.get("status") or "")
        if status in FAILED_STATUSES:
            status_details = step.get("statusDetails") if isinstance(step.get("statusDetails"), dict) else {}
            entries.append(
                {
                    "path": list(path),
                    "name": name or "unknown",
                    "status": status,
                    "message": status_details.get("message") or "",
                }
            )
    return entries


def _step_path_text(path):
    return " → ".join(item for item in path if item)


def _failed_step_info(item):
    failed_steps = item.get("failed_steps")
    if isinstance(failed_steps, list) and failed_steps:
        first = failed_steps[0] if isinstance(failed_steps[0], dict) else {}
        path = first.get("path") if isinstance(first.get("path"), list) else []
        clean_path = [str(part) for part in path if str(part).strip()]
        return {
            "inner_test": clean_path[0] if clean_path else "",
            "failed_step": _step_path_text(clean_path),
            "failed_step_short": clean_path[-1] if clean_path else str(first.get("name") or ""),
        }
    return {"inner_test": "", "failed_step": "", "failed_step_short": ""}


def _structured_failure_details(text):
    if "Smartup transition failed" not in text:
        return {}

    labels = {
        "before_page": "Before page",
        "action": "Action",
        "expected": "Expected",
        "actual": "Actual",
        "ui_error": "UI error",
        "location_hint": "Location hint",
    }
    details = {"kind": "Smartup transition failed"}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("E "):
            line = line[2:].strip()
        if line.startswith("AssertionError:"):
            line = line.split(":", 1)[1].strip()
        for key, label in labels.items():
            prefix = f"{label}:"
            if line.startswith(prefix):
                details[key] = line[len(prefix):].strip()
                break
    return details


def _human_reason(message):
    structured = _structured_failure_details(message)
    if structured:
        action = structured.get("action") or "save/transition action"
        actual = structured.get("actual") or "expected state ochilmadi"
        ui_error = structured.get("ui_error") or ""
        reason = f"{action} vaqtida transition bajarilmadi. Actual: {actual}."
        if ui_error:
            reason += f" UI error: {ui_error}"
        return _truncate(reason, 500)

    if "using Playwright Sync API inside the asyncio loop" in message:
        return (
            "Pytest fixture yangi Sync Playwright runtime ochishga urindi, lekin shu sessiyadagi "
            "boshqa Sync Playwright runtime hali faol edi. Test UI qadamlariga yetib bormagan."
        )

    timeout = _timeout_text(message)
    target = _waited_target(message)
    target_text = _target_text(target)
    element_state = _element_state(message)
    if "Locator.click: Timeout" in message:
        if element_state == "hidden":
            return (
                f"Element topildi, ammo ko'rinmagani uchun {timeout} ichida bosilmadi."
                f"{target_text} Locator yashirin/dublikat elementga tushgan yoki sahifa headeri hali ochilmagan."
            )
        if element_state == "disabled":
            return (
                f"Element topildi, ammo faol bo'lmagani uchun {timeout} ichida bosilmadi."
                f"{target_text} Elementni yoqadigan precondition yoki loader tugashi kutilmagan."
            )
        if element_state == "unstable":
            return (
                f"Element animatsiya yoki joylashuv o'zgarishi sabab {timeout} davomida barqarorlashmadi."
                f"{target_text}"
            )
        if element_state == "blocked":
            return (
                f"Elementni boshqa UI qatlami to'sib turgani uchun {timeout} ichida bosilmadi."
                f"{target_text} Overlay, modal yoki loader clickni ushlab qolgan."
            )
        if element_state == "not_found":
            return (
                f"Element DOM ichida topilmagani uchun {timeout} ichida bosilmadi."
                f"{target_text} Sahifa holati yoki locator UI bilan mos emas."
            )
        return (
            f"Element {timeout} ichida bosilmadi."
            f"{target_text} Playwright call logdagi element holatini tekshirish kerak."
        )
    if "Locator.fill: Timeout" in message:
        if element_state == "hidden":
            return (
                f"Input topildi, ammo ko'rinmagani uchun {timeout} ichida to'ldirilmadi."
                f"{target_text} Locator yashirin inputga tushgan bo'lishi mumkin."
            )
        if element_state == "not_found":
            return (
                f"Input DOM ichida topilmagani uchun {timeout} ichida to'ldirilmadi."
                f"{target_text} Forma yoki locator UI bilan mos emas."
            )
        return (
            f"Input maydoni {timeout} ichida to'ldirilmadi."
            f"{target_text} Element holati va forma yuklanishini tekshirish kerak."
        )
    if "Locator" in message and "Timeout" in message:
        return (
            f"UI amali {timeout} ichida tugamadi."
            f"{target_text} Element holati, sahifa yoki locator tekshirilishi kerak."
        )
    if "Page.goto: Timeout" in message:
        return (
            f"Sahifa {timeout} ichida yuklanmadi. Server sekin javob bergan, URL ochilmagan yoki tarmoq muammosi bo'lishi mumkin."
        )
    if "AssertionError" in message:
        return "Test kutgan natija bilan haqiqiy natija mos kelmadi. Expected/actual qiymatlarni Allure logdan solishtirish kerak."
    first_line = _first_non_empty_line(message)
    if first_line:
        return _truncate(first_line, 350)
    return "Xato sababi logda aniq ko'rinmadi. Allure trace va screenshotni tekshirish kerak."


def _humanize_failure(item):
    message = str(item.get("message") or "")
    trace = str(item.get("trace") or "")
    failure_text = f"{message}\n{trace}"
    auth_diagnostic = (
        item.get("auth_diagnostic")
        if isinstance(item.get("auth_diagnostic"), dict)
        else {}
    )
    structured = _structured_failure_details(failure_text)
    trace_source = _inner_source_from_trace(trace)
    step_info = _failed_step_info(item)
    runner_test = _runner_test(item)
    form_issues = _form_monitor_issues(item.get("form_monitor"))
    form_reason = _form_issue_reason(form_issues[0]) if form_issues else ""
    try:
        stop_millis = int(item.get("stop") or 0)
        if stop_millis <= 0:
            raise ValueError("Allure stop timestamp mavjud emas")
        stopped_at = datetime.fromtimestamp(
            stop_millis / 1000,
            timezone.utc,
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    except (OSError, OverflowError, TypeError, ValueError):
        stopped_at = ""
    browser_state = (
        item.get("browser_state")
        if isinstance(item.get("browser_state"), dict)
        else {}
    )
    target_url_match = re.search(r'navigating to "([^"]+)"', failure_text)
    target_url = _mask_sensitive(target_url_match.group(1)) if target_url_match else ""
    current_url = _mask_sensitive(str(browser_state.get("current_url") or ""))
    target_url_reached = bool(target_url and current_url and target_url == current_url)
    if "Page.goto: Timeout" in failure_text and target_url_reached:
        reason = (
            "Target URL ochilgan, ammo browser load eventi timeout ichida tugamagan. "
            "Bu sahifa ochilmaganini emas, navigatsiya synchronization muammosini ko'rsatadi."
        )
        classification = "TEST_SYNCHRONIZATION_DEFECT"
    elif "Page.goto: Timeout" in failure_text:
        reason = _human_reason(failure_text)
        classification = "NAVIGATION_TIMEOUT_DEFECT"
    elif auth_diagnostic:
        reason = auth_diagnostic.get("summary") or "Authorization precondition bajarilmadi."
        classification = "ENVIRONMENT_PRECONDITION_DEFECT"
    elif "Locator" in failure_text and "Timeout" in failure_text:
        reason = _human_reason(failure_text)
        classification = "LOCATOR_OR_UI_STATE_DEFECT"
    elif "download" in failure_text.casefold():
        reason = _human_reason(failure_text)
        classification = "DOWNLOAD_DEFECT"
    elif "AssertionError" in failure_text:
        reason = _human_reason(failure_text)
        classification = "VERIFICATION_DEFECT"
    else:
        reason = _human_reason(failure_text)
        classification = "UNCLASSIFIED_TEST_DEFECT"

    return {
        "name": item.get("name") or item.get("fullName") or "unknown",
        "status": item.get("status") or "unknown",
        "message": _truncate(message, 700),
        "error_type": (
            auth_diagnostic.get("error_type")
            or _error_type(f"{message}\n{trace}")
        ),
        "group": _group_name(item, runner_test),
        "runner_test": runner_test,
        "location": structured.get("location_hint") or trace_source.get("source") or _location(item),
        "source": trace_source.get("source") or "",
        "source_function": trace_source.get("function") or "",
        "inner_test": step_info.get("inner_test") or "",
        "failed_step": step_info.get("failed_step") or "",
        "failed_step_short": step_info.get("failed_step_short") or "",
        "before_page": structured.get("before_page") or "",
        "action": structured.get("action") or "",
        "expected": structured.get("expected") or "",
        "actual": structured.get("actual") or "",
        "ui_error": structured.get("ui_error") or "",
        "auth_diagnostic": auth_diagnostic.get("summary") or "",
        "auth_kind": auth_diagnostic.get("kind") or "",
        "auth_request": " ".join(
            value
            for value in (
                auth_diagnostic.get("method"),
                auth_diagnostic.get("path"),
            )
            if value
        ),
        "auth_status": auth_diagnostic.get("status") or "",
        "auth_server_message": auth_diagnostic.get("server_message") or "",
        "auth_ui_state": auth_diagnostic.get("ui_state") or "",
        "target": _waited_target(failure_text),
        "element_state": _element_state(failure_text),
        "timeout": _timeout_text(failure_text) if "Timeout" in failure_text else "",
        "reason": form_reason or reason,
        "classification": classification,
        "target_url": target_url,
        "target_url_reached": target_url_reached,
        "browser_state": browser_state,
        "failure_at_utc": stopped_at,
        "form_issues": form_issues,
    }


def collect_allure_results(results_dir, started_at):
    if not results_dir.exists():
        return []

    threshold = max(started_at - 5, 0)
    rows = []
    for path in sorted(results_dir.glob("*-result.json"), key=lambda item: item.stat().st_mtime):
        if threshold and path.stat().st_mtime < threshold:
            continue
        data = _read_json(path)
        if not data:
            continue
        if data.get("fullName") in {"ai.test.summary", "system.test.summary"}:
            continue
        status_details = data.get("statusDetails") if isinstance(data.get("statusDetails"), dict) else {}
        trace = str(status_details.get("trace") or "")
        form_suite = _form_suite_key(data)
        form_steps = _form_steps(data, form_suite=form_suite)
        auth_diagnostic = _auth_diagnostic_attachment(data, results_dir)
        form_monitor = _form_monitor_attachment(data, results_dir)
        rows.append(
            {
                "result_path": str(path),
                "name": data.get("name") or "",
                "fullName": data.get("fullName") or "",
                "status": data.get("status") or "unknown",
                "message": status_details.get("message") or "",
                "trace": _truncate(trace, 5000),
                "failed_steps": _failed_step_entries(data.get("steps")),
                "form_suite": form_suite,
                "form_steps": form_steps,
                "a2_form_steps": form_steps if form_suite == "a2_admin" else [],
                "auth_diagnostic": auth_diagnostic,
                "form_monitor": form_monitor,
                "browser_state": _json_attachment(data, results_dir, "01 - Browser State"),
                "trace_reference": _json_attachment(data, results_dir, "trace-reference"),
                "start": data.get("start"),
                "stop": data.get("stop"),
            }
        )
    return rows


def _failure_summary_payload(failure):
    state = failure.get("browser_state") if isinstance(failure.get("browser_state"), dict) else {}
    return {
        "test": failure.get("name") or "unknown",
        "status": failure.get("status") or "unknown",
        "classification": failure.get("classification") or "UNCLASSIFIED_TEST_DEFECT",
        "failed_step": failure.get("failed_step") or "Allure step aniqlanmadi",
        "reason": failure.get("reason") or "Xato sababi aniqlanmadi.",
        "action": failure.get("action") or "",
        "expected": failure.get("expected") or "",
        "actual": failure.get("actual") or "",
        "ui_error": failure.get("ui_error") or "",
        "location": failure.get("location") or "",
        "timeout": failure.get("timeout") or "",
        "target_url": failure.get("target_url") or "",
        "target_url_reached": bool(failure.get("target_url_reached")),
        "current_url": state.get("current_url") or "",
        "document_title": state.get("document_title") or "",
        "visible_headings": state.get("visible_headings") or [],
        "visible_alerts": state.get("visible_alerts") or [],
        "visible_loader_count": int(state.get("visible_loader_count") or 0),
        "failure_at_utc": failure.get("failure_at_utc") or "",
    }


def _render_failure_summary(payload):
    lines = [
        "# Failure Summary",
        "",
        f"- Test: {payload['test']}",
        f"- Status: `{str(payload['status']).upper()}`",
        f"- Klassifikatsiya: `{payload['classification']}`",
        f"- Yiqilgan qadam: {payload['failed_step']}",
        f"- Sabab: {payload['reason']}",
    ]
    if payload.get("location"):
        lines.append(f"- Kod joyi: `{payload['location']}`")
    if payload.get("timeout"):
        lines.append(f"- Timeout: {payload['timeout']}")
    if payload.get("action"):
        lines.append(f"- Amal: {payload['action']}")
    if payload.get("expected"):
        lines.append(f"- Kutilgan: {payload['expected']}")
    if payload.get("actual"):
        lines.append(f"- Haqiqiy: {payload['actual']}")
    if payload.get("ui_error"):
        lines.append(f"- UI xato: {payload['ui_error']}")
    lines.extend(
        [
            "",
            "## Browser holati",
            "",
            f"- Target URL ochildi: `{'HA' if payload['target_url_reached'] else 'YO‘Q/ANIQLANMADI'}`",
            f"- Joriy URL: `{payload['current_url'] or 'aniqlanmadi'}`",
            f"- Page title: {payload['document_title'] or 'aniqlanmadi'}",
            f"- Visible heading: {', '.join(payload['visible_headings']) or 'aniqlanmadi'}",
            f"- Visible loaderlar: `{payload['visible_loader_count']}`",
            f"- Visible UI xato: {', '.join(payload['visible_alerts']) or 'topilmadi'}",
            "",
            "Texnik stacktrace shu testning Allure `Status details` bo‘limida qoladi.",
            "",
        ]
    )
    return "\n".join(lines)


def _workspace_trace(path_text, *, minimum_mtime=0):
    if not path_text:
        return None
    candidate = (ROOT / path_text).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    try:
        if minimum_mtime and candidate.stat().st_mtime < minimum_mtime:
            return None
    except OSError:
        return None
    return candidate


def enrich_failed_allure_results(results, results_dir):
    """Har bir failed resultga human summary va tayyor Playwright trace'ni biriktiradi."""
    trace_sources = {}
    for item in results:
        if item.get("status") not in FAILED_STATUSES:
            continue
        result_path = Path(str(item.get("result_path") or ""))
        result = _read_json(result_path)
        if not result:
            continue

        failure = _humanize_failure(item)
        payload = _failure_summary_payload(failure)
        result_uuid = str(result.get("uuid") or uuid.uuid4())
        markdown_source = f"{result_uuid}-failure-summary.md"
        json_source = f"{result_uuid}-failure-summary.json"
        (results_dir / markdown_source).write_text(
            _render_failure_summary(payload),
            encoding="utf-8",
        )
        (results_dir / json_source).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        old_attachments = result.get("attachments")
        if not isinstance(old_attachments, list):
            old_attachments = []
        attachments = [
            {
                "name": "00 - Failure Summary",
                "source": markdown_source,
                "type": "text/markdown",
            },
            {
                "name": "00 - Failure Summary JSON",
                "source": json_source,
                "type": "application/json",
            },
        ]

        trace_reference = item.get("trace_reference") if isinstance(item.get("trace_reference"), dict) else {}
        try:
            minimum_trace_mtime = max(int(item.get("start") or 0) / 1000 - 5, 0)
        except (TypeError, ValueError):
            minimum_trace_mtime = 0
        trace_path = _workspace_trace(
            str(trace_reference.get("path") or ""),
            minimum_mtime=minimum_trace_mtime,
        )
        if trace_path is not None:
            trace_key = str(trace_path)
            trace_source = trace_sources.get(trace_key)
            if trace_source is None:
                trace_source = f"{uuid.uuid5(uuid.NAMESPACE_URL, trace_key)}-playwright-trace.zip"
                shutil.copyfile(trace_path, results_dir / trace_source)
                trace_sources[trace_key] = trace_source
            attachments.append(
                {
                    "name": "03 - Playwright Trace",
                    "source": trace_source,
                    "type": "application/zip",
                }
            )

        for attachment in old_attachments:
            if not isinstance(attachment, dict):
                continue
            attachment_name = str(attachment.get("name") or "")
            if attachment_name in {"00 - Failure Summary", "00 - Failure Summary JSON"}:
                continue
            if attachment_name == "03 - Playwright Trace" and trace_path is not None:
                continue
            if attachment_name == "trace-reference":
                reference_source = Path(str(attachment.get("source") or "")).name
                if reference_source:
                    (results_dir / reference_source).unlink(missing_ok=True)
                continue
            attachments.append(attachment)

        result["attachments"] = attachments
        existing_description = str(result.get("description") or "").strip()
        summary_description = (
            f"**{payload['classification']}** — {payload['reason']}\n\n"
            f"Yiqilgan qadam: {payload['failed_step']}"
        )
        result["description"] = (
            f"{summary_description}\n\n---\n\n{existing_description}"
            if existing_description
            else summary_description
        )
        status_details = result.get("statusDetails") if isinstance(result.get("statusDetails"), dict) else {}
        status_details["message"] = _mask_sensitive(str(status_details.get("message") or ""))
        status_details["trace"] = _mask_sensitive(str(status_details.get("trace") or ""))
        marker = f"[{payload['classification']}]"
        if marker not in status_details["message"]:
            status_details["message"] = f"{marker} {status_details['message']}".strip()
        result["statusDetails"] = status_details
        result_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")


def collect_failure_logs(logs_dir, started_at):
    if not logs_dir.exists():
        return []

    threshold = max(started_at - 5, 0)
    logs = []
    for path in sorted(logs_dir.glob("*.log"), key=lambda item: item.stat().st_mtime, reverse=True):
        if threshold and path.stat().st_mtime < threshold:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.strip():
            continue
        logs.append({"path": str(path.relative_to(ROOT)), "content": _truncate(_mask_sensitive(text), 7000)})
        if len(logs) >= 5:
            break
    return logs


def _iter_steps(steps):
    if not isinstance(steps, list):
        return
    for step in steps:
        if not isinstance(step, dict):
            continue
        yield step
        yield from _iter_steps(step.get("steps"))


def _is_a2_admin_forms_result(item):
    return _form_suite_key(item) == "a2_admin"


def _form_suite_key(item):
    identity = " ".join(
        (
            str(item.get("name") or ""),
            str(item.get("fullName") or ""),
            str(item.get("form_suite") or ""),
        )
    ).lower()
    if (
        "test_forms_05_spravochniki" in identity
        or "test_forms_04_spravochniki" in identity
        or "test_forms_01_spravochniki" in identity
        or "test_spravochniki_menu_forms" in identity
        or "spravochniki" in identity
        or "справочники" in identity
    ):
        return "spravochniki"
    if (
        A2_ADMIN_FORMS_TEST in identity
        or A2_ANGULAR_FORMS_TEST in identity
        or "test_a2_menu_identity_forms" in identity
        or "test_a2_angular_forms" in identity
        or "test_forms_02_a2_admin" in identity
        or "a2angular" in identity
        or "a2 angular" in identity
        or "a2 admin" in identity
    ):
        return "a2_admin"
    if (
        "test_forms_03_prodaja" in identity
        or "test_forms_02_prodaja" in identity
        or "test_prodaja_menu_forms" in identity
        or "продажа" in identity
        or "prodaja" in identity
    ):
        return "prodaja"
    if "главное" in identity or "glavnoe" in identity:
        return "glavnoe"
    if "склад" in identity or "sklad" in identity:
        return "sklad"
    if "финансы" in identity or "finansy" in identity:
        return "finansy"
    main_runner_match = re.search(r"test_forms_\d+_([a-z0-9_]+)", identity)
    if main_runner_match:
        return main_runner_match.group(1)
    leaf_match = re.search(r"test_([a-z0-9_]+)_forms", identity)
    if leaf_match:
        return leaf_match.group(1)
    return ""


def _form_steps(item, *, form_suite=None):
    suite = form_suite or _form_suite_key(item)
    if suite == "a2_admin":
        pattern = A2_FORM_STEP_PATTERN
    elif suite:
        pattern = SPRAVOCHNIKI_FORM_STEP_PATTERN
    else:
        return []
    return [
        {
            "name": str(step.get("name") or "").strip(),
            "status": str(step.get("status") or "").lower(),
        }
        for step in _iter_steps(item.get("steps"))
        if pattern.match(str(step.get("name") or "").strip())
    ]


def _a2_form_steps(item):
    return _form_steps(item, form_suite="a2_admin") if _is_a2_admin_forms_result(item) else []


def _empty_form_counts():
    return {
        "checked": 0,
        "passed": 0,
        "observed": 0,
        "failed": 0,
        "skipped": 0,
    }


def _form_monitor_counts(form_monitor):
    results = form_monitor.get("results")
    if not isinstance(results, list):
        return {}

    statuses = [
        str(result.get("status") or "").upper()
        for result in results
        if isinstance(result, dict)
    ]
    try:
        planned = int(form_monitor.get("planned") or 0)
    except (TypeError, ValueError):
        planned = 0
    try:
        intentional_skips = int((form_monitor.get("inventory") or {}).get("intentional_skips") or 0)
    except (AttributeError, TypeError, ValueError):
        intentional_skips = 0
    return {
        "checked": max(planned, len(statuses)),
        "passed": statuses.count("PASSED"),
        "observed": statuses.count("OBSERVED_ONLY"),
        "failed": sum(
            status in FORM_MONITOR_FAILURE_STATUSES for status in statuses
        ),
        "skipped": intentional_skips + statuses.count("NOT_CHECKED"),
    }


def _normalized_form_signals(result):
    """Schema-v3 flat va schema-v4 nested signal natijalarini birlashtiradi."""
    raw_checks = result.get("checks")
    checks = raw_checks if isinstance(raw_checks, dict) else {}
    raw_hard_checks = result.get("hard_checks") or checks.get("hard_checks")
    hard_checks = raw_hard_checks if isinstance(raw_hard_checks, dict) else {}
    raw_diagnostics = result.get("diagnostics") or checks.get("diagnostics")
    diagnostics = raw_diagnostics if isinstance(raw_diagnostics, dict) else {}

    normalized = {
        "page_reached": bool(result.get("page_reached")),
        **{
            key: value
            for key, value in checks.items()
            if key in {
                "url_matches",
                "title_matches",
                "title_verified",
                "content_ready",
                "loader_visible",
                "visible_error",
            }
        },
    }
    failed_checks = [
        name
        for name, item in hard_checks.items()
        if isinstance(item, dict)
        and item.get("enabled")
        and item.get("passed") is False
    ]
    if failed_checks:
        normalized["failed_checks"] = ", ".join(failed_checks)
    not_run_checks = [
        name
        for name, item in hard_checks.items()
        if isinstance(item, dict)
        and item.get("enabled")
        and item.get("execution_status") == "NOT_RUN"
    ]
    if not_run_checks:
        normalized["not_run_checks"] = ", ".join(not_run_checks)
    url_check = hard_checks.get("url")
    if isinstance(url_check, dict) and url_check.get("reason_code") == "EXPECTED_URL_NOT_REACHED":
        normalized["url_timeout_ms"] = url_check.get("timeout_ms")
        normalized["direct_probe_executed"] = bool(url_check.get("direct_probe_executed"))
        if url_check.get("direct_probe_executed"):
            normalized["direct_url_reached"] = bool(url_check.get("direct_url_reached"))
            normalized["direct_expected_url"] = str(url_check.get("direct_expected_url") or "")
            normalized["direct_actual_url"] = str(url_check.get("direct_actual_url") or "")
            normalized["direct_summary"] = str(url_check.get("direct_summary") or "")
            if url_check.get("direct_error"):
                normalized["direct_error"] = str(url_check["direct_error"])
    diagnostic_signals = []
    for name, item in diagnostics.items():
        if not isinstance(item, dict) or not item.get("enabled"):
            continue
        count = int(item.get("count") or 0)
        if count:
            diagnostic_signals.append(f"{name}={count}")
    if diagnostic_signals:
        normalized["diagnostic_signals"] = ", ".join(diagnostic_signals)
    return normalized


def _form_monitor_issues(form_monitor):
    if not isinstance(form_monitor, dict):
        return []
    results = form_monitor.get("results")
    if not isinstance(results, list):
        return []

    issues = []
    for result in results:
        if not isinstance(result, dict):
            continue
        status = str(result.get("status") or "").upper()
        if status not in FORM_MONITOR_FAILURE_STATUSES:
            continue
        issues.append(
            {
                "number": result.get("number") or "",
                "title": str(result.get("title") or "unknown"),
                "identity": str(
                    result.get("identity") or result.get("test_identity") or ""
                ),
                "label": str(result.get("label") or ""),
                "track": str(result.get("track") or ""),
                "status": status,
                "reason_code": str(result.get("reason_code") or ""),
                "failed_stage": str(result.get("failed_stage") or ""),
                "expected_url": str(result.get("expected_path") or ""),
                "actual_url": str(result.get("actual_url") or ""),
                "expected_title": str(result.get("expected_title") or ""),
                "actual_title": str(result.get("actual_title") or ""),
                "reason": _truncate(
                    _mask_sensitive(str(result.get("reason_summary") or "")),
                    350,
                ),
                "detail": _truncate(
                    _mask_sensitive(str(result.get("detail") or "")),
                    500,
                ),
                "checks": _normalized_form_signals(result),
            }
        )
    return issues


def _form_issue_reason(issue):
    """Structured form-monitor issue'ni user o'qiydigan qisqa sababga aylantiradi."""
    if not isinstance(issue, dict):
        return ""
    title = issue.get("title") or "Forma"
    status = issue.get("status") or "FAILED"
    reason = issue.get("reason") or issue.get("detail") or "Sabab ko'rsatilmagan."
    location = issue.get("actual_url") or issue.get("expected_url") or ""
    text = f"{title} formasi {status}: {reason}"
    if location:
        text += f" URL: {location}."
    return _truncate(text, 700)


def _form_coverage_summary(results):
    suites = {}
    for item in results:
        suite = str(item.get("form_suite") or "") or _form_suite_key(item)
        if not suite:
            continue
        form_monitor = item.get("form_monitor")
        monitor_counts = (
            _form_monitor_counts(form_monitor)
            if isinstance(form_monitor, dict)
            else {}
        )
        if monitor_counts:
            monitor_suite = str(form_monitor.get("suite") or "")
            monitor_label = monitor_suite.split("—", 1)[-1].strip() if "—" in monitor_suite else ""
            counts = suites.setdefault(
                suite,
                {
                    "label": FORM_SUITE_LABELS.get(suite) or monitor_label or suite.replace("_", " ").title(),
                    **_empty_form_counts(),
                },
            )
            for key in _empty_form_counts():
                counts[key] += int(monitor_counts.get(key) or 0)
            continue
        form_steps = item.get("form_steps")
        if not isinstance(form_steps, list):
            form_steps = []
        if not form_steps and suite == "a2_admin":
            legacy_steps = item.get("a2_form_steps")
            if isinstance(legacy_steps, list):
                form_steps = legacy_steps
        if not form_steps:
            form_steps = _form_steps(item, form_suite=suite)
        counts = suites.setdefault(
            suite,
            {
                "label": FORM_SUITE_LABELS.get(suite) or suite.replace("_", " ").title(),
                **_empty_form_counts(),
            },
        )
        for step in form_steps:
            if not isinstance(step, dict):
                continue
            counts["checked"] += 1
            status = str(step.get("status") or "").lower()
            if status == "passed":
                counts["passed"] += 1
            elif status in FAILED_STATUSES:
                counts["failed"] += 1
            elif status == "skipped":
                counts["skipped"] += 1

    if not suites:
        return {}

    total = _empty_form_counts()
    for counts in suites.values():
        for key in total:
            total[key] += int(counts.get(key) or 0)
    return {**total, "suites": suites}


def build_deterministic_summary(exit_code, results):
    counts = {}
    for item in results:
        status = str(item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    result = "PASSED" if exit_code == 0 else "FAILED"
    failed = [item for item in results if item.get("status") in {"failed", "broken"}]
    skipped = [item for item in results if item.get("status") == "skipped"]
    skipped_count = len(skipped)
    form_coverage = _form_coverage_summary(results)
    a2_suite = (
        form_coverage.get("suites", {}).get("a2_admin", {})
        if isinstance(form_coverage, dict)
        else {}
    )
    a2_admin_forms = (
        {
            key: int(a2_suite.get(key) or 0)
            for key in ("checked", "passed", "observed", "failed", "skipped")
        }
        if isinstance(a2_suite, dict) and a2_suite
        else {}
    )
    return {
        "result": result,
        "exit_code": exit_code,
        "counts": counts,
        "failed_count": len(failed),
        "skipped_count": skipped_count,
        "failed_tests": [_humanize_failure(item) for item in failed],
        "form_coverage": form_coverage,
        "a2_admin_forms": a2_admin_forms,
    }


def build_local_summary(deterministic):
    result = str(deterministic.get("result") or "UNKNOWN")
    failed_tests = deterministic.get("failed_tests")
    skipped_count = int(deterministic.get("skipped_count") or 0)
    failed_count = int(deterministic.get("failed_count") or 0)

    if result == "PASSED":
        summary = "Barcha testlar muvaffaqiyatli o'tdi."
        confidence = "high"
    elif isinstance(failed_tests, list) and failed_tests:
        first = failed_tests[0] if isinstance(failed_tests[0], dict) else {}
        reason = str(first.get("reason") or "Xato sababi logdan aniq ajratilmadi.")
        failed_place = first.get("inner_test") or first.get("name") or "Test"
        summary = f"{failed_place} stepida xato bo'ldi. {reason}"
        if skipped_count:
            summary += f" {skipped_count} ta keyingi test skip bo'lgan."
        confidence = "medium"
    elif failed_count:
        summary = f"{failed_count} ta test failed bo'lgan, lekin Allure logdan aniq xato ajratilmadi."
        confidence = "low"
    else:
        summary = "Test run failed bo'lgan, lekin failure detali topilmadi. GitHub Actions log va Allure artifactni ochish kerak."
        confidence = "low"

    return {
        "result": result,
        "summary": summary,
        "failed_tests": failed_tests if isinstance(failed_tests, list) else [],
        "skipped": {"count": skipped_count, "reason": "Oldingi xato sabab skip bo'lishi mumkin." if skipped_count else ""},
        "a2_admin_forms": (
            deterministic.get("a2_admin_forms")
            if isinstance(deterministic.get("a2_admin_forms"), dict)
            else {}
        ),
        "form_coverage": (
            deterministic.get("form_coverage")
            if isinstance(deterministic.get("form_coverage"), dict)
            else {}
        ),
        "confidence": confidence,
        "provider_status": "system",
        "deterministic_summary": deterministic,
    }


def enrich_ai_summary(summary, deterministic):
    """AI javobini Telegram va Allure uchun kichik, barqaror contractga keltiradi."""
    observed = _truncate(
        _mask_sensitive(
            str(summary.get("observed") or summary.get("summary") or "").strip()
        ),
        1200,
    )
    probable_cause = _truncate(
        _mask_sensitive(str(summary.get("probable_cause") or "").strip()),
        1200,
    )
    confidence = str(summary.get("confidence") or "low").strip().lower()
    if confidence not in {"low", "medium", "high"}:
        confidence = "low"
    if not observed:
        observed = "Test loglaridan kuzatilgan holatni aniq ajratib bo'lmadi."
    if not probable_cause:
        probable_cause = "Test loglaridan xatolikning aniq sababi topilmadi."
    return {
        "result": deterministic.get("result", summary.get("result", "UNKNOWN")),
        "observed": observed,
        "probable_cause": probable_cause,
        "summary": f"{observed} {probable_cause}".strip(),
        "confidence": confidence,
        "provider_status": "ai",
    }


def build_prompt(command, deterministic, logs):
    payload = {
        "command": command,
        "deterministic_summary": {
            "result": deterministic.get("result"),
            "failed_count": deterministic.get("failed_count"),
            "skipped_count": deterministic.get("skipped_count"),
            "failed_tests": deterministic.get("failed_tests"),
        },
        "failure_logs": logs,
    }
    return (
        "Smartup Playwright + pytest FAILED natijasini user uchun qisqa tahlil qil.\n"
        "Qoidalar:\n"
        "- Faqat berilgan deterministic failure dalili va lokal test loglariga tayan.\n"
        "- Smartup server loglari berilmagan; backend sababini tasdiqlangan fakt sifatida yozma.\n"
        "- observed faqat logda aniq kuzatilgan holatni sodda tilda aytsin.\n"
        "- probable_cause eng ehtimoliy sababni aytsin; dalil yetarli bo'lmasa aynan sabab topilmaganini yoz.\n"
        "- 'Cheklov', 'Developer uchun', umumiy tavsiya yoki takroriy failure vaqtini yozma.\n"
        "- Har bir matn 1-2 qisqa gapdan oshmasin.\n"
        "- Ishonch past bo'lsa confidence=low qil.\n"
        "- Javob Uzbek tilida bo'lsin.\n"
        "- Faqat JSON qaytar.\n\n"
        "JSON schema:\n"
        "{\n"
        '  "result": "FAILED",\n'
        '  "observed": "Logda kuzatilgan aniq holat",\n'
        '  "probable_cause": "Ehtimoliy sabab yoki aniq sabab topilmagani",\n'
        '  "confidence": "low|medium|high"\n'
        "}\n\n"
        f"INPUT:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def call_gemini(prompt, model, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Siz QA test natijalarini tahlil qiladigan yordamchisiz. "
                        "Faqat berilgan loglarga tayaning va JSON formatida javob bering."
                    )
                }
            ]
        },
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code}: {_truncate(detail, 1000)}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini API network xatosi: {exc}") from exc

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "".join(str(part.get("text") or "") for part in parts if isinstance(part, dict)).strip()
    if not text:
        raise RuntimeError("Gemini API bo'sh javob qaytardi")
    return text


def parse_ai_json(text):
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("AI JSON object qaytarmadi")
    return data


def render_markdown(
    summary,
    title,
    model="",
    note="",
):
    lines = [
        f"# {title}",
        "",
        f"- Result: `{summary.get('result', 'UNKNOWN')}`",
        f"- Confidence: `{summary.get('confidence', 'unknown')}`",
    ]
    if model:
        lines.insert(2, f"- Model: `{model}`")
    if summary.get("provider_status") == "ai":
        lines.extend(
            [
                "",
                "## Kuzatilgan",
                str(summary.get("observed") or "Kuzatilgan holat mavjud emas."),
                "",
                "## Ehtimoliy sabab",
                str(summary.get("probable_cause") or "Aniq sabab topilmadi."),
            ]
        )
    else:
        lines.extend(["", str(summary.get("summary") or "Xulosa mavjud emas.")])
    failed_tests = summary.get("failed_tests")
    if isinstance(failed_tests, list) and failed_tests:
        lines.extend(["", "## Failed Tests"])
        for item in failed_tests:
            if not isinstance(item, dict):
                continue
            lines.extend(["", f"### {item.get('name', 'unknown')}"])
            for label, key in (
                ("Group", "group"),
                ("Runner test", "runner_test"),
                ("Inner test", "inner_test"),
                ("Failed step", "failed_step"),
                ("Before page", "before_page"),
                ("Action", "action"),
                ("Expected", "expected"),
                ("Actual", "actual"),
                ("UI error", "ui_error"),
                ("Auth diagnostic", "auth_diagnostic"),
                ("Error type", "error_type"),
                ("Location", "location"),
            ):
                value = item.get(key)
                if value:
                    lines.append(f"- {label}: `{value}`")
            if item.get("reason"):
                lines.append(f"- Reason: {item['reason']}")

            form_issues = item.get("form_issues")
            if isinstance(form_issues, list) and form_issues:
                lines.append("- Form monitor issues:")
                for issue in form_issues:
                    if not isinstance(issue, dict):
                        continue
                    lines.append(
                        "  - "
                        f"{issue.get('number') or '—'} | "
                        f"{issue.get('title') or 'unknown'} | "
                        f"{issue.get('status') or 'FAILED'} | "
                        f"{issue.get('reason_code') or '—'} | "
                        f"{issue.get('reason') or issue.get('detail') or '—'}"
                    )
                    if issue.get("actual_url") or issue.get("expected_url"):
                        lines.append(
                            "    - URL: "
                            f"actual=`{issue.get('actual_url') or '—'}`, "
                            f"expected=`{issue.get('expected_url') or '—'}`"
                        )
                    if issue.get("actual_title") or issue.get("expected_title"):
                        lines.append(
                            "    - Title: "
                            f"actual=`{issue.get('actual_title') or '—'}`, "
                            f"expected=`{issue.get('expected_title') or '—'}`"
                        )
                    checks = issue.get("checks")
                    if isinstance(checks, dict) and checks:
                        check_text = ", ".join(
                            f"{key}={value}"
                            for key, value in checks.items()
                            if value not in {"", None}
                        )
                        if check_text:
                            lines.append(f"    - Checks: `{check_text}`")
    skipped = summary.get("skipped")
    if isinstance(skipped, dict) and skipped.get("count"):
        lines.extend(["", "## Skipped", f"- Count: `{skipped.get('count')}`", f"- Reason: {skipped.get('reason', '')}"])
    if note:
        lines.extend(["", "## Note", note])
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    summary,
    output_md,
    output_json,
    title,
    model="",
    note="",
):
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(summary, title=title, model=model, note=note), encoding="utf-8")


def write_allure_summary(
    summary,
    output_md,
    output_json,
    results_dir,
    *,
    title,
    full_name,
    epic,
    feature,
    story,
):
    results_dir.mkdir(parents=True, exist_ok=True)
    result_uuid = str(uuid.uuid4())
    slug = full_name.replace(".", "-")
    md_source = f"{result_uuid}-{slug}.md"
    json_source = f"{result_uuid}-{slug}.json"
    (results_dir / md_source).write_text(output_md.read_text(encoding="utf-8"), encoding="utf-8")
    (results_dir / json_source).write_text(output_json.read_text(encoding="utf-8"), encoding="utf-8")

    now_ms = int(time.time() * 1000)
    result = {
        "name": title,
        "status": "passed",
        "description": str(summary.get("summary") or title),
        "attachments": [
            {"name": title, "source": md_source, "type": "text/markdown"},
            {"name": f"{title} JSON", "source": json_source, "type": "application/json"},
        ],
        "start": now_ms,
        "stop": now_ms,
        "uuid": result_uuid,
        "historyId": full_name,
        "testCaseId": full_name,
        "fullName": full_name,
        "labels": [
            {"name": "epic", "value": epic},
            {"name": "feature", "value": feature},
            {"name": "story", "value": story},
            {"name": "parentSuite", "value": epic},
            {"name": "suite", "value": feature},
            {"name": "framework", "value": "pytest"},
            {"name": "language", "value": "python"},
            {"name": "package", "value": full_name.rsplit(".", 1)[0]},
        ],
        "titlePath": [epic, feature],
    }
    (results_dir / f"{result_uuid}-result.json").write_text(
        json.dumps(result, ensure_ascii=False),
        encoding="utf-8",
    )


def main():
    args = parse_args()
    command = _mask_sensitive(args.command)
    results = collect_allure_results(args.results_dir, args.started_at)
    logs = collect_failure_logs(args.logs_dir, args.started_at)
    deterministic = build_deterministic_summary(args.exit_code, results)
    enrich_failed_allure_results(results, args.results_dir)
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    args.ai_output_md.unlink(missing_ok=True)
    args.ai_output_json.unlink(missing_ok=True)

    system_summary = build_local_summary(deterministic)
    write_outputs(
        system_summary,
        args.system_output_md,
        args.system_output_json,
        title="System Test Summary",
    )
    write_allure_summary(
        system_summary,
        args.system_output_md,
        args.system_output_json,
        args.results_dir,
        title="System Test Summary",
        full_name="system.test.summary",
        epic="System",
        feature="Test Summary",
        story="Deterministic",
    )
    print(f"System summary yozildi: {args.system_output_md}")

    if not env_flag("AI_ANALYSIS"):
        print("AI tahlili o'chirilgan: AI_ANALYSIS=0")
        return 0

    if deterministic.get("result") != "FAILED":
        print("AI tahlili skipped: natija FAILED emas")
        return 0

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("AI summary skipped: GEMINI_API_KEY set qilinmagan", file=sys.stderr)
        return 0

    prompt = build_prompt(command, deterministic, logs)
    try:
        raw = call_gemini(prompt, model=model, api_key=api_key)
        summary = parse_ai_json(raw)
    except Exception as exc:
        print(f"AI summary xato bilan tugadi, test exit code o'zgarmaydi: {exc}", file=sys.stderr)
        return 0

    summary = enrich_ai_summary(summary, deterministic)
    write_outputs(
        summary,
        args.ai_output_md,
        args.ai_output_json,
        title="AI xatolik tahlili",
        model=model,
    )
    write_allure_summary(
        summary,
        args.ai_output_md,
        args.ai_output_json,
        args.results_dir,
        title="AI xatolik tahlili",
        full_name="ai.test.summary",
        epic="AI",
        feature="Xatolik tahlili",
        story="Gemini",
    )
    print(f"AI summary yozildi: {args.ai_output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
