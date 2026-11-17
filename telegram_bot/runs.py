"""Serialize manual dispatch and monitor active workflow runs."""

from __future__ import annotations

import sys
import threading
import time

from .bot_delivery import safe_delete_transient_messages
from .bot_messages import active_run_text, busy_run_text, report_keyboard
from .constants import STATUS_POLL_ERROR_LIMIT, STATUS_POLL_INTERVAL_SECONDS
from .models import ActiveRun
from .reply_chat import encode_reply_chat


def find_busy_run(github, active_store):
    active = active_store.get()
    if active is not None:
        return active.workflow_run, active
    return github.find_active_run(), None


def start_run(
    telegram,
    github,
    chat_id,
    message_id,
    request,
    active_store,
    dispatch_lock,
):
    with dispatch_lock:
        try:
            busy_run, _local_active = find_busy_run(github, active_store)
        except Exception as exc:
            print(f"GitHub active run check failed: {exc}", file=sys.stderr)
            telegram.edit_message(
                chat_id,
                message_id,
                "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
            )
            return
        if busy_run is not None:
            telegram.edit_message(chat_id, message_id, busy_run_text(busy_run))
            return

        telegram.edit_message(
            chat_id,
            message_id,
            f"{request.suite_label} testi boshlanyapti...",
        )
        try:
            route = encode_reply_chat(telegram.token, chat_id)
            workflow_run = github.dispatch(request, telegram_reply_route=route)
        except Exception as exc:
            telegram.edit_message(chat_id, message_id, f"Testni boshlashda xato: {exc}")
            return

    telegram.edit_message(
        chat_id,
        message_id,
        f"{request.suite_label} run boshlandi: {workflow_run.html_url}",
    )

    if workflow_run.run_id is not None:
        active = ActiveRun(
            chat_id=chat_id,
            request=request,
            workflow_run=workflow_run,
            started_at=time.monotonic(),
            status_message_id=message_id,
        )
        if not active_store.set(active):
            current = active_store.get()
            if current is not None:
                telegram.send_message(chat_id, active_run_text(current))
            return

    if workflow_run.run_id is None:
        telegram.edit_message(chat_id, message_id, f"Run boshlandi, status GitHub linkda: {workflow_run.html_url}")
        return

    thread = threading.Thread(
        target=monitor_run,
        args=(telegram, github, chat_id, workflow_run, active_store),
        daemon=True,
    )
    thread.start()


def monitor_run(
    telegram,
    github,
    chat_id,
    workflow_run,
    active_store,
):
    assert workflow_run.run_id is not None
    status_errors = 0

    while True:
        try:
            status, conclusion, _html_url = github.get_run_status(workflow_run.run_id)
            if status == "completed":
                records = github.delivery_statuses(workflow_run.run_id)
                report = next((item for item in records if item.get("report_url")), {})
                if report.get("status") not in {"delivered", "recovered", "fallback_sent", "sent_new"}:
                    keyboard = report_keyboard(report["report_url"]) if report else None
                    outcome = (conclusion or "unknown").upper()
                    text = f"API setup + Regression · {outcome}\n{workflow_run.html_url}"
                    if not report:
                        text += "\nAllure hisoboti mavjud emas."
                    telegram.send_message(chat_id, text, reply_markup=keyboard)
        except Exception as exc:
            status_errors += 1
            print(
                f"Temporary GitHub status polling error for run {workflow_run.run_id}: {exc}",
                file=sys.stderr,
            )
            if status_errors >= STATUS_POLL_ERROR_LIMIT:
                active = active_store.get()
                active_store.clear(workflow_run.run_id)
                safe_delete_transient_messages(telegram, active)
                telegram.send_message(
                    chat_id,
                    (
                        f"Run statusini {STATUS_POLL_ERROR_LIMIT} marta olishda xato bo'ldi.\n"
                        "Test GitHub Actionsda davom etayotgan bo'lishi mumkin.\n"
                        f"Run: {workflow_run.html_url}"
                    ),
                )
                return
            time.sleep(STATUS_POLL_INTERVAL_SECONDS)
            continue

        status_errors = 0

        if status == "completed":
            active = active_store.get()
            active_store.clear(workflow_run.run_id)
            safe_delete_transient_messages(telegram, active)
            return

        time.sleep(STATUS_POLL_INTERVAL_SECONDS)
