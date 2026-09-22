"""CI progress throttling, final retries and delivery status artifacts."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import json
import sys
import time

from .constants import (
    FINAL_DELIVERY_ATTEMPTS,
    FINAL_RETRY_WAIT_BUDGET_SECONDS,
    PROGRESS_EDIT_INTERVAL_SECONDS,
)
from .environment import env_value, telegram_enabled
from .formatting import now_tashkent, target_label
from .messages import render_message, render_plain_message
from .paths import DELIVERY_FILE
from .progress_state import save_state
from .telegram_api import (
    request_once,
    retry_delay_seconds,
    sanitize_telegram_error,
    telegram_error_result,
)


def telegram_request(method, payload):
    if not telegram_enabled():
        return telegram_error_result(
            method, description="Telegram credentials sozlanmagan", category="disabled",
        )
    return request_once(env_value("TELEGRAM_BOT_TOKEN"), method, payload)


def telegram_result_summary(result):
    code = f"{result.error_code} " if result.error_code is not None else ""
    return f"{code}{result.description}".strip()


def log_telegram_warning(result, *, attempt=1):
    print(
        "Telegram progress warning: "
        f"method={result.method} category={result.category or 'unknown'} "
        f"code={result.error_code or '-'} retry_after={result.retry_after}s "
        f"attempt={attempt} error={result.description}",
        file=sys.stderr,
    )


def record_telegram_error(state, result, *, attempt=1, waited_seconds=0):
    summary = telegram_result_summary(result)
    if waited_seconds:
        summary += (
            f". {waited_seconds} soniya kutildi; "
            f"qayta urinish {attempt}/{FINAL_DELIVERY_ATTEMPTS}"
        )
    state["telegram_notification_warning"] = summary
    retry_at = (
        now_tashkent() + timedelta(seconds=result.retry_after)
        if result.retry_after
        else None
    )
    state["telegram_last_error"] = {
        "method": result.method,
        "category": result.category,
        "error_code": result.error_code,
        "description": result.description,
        "retry_after": result.retry_after,
        "retry_at": retry_at.isoformat(timespec="seconds") if retry_at else "",
        "attempt": attempt,
        "at": now_tashkent().isoformat(timespec="seconds"),
    }
    log_telegram_warning(result, attempt=attempt)


def record_telegram_success(state, text):
    state["telegram_last_sent_epoch"] = time.time()
    state["telegram_last_text"] = text
    state.pop("telegram_backoff_until", None)


def telegram_payload(state, *, message_id=None, plain=False):
    payload = {
        "chat_id": env_value("TELEGRAM_CHAT_ID"),
        "text": render_plain_message(state) if plain else render_message(state),
        "disable_web_page_preview": "true",
    }
    if message_id is not None:
        payload["message_id"] = str(message_id)
    if not plain:
        payload["parse_mode"] = "HTML"
    return payload


def is_format_error(result):
    if result.category != "bad_request":
        return False
    description = result.description.lower()
    return any(
        marker in description
        for marker in ("parse", "entities", "message text", "too long")
    )


def edit_progress(state, *, force=False):
    message_id = state.get("message_id")
    if not message_id:
        return None

    now = time.time()
    text = render_message(state)
    if not force:
        if text == state.get("telegram_last_text"):
            return None
        if now < float(state.get("telegram_backoff_until") or 0):
            return None
        last_sent = float(state.get("telegram_last_sent_epoch") or 0)
        if now - last_sent < PROGRESS_EDIT_INTERVAL_SECONDS:
            return None

    result = telegram_request(
        "editMessageText",
        telegram_payload(state, message_id=message_id),
    )
    if not result.ok and is_format_error(result):
        record_telegram_error(state, result)
        result = telegram_request(
            "editMessageText",
            telegram_payload(state, message_id=message_id, plain=True),
        )

    if result.ok:
        record_telegram_success(state, text)
    else:
        record_telegram_error(state, result)
        delay = result.retry_after or PROGRESS_EDIT_INTERVAL_SECONDS
        if result.retryable:
            state["telegram_backoff_until"] = time.time() + delay
    save_state(state)
    return result


def attempt_final_method(state, method, *, message_id=None, retry_deadline=None):
    plain = False
    errors = []
    last_result = None
    if retry_deadline is None:
        retry_deadline = time.monotonic() + FINAL_RETRY_WAIT_BUDGET_SECONDS
    for attempt in range(1, FINAL_DELIVERY_ATTEMPTS + 1):
        result = telegram_request(
            method,
            telegram_payload(state, message_id=message_id, plain=plain),
        )
        last_result = result
        if result.ok:
            return result, attempt, errors, plain

        errors.append(result)
        record_telegram_error(state, result, attempt=attempt)
        if is_format_error(result) and not plain:
            plain = True
            state["telegram_notification_warning"] = (
                f"{telegram_result_summary(result)}. "
                "Oddiy matn formatida qayta yuborildi"
            )
            save_state(state)
            continue
        if not result.retryable or attempt >= FINAL_DELIVERY_ATTEMPTS:
            break

        delay = retry_delay_seconds(result, attempt)
        remaining_budget = max(0, retry_deadline - time.monotonic())
        if delay > remaining_budget:
            state["telegram_notification_warning"] = (
                f"{telegram_result_summary(result)}. Telegram {delay} soniya kutishni "
                "so'radi; CI bloklanmasligi uchun qayta urinish to'xtatildi"
            )
            save_state(state)
            break
        state["telegram_notification_warning"] = (
            f"{telegram_result_summary(result)}. {delay} soniyadan keyin "
            f"qayta urinish {attempt + 1}/{FINAL_DELIVERY_ATTEMPTS}"
        )
        save_state(state)
        time.sleep(delay)

    return last_result, len(errors), errors, plain


def extract_message_id(result):
    data = result.data if result and result.ok else None
    message = data.get("result") if isinstance(data, dict) else None
    if isinstance(message, dict) and isinstance(message.get("message_id"), int):
        return message["message_id"]
    return None


def delivery_payload(state, *, status, method, attempts, errors):
    last_error = errors[-1] if errors else None
    retry_at = (
        now_tashkent() + timedelta(seconds=last_error.retry_after)
        if last_error is not None and last_error.retry_after
        else None
    )
    return {
        "suite": target_label(str(state.get("target") or "all")),
        "test_result": str(state.get("result") or ""),
        "run_url": str(state.get("run_url") or ""),
        "status": status,
        "method": method,
        "attempts": attempts,
        "recovered": bool(
            errors
            and status in {"recovered", "fallback_sent", "sent_new"}
        ),
        "error": (
            {
                "category": last_error.category,
                "error_code": last_error.error_code,
                "description": last_error.description,
                "retry_after": last_error.retry_after,
                "retry_at": retry_at.isoformat(timespec="seconds") if retry_at else "",
            }
            if last_error is not None
            else None
        ),
        "updated_at": now_tashkent().isoformat(timespec="seconds"),
    }


def write_delivery_status(state, delivery):
    state["telegram_delivery"] = delivery
    DELIVERY_FILE.parent.mkdir(parents=True, exist_ok=True)
    DELIVERY_FILE.write_text(
        json.dumps(delivery, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    status = str(delivery.get("status") or "unknown")
    error = delivery.get("error")
    error = error if isinstance(error, dict) else {}
    detail = sanitize_telegram_error(error.get("description"))
    summary_path = env_value("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary_file:
            summary_file.write("\n### Telegram notification\n\n")
            summary_file.write(f"- Delivery: `{status}`\n")
            summary_file.write(f"- Method: `{delivery.get('method') or 'none'}`\n")
            summary_file.write(f"- Attempts: `{delivery.get('attempts') or 0}`\n")
            if detail:
                summary_file.write(f"- Error: `{detail}`\n")

    if status in {"failed", "disabled"} or delivery.get("recovered"):
        warning = detail or status
        print(
            f"::warning title=Telegram notification::{warning}",
            file=sys.stderr,
        )


def deliver_final(state):
    if not telegram_enabled():
        result = telegram_error_result(
            "sendMessage",
            description="Telegram credentials sozlanmagan",
            category="disabled",
        )
        record_telegram_error(state, result)
        return delivery_payload(
            state,
            status="disabled",
            method="none",
            attempts=0,
            errors=[result],
        )

    all_errors = []
    retry_deadline = time.monotonic() + FINAL_RETRY_WAIT_BUDGET_SECONDS
    message_id = state.get("message_id")
    if message_id:
        result, attempts, errors, _plain = attempt_final_method(
            state,
            "editMessageText",
            message_id=message_id,
            retry_deadline=retry_deadline,
        )
        all_errors.extend(errors)
        if result and result.ok:
            record_telegram_success(state, render_message(state))
            return delivery_payload(
                state,
                status="recovered" if errors else "delivered",
                method="editMessageText",
                attempts=attempts,
                errors=all_errors,
            )

        state["telegram_notification_warning"] = (
            f"{telegram_result_summary(result)}. "
            "Eski RUNNING xabari yangilanmadi; yangi final xabar yuborildi"
        )
        save_state(state)

    result, _attempts, errors, _plain = attempt_final_method(
        state,
        "sendMessage",
        retry_deadline=retry_deadline,
    )
    all_errors.extend(errors)
    if result and result.ok:
        new_message_id = extract_message_id(result)
        if new_message_id is not None:
            state["message_id"] = new_message_id
        record_telegram_success(state, render_message(state))
        return delivery_payload(
            state,
            status="fallback_sent" if message_id else "sent_new",
            method="sendMessage",
            attempts=len(all_errors) + 1,
            errors=all_errors,
        )

    return delivery_payload(
        state,
        status="failed",
        method="sendMessage",
        attempts=len(all_errors),
        errors=all_errors,
    )
