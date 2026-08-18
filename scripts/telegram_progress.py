from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "test-results" / "telegram-progress.json"
DELIVERY_FILE = ROOT / "test-results" / "telegram-delivery.json"
SYSTEM_SUMMARY_JSON = ROOT / "test-results" / "system-summary.json"
AI_SUMMARY_JSON = ROOT / "test-results" / "ai-summary.json"
EVENT_PREFIX = "SMARTUP_PROGRESS "
MAX_MESSAGE_LENGTH = 3900
OPERATIONAL_FILIAL_PLACEHOLDER = "<operatsion filial>"
PROGRESS_EDIT_INTERVAL_SECONDS = 10
FINAL_DELIVERY_ATTEMPTS = 3
TRANSIENT_RETRY_DELAYS_SECONDS = (2, 5, 10)
FINAL_RETRY_WAIT_BUDGET_SECONDS = 10

TASHKENT_TZ = timezone(timedelta(hours=5))
TARGET_LABELS = {
    "all": "All",
    "setup": "Setup",
    "setup-group-0": "Smoke",
    "setup-report": "Setup + Report",
    "setup-a2-admin": "Setup + A2 Admin Forms",
    "setup-forms": "Setup + Forms",
    "company": "Company",
    "groups": "Groups",
    "group-report": "Report Group",
    "forms": "Forms",
}
TARGET_SUITE_LABELS = {
    "all": "All",
    "setup": "Setup",
    "setup-group-0": "Smoke · Setup + A group",
    "setup-report": "Setup + Report group",
    "setup-a2-admin": "Setup + A2 Admin Forms",
    "setup-forms": "Setup + Forms",
    "company": "Company",
    "groups": "Groups",
    "group-report": "Report group",
    "forms": "Forms",
}
GROUP_ORDER = [
    "Setup",
    "A2 Admin Forms group",
    "Report group",
    "Forms group",
]
STATUS_MARK = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭"}
ELEMENT_STATE_LABELS = {
    "ambiguous": "bir nechta element",
    "hidden": "element yashirin",
    "disabled": "element faol emas",
    "unstable": "element beqaror",
    "blocked": "element to'silgan",
    "resolved": "element topilgan",
    "not_found": "element topilmagan",
}
AI_CONFIDENCE_LABELS = {
    "low": "past",
    "medium": "o‘rta",
    "high": "yuqori",
}


@dataclass(frozen=True)
class TelegramRequestResult:
    ok: bool
    method: str
    data: dict | None = None
    error_code: int | None = None
    description: str = ""
    retry_after: int = 0
    category: str = ""

    @property
    def retryable(self):
        return self.category in {"flood_control", "network", "server"}


def env_value(name):
    return os.getenv(name, "").strip()


def telegram_enabled():
    return bool(env_value("TELEGRAM_BOT_TOKEN") and env_value("TELEGRAM_CHAT_ID"))


def sanitize_telegram_error(value):
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(
        r"https://api\.telegram\.org/bot[^/\s]+",
        "https://api.telegram.org/bot<redacted>",
        text,
    )
    return text[:300]


def telegram_error_category(error_code):
    if error_code == 429:
        return "flood_control"
    if error_code in {401, 403}:
        return "authorization"
    if error_code == 400:
        return "bad_request"
    if isinstance(error_code, int) and error_code >= 500:
        return "server"
    return "telegram"


def telegram_error_result(method, *, error_code=None, description="", retry_after=0, category=""):
    return TelegramRequestResult(
        ok=False,
        method=method,
        error_code=error_code,
        description=sanitize_telegram_error(description) or "Telegram API xatosi",
        retry_after=max(0, int(retry_after or 0)),
        category=category or telegram_error_category(error_code),
    )


def telegram_response_error(method, data, fallback_code=None):
    data = data if isinstance(data, dict) else {}
    error_code = data.get("error_code", fallback_code)
    try:
        error_code = int(error_code) if error_code is not None else None
    except (TypeError, ValueError):
        error_code = fallback_code
    parameters = data.get("parameters")
    parameters = parameters if isinstance(parameters, dict) else {}
    retry_after = parameters.get("retry_after", 0)
    try:
        retry_after = int(retry_after or 0)
    except (TypeError, ValueError):
        retry_after = 0
    description = sanitize_telegram_error(data.get("description"))
    if error_code == 400 and "message is not modified" in description.lower():
        return TelegramRequestResult(ok=True, method=method, data=data)
    return telegram_error_result(
        method,
        error_code=error_code,
        description=description,
        retry_after=retry_after,
    )


