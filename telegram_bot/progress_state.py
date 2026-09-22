"""Persist CI progress and apply incoming test events."""

from __future__ import annotations

import json

from .formatting import _utc_now_text
from .metrics import _metric_count
from .paths import DATA_STORE_JSON, STATE_FILE


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


def sync_run_code_from_data_store(state):
    """Data-store'dagi joriy test kodini Smoke progress state'iga ko'chiradi."""
    target = str(state.get("target") or "").strip().lower()
    if target == "forms" or not DATA_STORE_JSON.exists():
        return
    new_code_targets = {
        "all",
        "setup",
        "setup-group-0",
        "setup-smoke",
        "setup-report",
        "setup-a2-admin",
        "setup-forms",
        "company",
    }
    test_started_epoch = state.get("test_started_epoch")
    if target in new_code_targets and isinstance(test_started_epoch, (int, float)):
        try:
            if DATA_STORE_JSON.stat().st_mtime < test_started_epoch:
                return
        except OSError:
            return
    try:
        data = json.loads(DATA_STORE_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    run_code = str(data.get("code") or "").strip()
    if run_code:
        state["run_code"] = run_code


def update_from_event(state, event):
    event_name = str(event.get("event") or "")
    display = str(event.get("display") or event.get("title") or event.get("test_id") or "unknown")
    occurred_at_utc = str(event.get("occurred_at_utc") or "").strip() or _utc_now_text()
    test_total = _metric_count(event, "test_total")
    if test_total:
        state["current_test_total"] = test_total
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

    if event_name not in {"passed", "failed", "skipped", "deselected"}:
        return

    status = {
        "passed": "PASSED",
        "failed": "FAILED",
        "skipped": "SKIPPED",
        "deselected": "DESELECTED",
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
