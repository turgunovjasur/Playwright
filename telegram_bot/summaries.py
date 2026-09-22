"""Read deterministic and AI summaries into Telegram progress state."""

from __future__ import annotations

import json

from .formatting import truncate_message
from .paths import AI_SUMMARY_JSON, SYSTEM_SUMMARY_JSON


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
    result = {
        "observed": observed,
        "probable_cause": probable_cause,
        "confidence": str(data.get("confidence") or "low").strip().lower(),
    }
    analyses = data.get("analyses")
    if isinstance(analyses, list):
        analyses = [item for item in analyses if isinstance(item, dict)]
        available = sum(item.get("provider_status") == "ai" for item in analyses)
        result["coverage"] = f"{len(analyses)} ta failed testdan {available} tasi AI bilan tahlil qilindi."
        skipped_limit = sum(item.get("provider_status") == "skipped_limit" for item in analyses)
        if skipped_limit:
            result["coverage"] += f" AI limiti sabab {skipped_limit} ta test tahlil qilinmadi."
        result["cases"] = [{
            "name": str(item.get("name") or "Test")[:160],
            "provider_status": item.get("provider_status"),
            "observed": truncate_message(str(item.get("observed") or ""), 240),
            "probable_cause": truncate_message(str(item.get("probable_cause") or ""), 240),
            "confidence": str(item.get("confidence") or "low").lower(),
            "availability_note": str(item.get("availability_note") or "AI javobi olinmadi.")[:180],
        } for item in analyses[:3]]
        result["remaining_cases"] = max(0, len(analyses) - 3)
    return result
