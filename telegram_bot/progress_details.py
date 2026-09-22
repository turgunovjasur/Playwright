"""Forms navigation, coverage and failure sections for CI messages."""

from __future__ import annotations

from datetime import timezone

from .constants import GROUP_ORDER, OPERATIONAL_FILIAL_PLACEHOLDER, STATUS_MARK, TASHKENT_TZ
from .formatting import _clock_text, first_message_line
from .metrics import (
    _count_line,
    _failed_result_entries,
    _form_context,
    _forms_results,
    _forms_total,
    _metric_count,
    _progress_line,
    _result_metrics,
    _result_names,
)


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


def _form_context_lines(context):
    try:
        number = f"{int(context.get('number') or 0):03d}"
    except (TypeError, ValueError):
        number = "—"
    title = str(context.get("title") or "Noma’lum forma").strip()
    short_title = title.split(" → ")[-1].strip() or "Noma’lum forma"
    lines = [f"{number} · {short_title}"]
    user_trace = " → ".join(
        str(value).strip()
        for value in (context.get("navbar"), context.get("menu"), title)
        if str(value or "").strip()
    )
    if user_trace:
        lines.append(f"User trace: {user_trace}")
    filial = _form_filial_label(context)
    if filial:
        lines.append(f"Filial: {filial}")
    return lines


def _form_filial_label(context):
    filial = str(context.get("filial") or "").strip()
    if filial == OPERATIONAL_FILIAL_PLACEHOLDER:
        return "Operatsion filial"
    return filial


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
        _progress_line(completed, total, "forma"),
        _count_line("Passed", metrics["passed"], "forma"),
        _count_line("Failed", metrics["failed_total"], "forma"),
        _count_line("Skipped", metrics["skipped"]),
    ]
    if metrics["deselected"]:
        lines.append(
            _count_line(
                "Tanlanmagan",
                metrics["deselected"],
                names=_result_names(state, "DESELECTED", is_forms=True),
            )
        )
    if not metrics["failed_total"]:
        lines.append("Hozirgacha xatolik aniqlanmadi")

    if include_current and current:
        lines.extend(["", "Hozir tekshirilmoqda:"])
        lines.extend(_form_context_lines(current))
    return lines


def _failure_time_text(failed):
    timestamp = failed.get("failure_at_utc") or failed.get("occurred_at_utc")
    local_text = _clock_text(timestamp, TASHKENT_TZ)
    utc_text = _clock_text(timestamp, timezone.utc)
    if not local_text:
        return "aniqlanmadi"
    return f"{local_text} UZT · {utc_text} UTC"


def _append_spaced_field(lines, label, value):
    if lines:
        lines.append("")
    text = str(value or "").strip() or "aniqlanmadi"
    lines.append(f"{label}: {text}")


def _form_user_trace(failed_form, issue):
    if isinstance(issue, dict):
        track = str(issue.get("track") or "").strip()
        if track:
            return track
        label = str(issue.get("label") or "").strip()
    else:
        label = ""
    tail = label or str(failed_form.get("title") or "").strip()
    return " → ".join(
        str(value).strip()
        for value in (
            failed_form.get("navbar"),
            failed_form.get("menu"),
            tail,
        )
        if str(value or "").strip()
    )


def _failed_entry_lines(failed, issue, *, is_forms):
    lines = []
    failed_form = _form_context(failed)
    step = str(failed.get("failed_step") or failed.get("step") or "").strip()
    error_type = str(failed.get("error_type") or "").strip()
    reason = str(failed.get("reason") or "").strip()

    if is_forms:
        issue = issue if isinstance(issue, dict) else {}
        issue_number = failed_form.get("number") or issue.get("number")
        try:
            number = f"{int(issue_number):03d}"
        except (TypeError, ValueError):
            number = str(issue_number or "—")
        title = str(issue.get("title") or failed_form.get("title") or "Noma’lum forma").strip()
        title = title.split(" → ")[-1].strip() or "Noma’lum forma"
        _append_spaced_field(lines, "Forma nomi", f"{number} · {title}")
        _append_spaced_field(lines, "User trace", _form_user_trace(failed_form, issue))
        _append_spaced_field(lines, "Filial", _form_filial_label(failed_form))
        step = str(issue.get("failed_stage") or step).strip()
        error_type = str(
            error_type
            or issue.get("reason_code")
            or issue.get("status")
            or ""
        ).strip()
        reason = str(
            issue.get("reason")
            or issue.get("detail")
            or reason
            or first_message_line(failed.get("message"))
        ).strip()
    else:
        test_name = str(
            failed.get("display")
            or failed.get("title")
            or failed.get("inner_test")
            or ""
        ).strip()
        _append_spaced_field(lines, "Test nomi", test_name)
        reason = reason or first_message_line(failed.get("message"))

    _append_spaced_field(lines, "Bosqich", step)
    _append_spaced_field(lines, "Xato turi", error_type)
    _append_spaced_field(lines, "Sabab", reason)
    _append_spaced_field(lines, "Xato vaqti", _failure_time_text(failed))
    return lines


def failed_block(state):
    entries = _failed_result_entries(state)
    lines = []
    is_forms = str(state.get("target") or "").strip().lower() == "forms"
    for failed, issue in entries:
        if lines:
            lines.extend(["", ""])
        lines.extend(_failed_entry_lines(failed, issue, is_forms=is_forms))
    return lines


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
