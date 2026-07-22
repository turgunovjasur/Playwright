from __future__ import annotations

import json


EVENT_PREFIX = "SMARTUP_PROGRESS "


def emit_progress_event(
    *,
    event,
    group,
    runner,
    test_id,
    title,
    display=None,
    error_type=None,
    message=None,
):
    shown_name = display or title or test_id
    payload = {
        "event": event,
        "group": group,
        "runner": runner,
        "test_id": test_id,
        "title": title,
        "display": shown_name,
    }
    if error_type:
        payload["error_type"] = error_type
    if message:
        payload["message"] = message
    print("\n" + EVENT_PREFIX + json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)
