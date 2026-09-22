"""Shared dependency-free Telegram transport and response handling."""

from __future__ import annotations

from dataclasses import dataclass
from http.client import HTTPException
import json
import mimetypes
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4

from .constants import TELEGRAM_RETRY_DELAYS_SECONDS


@dataclass(frozen=True)
class TelegramRequestResult:
    ok: bool
    method: str
    data: dict | None = None
    error_code: int | None = None
    description: str = ""
    retry_after: int = 0
    category: str = ""

    @property
    def retryable(self):
        return self.category in {"flood_control", "network", "server"}


def sanitize_telegram_error(value):
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(
        r"https://api\.telegram\.org/bot[^/\s]+",
        "https://api.telegram.org/bot<redacted>",
        text,
    )
    return text[:300]


def telegram_error_category(error_code):
    if error_code == 429:
        return "flood_control"
    if error_code in {401, 403}:
        return "authorization"
    if error_code == 400:
        return "bad_request"
    if isinstance(error_code, int) and error_code >= 500:
        return "server"
    return "telegram"


def telegram_error_result(method, *, error_code=None, description="", retry_after=0, category=""):
    return TelegramRequestResult(
        ok=False,
        method=method,
        error_code=error_code,
        description=sanitize_telegram_error(description) or "Telegram API xatosi",
        retry_after=max(0, int(retry_after or 0)),
        category=category or telegram_error_category(error_code),
    )


def telegram_response_error(method, data, fallback_code=None):
    data = data if isinstance(data, dict) else {}
    error_code = data.get("error_code", fallback_code)
    try:
        error_code = int(error_code) if error_code is not None else None
    except (TypeError, ValueError):
        error_code = fallback_code
    parameters = data.get("parameters")
    parameters = parameters if isinstance(parameters, dict) else {}
    retry_after = parameters.get("retry_after", 0)
    try:
        retry_after = int(retry_after or 0)
    except (TypeError, ValueError):
        retry_after = 0
    description = sanitize_telegram_error(data.get("description"))
    if error_code == 400 and "message is not modified" in description.lower():
        return TelegramRequestResult(ok=True, method=method, data={"ok": True, "result": True})
    return telegram_error_result(
        method,
        error_code=error_code,
        description=description,
        retry_after=retry_after,
    )


def retry_delay_seconds(result, attempt):
    if result.retry_after:
        return result.retry_after
    index = min(max(0, attempt - 1), len(TELEGRAM_RETRY_DELAYS_SECONDS) - 1)
    return TELEGRAM_RETRY_DELAYS_SECONDS[index]


def _encode_payload(payload, files):
    if not files:
        return urllib.parse.urlencode(payload).encode("utf-8"), "application/x-www-form-urlencoded"
    boundary = uuid4().hex
    parts = []
    for name, value in payload.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    for name, file_path in files.items():
        path = Path(file_path)
        filename = path.name.replace('"', '').replace('\r', '').replace('\n', '')
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        parts.extend([
            (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; '
             f'filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n').encode("utf-8"),
            path.read_bytes(),
            b"\r\n",
        ])
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def request_once(token, method, payload, *, timeout=30, files=None):
    """One API attempt; polling cooldown and CI delivery retries belong to callers.

    Uses only the standard library so CI can report dependency-install progress.
    """
    if not token:
        return telegram_error_result(method, description="Telegram credentials sozlanmagan", category="disabled")
    try:
        encoded, content_type = _encode_payload(payload, files)
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/{method}",
            data=encoded,
            headers={"Content-Type": content_type},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8"))
        except (OSError, HTTPException) as read_error:
            return telegram_error_result(method, description=read_error.__class__.__name__, category="network")
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {}
        result = telegram_response_error(method, data, fallback_code=exc.code)
        if result.ok:
            return result
        if result.description == "Telegram API xatosi":
            return telegram_error_result(method, error_code=exc.code, description=exc.reason)
        return result
    except (OSError, HTTPException, urllib.error.URLError) as exc:
        return telegram_error_result(method, description=exc.__class__.__name__, category="network")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return telegram_error_result(method, description="Telegram noto'g'ri JSON javob qaytardi", category="server")
    if not isinstance(data, dict):
        return telegram_error_result(method, description="Telegram JSON object qaytarmadi", category="server")
    if not data.get("ok"):
        return telegram_response_error(method, data)
    return TelegramRequestResult(ok=True, method=method, data=data)
