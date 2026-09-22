"""Start, update, finish and delete actions for the CI CLI."""

from __future__ import annotations

import time

from .environment import env_value, telegram_enabled
from .formatting import _utc_now_text, format_duration, now_tashkent
from .messages import render_message
from .metrics import derive_summary
from .paths import STATE_FILE
from .progress_delivery import (
    deliver_final,
    edit_progress,
    record_telegram_error,
    record_telegram_success,
    telegram_payload,
    telegram_request,
    write_delivery_status,
)
from .progress_state import load_state, save_state
from .summaries import enrich_failed_result_from_summary, read_ai_analysis, sync_summary_metrics


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
