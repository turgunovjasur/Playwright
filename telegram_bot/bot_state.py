"""Thread-safe active run and independent pending-request stores."""

from __future__ import annotations

from dataclasses import replace
import threading


class ActiveRunStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._active = None

    def get(self):
        with self._lock:
            return self._active

    def set(self, active):
        with self._lock:
            if self._active is not None:
                return False
            self._active = active
            return True

    def clear(self, run_id):
        with self._lock:
            if self._active is None:
                return
            if run_id is None or self._active.workflow_run.run_id == run_id:
                self._active = None

    def add_status_message(self, run_id, message_id):
        if message_id is None:
            return
        with self._lock:
            if self._active is None:
                return
            if run_id is not None and self._active.workflow_run.run_id != run_id:
                return
            message_ids = self._active.extra_status_message_ids
            if message_id == self._active.status_message_id or message_id in message_ids:
                return
            self._active = replace(
                self._active,
                extra_status_message_ids=message_ids + (message_id,),
            )


class PendingStore:
    """Chat bo'yicha pending so'rovlar; har bir instansiyaning holati alohida."""

    def __init__(self):
        self._lock = threading.Lock()
        self._pending = {}

    def set(self, chat_id, pending):
        with self._lock:
            self._pending[chat_id] = pending

    def get(self, chat_id):
        with self._lock:
            return self._pending.get(chat_id)

    def has(self, chat_id):
        with self._lock:
            return chat_id in self._pending

    def clear(self, chat_id):
        with self._lock:
            self._pending.pop(chat_id, None)
