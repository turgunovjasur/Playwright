"""Data records shared by the bot, scheduler and GitHub client."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import SUITES


@dataclass(frozen=True)
class RunRequest:
    suite_key: str
    server_key: str

    @property
    def suite_label(self):
        return SUITES[self.suite_key]


@dataclass(frozen=True)
class WorkflowRun:
    run_id: int | None
    html_url: str
    status: str = ""
    conclusion: str | None = None
    event: str = ""


@dataclass(frozen=True)
class WorkflowJob:
    suite: str
    status: str
    conclusion: str | None = None
    current_step: str = ""


@dataclass(frozen=True)
class CancelRunsResult:
    active_run_ids: tuple[int, ...]
    cancelled_run_ids: tuple[int, ...]
    failed_run_ids: tuple[int, ...]


@dataclass(frozen=True)
class ActiveRun:
    chat_id: str
    request: RunRequest
    workflow_run: WorkflowRun
    started_at: float
    status_message_id: int | None
    extra_status_message_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class PendingRun:
    request: RunRequest
    prompt_message_id: int


@dataclass(frozen=True)
class PendingStop:
    prompt_message_id: int | None


@dataclass(frozen=True)
class BotConfig:
    telegram_token: str
    run_password: str
    github_token: str
    repository: str
    workflow: str
    ref: str
    servers: dict[str, str]
    allowed_server_keys: set[str]
    hourly_schedule: HourlyScheduleConfig


@dataclass(frozen=True)
class HourlyScheduleConfig:
    enabled: bool
    minute: int
    timezone_name: str
    server_key: str
