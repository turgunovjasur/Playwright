"""Human diagnostika uchun URL querylari va credentiallarni yashirish."""

import os
import re
from urllib.parse import urlsplit, urlunsplit


def safe_url(value):
    try:
        parts = urlsplit(str(value or ""))
        fragment = re.sub(r"^/[^/]+", "/<session>", parts.fragment)
        fragment = fragment.split("?", 1)[0]
        hostname = parts.netloc.rsplit("@", 1)[-1]
        return urlunsplit((parts.scheme, hostname, parts.path, "", fragment))
    except ValueError:
        return "<URL aniqlanmadi>"


def safe_text(value):
    text = str(value or "")
    # Playwright Expected/Actual/fill qiymatlari labeldan alohida chiqishi mumkin.
    for key, secret in sorted(os.environ.items(), key=lambda item: len(item[1]), reverse=True):
        if secret and re.search(r"password|secret|token|api.?key|head.*email", key, re.I):
            if len(secret) >= 4:
                text = text.replace(secret, "<secret>")
            else:
                text = re.sub(r"(?<!\w)" + re.escape(secret) + r"(?!\w)", "<secret>", text)
    if re.search(r"password|пароль", text, re.I):
        text = re.sub(r"((?:Expected|Actual|Received)(?:\s+(?:value|string))?\s*:)\s*[^\r\n]*", r"\1 <secret>", text, flags=re.I)
        text = re.sub(r"(expected(?: not)? to have value)\s+[^\r\n]+", r"\1 <secret>", text, flags=re.I)
        text = re.sub(r"((?:fill|type|to_have_value)\s*\()([^\r\n)]*)(\))", r"\1<secret>\3", text)
        text = re.sub(r"(unexpected value\s*)[\"'][^\r\n]*", r"\1<secret>", text, flags=re.I)
    text = re.sub(r"\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", "<authorization>", text, flags=re.I)
    text = re.sub(r"((?:authorization|cookie|set-cookie)[\"']?\s*[:=]\s*)[^\r\n]+", r"\1***", text, flags=re.I)
    text = re.sub(r"(?:https?|wss?)://[^\s\"'<>]+", lambda m: safe_url(m[0]), text)
    text = re.sub(r"(#/)[^/\s\"']+", r"\1<session>", text)
    text = re.sub(
        r"((?:password|пароль|token|secret|api[_-]?key)[\"']?\s*[:=]\s*)([\"'])(.*?)\2",
        r"\1\2***\2", text, flags=re.I,
    )
    text = re.sub(
        r"((?:password|пароль|token|secret|api[_-]?key|authorization|cookie)"
        r"[\"']?\s*[:=]\s*[\"']?)([^\s,;\"']+)",
        r"\1***", text, flags=re.I,
    )
    text = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\b", "<login>", text, flags=re.I)
    text = re.sub(r"\b(?:AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,})", "<api-key>", text)
    return text


def safe_payload(value):
    """AI chegarasida nested maydonlarning hammasini tozalash."""
    if isinstance(value, dict):
        return {
            key: "***" if re.search(
                r"password|пароль|secret|token|api.?key|authorization|cookie", str(key), re.I
            ) else safe_payload(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [safe_payload(item) for item in value]
    return safe_text(value) if isinstance(value, str) else value
