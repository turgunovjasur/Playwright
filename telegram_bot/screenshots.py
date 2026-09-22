"""Best-effort CI failure screenshot notification through the shared API."""

from .environment import env_value, telegram_enabled
from .paths import ROOT
from .telegram_api import request_once


def main():
    if env_value("JOB_STATUS", "success") == "success" or not telegram_enabled():
        return 0
    screenshots = sorted((ROOT / "test-results").rglob("*.png"))
    screenshots = [path for path in screenshots if path.is_file()]
    if not screenshots:
        print("Failed screenshot not found; trace/log is in the artifact.")
        return 0
    result = request_once(
        env_value("TELEGRAM_BOT_TOKEN"),
        "sendPhoto",
        {"chat_id": env_value("TELEGRAM_CHAT_ID"), "caption": "Failed screenshot"},
        files={"photo": screenshots[-1]},
    )
    if not result.ok:
        print(f"Telegram screenshot upload failed: {result.category}; {result.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
