"""Validated JSON settings and environment credentials for bot and CLI."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import json
import os

from .environment import env_value
from .models import BotConfig, HourlyScheduleConfig


CONFIG_PATH = Path(__file__).with_name("telegram_ci_config.json")


class ConfigError(RuntimeError):
    pass


def env_required(name, *fallbacks):
    for key in (name, *fallbacks):
        value = os.getenv(key, "").strip()
        if value:
            return value
    names = ", ".join((name, *fallbacks))
    raise ConfigError(f"Required environment variable is missing: {names}")


def load_hourly_schedule_config(schedule):
    enabled_value = env_value("HOURLY_SCHEDULE_ENABLED", "0").lower()
    if enabled_value in {"1", "true", "yes", "on"}:
        enabled = True
    elif enabled_value in {"0", "false", "no", "off"}:
        enabled = False
    else:
        raise ConfigError("HOURLY_SCHEDULE_ENABLED must be boolean")

    return HourlyScheduleConfig(
        enabled=enabled,
        minute=schedule["minute"],
        timezone_name=schedule["timezone"],
        server_key=schedule["server"],
    )


def load_config():
    public = load_public_config()

    # Botdan hamma foydalana oladi; run/stop faqat to'g'ri parol bilan ochiladi.
    run_password = env_required("TELEGRAM_RUN_PASSWORD")

    return BotConfig(
        telegram_token=env_required("TELEGRAM_BOT_TOKEN"),
        run_password=run_password,
        github_token=env_required("GITHUB_TOKEN", "GITHUB_PAT"),
        repository=public["github"]["repository"],
        workflow=public["github"]["workflow"],
        ref=public["github"]["ref"],
        servers=public["servers"],
        allowed_server_keys=set(public["servers"]),
        hourly_schedule=load_hourly_schedule_config(public["schedule"]),
    )


def load_public_config():
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigError("telegram_ci_config.json o'qilmadi yoki JSON formati noto'g'ri") from exc
    if not isinstance(config, dict):
        raise ConfigError("telegram_ci_config.json object bo'lishi kerak")
    for section in ("github", "servers", "schedule"):
        if not isinstance(config.get(section), dict):
            raise ConfigError(f"telegram_ci_config.json: {section} bo'limi kerak")

    github = config["github"]
    for key in ("repository", "workflow", "ref"):
        value = github.get(key)
        if not isinstance(value, str) or not value.strip() or any(c.isspace() for c in value):
            raise ConfigError(f"telegram_ci_config.json: github.{key} noto'g'ri")
    if len(github["repository"].split("/")) != 2 or not all(github["repository"].split("/")):
        raise ConfigError("telegram_ci_config.json: github.repository owner/repo formatida bo'lishi kerak")

    servers = config["servers"]
    # Workflow credentiallari faqat shu ikki server keyiga bog'langan.
    if not servers or not set(servers).issubset({"smartup", "app3"}):
        raise ConfigError("telegram_ci_config.json: servers faqat smartup/app3 keylarini qabul qiladi")
    for key, value in servers.items():
        if not isinstance(value, str) or any(c.isspace() for c in value):
            raise ConfigError(f"telegram_ci_config.json: servers.{key} URL noto'g'ri")
        try:
            url = urlsplit(value)
            valid = url.scheme == "https" and url.hostname and not (url.username or url.password or url.query or url.fragment)
        except ValueError:
            valid = False
        if not valid:
            raise ConfigError(f"telegram_ci_config.json: servers.{key} toza HTTPS URL bo'lishi kerak")

    schedule = config["schedule"]
    if type(schedule.get("minute")) is not int or not 0 <= schedule["minute"] <= 59:
        raise ConfigError("telegram_ci_config.json: schedule.minute 0..59 oralig'idagi butun son bo'lishi kerak")
    timezone_name = schedule.get("timezone")
    if not isinstance(timezone_name, str) or not timezone_name:
        raise ConfigError("telegram_ci_config.json: schedule.timezone kerak")
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConfigError("telegram_ci_config.json: schedule.timezone noto'g'ri") from exc
    if not isinstance(schedule.get("server"), str) or schedule["server"] not in servers:
        raise ConfigError("telegram_ci_config.json: schedule.server servers ichida bo'lishi kerak")
    return config
