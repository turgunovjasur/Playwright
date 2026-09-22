"""CI progress and final message composition with bounded HTML."""

from __future__ import annotations

import html
import re
import time

from .constants import AI_CONFIDENCE_LABELS, MAX_MESSAGE_LENGTH, TASHKENT_TZ
from .formatting import (
    _clock_text,
    format_duration,
    server_host,
    target_label,
    target_suite_label,
    truncate_message,
)
from .metrics import _count_line, _metric_count, _progress_line, _result_metrics, _result_names
from .progress_details import failed_block, final_coverage_lines, forms_progress_lines


def title_line(state):
    name = f"{target_label(str(state.get('target') or 'all'))} CI"
    result = str(state.get("result") or "").upper()
    if result == "PASSED":
        return f"✅ {name} — PASSED"
    if result == "FAILED":
        return f"❌ {name} — FAILED"
    return f"🟡 {name} — RUNNING"


def _finished_time_lines(state):
    start_utc = state.get("started_at_utc")
    finish_utc = state.get("finished_at_utc")
    lines = []
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


def _progress_time_lines(state):
    start_clock = _clock_text(
        state.get("started_at_utc"),
        TASHKENT_TZ,
    ) or str(state.get("started_clock") or "").strip()
    lines = []
    if start_clock:
        lines.append(f"Vaqt: {start_clock} UZT da boshlangan")
    started_epoch = state.get("started_epoch")
    if isinstance(started_epoch, (int, float)):
        lines.append(
            f"Davomiylik: {format_duration(time.time() - started_epoch)}"
        )
    run_code = str(state.get("run_code") or "").strip()
    target = str(state.get("target") or "").strip().lower()
    if run_code and run_code != "not found" and target != "forms":
        lines.append(f"Test data kodi: {run_code}")
    return lines


def _final_result_lines(state):
    metrics = _result_metrics(state)
    result = str(state.get("result") or "").upper()
    is_forms = str(state.get("target") or "").strip().lower() == "forms"
    noun = "forma" if is_forms else "test"
    completed = str(metrics["completed"])
    if metrics["total"] and metrics["total"] != metrics["completed"]:
        completed = f"{metrics['completed']}/{metrics['total']}"
    action = "Tekshirildi" if is_forms else "Yakunlandi"
    deselected_names = _result_names(state, "DESELECTED", is_forms=is_forms)
    lines = [f"{action}: {completed} ta {noun}"]
    if result == "PASSED":
        lines.append(_count_line("Passed", metrics["passed"], noun))
        lines.append(_count_line("Skipped", metrics["skipped"]))
        if metrics["deselected"]:
            lines.append(
                _count_line(
                    "Tanlanmagan",
                    metrics["deselected"],
                    names=deselected_names,
                )
            )
        lines.append("Xatolik aniqlanmadi")
        return lines

    lines.append(_count_line("Passed", metrics["passed"], noun))
    lines.append(
        _count_line(
            "Failed",
            metrics["failed_total"],
            noun if is_forms else "",
        )
    )
    lines.append(_count_line("Skipped", metrics["skipped"]))
    if metrics["deselected"]:
        lines.append(
            _count_line(
                "Tanlanmagan",
                metrics["deselected"],
                names=deselected_names,
            )
        )
    return lines


def _generic_progress_lines(state):
    metrics = _result_metrics(state)
    lines = []
    test_started_epoch = state.get("test_started_epoch")
    if not isinstance(test_started_epoch, (int, float)):
        status = str(state.get("status") or "").strip()
        if status:
            lines.append(f"Bosqich: {status}")
        return lines

    total = _metric_count(state, "current_test_total")
    lines.extend(
        [
            _progress_line(metrics["completed"], total, "test"),
            _count_line("Passed", metrics["passed"], "test"),
            _count_line("Failed", metrics["failed_total"], "test"),
            _count_line("Skipped", metrics["skipped"]),
        ]
    )
    if metrics["deselected"]:
        lines.append(
            _count_line(
                "Tanlanmagan",
                metrics["deselected"],
                names=_result_names(state, "DESELECTED"),
            )
        )
    if not metrics["failed_total"]:
        lines.append("Hozirgacha xatolik aniqlanmadi")
    current = str(state.get("current") or "").strip()
    if current:
        current = re.sub(r"^(\d+)\s*-\s*", r"\1 · ", current)
        lines.extend(["", "Hozir tekshirilmoqda:", current])
    return lines


