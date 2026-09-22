"""Test and Forms counts derived from progress state."""

from __future__ import annotations

import re


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
        "deselected": max(
            statuses.count("DESELECTED"),
            summary_counts["deselected"],
        ),
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


def _result_short_name(item, *, is_forms=False):
    context = _form_context(item)
    if is_forms and context:
        try:
            number = f"{int(context.get('number') or 0):03d}"
        except (TypeError, ValueError):
            number = "—"
        title = str(context.get("title") or "Noma’lum forma").strip()
        title = title.split(" → ")[-1].strip() or "Noma’lum forma"
        return f"{number} · {title}"
    return str(
        item.get("display")
        or item.get("title")
        or item.get("test_id")
        or "unknown"
    ).strip()


def _result_names(state, status, *, is_forms=False):
    names = []
    seen = set()
    for item in state.get("results", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").upper() != status:
            continue
        name = _result_short_name(item, is_forms=is_forms)
        if name and name not in seen:
            names.append(name)
            seen.add(name)
    return names


def _count_line(label, count, noun="", names=None):
    line = f"{label}: {count} ta"
    if noun:
        line += f" {noun}"
    if names:
        line += f" ({', '.join(names)})"
    return line


def _progress_line(completed, total, noun):
    if total:
        percentage = round(completed * 100 / total)
        return f"Jarayon: {completed}/{total} ta {noun} · {percentage}%"
    return f"Jarayon: {completed} ta {noun}"


def first_failed_result(state):
    for item in state.get("results", []):
        if isinstance(item, dict) and item.get("status") == "FAILED":
            return item
    return {}


def _form_context(item):
    context = item.get("form") if isinstance(item, dict) else None
    return context if isinstance(context, dict) else {}


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


def _metric_count(metrics, key):
    try:
        return int(metrics.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def derive_summary(state):
    results = [item for item in state.get("results", []) if isinstance(item, dict)]
    passed = sum(1 for item in results if str(item.get("status")).upper() == "PASSED")
    failed = sum(1 for item in results if str(item.get("status")).upper() == "FAILED")
    parts = [f"{passed} passed"]
    if failed:
        parts.append(f"{failed} failed")
    return ", ".join(parts)
