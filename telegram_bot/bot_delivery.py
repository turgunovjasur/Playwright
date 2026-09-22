"""Transient bot message cleanup and reply updates."""

from __future__ import annotations

import sys


def transient_status_message_ids(active):
    # Only the throwaway "test jarayonda" reminder replies. The main progress
    # message (status_message_id) becomes the final report and must be kept.
    if active is None:
        return ()
    return tuple(active.extra_status_message_ids)


def safe_delete_message(telegram, chat_id, message_id):
    if message_id is None:
        return
    try:
        telegram.delete_message(chat_id, message_id)
    except Exception as exc:
        print(f"Telegram process message delete failed: {exc}", file=sys.stderr)


def safe_delete_transient_messages(telegram, active):
    if active is None:
        return
    for message_id in transient_status_message_ids(active):
        safe_delete_message(telegram, active.chat_id, message_id)


def edit_or_send_message(telegram, chat_id, message_id, text):
    if message_id is None:
        telegram.send_message(chat_id, text)
        return
    telegram.edit_message(chat_id, message_id, text)
