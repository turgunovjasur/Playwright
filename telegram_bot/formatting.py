"""Pure message and timestamp formatting helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from .constants import MAX_MESSAGE_LENGTH, TARGET_LABELS, TARGET_SUITE_LABELS, TASHKENT_TZ


def now_tashkent():
    return datetime.now(TASHKENT_TZ)


def format_duration(seconds):
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    if minutes:
        return f"{minutes} daqiqa {secs} soniya"
    return f"{secs} soniya"


def server_host(server):
    value = (server or "").strip()
    for prefix in ("https://", "http://"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value.rstrip("/") or "unknown"


def target_label(target):
    key = (target or "all").strip().lower()
    return TARGET_LABELS.get(key, key.title() if key else "All")


def target_suite_label(target):
    key = (target or "all").strip().lower()
    return TARGET_SUITE_LABELS.get(key, target_label(key))


def _utc_now_text():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _parse_utc_text(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _clock_text(value, tz):
    parsed = _parse_utc_text(value)
    if parsed is None:
        return ""
    return parsed.astimezone(tz).strftime("%H:%M:%S")


def first_message_line(value):
    for line in str(value or "").splitlines():
        text = line.strip()
        if text:
            return text
    return ""


def truncate_message(text, limit=MAX_MESSAGE_LENGTH):
    if len(text) <= limit:
        return text
    lines = text.splitlines()
    while lines and len("\n".join(lines) + "\n...") > limit:
        lines.pop(-1)
    if lines:
        return "\n".join(lines) + "\n..."
    return text[: max(0, limit - 3)] + "..."
