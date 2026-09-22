"""Compatibility: umumiy implementatsiya tests.shared.progress modulida."""

from tests.shared.progress import (
    EVENT_PREFIX as EVENT_PREFIX,
    emit_progress_event as emit_progress_event,
)

__all__ = ["EVENT_PREFIX", "emit_progress_event"]