def render_html_message(
    main_lines,
    expandable_sections=None,
    footer_lines=None,
    footer_links=None,
):
    main = "\n".join(str(line) for line in main_lines).strip()
    expandables = []
    for heading, section_lines in expandable_sections or []:
        heading = str(heading or "").strip()
        content = "\n".join(str(line) for line in section_lines or []).strip()
        if heading and content:
            expandables.append((heading, content))
    footer = "\n".join(str(line) for line in (footer_lines or [])).strip()
    links = [
        (str(label).strip(), str(url).strip())
        for label, url in (footer_links or [])
        if str(label).strip() and str(url).strip()
    ]

    footer_visible_length = len(footer) + sum(
        len(label) + len(url) + 2 for label, url in links
    )
    section_transitions = len(expandables) + int(bool(footer or links))
    separators = 2 * section_transitions
    headings_length = sum(len(heading) for heading, _content in expandables)
    minimum_expandable_length = 3 * len(expandables)
    fixed_length = (
        len(main)
        + footer_visible_length
        + headings_length
        + separators
    )
    if fixed_length + minimum_expandable_length > MAX_MESSAGE_LENGTH:
        main = truncate_message(
            main,
            limit=max(
                3,
                MAX_MESSAGE_LENGTH
                - footer_visible_length
                - headings_length
                - separators
                - minimum_expandable_length,
            ),
        )
        fixed_length = (
            len(main)
            + footer_visible_length
            + headings_length
            + separators
        )

    remaining = max(0, MAX_MESSAGE_LENGTH - fixed_length)
    fitted_expandables = []
    for index, (heading, content) in enumerate(expandables):
        remaining_sections = len(expandables) - index
        limit = max(3, remaining // remaining_sections)
        fitted = truncate_message(content, limit=limit)
        fitted_expandables.append((heading, fitted))
        remaining = max(0, remaining - len(fitted))

    sections = [html.escape(main, quote=False)]
    for heading, content in fitted_expandables:
        sections.append(
            f"<b>{html.escape(heading, quote=False)}</b>\n"
            f"<blockquote expandable>{html.escape(content, quote=False)}</blockquote>"
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
        lines.extend(["", *_finished_time_lines(state)])
        run_code = str(state.get("run_code") or "").strip()
        if run_code and run_code != "not found" and target != "forms":
            lines.append(f"Test data kodi: {run_code}")
        lines.extend(["", *_final_result_lines(state)])
        if target in {"setup-forms", "setup-a2-admin"}:
            lines.extend(final_coverage_lines(state))

    expandables = []
    if not finished:
        lines.extend(["", *_progress_time_lines(state), ""])
        forms_lines = forms_progress_lines(state)
        lines.extend(forms_lines or _generic_progress_lines(state))
    elif result == "FAILED":
        details = failed_block(state)
        if details:
            expandables.append(("Xato tafsiloti:", details))

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
            ai_lines = [
                f"Kuzatilgan: {observed}",
                "",
                f"Ehtimoliy sabab: {probable_cause}",
                "",
                f"Ishonch darajasi: {confidence}",
            ]
            cases = ai.get("cases")
            if isinstance(cases, list) and cases:
                ai_lines = [ai["coverage"]]
                for case in cases:
                    if case["provider_status"] == "ai":
                        label = AI_CONFIDENCE_LABELS.get(case["confidence"], "past")
                        outcome = f"AI tahlil qilindi; ishonch darajasi: {label}"
                    else:
                        outcome = f"Tahlil olinmadi: {case['availability_note']}"
                    ai_lines.extend(["", f"{case['name']} — {outcome}"])
                if ai.get("remaining_cases"):
                    ai_lines.extend(["", f"Yana {ai['remaining_cases']} ta testning AI holati Allure hisobotida."])
                # Limitga sig'dirishda avval qisqa holatlar, keyin ixtiyoriy izoh qoladi.
                ai_lines.extend(["", "To'liq izohlar Allure hisobotida."])
                for case in cases:
                    if case["provider_status"] == "ai":
                        ai_lines.extend([
                            "", case["name"],
                            f"Kuzatilgan: {case['observed']}", "",
                            f"Ehtimoliy sabab: {case['probable_cause']}",
                        ])
            expandables.append(
                (
                    "AI tahlili:",
                    ai_lines,
                )
            )

    return render_html_message(lines, expandables, footer, footer_links)


def render_plain_message(state):
    rendered = render_message(state)
    rendered = re.sub(
        r'<a href="([^"]+)">([^<]+)</a>',
        lambda match: f"{match.group(2)}: {match.group(1)}",
        rendered,
    )
    return html.unescape(re.sub(r"<[^>]+>", "", rendered))
