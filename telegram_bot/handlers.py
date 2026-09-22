"""Telegram commands, callback routing and password authorization."""

from __future__ import annotations

import hmac
import requests
import sys

from .bot_delivery import edit_or_send_message, safe_delete_message, safe_delete_transient_messages
from .bot_messages import (
    busy_run_text,
    help_text,
    server_keyboard,
    start_text,
    status_text,
    stop_result_text,
    suite_keyboard,
)
from .constants import SUITES
from .models import PendingRun, PendingStop, RunRequest
from .runs import find_busy_run, start_run


def show_stop_prompt(telegram, chat_id, pending_stop_store):
    prompt_message_id = telegram.send_message(
        chat_id,
        (
            "🔒 Barcha active CI runlarini to'xtatish uchun parolni yuboring.\n"
            "Bu queued va running workflow runlarning barchasini bekor qiladi."
        ),
    )
    pending_stop_store.set(
        chat_id,
        PendingStop(prompt_message_id=prompt_message_id),
    )


def verify_stop_password(
    telegram,
    github,
    config,
    active_store,
    pending_stop_store,
    chat_id,
    text,
    user_message_id,
):
    pending = pending_stop_store.get(chat_id)
    if pending is None:
        return

    safe_delete_message(telegram, chat_id, user_message_id)
    if not password_matches(config.run_password, text):
        edit_or_send_message(
            telegram,
            chat_id,
            pending.prompt_message_id,
            "❌ Parol noto'g'ri. Qaytadan parolni yuboring yoki /stop bilan boshidan boshlang.",
        )
        return

    pending_stop_store.clear(chat_id)
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
    telegram.send_message(chat_id, "Qaysi testni run qilamiz?", reply_markup=suite_keyboard())


def password_matches(expected, provided):
    return hmac.compare_digest(expected, (provided or "").strip())


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
):
    """Parol kutilayotgan chatda kelgan matnni parol sifatida tekshiradi."""
    pending = pending_store.get(chat_id)
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
        pending_store.clear(chat_id)
        return

    if workflow_run is not None:
        pending_store.clear(chat_id)
        telegram.edit_message(chat_id, pending.prompt_message_id, busy_run_text(workflow_run))
        return

    if password_matches(config.run_password, text):
        pending_store.clear(chat_id)
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
):
    is_command = text.startswith("/")

    if pending_stop_store.has(chat_id) and not is_command:
        verify_stop_password(
            telegram,
            github,
            config,
            active_store,
            pending_stop_store,
            chat_id,
            text,
            message_id,
        )
        return

    # Parol kutilayotgan bo'lsa va bu buyruq bo'lmasa — matnni parol urinishi deb qaraymiz.
    if pending_store.has(chat_id) and not is_command:
        verify_run_password(telegram, github, config, active_store, pending_store, chat_id, text, message_id, dispatch_lock)
        return

    # Buyruq kelsa, oldingi parol kutish holatini bekor qilamiz.
    if is_command:
        pending_store.clear(chat_id)
        pending_stop_store.clear(chat_id)

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
        show_stop_prompt(telegram, chat_id, pending_stop_store)
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
    callback,
):
    callback_id = str(callback.get("id", ""))
    data = str(callback.get("data", ""))
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    message_id = message.get("message_id")

    if not isinstance(message_id, int):
        telegram.answer_callback(callback_id)
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

    if data.startswith("suite:"):
        suite_key = data.split(":", 1)[1]
        if suite_key not in SUITES:
            telegram.answer_callback(callback_id, "Unknown suite")
            return
        telegram.answer_callback(callback_id, "Serverni tanlang")
        telegram.edit_message(
            chat_id,
            message_id,
            f"{SUITES[suite_key]}: qaysi serverda run qilamiz?",
            reply_markup=server_keyboard(config, suite_key),
        )
        return

    if data.startswith("server:"):
        parts = data.split(":")
        if len(parts) != 3:
            telegram.answer_callback(callback_id, "Unknown server action")
            return
        _action, suite_key, server_key = parts
        if suite_key not in SUITES:
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
        pending_store.set(chat_id, PendingRun(request=request, prompt_message_id=message_id))
        telegram.edit_message(
            chat_id,
            message_id,
            (
                f"🔒 {SUITES[suite_key]} · {config.servers[server_key]}\n\n"
                "Testni run qilish uchun parolni yuboring:"
            ),
        )
        return

    telegram.answer_callback(callback_id, "Unknown action")
