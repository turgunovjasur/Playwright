from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "test-results" / "telegram-progress.json"
SYSTEM_SUMMARY_JSON = ROOT / "test-results" / "system-summary.json"
AI_SUMMARY_JSON = ROOT / "test-results" / "ai-summary.json"
EVENT_PREFIX = "SMARTUP_PROGRESS "
MAX_MESSAGE_LENGTH = 3900

TASHKENT_TZ = timezone(timedelta(hours=5))
TARGET_LABELS = {
    "all": "All",
    "setup": "Setup",
    "setup-report": "Setup + Report",
    "setup-a2-admin": "Setup + A2 Admin Forms",
    "setup-forms": "Setup + Forms",
    "company": "Company",
    "groups": "Groups",
    "group-report": "Report Group",
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


def env_value(name):
    return os.getenv(name, "").strip()


def telegram_enabled():
    return bool(env_value("TELEGRAM_BOT_TOKEN") and env_value("TELEGRAM_CHAT_ID"))


def telegram_request(method, payload):
    if not telegram_enabled():
        return None
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
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"Telegram progress warning: {exc}", file=sys.stderr)
        return None
    if not isinstance(data, dict) or not data.get("ok"):
        print(f"Telegram progress warning: {data}", file=sys.stderr)
        return None
    return data


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
        return f"{minutes}m {secs}s"
    return f"{secs}s"


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


def failed_block(state):
    failed = first_failed_result(state)
    if not failed:
        return []

    group = str(failed.get("group") or "").strip()
    test_name = str(failed.get("display") or failed.get("title") or failed.get("inner_test") or "").strip()
    test_context = " → ".join(value for value in (group, test_name) if value)
    step = str(failed.get("failed_step") or failed.get("step") or "").strip()
    if step == test_name:
        step = ""

    error_message = first_message_line(failed.get("message"))

    form_issues = failed.get("form_issues")
    if isinstance(form_issues, list) and form_issues:
        status_labels = {
            "OPENED_WITH_DEFECT": "nuqson bilan ochildi",
            "NOT_OPENED": "ochilmadi",
            "TEST_BLOCKED": "test bloklandi",
            "NOT_CHECKED": "tekshirilmadi",
        }
        lines = ["", f"❌ Muammoli formalar: {len(form_issues)} ta"]
        for index, issue in enumerate(form_issues, start=1):
            if not isinstance(issue, dict):
                continue
            try:
                number = f"{int(issue.get('number')):03d}"
            except (TypeError, ValueError):
                number = str(issue.get("number") or "—")
            title = str(issue.get("title") or "unknown").strip()
            status = str(issue.get("status") or "").upper()
            status_text = status_labels.get(status, status or "xato")
            lines.append(f"{index}. {number} - {title} — {status_text}")
            reason = str(issue.get("reason") or issue.get("reason_code") or "").strip()
            detail = first_message_line(issue.get("detail"))
            if reason:
                lines.append(f"   Sabab: {reason}")
            if detail and detail != reason:
                lines.append(f"   Texnik: {detail}")
        if test_context:
            lines.extend(["", f"Test: {test_context}"])
        location = str(failed.get("location") or "").strip()
        if location:
            lines.append(f"Kod: {location}")
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
        ("Test", test_context),
        ("Allure step", step),
        ("Sahifa", failed.get("before_page")),
        ("Amal", failed.get("action")),
        ("Kutilgan", failed.get("expected")),
        ("Haqiqiy", failed.get("actual")),
        ("UI xabari", failed.get("ui_error")),
        ("Auth diagnostika", failed.get("auth_diagnostic")),
        ("Xato", error_message),
        ("Texnik", " · ".join(technical)),
        ("Kod", failed.get("location")),
    ]
    lines = ["", "❌ Xato tafsiloti:"]
    for label, value in pairs:
        text = str(value or "").strip()
        if text:
            lines.append(f"{label}: {text}")
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
        setup_parts = [f"✅ {setup_statuses.count('PASSED')}"]
        if setup_statuses.count("FAILED"):
            setup_parts.append(f"❌ {setup_statuses.count('FAILED')}")
        if setup_statuses.count("SKIPPED"):
            setup_parts.append(f"⏭ {setup_statuses.count('SKIPPED')}")
        lines.append(
            f"⚙️ Setup: {len(setup_results)} qadam · " + " · ".join(setup_parts)
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
        lines.append(f"🧾 Forms: ✅ {passed}/{checked} muvaffaqiyatli")

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


def render_html_message(main_lines, expandable_lines=None, footer_lines=None):
    main = "\n".join(str(line) for line in main_lines).strip()
    expandable = "\n".join(str(line) for line in (expandable_lines or [])).strip()
    footer = "\n".join(str(line) for line in (footer_lines or [])).strip()

    separators = 2 * sum(bool(part) for part in (expandable, footer))
    fixed_length = len(main) + len(footer) + separators
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
    if footer:
        sections.append(html.escape(footer, quote=False))
    return "\n\n".join(section for section in sections if section)


def render_message(state):
    finished = bool(state.get("result"))
    lines = [title_line(state)]

    started_at = str(state.get("started_at") or "").strip()
    if finished:
        start_clock = str(state.get("started_clock") or "").strip()
        finish_clock = str(state.get("finished_clock") or "").strip()
        duration = str(state.get("duration") or "").strip()
        bits = []
        if start_clock and finish_clock:
            bits.append(f"{start_clock}–{finish_clock}")
        elif started_at:
            bits.append(started_at)
        if duration:
            bits.append(duration)
        if bits:
            lines.append("🕒 " + " · ".join(bits))
    elif started_at:
        lines.append(f"🕒 Started: {started_at}")

    lines.append(
        f"🖥 {server_host(str(state.get('server') or ''))}"
        f" · {target_label(str(state.get('target') or 'all'))}"
    )

    if finished:
        summary = str(state.get("summary") or "").strip()
        if summary:
            lines.append(f"🧪 Pytest cases: {summary}")
    else:
        status = str(state.get("status") or "").strip()
        if status:
            lines.append(f"Status: {status}")

    if finished:
        lines.extend(final_coverage_lines(state))

    expandable = []
    if not finished:
        lines.extend(grouped_result_lines(state))
    elif str(state.get("result") or "").upper() == "FAILED":
        expandable.extend(grouped_result_lines(state))
        expandable.extend(failed_block(state))

    footer = []
    if finished:
        run_code = str(state.get("run_code") or "").strip()
        run_url = str(state.get("run_url") or "").strip()
        if run_code and run_code != "not found":
            footer.append(f"🆔 Code: {run_code}")
        if run_url:
            footer.append(f"🔗 {run_url}")
        ai = str(state.get("ai_conclusion") or "").strip()
        if ai and str(state.get("result") or "").upper() == "FAILED":
            expandable.extend(["", "🤖 AI:", ai])

    return render_html_message(lines, expandable, footer)


def edit_progress(state):
    message_id = state.get("message_id")
    if not message_id:
        return
    telegram_request(
        "editMessageText",
        {
            "chat_id": env_value("TELEGRAM_CHAT_ID"),
            "message_id": str(message_id),
            "text": render_message(state),
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
    )


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
        "started_at": now.strftime("%Y-%m-%d %H:%M"),
        "started_clock": now.strftime("%H:%M"),
        "started_epoch": time.time(),
    }
    if not telegram_enabled():
        save_state(state)
        return 0

    if args.message_id:
        state["message_id"] = args.message_id
        edit_progress(state)
    else:
        data = telegram_request(
            "sendMessage",
            {
                "chat_id": env_value("TELEGRAM_CHAT_ID"),
                "text": render_message(state),
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
            },
        )
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, dict) and result.get("message_id"):
            state["message_id"] = result["message_id"]
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
    edit_progress(state)
    return 0


