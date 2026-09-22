"""Shared display labels and explicit bot/CI delivery policies."""

from __future__ import annotations

from datetime import timedelta, timezone

STATUS_POLL_INTERVAL_SECONDS = 30

STATUS_POLL_ERROR_LIMIT = 5

TELEGRAM_REQUEST_ATTEMPTS = 3

TELEGRAM_RETRY_DELAYS_SECONDS = (2, 5, 10)

TELEGRAM_MAX_RETRY_WAIT_SECONDS = 10

TASHKENT_TZ = timezone(timedelta(hours=5))

SUITES = {
    "smoke": "Smoke",
    "forms": "Forms",
}

WORKFLOW_JOB_SUITES = ("Smoke", "Report", "Forms")

WORKFLOW_JOB_ORDER = {suite: index for index, suite in enumerate(WORKFLOW_JOB_SUITES)}

DELIVERY_SUITE_ORDER = {
    "Smoke": 0,
    "Report": 1,
    "Report Group": 1,
    "Forms": 2,
}

ACTIVE_WORKFLOW_RUN_STATUSES = (
    "queued",
    "in_progress",
    "waiting",
    "requested",
    "pending",
)

EVENT_PREFIX = "SMARTUP_PROGRESS "

MAX_MESSAGE_LENGTH = 3900

OPERATIONAL_FILIAL_PLACEHOLDER = "<operatsion filial>"

PROGRESS_EDIT_INTERVAL_SECONDS = 10

FINAL_DELIVERY_ATTEMPTS = TELEGRAM_REQUEST_ATTEMPTS

FINAL_RETRY_WAIT_BUDGET_SECONDS = TELEGRAM_MAX_RETRY_WAIT_SECONDS

TARGET_LABELS = {
    "all": "All",
    "setup": "Setup",
    "setup-group-0": "Smoke",
    "setup-smoke": "Smoke",
    "setup-report": "Setup + Report",
    "setup-a2-admin": "Setup + A2 Admin Forms",
    "setup-forms": "Setup + Forms",
    "company": "Company",
    "groups": "Groups",
    "group-report": "Report Group",
    "forms": "Forms",
}

TARGET_SUITE_LABELS = {
    "all": "All",
    "setup": "Setup",
    "setup-group-0": "Smoke · Setup + A group",
    "setup-smoke": "Smoke · Setup + 0 group + Visit group",
    "setup-report": "Setup + Report group",
    "setup-a2-admin": "Setup + A2 Admin Forms",
    "setup-forms": "Setup + Forms",
    "company": "Company",
    "groups": "Groups",
    "group-report": "Report group",
    "forms": "Forms",
}

GROUP_ORDER = [
    "Setup",
    "0 group",
    "visit group",
    "A2 Admin Forms group",
    "Report group",
    "Forms group",
]

STATUS_MARK = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭"}

AI_CONFIDENCE_LABELS = {
    "low": "past",
    "medium": "o‘rta",
    "high": "yuqori",
}
