"""Environment access without loading files or starting services."""

from __future__ import annotations

import os


def env_value(name, default=""):
    return os.getenv(name, default).strip() or default


def telegram_enabled():
    return bool(env_value("TELEGRAM_BOT_TOKEN") and env_value("TELEGRAM_CHAT_ID"))
