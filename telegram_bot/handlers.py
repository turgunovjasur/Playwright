"""Telegram commands, callback routing and password authorization."""

from __future__ import annotations

import hmac
import re
import requests
import sys

from .bot_client import TelegramAPIError
from .bot_delivery import edit_or_send_message, safe_delete_message, safe_delete_transient_messages
from .bot_messages import (
    busy_run_text,
    help_text,
    server_keyboard,
    start_text,
    status_text,
    stop_result_text,
)
from .constants import ACTIVE_WORKFLOW_RUN_STATUSES, MANUAL_SUITE, MANUAL_SUITE_LABEL
from .models import PendingRun, PendingStop, RunRequest
from .runs import find_busy_run, start_run


def show_stop_prompt(
    telegram, chat_id, pending_stop_store, pending_key, *,
    run_id=None, attempt=None, progress_message_id=None,
):
    prompt = (
        "🔒 Barcha active CI runlarini to'xtatish uchun parolni yuboring.\n"
        "Bu queued va running workflow runlarning barchasini bekor qiladi."
    )
    if run_id is not None:
        prompt = f"🔒 #{run_id} test runini to‘xtatish uchun parolni yuboring."
    prompt_message_id = telegram.send_message(chat_id, prompt)
    pending_stop_store.set(
        pending_key,
        PendingStop(prompt_message_id, run_id, attempt, progress_message_id),
    )


def stop_progress_run(telegram, github, chat_id, pending):
    try:
        run = github.get_run(pending.run_id)
        if (
            run.get("run_attempt") != pending.attempt
            or run.get("status") not in ACTIVE_WORKFLOW_RUN_STATUSES
        ):
            edit_or_send_message(telegram, chat_id, pending.prompt_message_id, "Bu urinish endi faol emas.")
            return
        github.force_cancel_run(pending.run_id)
    except requests.RequestException as exc:
        if exc.response is not None and exc.response.status_code == 409:
            message = "GitHub Actions bu runni hozir to‘xtata olmaydi. Holatini /status orqali ko‘ring."
        else:
            message = "GitHub Actions bilan bog‘lanishda xato. Run holatini /status orqali tekshiring."
    else:
        message = f"⏹ #{pending.run_id} uchun to‘xtatish so‘rovi GitHub Actions’ga yuborildi."
        try:
            telegram.edit_message(chat_id, pending.progress_message_id, message)
        except TelegramAPIError:
            pass  # The password prompt can still carry the acknowledgement.
        else:
            safe_delete_message(telegram, chat_id, pending.prompt_message_id)
            return
    edit_or_send_message(telegram, chat_id, pending.prompt_message_id, message)


def verify_stop_password(
    telegram,
    github,
    config,
    active_store,
    pending_stop_store,
    chat_id,
    text,
    user_message_id,
    pending_key,
):
    pending = pending_stop_store.get(pending_key)
    if pending is None:
        return

    safe_delete_message(telegram, chat_id, user_message_id)
    if not password_matches(config.run_password, text):
        edit_or_send_message(
            telegram,
            chat_id,
            pending.prompt_message_id,
            "❌ Parol noto'g'ri. Qaytadan parolni yuboring.",
        )
        return

    pending_stop_store.clear(pending_key)
    if pending.run_id is not None:
        stop_progress_run(telegram, github, chat_id, pending)
        return
    edit_or_send_message(
        telegram,
        chat_id,
        pending.prompt_message_id,
        "Active CI runlar to'xtatilmoqda...",
    )
    local_active = active_store.get()
    try:
        result = github.force_cancel_all_active_runs()
    except Exception as exc:
        print(
            f"GitHub stop request failed: {exc.__class__.__name__}",
            file=sys.stderr,
        )
        edit_or_send_message(
            telegram,
            chat_id,
            pending.prompt_message_id,
            "❌ CI runlarini GitHub'da to'xtatib bo'lmadi. Iltimos, keyinroq qayta urinib ko'ring.",
        )
        return

    if (
        local_active is not None
        and local_active.workflow_run.run_id in result.cancelled_run_ids
    ):
        active_store.clear(local_active.workflow_run.run_id)
        safe_delete_transient_messages(telegram, local_active)
        edit_or_send_message(
            telegram,
            local_active.chat_id,
            local_active.status_message_id,
            f"⚪ {local_active.request.suite_label} CI run uchun "
            "force-cancel yuborildi.\n"
            f"Run: {local_active.workflow_run.html_url}",
        )

    edit_or_send_message(
        telegram,
        chat_id,
        pending.prompt_message_id,
        stop_result_text(result),
    )


def show_run_start(
    telegram,
    github,
    chat_id,
    config,
    active_store,
):
    try:
        workflow_run, local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.send_message(chat_id, "Test holatini tekshirib bo'lmadi. Iltimos, qayta urinib ko'ring.")
        return
    if workflow_run is not None:
        message_id = telegram.send_message(chat_id, busy_run_text(workflow_run))
        if local_active is not None:
            active_store.add_status_message(workflow_run.run_id, message_id)
        return
    telegram.send_message(
        chat_id, f"{MANUAL_SUITE_LABEL} uchun serverni tanlang.",
        reply_markup=server_keyboard(config, MANUAL_SUITE),
    )


def password_matches(expected, provided):
    return hmac.compare_digest(expected.encode(), (provided or "").strip().encode())


