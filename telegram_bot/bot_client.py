"""Bot Telegram methods, per-method cooldown and bounded retries."""

from __future__ import annotations

import json
import math
import time

from .telegram_api import request_once, retry_delay_seconds, sanitize_telegram_error

from .constants import TELEGRAM_MAX_RETRY_WAIT_SECONDS, TELEGRAM_REQUEST_ATTEMPTS


class TelegramAPIError(RuntimeError):
    def __init__(
        self,
        method,
        *,
        category,
        description,
        error_code=None,
        retry_after=0,
        attempts=1,
    ):
        self.method = method
        self.category = category
        self.description = sanitize_telegram_error(description) or "Telegram API xatosi"
        self.error_code = error_code
        self.retry_after = max(0, int(retry_after or 0))
        self.attempts = attempts
        code = f"{error_code} " if error_code is not None else ""
        super().__init__(
            f"Telegram {method} error: {code}{self.description}; "
            f"attempts={attempts}; retry_after={self.retry_after}s"
        )

    def as_dict(self, *, retry_at_epoch=None):
        data = {
            "method": self.method,
            "category": self.category,
            "description": self.description,
            "error_code": self.error_code,
            "retry_after": self.retry_after,
            "attempts": self.attempts,
        }
        if retry_at_epoch is not None:
            data["retry_at_epoch"] = float(retry_at_epoch)
        return data


class TelegramClient:
    def __init__(self, token):
        self.token = token
        self.last_error = None
        self.last_recovered_error = None
        self._retry_not_before = {}


    def _remember_error(self, error, *, retry_at_epoch=None):
        if retry_at_epoch is None and error.retry_after:
            retry_at_epoch = time.time() + error.retry_after
        self.last_error = error.as_dict(retry_at_epoch=retry_at_epoch)
        if error.category == "flood_control" and retry_at_epoch is not None:
            self._retry_not_before[error.method] = retry_at_epoch

    def _cooldown_error(self, method):
        retry_at_epoch = float(self._retry_not_before.get(method) or 0)
        remaining = retry_at_epoch - time.time()
        if remaining <= 0:
            self._retry_not_before.pop(method, None)
            return None
        error = TelegramAPIError(
            method,
            category="flood_control",
            description="Too Many Requests: retry muddati hali tugamagan",
            error_code=429,
            retry_after=max(1, math.ceil(remaining)),
            attempts=0,
        )
        self._remember_error(error, retry_at_epoch=retry_at_epoch)
        return error

    def _remember_success(self, method, recovered_error=None):
        current_error = self.last_error
        if recovered_error is not None:
            self.last_recovered_error = recovered_error.as_dict()
        elif isinstance(current_error, dict) and current_error.get("method") == method:
            self.last_recovered_error = current_error
        if isinstance(current_error, dict) and current_error.get("method") == method:
            self.last_error = None
        self._retry_not_before.pop(method, None)

    def request(self, method, payload, *, max_attempts=TELEGRAM_REQUEST_ATTEMPTS):
        cooldown_error = self._cooldown_error(method)
        if cooldown_error is not None:
            raise cooldown_error

        recovered_error = None
        waited_seconds = 0
        attempts = max(1, int(max_attempts or 1))
        for attempt in range(1, attempts + 1):
            result = request_once(self.token, method, payload, timeout=60)
            if result.ok:
                self._remember_success(method, recovered_error)
                return result.data
            error = TelegramAPIError(
                method,
                category=result.category,
                description=result.description,
                error_code=result.error_code,
                retry_after=result.retry_after,
                attempts=attempt,
            )
            self._remember_error(error)
            recovered_error = error
            if not result.retryable or attempt >= attempts:
                raise error
            delay = retry_delay_seconds(result, attempt)
            if waited_seconds + delay > TELEGRAM_MAX_RETRY_WAIT_SECONDS:
                raise error
            time.sleep(delay)
            waited_seconds += delay

        raise RuntimeError("Telegram request loop completed without a result")

    def get_updates(self, offset):
        payload = {"timeout": 50, "allowed_updates": '["message","callback_query"]'}
        if offset is not None:
            payload["offset"] = offset
        return self.request("getUpdates", payload).get("result", [])

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup)
        data = self.request("sendMessage", payload).get("result")
        if isinstance(data, dict) and isinstance(data.get("message_id"), int):
            return data["message_id"]
        return None

    def edit_message(
        self,
        chat_id,
        message_id,
        text,
        reply_markup=None,
    ):
        payload = {
            "chat_id": chat_id,
            "message_id": str(message_id),
            "text": text,
            "disable_web_page_preview": "true",
        }
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup)
        self.request(
            "editMessageText",
            payload,
        )

    def delete_message(self, chat_id, message_id):
        self.request(
            "deleteMessage",
            {"chat_id": chat_id, "message_id": str(message_id)},
            max_attempts=1,
        )

    def answer_callback(self, callback_id, text=""):
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        self.request("answerCallbackQuery", payload)
