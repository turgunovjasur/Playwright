"""FormMonitor observation diagnostikalari uchun public package API."""

from tests.smoke.test_forms.monitoring.diagnostics.core import (
    DIAGNOSTIC_NAMES,
    FormDiagnostics,
    capture_form_state,
)
from tests.smoke.test_forms.monitoring.diagnostics.failed_requests import (
    MAX_PAGE_EVENTS,
)


__all__ = [
    "DIAGNOSTIC_NAMES",
    "FormDiagnostics",
    "MAX_PAGE_EVENTS",
    "capture_form_state",
]
