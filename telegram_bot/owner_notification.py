"""Send a short owner DM for a Telegram-initiated CI run."""

import json
import os
from pathlib import Path
import sys

from .bot_client import TelegramAPIError, TelegramClient
from .constants import MANUAL_SUITE_LABEL
from .formatting import format_duration, now_tashkent
from .github_api import parse_github_time
from .reply_chat import decode_requester


def requester_label(client, sender_id, name):
    if name:
        return name
    # Older bot versions only supplied the originating chat.
    if sender_id:
        try:
            profile = client.request("getChat", {"chat_id": sender_id})["result"]
            label = " ".join(filter(None, [profile.get("first_name"), profile.get("last_name")]))
            return " ".join(label.split()) or profile.get("username") or f"Telegram ID {sender_id}"
        except TelegramAPIError:
            return f"Telegram ID {sender_id}"
    return "Telegram guruhidagi foydalanuvchi"


def final_text(run, details_path, label, server):
    outcomes = {
        "success": "✅ Muvaffaqiyatli",
        "failure": "❌ Xatolik bilan tugadi",
        "cancelled": "⏹ Bekor qilindi",
        "timed_out": "⏱ Vaqt tugadi",
    }
    lines = [
        f"{outcomes.get(run['conclusion'], run['conclusion'])} · #{run['run_number']}",
        f"{label} · {server} · {MANUAL_SUITE_LABEL}",
    ]
    if details_path.is_file():
        details = json.loads(details_path.read_text())
        counts = details.get("counts") or {}
        if details.get("run_attempt") == str(run["run_attempt"]) and counts.get("total"):
            lines.append(f"{counts['passed']} ta o‘tdi · {counts['failed']} ta yiqildi · "
                         f"{counts['skipped']} ta o‘tkazib yuborildi")
    start = parse_github_time(run["run_started_at"])
    finish = parse_github_time(run["updated_at"])
    if start and finish:
        lines.append(f"Davomiylik · {format_duration((finish - start).total_seconds())}")
    lines.append(run["html_url"])
    return "\n".join(lines)


def main():
    stage, context_path, *details = sys.argv[1:]
    context = json.loads(Path(context_path).read_text())
    owner = os.environ["TELEGRAM_CHAT_ID"].strip()
    if not owner.isdecimal() or int(owner) <= 0:
        raise ValueError("TELEGRAM_CHAT_ID must identify the owner's private chat")
    client = TelegramClient(os.environ["TELEGRAM_BOT_TOKEN"])
    chat_id, sender_id, name = decode_requester(client.token, context["route"])
    if owner in (sender_id, chat_id):
        return
    label = requester_label(client, sender_id, name)
    server = {"smartup": "Online", "app3": "Xtrade"}[context["server"]]
    if stage == "started":
        url = f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
        text = (f"🚀 {label} testlarni boshladi · #{os.environ['GITHUB_RUN_NUMBER']}\n"
                f"{server} · {MANUAL_SUITE_LABEL} · {now_tashkent():%H:%M} UZT\n{url}")
    elif stage == "finished":
        run = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())["workflow_run"]
        text = final_text(run, Path(details[0]), label, server)
    else:
        raise ValueError("Unknown owner notification stage")
    client.send_message(owner, text)


if __name__ == "__main__":
    main()