def verify_run_password(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    chat_id,
    text,
    user_message_id,
    dispatch_lock,
    pending_key,
):
    """Parol kutilayotgan chatda kelgan matnni parol sifatida tekshiradi."""
    pending = pending_store.get(pending_key)
    if pending is None:
        return

    # Parol xabari chatda qolmasligi uchun foydalanuvchi yuborgan matnni o'chiramiz.
    safe_delete_message(telegram, chat_id, user_message_id)

    try:
        workflow_run, _local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.edit_message(
            chat_id,
            pending.prompt_message_id,
            "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
        )
        pending_store.clear(pending_key)
        return

    if workflow_run is not None:
        pending_store.clear(pending_key)
        telegram.edit_message(chat_id, pending.prompt_message_id, busy_run_text(workflow_run))
        return

    if password_matches(config.run_password, text):
        pending_store.clear(pending_key)
        start_run(telegram, github, chat_id, pending.prompt_message_id, pending.request, active_store, dispatch_lock)
    else:
        telegram.edit_message(
            chat_id,
            pending.prompt_message_id,
            "❌ Parol noto'g'ri. Qaytadan parolni yuboring yoki /run bilan boshidan boshlang.",
        )


def handle_message(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    pending_stop_store,
    chat_id,
    text,
    message_id,
    dispatch_lock,
    sender_id=None,
):
    is_command = text.startswith("/")
    pending_key = (chat_id, sender_id)

    if pending_stop_store.has(pending_key) and not is_command:
        verify_stop_password(
            telegram,
            github,
            config,
            active_store,
            pending_stop_store,
            chat_id,
            text,
            message_id,
            pending_key,
        )
        return

    # Parol kutilayotgan bo'lsa va bu buyruq bo'lmasa — matnni parol urinishi deb qaraymiz.
    if pending_store.has(pending_key) and not is_command:
        verify_run_password(telegram, github, config, active_store, pending_store, chat_id, text, message_id, dispatch_lock, pending_key)
        return

    # Buyruq kelsa, oldingi parol kutish holatini bekor qilamiz.
    if is_command:
        pending_store.clear(pending_key)
        pending_stop_store.clear(pending_key)

    command = text.split(maxsplit=1)[0].split("@", 1)[0].lower() if text else ""
    if command == "/start":
        telegram.send_message(chat_id, start_text(config))
        return
    if command == "/help":
        telegram.send_message(chat_id, help_text())
        return
    if command == "/servers":
        lines = [config.servers[key] for key in sorted(config.allowed_server_keys)]
        telegram.send_message(chat_id, "Mavjud serverlar:\n" + "\n".join(lines))
        return
    if command == "/status":
        try:
            message = status_text(telegram, github)
        except requests.RequestException as exc:
            print(
                f"GitHub status request failed: {exc.__class__.__name__}",
                file=sys.stderr,
            )
            message = (
                "❌ CI statusini GitHub'dan olib bo'lmadi. "
                "Iltimos, keyinroq qayta urinib ko'ring."
            )
        telegram.send_message(chat_id, message)
        return
    if command == "/run":
        show_run_start(telegram, github, chat_id, config, active_store)
        return
    if command == "/stop":
        show_stop_prompt(telegram, chat_id, pending_stop_store, pending_key)
        return

    telegram.send_message(
        chat_id,
        "Noto'g'ri command. /run, /stop, /status yoki /help yuboring.",
    )


def handle_callback(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    pending_stop_store,
    callback,
):
    callback_id = str(callback.get("id", ""))
    data = str(callback.get("data", ""))
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    message_id = message.get("message_id")
    pending_key = (chat_id, (callback.get("from") or {}).get("id"))

    if not isinstance(message_id, int):
        telegram.answer_callback(callback_id)
        return

    if data.startswith("stop:"):
        rows = (message.get("reply_markup") or {}).get("inline_keyboard", [])
        target = re.fullmatch(r"stop:([0-9]+):([0-9]+)", data)
        if not target or not any(button.get("callback_data") == data for row in rows for button in row):
            telegram.answer_callback(callback_id, "Tugma endi faol emas")
            return
        telegram.answer_callback(callback_id, "Parol kerak")
        pending_store.clear(pending_key)
        show_stop_prompt(
            telegram, chat_id, pending_stop_store, pending_key,
            run_id=int(target[1]), attempt=int(target[2]), progress_message_id=message_id,
        )
        return

    try:
        workflow_run, local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.answer_callback(callback_id, "Statusni tekshirib bo'lmadi")
        telegram.edit_message(
            chat_id,
            message_id,
            "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
        )
        return

    if workflow_run is not None:
        telegram.answer_callback(callback_id, "Test jarayonda")
        active_message_id = telegram.send_message(chat_id, busy_run_text(workflow_run))
        if local_active is not None:
            active_store.add_status_message(workflow_run.run_id, active_message_id)
        return

    if data.startswith("server:"):
        parts = data.split(":")
        if len(parts) != 3:
            telegram.answer_callback(callback_id, "Unknown server action")
            return
        _action, suite_key, server_key = parts
        if suite_key != MANUAL_SUITE:
            telegram.answer_callback(callback_id, "Unknown suite")
            return
        if server_key not in config.allowed_server_keys or server_key not in config.servers:
            telegram.answer_callback(callback_id, "Server not allowed")
            return
        telegram.answer_callback(callback_id, "Parol kerak")
        request = RunRequest(
            suite_key=suite_key,
            server_key=server_key,
        )
        pending_stop_store.clear(pending_key)
        pending_store.set(pending_key, PendingRun(request=request, prompt_message_id=message_id))
        telegram.edit_message(
            chat_id,
            message_id,
            (
                f"🔒 {MANUAL_SUITE_LABEL} · {config.servers[server_key]}\n\n"
                "Testni run qilish uchun parolni yuboring:"
            ),
        )
        return

    telegram.answer_callback(callback_id, "Unknown action")
