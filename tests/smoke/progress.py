from __future__ import annotations

import json
from datetime import datetime, timezone


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
    writer=None,
    **details,
):
    shown_name = display or title or test_id
    payload = {
        "event": event,
        "group": group,
        "runner": runner,
        "test_id": test_id,
        "title": title,
        "display": shown_name,
        "occurred_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z"),
    }
    if error_type:
        payload["error_type"] = error_type
    if message:
        payload["message"] = message
    payload.update(details)
    line = EVENT_PREFIX + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if writer is not None:
        writer(line)
    else:
        print("\n" + line, flush=True)
    return payload
