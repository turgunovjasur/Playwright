"""Carry the initiating Telegram chat through public workflow dispatch metadata."""

import base64
import hashlib
import json
import os
import re

from cryptography.fernet import Fernet, InvalidToken


def _cipher(bot_token):
    if not bot_token:
        raise ValueError("Telegram bot token is missing")
    key = hashlib.sha256(b"playwright-ci/reply-chat/v1\0" + bot_token.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encode_reply_chat(bot_token, chat_id, sender_id=None, sender_name=""):
    if not re.fullmatch(r"-?[1-9][0-9]*", str(chat_id)):
        raise ValueError("Invalid Telegram chat ID")
    value = str(chat_id)
    if sender_id is not None:
        value = json.dumps([value, str(sender_id), sender_name], ensure_ascii=False)
    return _cipher(bot_token).encrypt(value.encode("utf-8")).decode("ascii")


def decode_requester(bot_token, route):
    try:
        value = json.loads(_cipher(bot_token).decrypt(route.encode("ascii")))
    except (InvalidToken, UnicodeError, ValueError):
        raise ValueError("Invalid Telegram reply route") from None
    # Older bot versions encrypted only the numeric chat ID.
    if type(value) is int and value:
        return str(value), str(value) if value > 0 else "", ""
    if isinstance(value, list) and len(value) == 3:
        chat_id, sender_id, name = value
        if (all(isinstance(item, str) for item in value)
                and re.fullmatch(r"-?[1-9][0-9]*", chat_id)
                and re.fullmatch(r"[1-9][0-9]*", sender_id)):
            return chat_id, sender_id, " ".join(name.split())[:160]
    raise ValueError("Invalid Telegram reply route")


def decode_reply_chat(bot_token, route):
    return decode_requester(bot_token, route)[0]


if __name__ == "__main__":
    chat_id = decode_reply_chat(os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_REPLY_ROUTE"])
    print(f"::add-mask::{chat_id}", flush=True)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"chat_id={chat_id}\n")
