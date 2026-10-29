"""Telegram bot entry point: wire services and poll for updates."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "telegram_bot"

import threading
import time

from .bot_client import TelegramClient
from .bot_state import ActiveRunStore, PendingStore
from .github_api import GitHubActionsClient
from .handlers import handle_callback, handle_message
from .scheduler import DailyScheduler, dispatch_daily_slot
from .telegram_ci_settings import ConfigError, load_config


def main():
    try:
        config = load_config()
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2

    telegram = TelegramClient(config.telegram_token)
    github = GitHubActionsClient(config.github_token, config.repository, config.workflow, config.ref)
    active_store = ActiveRunStore()
    pending_store = PendingStore()
    pending_stop_store = PendingStore()
    dispatch_lock = threading.Lock()

    daily_scheduler = DailyScheduler(
        config.daily_schedule,
        dispatch_slot=lambda slot: dispatch_daily_slot(github, active_store, dispatch_lock, config.daily_schedule, slot),
    )
    if config.daily_schedule.enabled:
        threading.Thread(target=daily_scheduler.run_forever, daemon=True).start()

    offset = None
    print(f"Telegram CI bot started for {config.repository}/{config.workflow} on {config.ref}")
    if config.daily_schedule.enabled:
        print(
            "Daily scheduler enabled: "
            f"time={config.daily_schedule.hour:02d}:{config.daily_schedule.minute:02d} "
            f"timezone={config.daily_schedule.timezone_name} "
            f"suite=all server={config.daily_schedule.server_key}"
        )
    else:
        print("Daily scheduler disabled; bot manual trigger rejimida.")

    while True:
        try:
            updates = telegram.get_updates(offset)
            for update in updates:
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    offset = update_id + 1

                message = update.get("message")
                if isinstance(message, dict):
                    chat = message.get("chat") or {}
                    chat_id = str(chat.get("id", ""))
                    text = message.get("text")
                    message_id = message.get("message_id")
                    if isinstance(text, str):
                        handle_message(
                            telegram,
                            github,
                            config,
                            active_store,
                            pending_store,
                            pending_stop_store,
                            chat_id,
                            text.strip(),
                            message_id if isinstance(message_id, int) else None,
                            dispatch_lock,
                        )
                    continue

                callback = update.get("callback_query")
                if isinstance(callback, dict):
                    handle_callback(telegram, github, config, active_store, pending_store, callback)
        except KeyboardInterrupt:
            print("Stopping Telegram CI bot.")
            return 0
        except Exception as exc:
            print(f"Bot loop error: {exc}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
