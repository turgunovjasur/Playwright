"""Carry the initiating Telegram chat through public workflow dispatch metadata."""

import base64
import hashlib
import os
import re

from cryptography.fernet import Fernet, InvalidToken


def _cipher(bot_token):
    if not bot_token:
        raise ValueError("Telegram bot token is missing")
    key = hashlib.sha256(b"playwright-ci/reply-chat/v1\0" + bot_token.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encode_reply_chat(bot_token, chat_id):
    if not re.fullmatch(r"-?[1-9][0-9]*", str(chat_id)):
        raise ValueError("Invalid Telegram chat ID")
    return _cipher(bot_token).encrypt(str(chat_id).encode("ascii")).decode("ascii")


def decode_reply_chat(bot_token, route):
    try:
        value = _cipher(bot_token).decrypt(route.encode("ascii")).decode("ascii")
    except (InvalidToken, UnicodeError):
        raise ValueError("Invalid Telegram reply route") from None
    if not re.fullmatch(r"-?[1-9][0-9]*", value):
        raise ValueError("Invalid Telegram reply route")
    return value


if __name__ == "__main__":
    chat_id = decode_reply_chat(os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_REPLY_ROUTE"])
    print(f"::add-mask::{chat_id}", flush=True)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"chat_id={chat_id}\n")