def telegram_request(method, payload):
    if not telegram_enabled():
        return telegram_error_result(
            method,
            description="Telegram credentials sozlanmagan",
            category="disabled",
        )
    token = env_value("TELEGRAM_BOT_TOKEN")
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=encoded,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            data = {}
        result = telegram_response_error(method, data, fallback_code=exc.code)
        if not result.description or result.description == "Telegram API xatosi":
            result = telegram_error_result(
                method,
                error_code=exc.code,
                description=exc.reason,
            )
        return result
    except (OSError, urllib.error.URLError) as exc:
        return telegram_error_result(
            method,
            description=exc,
            category="network",
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return telegram_error_result(
            method,
            description=exc,
            category="server",
        )
    if not isinstance(data, dict) or not data.get("ok"):
        return telegram_response_error(method, data)
    return TelegramRequestResult(ok=True, method=method, data=data)


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def now_tashkent():
    return datetime.now(TASHKENT_TZ)


def format_duration(seconds):
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    if minutes:
        return f"{minutes} daq {secs} son"
    return f"{secs} son"


def server_host(server):
    value = (server or "").strip()
    for prefix in ("https://", "http://"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value.rstrip("/") or "unknown"


def target_label(target):
    key = (target or "all").strip().lower()
    return TARGET_LABELS.get(key, key.title() if key else "All")


def target_suite_label(target):
    key = (target or "all").strip().lower()
    return TARGET_SUITE_LABELS.get(key, target_label(key))


def _utc_now_text():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _parse_utc_text(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _timestamp_text(value, tz, suffix):
    parsed = _parse_utc_text(value)
    if parsed is None:
        return ""
    return parsed.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S") + f" {suffix}"


def _clock_text(value, tz):
    parsed = _parse_utc_text(value)
    if parsed is None:
        return ""
    return parsed.astimezone(tz).strftime("%H:%M:%S")


def _summary_counts(summary):
    counts = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "deselected": 0,
    }
    aliases = {"error": "errors", "errors": "errors"}
    for raw_count, raw_name in re.findall(
        r"(\d+)\s+(passed|failed|errors?|skipped|deselected)\b",
        str(summary or "").lower(),
    ):
        key = aliases.get(raw_name, raw_name)
        counts[key] += int(raw_count)
    return counts


def _result_counts(state):
    summary_counts = _summary_counts(state.get("summary"))
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    if not results:
        return summary_counts
    statuses = [str(item.get("status") or "").upper() for item in results]
    return {
        "passed": max(statuses.count("PASSED"), summary_counts["passed"]),
        "failed": max(statuses.count("FAILED"), summary_counts["failed"]),
        "errors": summary_counts["errors"],
        "skipped": max(statuses.count("SKIPPED"), summary_counts["skipped"]),
        "deselected": summary_counts["deselected"],
    }


def _result_metrics(state):
    counts = _result_counts(state)
    failed = counts["failed"] + counts["errors"]
    completed = counts["passed"] + failed + counts["skipped"]
    total = completed
    if str(state.get("target") or "").strip().lower() == "forms":
        forms_results = _forms_results(state)
        total = max(total, _forms_total(state, forms_results))
    return {**counts, "failed_total": failed, "completed": completed, "total": total}


def title_line(state):
    name = f"{target_label(str(state.get('target') or 'all'))} CI"
    result = str(state.get("result") or "").upper()
    if result == "PASSED":
        return f"✅ {name} — PASSED"
    if result == "FAILED":
        return f"❌ {name} — FAILED"
    return f"🟡 {name} — RUNNING"


def first_failed_result(state):
    for item in state.get("results", []):
        if isinstance(item, dict) and item.get("status") == "FAILED":
            return item
    return {}


def first_message_line(value):
    for line in str(value or "").splitlines():
        text = line.strip()
        if text:
            return text
    return ""


def truncate_message(text, limit=MAX_MESSAGE_LENGTH):
    if len(text) <= limit:
        return text
    lines = text.splitlines()
    while lines and len("\n".join(lines) + "\n...") > limit:
        lines.pop(-1)
    if lines:
        return "\n".join(lines) + "\n..."
    return text[: max(0, limit - 3)] + "..."


def grouped_result_lines(state):
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    current = str(state.get("current") or "").strip()
    current_group = str(state.get("current_group") or "").strip()
    finished = bool(state.get("result"))

    groups = {}
    seen_order = []

    def bucket(name):
        if name not in groups:
            groups[name] = []
            seen_order.append(name)
        return groups[name]

    for item in results:
        group = str(item.get("group") or "Other").strip() or "Other"
        mark = STATUS_MARK.get(str(item.get("status") or "").upper(), "•")
        display = str(item.get("display") or item.get("test_id") or "unknown")
        bucket(group).append(f"{mark} {display}")

    if not finished and current:
        bucket(current_group or "Other").append(f"⏳ {current}")

    ordered = [g for g in GROUP_ORDER if g in groups]
    ordered += [g for g in seen_order if g not in GROUP_ORDER]

    lines = []
    for name in ordered:
        lines.append("")
        lines.append(name)
        lines.extend(groups[name])
    return lines


def _form_context(item):
    context = item.get("form") if isinstance(item, dict) else None
    return context if isinstance(context, dict) else {}


def _form_context_display(context):
    try:
        number = f"{int(context.get('number') or 0):03d}"
    except (TypeError, ValueError):
        number = "—"
    path = " → ".join(
        str(value).strip()
        for value in (
            context.get("navbar"),
            context.get("menu"),
            context.get("title"),
        )
        if str(value or "").strip()
    )
    return f"{number} | {path or 'Noma’lum forma'}"


def _form_context_lines(context):
    try:
        number = f"{int(context.get('number') or 0):03d}"
    except (TypeError, ValueError):
        number = "—"
    title = str(context.get("title") or "Noma’lum forma").strip()
    lines = [f"{number} · {title}"]
    path = " → ".join(
        str(value).strip()
        for value in (context.get("navbar"), context.get("menu"))
        if str(value or "").strip()
    )
    if path:
        lines.append(path)
    filial = _form_filial_label(context)
    if filial:
        lines.append(f"Filial: {filial}")
    return lines


def _form_filial_label(context):
    filial = str(context.get("filial") or "").strip()
    if filial == OPERATIONAL_FILIAL_PLACEHOLDER:
        return "Operatsion filial"
    return filial


def _forms_results(state):
    return [
        item
        for item in state.get("results", [])
        if isinstance(item, dict) and _form_context(item)
    ]


def _forms_total(state, results):
    totals = [_metric_count(state, "current_form_total")]
    totals.extend(_metric_count(item, "form_total") for item in results)
    return max(totals, default=0)


def forms_progress_lines(state, *, include_current=True):
    """Forms run uchun hisoblar va joriy formani ixcham ko'rsatadi."""
    results = _forms_results(state)
    current = state.get("current_form")
    current = current if isinstance(current, dict) else {}
    if not results and not current:
        return []

    total = _forms_total(state, results)
    metrics = _result_metrics(state)
    completed = metrics["completed"]
    lines = [
        "",
        f"Jarayon: {completed}/{total or completed}"
        + (f" · {round(completed * 100 / total)}%" if total else ""),
        f"Passed: {metrics['passed']} · Skipped: {metrics['skipped']}",
    ]
    if metrics["failed_total"]:
        lines.append(f"Xatolar: {metrics['failed_total']} ta")
    else:
        lines.append("Xatolik aniqlanmadi")

    started_epoch = state.get("test_started_epoch")
    if isinstance(started_epoch, (int, float)):
        lines.append(f"O'tgan vaqt: {format_duration(time.time() - started_epoch)}")

    if include_current and current:
        lines.extend(["", "Hozir tekshirilmoqda:"])
        lines.extend(_form_context_lines(current))
    return lines


def _failure_time_lines(failed):
    timestamp = failed.get("failure_at_utc") or failed.get("occurred_at_utc")
    local_text = _timestamp_text(timestamp, TASHKENT_TZ, "UZT")
    utc_text = _timestamp_text(timestamp, timezone.utc, "UTC")
    if not local_text:
        return ["Xato vaqti: aniqlanmadi"]
    return [f"Xato vaqti: {local_text}", f"UTC vaqti: {utc_text}"]


def _failed_result_entries(state):
    entries = []
    for failed in state.get("results", []):
        if not isinstance(failed, dict) or failed.get("status") != "FAILED":
            continue
        form_issues = failed.get("form_issues")
        if isinstance(form_issues, list) and form_issues:
            entries.extend(
                (failed, issue)
                for issue in form_issues
                if isinstance(issue, dict)
            )
        else:
            entries.append((failed, None))
    return entries


def _failed_entry_lines(failed, issue, *, index, total):
    group = str(failed.get("group") or "").strip()
    test_name = str(failed.get("display") or failed.get("title") or failed.get("inner_test") or "").strip()
    test_context = " → ".join(value for value in (group, test_name) if value)
    step = str(failed.get("failed_step") or failed.get("step") or "").strip()
    if step == test_name:
        step = ""

    error_message = first_message_line(failed.get("message"))

    failed_form = _form_context(failed)
    lines = ["", f"❌ Xatolik {index}/{total}"]
    lines.extend(_failure_time_lines(failed))

    if isinstance(issue, dict):
        status_labels = {
            "OPENED_WITH_DEFECT": "nuqson bilan ochildi",
            "NOT_OPENED": "ochilmadi",
            "TEST_BLOCKED": "test bloklandi",
            "NOT_CHECKED": "tekshirilmadi",
        }
        issue_number = failed_form.get("number") or issue.get("number")
        try:
            number = f"{int(issue_number):03d}"
        except (TypeError, ValueError):
            number = str(issue_number or "—")
        title = str(failed_form.get("title") or issue.get("title") or "Noma’lum forma").strip()
        lines.append(f"Forma: {number}")
        path = " → ".join(
            str(value).strip()
            for value in (failed_form.get("navbar"), failed_form.get("menu"))
            if str(value or "").strip()
        )
        if path:
            lines.append(path)
        lines.append(title)
        filial = _form_filial_label(failed_form)
        if filial:
            lines.append(f"Filial: {filial}")
        status = str(issue.get("status") or "").upper()
        reason = str(issue.get("reason") or issue.get("reason_code") or "").strip()
        if not reason:
            reason = status_labels.get(status, status or "Xato sababi aniqlanmadi")
        lines.append(f"Sabab: {reason}")
        expected_url = str(issue.get("expected_url") or failed_form.get("expected_url") or "").strip()
        actual_url = str(issue.get("actual_url") or "").strip()
        if expected_url:
            lines.append(f"Kutilgan URL: {expected_url}")
        if actual_url:
            lines.append(f"Amaldagi URL: {actual_url}")
        detail = first_message_line(issue.get("detail"))
        if detail and detail != reason:
            lines.append(f"Texnik: {detail}")
        return lines

    technical = []
    error_type = str(failed.get("error_type") or "").strip()
    timeout = str(failed.get("timeout") or "").strip()
    element_state = str(failed.get("element_state") or "").strip()
    target = str(failed.get("target") or "").strip()
    if error_type:
        technical.append(error_type)
    if timeout:
        technical.append(timeout)
    if element_state:
        technical.append(ELEMENT_STATE_LABELS.get(element_state, element_state))
    if target:
        technical.append(target)

    pairs = [
        ("Forma", _form_context_display(failed_form) if failed_form else ""),
        ("Navbar", failed_form.get("navbar")),
        ("Menu", failed_form.get("menu")),
        ("Filial", _form_filial_label(failed_form)),
        ("Kutilgan URL", failed_form.get("expected_url")),
        ("Test", test_context),
        ("Qadam", step),
        ("Sahifa", failed.get("before_page")),
        ("Amal", failed.get("action")),
        ("Kutilgan", failed.get("expected")),
        ("Amaldagi", failed.get("actual")),
        ("UI xabari", failed.get("ui_error")),
        ("Auth diagnostika", failed.get("auth_diagnostic")),
        ("Sabab", failed.get("reason") or error_message),
        ("Texnik", " · ".join(technical)),
        ("Kod", failed.get("location")),
    ]
    for label, value in pairs:
        text = str(value or "").strip()
        if text:
            lines.append(f"{label}: {text}")
    return lines


def failed_block(state):
    entries = _failed_result_entries(state)
    lines = []
    for index, (failed, issue) in enumerate(entries, start=1):
        lines.extend(
            _failed_entry_lines(
                failed,
                issue,
                index=index,
                total=len(entries),
            )
        )
    return lines


def _metric_count(metrics, key):
    try:
        return int(metrics.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def final_coverage_lines(state):
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    setup_results = [
        item for item in results if str(item.get("group") or "").strip() == "Setup"
    ]
    lines = []
    if setup_results:
        setup_statuses = [
            str(item.get("status") or "").upper() for item in setup_results
        ]
        setup_parts = [f"Passed: {setup_statuses.count('PASSED')}"]
        if setup_statuses.count("FAILED"):
            setup_parts.append(f"Failed: {setup_statuses.count('FAILED')}")
        if setup_statuses.count("SKIPPED"):
            setup_parts.append(f"Skipped: {setup_statuses.count('SKIPPED')}")
        lines.append(
            f"Setup: {len(setup_results)} qadam · " + " · ".join(setup_parts)
        )

    coverage = state.get("form_coverage")
    if not isinstance(coverage, dict) or not coverage:
        a2_metrics = state.get("a2_admin_forms")
        if isinstance(a2_metrics, dict) and a2_metrics:
            coverage = {
                **a2_metrics,
                "suites": {
                    "a2_admin": {
                        "label": "A2 Admin",
                        **a2_metrics,
                    }
                },
            }
        else:
            return lines

    checked = _metric_count(coverage, "checked")
    passed = _metric_count(coverage, "passed")
    if checked:
        lines.append(f"Forms: {passed}/{checked} muvaffaqiyatli")

    suites = coverage.get("suites")
    if isinstance(suites, dict):
        for key in ("spravochniki", "a2_admin"):
            metrics = suites.get(key)
            if not isinstance(metrics, dict):
                continue
            suite_checked = _metric_count(metrics, "checked")
            suite_passed = _metric_count(metrics, "passed")
            if not suite_checked:
                continue
            label = str(metrics.get("label") or key)
            lines.append(f"  • {label}: {suite_passed}/{suite_checked}")
    return lines


def _finished_time_lines(state):
    result = str(state.get("result") or "").upper()
    start_utc = state.get("started_at_utc")
    finish_utc = state.get("finished_at_utc")
    start_local = _timestamp_text(start_utc, TASHKENT_TZ, "UZT")
    finish_local = _timestamp_text(finish_utc, TASHKENT_TZ, "UZT")
    lines = []
    if result == "FAILED" and start_local:
        lines.append(f"Boshlanish: {start_local}")
        if finish_local:
            lines.append(f"Yakunlanish: {finish_local}")
    else:
        start_clock = _clock_text(start_utc, TASHKENT_TZ) or str(state.get("started_clock") or "").strip()
        finish_clock = _clock_text(finish_utc, TASHKENT_TZ) or str(state.get("finished_clock") or "").strip()
        if start_clock and finish_clock:
            lines.append(f"Vaqt: {start_clock}–{finish_clock} UZT")
        elif str(state.get("started_at") or "").strip():
            lines.append(f"Vaqt: {str(state.get('started_at')).strip()}")
    duration = str(state.get("duration") or "").strip()
    if duration:
        lines.append(f"Davomiylik: {duration}")
    return lines


def _final_result_lines(state):
    metrics = _result_metrics(state)
    result = str(state.get("result") or "").upper()
    is_forms = str(state.get("target") or "").strip().lower() == "forms"
    noun = "forma" if is_forms else "test"
    lines = [""]
    if result == "PASSED":
        if is_forms:
            lines.append(f"✅ {metrics['completed']} ta forma tekshirildi")
        else:
            lines.append(f"✅ Yakunlandi: {metrics['completed']} ta test")
        lines.append(
            f"✅ Passed: {metrics['passed']} · Skipped: {metrics['skipped']}"
        )
        lines.append("✅ Xatolik aniqlanmadi")
        if metrics["deselected"]:
            lines.append(f"Tanlanmagan: {metrics['deselected']}")
        return lines

    if metrics["failed_total"]:
        lines.append(f"❌ {metrics['failed_total']} ta xatolik aniqlandi")
    else:
        lines.append("❌ CI jarayonida xatolik aniqlandi")
    if metrics["total"] and metrics["total"] != metrics["completed"]:
        action = "Tekshirildi" if is_forms else "Yakunlandi"
        lines.append(f"{action}: {metrics['completed']}/{metrics['total']}")
    else:
        lines.append(f"Yakunlandi: {metrics['completed']} ta {noun}")
    result_parts = [
        f"Passed: {metrics['passed']}",
        f"Failed: {metrics['failed_total']}",
        f"Skipped: {metrics['skipped']}",
    ]
    lines.append(" · ".join(result_parts))
    if metrics["deselected"]:
        lines.append(f"Tanlanmagan: {metrics['deselected']}")
    return lines


def _generic_progress_lines(state):
    metrics = _result_metrics(state)
    lines = [""]
    test_started_epoch = state.get("test_started_epoch")
    if not isinstance(test_started_epoch, (int, float)):
        status = str(state.get("status") or "").strip()
        if status:
            lines.append(f"Bosqich: {status}")
        started_at = str(state.get("started_at") or "").strip()
        if started_at:
            lines.append(f"Boshlangan: {started_at}")
        return lines

    if metrics["completed"]:
        lines.append(f"Yakunlandi: {metrics['completed']} ta test")
        lines.append(
            f"Passed: {metrics['passed']} · Failed: {metrics['failed_total']} · "
            f"Skipped: {metrics['skipped']}"
        )
    current = str(state.get("current") or "").strip()
    if current:
        lines.extend(["", "Hozir tekshirilmoqda:", current])
    lines.append(
        f"O'tgan vaqt: {format_duration(time.time() - test_started_epoch)}"
    )
    return lines


def render_html_message(
    main_lines,
    expandable_lines=None,
    footer_lines=None,
    footer_links=None,
):
    main = "\n".join(str(line) for line in main_lines).strip()
    expandable = "\n".join(str(line) for line in (expandable_lines or [])).strip()
    footer = "\n".join(str(line) for line in (footer_lines or [])).strip()
    links = [
        (str(label).strip(), str(url).strip())
        for label, url in (footer_links or [])
        if str(label).strip() and str(url).strip()
    ]

    footer_visible_length = len(footer) + sum(
        len(label) + len(url) + 2 for label, url in links
    )
    separators = 2 * sum(bool(part) for part in (expandable, footer or links))
    fixed_length = len(main) + footer_visible_length + separators
    if expandable:
        expandable = truncate_message(
            expandable,
            limit=max(3, MAX_MESSAGE_LENGTH - fixed_length),
        )
    elif fixed_length > MAX_MESSAGE_LENGTH:
        main = truncate_message(
            main,
            limit=max(3, MAX_MESSAGE_LENGTH - len(footer) - separators),
        )

    sections = [html.escape(main, quote=False)]
    if expandable:
        sections.append(
            f"<blockquote expandable>{html.escape(expandable, quote=False)}</blockquote>"
        )
    footer_sections = [html.escape(footer, quote=False)] if footer else []
    footer_sections.extend(
        f'<a href="{html.escape(url, quote=True)}">🔗 {html.escape(label, quote=False)}</a>'
        for label, url in links
    )
    if footer_sections:
        sections.append("\n".join(footer_sections))
    return "\n\n".join(section for section in sections if section)


def render_message(state):
    finished = bool(state.get("result"))
    target = str(state.get("target") or "all").strip().lower()
    result = str(state.get("result") or "").upper()
    lines = [
        title_line(state),
        "",
        f"Server: {server_host(str(state.get('server') or ''))}",
        f"Suite: {target_suite_label(target)}",
    ]

    if finished:
        lines.extend(_final_result_lines(state))
        if target in {"setup-forms", "setup-a2-admin"}:
            lines.extend(final_coverage_lines(state))
        lines.extend(["", *_finished_time_lines(state)])
        run_code = str(state.get("run_code") or "").strip()
        if run_code and run_code != "not found" and target != "forms":
            lines.append(f"Test data kodi: {run_code}")

    expandable = []
    if not finished:
        forms_lines = forms_progress_lines(state)
        lines.extend(forms_lines or _generic_progress_lines(state))
    elif result == "FAILED":
        details = failed_block(state)
        if details:
            lines.extend(details)

    footer = []
    footer_links = []
    notification_warning = str(
        state.get("telegram_notification_warning") or ""
    ).strip()
    if notification_warning:
        footer.extend(["Telegram ogohlantirishi:", notification_warning])
    if finished:
        run_url = str(state.get("run_url") or "").strip()
        if run_url:
            label = (
                "Xato loglari va batafsil natija"
                if result == "FAILED"
                else "Batafsil natija"
            )
            footer_links.append((label, run_url))
        ai = state.get("ai_analysis")
        if isinstance(ai, dict) and ai and result == "FAILED":
            confidence = AI_CONFIDENCE_LABELS.get(
                str(ai.get("confidence") or "").lower(),
                "past",
            )
            observed = str(ai.get("observed") or "").strip()
            probable_cause = str(ai.get("probable_cause") or "").strip()
            expandable.extend(
                [
                    f"🤖 AI tahlili · Ishonch: {confidence}",
                    "",
                    "Kuzatilgan:",
                    observed,
                    "",
                    "Ehtimoliy sabab:",
                    probable_cause,
                ]
            )

    return render_html_message(lines, expandable, footer, footer_links)


def render_plain_message(state):
    rendered = render_message(state)
    rendered = re.sub(
        r'<a href="([^"]+)">([^<]+)</a>',
        lambda match: f"{match.group(2)}: {match.group(1)}",
        rendered,
    )
    return html.unescape(re.sub(r"<[^>]+>", "", rendered))


def telegram_result_summary(result):
    code = f"{result.error_code} " if result.error_code is not None else ""
    return f"{code}{result.description}".strip()


def log_telegram_warning(result, *, attempt=1):
    print(
        "Telegram progress warning: "
        f"method={result.method} category={result.category or 'unknown'} "
        f"code={result.error_code or '-'} retry_after={result.retry_after}s "
        f"attempt={attempt} error={result.description}",
        file=sys.stderr,
    )


def record_telegram_error(state, result, *, attempt=1, waited_seconds=0):
    summary = telegram_result_summary(result)
    if waited_seconds:
        summary += (
            f". {waited_seconds} soniya kutildi; "
            f"qayta urinish {attempt}/{FINAL_DELIVERY_ATTEMPTS}"
        )
    state["telegram_notification_warning"] = summary
    retry_at = (
        now_tashkent() + timedelta(seconds=result.retry_after)
        if result.retry_after
        else None
    )
    state["telegram_last_error"] = {
        "method": result.method,
        "category": result.category,
        "error_code": result.error_code,
        "description": result.description,
        "retry_after": result.retry_after,
        "retry_at": retry_at.isoformat(timespec="seconds") if retry_at else "",
        "attempt": attempt,
        "at": now_tashkent().isoformat(timespec="seconds"),
    }
    log_telegram_warning(result, attempt=attempt)


def record_telegram_success(state, text):
    state["telegram_last_sent_epoch"] = time.time()
    state["telegram_last_text"] = text
    state.pop("telegram_backoff_until", None)


def telegram_payload(state, *, message_id=None, plain=False):
    payload = {
        "chat_id": env_value("TELEGRAM_CHAT_ID"),
        "text": render_plain_message(state) if plain else render_message(state),
        "disable_web_page_preview": "true",
    }
    if message_id is not None:
        payload["message_id"] = str(message_id)
    if not plain:
        payload["parse_mode"] = "HTML"
    return payload


def is_format_error(result):
    if result.category != "bad_request":
        return False
    description = result.description.lower()
    return any(
        marker in description
        for marker in ("parse", "entities", "message text", "too long")
    )


def edit_progress(state, *, force=False):
    message_id = state.get("message_id")
    if not message_id:
        return None

    now = time.time()
    text = render_message(state)
    if not force:
        if text == state.get("telegram_last_text"):
            return None
        if now < float(state.get("telegram_backoff_until") or 0):
            return None
        last_sent = float(state.get("telegram_last_sent_epoch") or 0)
        if now - last_sent < PROGRESS_EDIT_INTERVAL_SECONDS:
            return None

    result = telegram_request(
        "editMessageText",
        telegram_payload(state, message_id=message_id),
    )
    if not result.ok and is_format_error(result):
        record_telegram_error(state, result)
        result = telegram_request(
            "editMessageText",
            telegram_payload(state, message_id=message_id, plain=True),
        )

    if result.ok:
        record_telegram_success(state, text)
    else:
        record_telegram_error(state, result)
        delay = result.retry_after or PROGRESS_EDIT_INTERVAL_SECONDS
        if result.retryable:
            state["telegram_backoff_until"] = time.time() + delay
    save_state(state)
    return result


def command_start(args):
    now = now_tashkent()
    state = {
        "server": args.server,
        "target": args.target,
        "status": args.status,
        "current": "",
        "current_group": "",
        "results": [],
        "result": "",
        "started_at": now.strftime("%Y-%m-%d %H:%M:%S UZT"),
        "started_at_utc": _utc_now_text(),
        "started_clock": now.strftime("%H:%M:%S"),
        "started_epoch": time.time(),
    }
    if not telegram_enabled():
        save_state(state)
        return 0

    if args.message_id:
        state["message_id"] = args.message_id
        edit_progress(state, force=True)
    else:
        result = telegram_request(
            "sendMessage",
            telegram_payload(state),
        )
        response_data = result.data if result.ok else None
        message = (
            response_data.get("result")
            if isinstance(response_data, dict)
            else None
        )
        if isinstance(message, dict) and message.get("message_id"):
            state["message_id"] = message["message_id"]
            record_telegram_success(state, render_message(state))
        elif not result.ok:
            record_telegram_error(state, result)
    save_state(state)
    return 0


def command_update(args):
    state = load_state()
    if not state:
        return 0
    if args.status:
        state["status"] = args.status
    if args.current is not None:
        state["current"] = args.current
    save_state(state)
    edit_progress(state, force=bool(args.status))
    return 0


def update_from_event(state, event):
    event_name = str(event.get("event") or "")
    display = str(event.get("display") or event.get("title") or event.get("test_id") or "unknown")
    occurred_at_utc = str(event.get("occurred_at_utc") or "").strip() or _utc_now_text()
    if event_name == "form_result":
        state["status"] = "Forms running"
        state["form_progress"] = {
            "suite": str(event.get("title") or ""),
            "number": _metric_count(event, "form_number"),
            "total": _metric_count(event, "form_total"),
            "status": str(event.get("form_status") or ""),
            "reason": str(event.get("error_type") or ""),
        }
        return
    if event_name == "started":
        form = event.get("form")
        if isinstance(form, dict) and form:
            state["status"] = "Forms running"
            state["current_form"] = dict(form)
            state["current_form_total"] = _metric_count(event, "form_total")
        else:
            state["status"] = "Tests running"
        state["current"] = display
        state["current_group"] = str(event.get("group") or "")
        return

    if event_name not in {"passed", "failed", "skipped"}:
        return

    status = {
        "passed": "PASSED",
        "failed": "FAILED",
        "skipped": "SKIPPED",
    }[event_name]
    result = {
        "status": status,
        "display": display,
        "group": event.get("group") or "",
        "runner": event.get("runner") or "",
        "test_id": event.get("test_id") or "",
        "title": event.get("title") or "",
        "inner_test": event.get("title") or display,
        "error_type": event.get("error_type") or "",
        "message": event.get("message") or "",
        "occurred_at_utc": occurred_at_utc,
    }
    if event_name == "failed":
        result["failure_at_utc"] = occurred_at_utc
    form = event.get("form")
    if isinstance(form, dict) and form:
        result["form"] = dict(form)
        result["form_total"] = _metric_count(event, "form_total")
    state.setdefault("results", []).append(result)
    if isinstance(form, dict) and form:
        state["current"] = ""
        state["current_group"] = ""
        state["current_form"] = {}
    elif event_name in {"passed", "skipped"}:
        state["current"] = ""
        state["current_group"] = ""
    else:
        state["current"] = display


def failed_details_from_system_summary():
    if not SYSTEM_SUMMARY_JSON.exists():
        return {}
    try:
        data = json.loads(SYSTEM_SUMMARY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    failed_tests = data.get("failed_tests") if isinstance(data, dict) else None
    if not isinstance(failed_tests, list) or not failed_tests:
        return {}
    first = failed_tests[0] if isinstance(failed_tests[0], dict) else {}
    form_issues = first.get("form_issues")
    return {
        "group": str(first.get("group") or ""),
        "runner": str(first.get("runner_test") or ""),
        "inner_test": str(first.get("inner_test") or ""),
        "failed_step": str(first.get("failed_step") or ""),
        "message": str(first.get("message") or ""),
        "error_type": str(first.get("error_type") or ""),
        "reason": str(first.get("reason") or ""),
        "location": str(first.get("location") or ""),
        "before_page": str(first.get("before_page") or ""),
        "action": str(first.get("action") or ""),
        "expected": str(first.get("expected") or ""),
        "actual": str(first.get("actual") or ""),
        "ui_error": str(first.get("ui_error") or ""),
        "auth_diagnostic": str(first.get("auth_diagnostic") or ""),
        "target": str(first.get("target") or ""),
        "element_state": str(first.get("element_state") or ""),
        "timeout": str(first.get("timeout") or ""),
        "failure_at_utc": str(first.get("failure_at_utc") or ""),
        "form_issues": (
            [dict(issue) for issue in form_issues if isinstance(issue, dict)]
            if isinstance(form_issues, list)
            else []
        ),
    }


def sync_summary_metrics(state):
    if not SYSTEM_SUMMARY_JSON.exists():
        return
    try:
        data = json.loads(SYSTEM_SUMMARY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    coverage = data.get("form_coverage")
    if isinstance(coverage, dict) and coverage:
        state["form_coverage"] = coverage
    a2_metrics = data.get("a2_admin_forms")
    if isinstance(a2_metrics, dict) and a2_metrics:
        state["a2_admin_forms"] = a2_metrics


def enrich_failed_result_from_summary(state):
    details = failed_details_from_system_summary()
    if not details:
        return
    for item in state.get("results", []):
        if isinstance(item, dict) and item.get("status") == "FAILED":
            item.update({key: value for key, value in details.items() if value})
            return
    state.setdefault("results", []).append(
        {
            "status": "FAILED",
            "display": details.get("inner_test") or "unknown",
            **{key: value for key, value in details.items() if value},
        }
    )


def command_run(args):
    command = args.command
    if not command:
        print("telegram_progress.py run: command is required", file=sys.stderr)
        return 2

    state = load_state()
    now = now_tashkent()
    state["status"] = "Testlar boshlanmoqda"
    state["test_started_at"] = now.strftime("%Y-%m-%d %H:%M:%S UZT")
    state["test_started_at_utc"] = _utc_now_text()
    state["test_started_epoch"] = time.time()
    save_state(state)
    edit_progress(state, force=True)
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
        if not line.startswith(EVENT_PREFIX):
            continue
        try:
            event = json.loads(line[len(EVENT_PREFIX):])
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        update_from_event(state, event)
        save_state(state)
        edit_progress(state)

    exit_code = process.wait()
    sync_summary_metrics(state)
    if exit_code:
        enrich_failed_result_from_summary(state)
    save_state(state)
    edit_progress(state)
    return exit_code


def read_ai_analysis():
    if not AI_SUMMARY_JSON.exists():
        return {}
    try:
        data = json.loads(AI_SUMMARY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    observed = str(data.get("observed") or "").strip()[:600]
    probable_cause = str(data.get("probable_cause") or "").strip()[:600]
    if not observed or not probable_cause:
        return {}
    return {
        "observed": observed,
        "probable_cause": probable_cause,
        "confidence": str(data.get("confidence") or "low").strip().lower(),
    }


def derive_summary(state):
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    passed = sum(1 for item in results if str(item.get("status")).upper() == "PASSED")
    failed = sum(1 for item in results if str(item.get("status")).upper() == "FAILED")
    parts = [f"{passed} passed"]
    if failed:
        parts.append(f"{failed} failed")
    return ", ".join(parts)


def retry_delay_seconds(result, attempt):
    if result.retry_after:
        return result.retry_after
    index = min(max(0, attempt - 1), len(TRANSIENT_RETRY_DELAYS_SECONDS) - 1)
    return TRANSIENT_RETRY_DELAYS_SECONDS[index]


def attempt_final_method(state, method, *, message_id=None, retry_deadline=None):
    plain = False
    errors = []
    last_result = None
    if retry_deadline is None:
        retry_deadline = time.monotonic() + FINAL_RETRY_WAIT_BUDGET_SECONDS
    for attempt in range(1, FINAL_DELIVERY_ATTEMPTS + 1):
        result = telegram_request(
            method,
            telegram_payload(state, message_id=message_id, plain=plain),
        )
        last_result = result
        if result.ok:
            return result, attempt, errors, plain

        errors.append(result)
        record_telegram_error(state, result, attempt=attempt)
        if is_format_error(result) and not plain:
            plain = True
            state["telegram_notification_warning"] = (
                f"{telegram_result_summary(result)}. "
                "Oddiy matn formatida qayta yuborildi"
            )
            save_state(state)
            continue
        if not result.retryable or attempt >= FINAL_DELIVERY_ATTEMPTS:
            break

        delay = retry_delay_seconds(result, attempt)
        remaining_budget = max(0, retry_deadline - time.monotonic())
        if delay > remaining_budget:
            state["telegram_notification_warning"] = (
                f"{telegram_result_summary(result)}. Telegram {delay} soniya kutishni "
                "so'radi; CI bloklanmasligi uchun qayta urinish to'xtatildi"
            )
            save_state(state)
            break
        state["telegram_notification_warning"] = (
            f"{telegram_result_summary(result)}. {delay} soniyadan keyin "
            f"qayta urinish {attempt + 1}/{FINAL_DELIVERY_ATTEMPTS}"
        )
        save_state(state)
        time.sleep(delay)

    return last_result, len(errors), errors, plain


def extract_message_id(result):
    data = result.data if result and result.ok else None
    message = data.get("result") if isinstance(data, dict) else None
    if isinstance(message, dict) and isinstance(message.get("message_id"), int):
        return message["message_id"]
    return None


def delivery_payload(state, *, status, method, attempts, errors):
    last_error = errors[-1] if errors else None
    retry_at = (
        now_tashkent() + timedelta(seconds=last_error.retry_after)
        if last_error is not None and last_error.retry_after
        else None
    )
    return {
        "suite": target_label(str(state.get("target") or "all")),
        "test_result": str(state.get("result") or ""),
        "run_url": str(state.get("run_url") or ""),
        "status": status,
        "method": method,
        "attempts": attempts,
        "recovered": bool(
            errors
            and status in {"recovered", "fallback_sent", "sent_new"}
        ),
        "error": (
            {
                "category": last_error.category,
                "error_code": last_error.error_code,
                "description": last_error.description,
                "retry_after": last_error.retry_after,
                "retry_at": retry_at.isoformat(timespec="seconds") if retry_at else "",
            }
            if last_error is not None
            else None
        ),
        "updated_at": now_tashkent().isoformat(timespec="seconds"),
    }


def write_delivery_status(state, delivery):
    state["telegram_delivery"] = delivery
    DELIVERY_FILE.parent.mkdir(parents=True, exist_ok=True)
    DELIVERY_FILE.write_text(
        json.dumps(delivery, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    status = str(delivery.get("status") or "unknown")
    error = delivery.get("error")
    error = error if isinstance(error, dict) else {}
    detail = sanitize_telegram_error(error.get("description"))
    summary_path = env_value("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary_file:
            summary_file.write("\n### Telegram notification\n\n")
            summary_file.write(f"- Delivery: `{status}`\n")
            summary_file.write(f"- Method: `{delivery.get('method') or 'none'}`\n")
            summary_file.write(f"- Attempts: `{delivery.get('attempts') or 0}`\n")
            if detail:
                summary_file.write(f"- Error: `{detail}`\n")

    if status in {"failed", "disabled"} or delivery.get("recovered"):
        warning = detail or status
        print(
            f"::warning title=Telegram notification::{warning}",
            file=sys.stderr,
        )


def deliver_final(state):
    if not telegram_enabled():
        result = telegram_error_result(
            "sendMessage",
            description="Telegram credentials sozlanmagan",
            category="disabled",
        )
        record_telegram_error(state, result)
        return delivery_payload(
            state,
            status="disabled",
            method="none",
            attempts=0,
            errors=[result],
        )

    all_errors = []
    retry_deadline = time.monotonic() + FINAL_RETRY_WAIT_BUDGET_SECONDS
    message_id = state.get("message_id")
    if message_id:
        result, attempts, errors, _plain = attempt_final_method(
            state,
            "editMessageText",
            message_id=message_id,
            retry_deadline=retry_deadline,
        )
        all_errors.extend(errors)
        if result and result.ok:
            record_telegram_success(state, render_message(state))
            return delivery_payload(
                state,
                status="recovered" if errors else "delivered",
                method="editMessageText",
                attempts=attempts,
                errors=all_errors,
            )

        state["telegram_notification_warning"] = (
            f"{telegram_result_summary(result)}. "
            "Eski RUNNING xabari yangilanmadi; yangi final xabar yuborildi"
        )
        save_state(state)

    result, _attempts, errors, _plain = attempt_final_method(
        state,
        "sendMessage",
        retry_deadline=retry_deadline,
    )
    all_errors.extend(errors)
    if result and result.ok:
        new_message_id = extract_message_id(result)
        if new_message_id is not None:
            state["message_id"] = new_message_id
        record_telegram_success(state, render_message(state))
        return delivery_payload(
            state,
            status="fallback_sent" if message_id else "sent_new",
            method="sendMessage",
            attempts=len(all_errors) + 1,
            errors=all_errors,
        )

    return delivery_payload(
        state,
        status="failed",
        method="sendMessage",
        attempts=len(all_errors),
        errors=all_errors,
    )


def command_finish(args):
    state = load_state()
    if not state:
        return 0

    passed_values = {"success", "passed", "pass", "ok"}
    result = "PASSED" if str(args.result or "").strip().lower() in passed_values else "FAILED"
    state["result"] = result
    state["status"] = ""
    state["current"] = ""
    state["current_group"] = ""

    now = now_tashkent()
    state["finished_at"] = now.strftime("%Y-%m-%d %H:%M:%S UZT")
    state["finished_at_utc"] = _utc_now_text()
    state["finished_clock"] = now.strftime("%H:%M:%S")
    started_epoch = state.get("started_epoch")
    if isinstance(started_epoch, (int, float)):
        state["duration"] = format_duration(time.time() - started_epoch)

    if args.run_url:
        state["run_url"] = args.run_url
    if args.run_code:
        state["run_code"] = args.run_code

    summary = (args.summary or "").strip() or derive_summary(state)
    state["summary"] = summary

    if result == "FAILED":
        enrich_failed_result_from_summary(state)
    sync_summary_metrics(state)

    state.pop("ai_analysis", None)
    ai_analysis = read_ai_analysis()
    if ai_analysis:
        state["ai_analysis"] = ai_analysis

    save_state(state)
    delivery = deliver_final(state)
    write_delivery_status(state, delivery)
    save_state(state)
    return 0


def command_delete(_args):
    state = load_state()
    message_id = state.get("message_id")
    if message_id and telegram_enabled():
        telegram_request(
            "deleteMessage",
            {
                "chat_id": env_value("TELEGRAM_CHAT_ID"),
                "message_id": str(message_id),
            },
        )
    STATE_FILE.unlink(missing_ok=True)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Telegram progress message helper for GitHub Actions smoke runs.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--server", required=True)
    start.add_argument("--target", required=True)
    start.add_argument(
        "--status",
        default="Python kutubxonalari o‘rnatilmoqda",
    )
    start.add_argument("--message-id", default="")

    update = subparsers.add_parser("update")
    update.add_argument("--status", default="")
    update.add_argument("--current")

    run = subparsers.add_parser("run")
    run.add_argument("command", nargs=argparse.REMAINDER)

    finish = subparsers.add_parser("finish")
    finish.add_argument("--result", required=True)
    finish.add_argument("--run-url", default="")
    finish.add_argument("--run-code", default="")
    finish.add_argument("--summary", default="")

    subparsers.add_parser("delete")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.action == "start":
        return command_start(args)
    if args.action == "update":
        return command_update(args)
    if args.action == "run":
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        return command_run(args)
    if args.action == "finish":
        return command_finish(args)
    if args.action == "delete":
        return command_delete(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