def update_from_event(state, event):
    event_name = str(event.get("event") or "")
    display = str(event.get("display") or event.get("title") or event.get("test_id") or "unknown")
    if event_name == "form_result":
        state["status"] = "Forms running"
        state["current"] = display
        state["current_group"] = str(event.get("group") or "Forms group")
        state["form_progress"] = {
            "suite": str(event.get("title") or ""),
            "number": _metric_count(event, "form_number"),
            "total": _metric_count(event, "form_total"),
            "status": str(event.get("form_status") or ""),
            "reason": str(event.get("error_type") or ""),
        }
        return
    if event_name == "started":
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
    }
    state.setdefault("results", []).append(result)
    if event_name in {"passed", "skipped"}:
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
    state["status"] = "Starting tests"
    save_state(state)
    edit_progress(state)
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


def read_ai_conclusion():
    if not AI_SUMMARY_JSON.exists():
        return ""
    try:
        data = json.loads(AI_SUMMARY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(data, dict):
        return ""
    return str(data.get("summary") or "").strip()[:600]


def derive_summary(state):
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    passed = sum(1 for item in results if str(item.get("status")).upper() == "PASSED")
    failed = sum(1 for item in results if str(item.get("status")).upper() == "FAILED")
    parts = [f"{passed} passed"]
    if failed:
        parts.append(f"{failed} failed")
    return ", ".join(parts)


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
    state["finished_at"] = now.strftime("%Y-%m-%d %H:%M")
    state["finished_clock"] = now.strftime("%H:%M")
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

    ai_conclusion = read_ai_conclusion()
    if ai_conclusion:
        state["ai_conclusion"] = ai_conclusion

    save_state(state)
    edit_progress(state)
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
    start.add_argument("--status", default="Installing requirements")
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
