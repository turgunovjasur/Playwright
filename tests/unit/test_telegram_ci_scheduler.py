import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "telegram_ci_bot.py"


def _load_bot_module():
    spec = importlib.util.spec_from_file_location("telegram_ci_bot_scheduler_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bot = _load_bot_module()
SCHEDULE_ENV_NAMES = (
    "HOURLY_SCHEDULE_ENABLED",
    "HOURLY_SCHEDULE_MINUTE",
    "HOURLY_SCHEDULE_TIMEZONE",
    "HOURLY_SCHEDULE_SERVER",
)


def _clear_schedule_env(monkeypatch):
    for name in SCHEDULE_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def _config(**overrides):
    values = {
        "enabled": True,
        "minute": 17,
        "timezone_name": "Asia/Tashkent",
        "server_key": "smartup",
    }
    values.update(overrides)
    return bot.HourlyScheduleConfig(**values)


def test_hourly_schedule_config_defaults_to_disabled(monkeypatch):
    _clear_schedule_env(monkeypatch)

    config = bot.load_hourly_schedule_config({"smartup", "app3"})

    assert config == bot.HourlyScheduleConfig(
        enabled=False,
        minute=17,
        timezone_name="Asia/Tashkent",
        server_key="smartup",
    )


def test_hourly_schedule_config_reads_valid_server_values(monkeypatch):
    _clear_schedule_env(monkeypatch)
    monkeypatch.setenv("HOURLY_SCHEDULE_ENABLED", "1")
    monkeypatch.setenv("HOURLY_SCHEDULE_MINUTE", "17")
    monkeypatch.setenv("HOURLY_SCHEDULE_TIMEZONE", "Asia/Tashkent")
    monkeypatch.setenv("HOURLY_SCHEDULE_SERVER", "smartup")

    config = bot.load_hourly_schedule_config({"smartup"})

    assert config == _config()


@pytest.mark.parametrize("value", ["-1", "60", "not-a-number"])
def test_hourly_schedule_config_rejects_invalid_minute(monkeypatch, value):
    _clear_schedule_env(monkeypatch)
    monkeypatch.setenv("HOURLY_SCHEDULE_MINUTE", value)

    with pytest.raises(bot.ConfigError, match="HOURLY_SCHEDULE_MINUTE"):
        bot.load_hourly_schedule_config({"smartup"})


def test_hourly_schedule_config_rejects_invalid_timezone(monkeypatch):
    _clear_schedule_env(monkeypatch)
    monkeypatch.setenv("HOURLY_SCHEDULE_TIMEZONE", "Invalid/Timezone")

    with pytest.raises(bot.ConfigError, match="HOURLY_SCHEDULE_TIMEZONE"):
        bot.load_hourly_schedule_config({"smartup"})


def test_hourly_schedule_config_rejects_server_outside_allow_list(monkeypatch):
    _clear_schedule_env(monkeypatch)
    monkeypatch.setenv("HOURLY_SCHEDULE_ENABLED", "1")
    monkeypatch.setenv("HOURLY_SCHEDULE_SERVER", "app3")

    with pytest.raises(bot.ConfigError, match="HOURLY_SCHEDULE_SERVER"):
        bot.load_hourly_schedule_config({"smartup"})


def test_disabled_hourly_schedule_does_not_require_its_server_in_allow_list(monkeypatch):
    _clear_schedule_env(monkeypatch)

    config = bot.load_hourly_schedule_config({"app3"})

    assert config.enabled is False


def test_hourly_scheduler_dispatches_once_at_configured_minute():
    times = iter(
        (
            datetime(2026, 9, 4, 10, 16),
            datetime(2026, 9, 4, 10, 17),
            datetime(2026, 9, 4, 10, 17, 45),
        )
    )
    dispatched_slots = []
    scheduler = bot.HourlyScheduler(
        _config(),
        dispatch_slot=lambda slot: dispatched_slots.append(slot) or "dispatched",
        now_provider=lambda _timezone: next(times),
    )

    assert scheduler.tick() == "waiting"
    assert scheduler.tick() == "dispatched"
    assert scheduler.tick() == "already-checked"
    assert dispatched_slots == ["2026-09-04T10"]


def test_hourly_scheduler_does_not_catch_up_missed_slot():
    dispatched_slots = []
    scheduler = bot.HourlyScheduler(
        _config(),
        dispatch_slot=lambda slot: dispatched_slots.append(slot) or "dispatched",
        now_provider=lambda _timezone: datetime(2026, 9, 4, 10, 18),
    )

    assert scheduler.tick() == "waiting"
    assert dispatched_slots == []


class _ActiveStore:
    def get(self):
        return None


class _SpyLock:
    def __init__(self):
        self.entered = 0

    def __enter__(self):
        self.entered += 1
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class _GitHub:
    def __init__(self, active_run=None):
        self.active_run = active_run
        self.dispatched = []

    def find_active_run(self):
        return self.active_run

    def dispatch(self, request, telegram_progress_message_id=None):
        self.dispatched.append((request, telegram_progress_message_id))
        return bot.WorkflowRun(run_id=123, html_url="https://example.test/run/123")


def test_hourly_dispatch_skips_when_workflow_is_active():
    github = _GitHub(active_run=bot.WorkflowRun(run_id=99, html_url="https://example.test/run/99"))
    lock = _SpyLock()

    result = bot.dispatch_hourly_slot(github, _ActiveStore(), lock, _config(), "2026-09-04T10")

    assert result == "skipped-active"
    assert github.dispatched == []
    assert lock.entered == 1


def test_hourly_dispatch_sends_all_suite_to_configured_server():
    github = _GitHub()
    lock = _SpyLock()

    result = bot.dispatch_hourly_slot(github, _ActiveStore(), lock, _config(), "2026-09-04T10")

    assert result == "dispatched"
    assert github.dispatched == [
        (bot.RunRequest(suite_key="all", server_key="smartup"), None)
    ]
    assert lock.entered == 1


def test_scheduler_loop_contains_dispatch_exception_and_keeps_polling():
    logs = []

    class StopLoop(Exception):
        pass

    def fail_dispatch(_slot):
        raise RuntimeError("sensitive upstream response")

    def stop_after_first_tick(_seconds):
        raise StopLoop

    scheduler = bot.HourlyScheduler(
        _config(),
        dispatch_slot=fail_dispatch,
        now_provider=lambda _timezone: datetime(2026, 9, 4, 10, 17),
        wait=stop_after_first_tick,
        logger=lambda message, **_kwargs: logs.append(message),
    )

    with pytest.raises(StopLoop):
        scheduler.run_forever()

    assert logs == ["Hourly scheduler error: RuntimeError"]


def test_manual_start_run_uses_shared_dispatch_lock():
    class Telegram:
        def __init__(self):
            self.edits = []

        def edit_message(self, chat_id, message_id, text):
            self.edits.append((chat_id, message_id, text))

    class ManualGitHub(_GitHub):
        def dispatch(self, request, telegram_progress_message_id=None):
            self.dispatched.append((request, telegram_progress_message_id))
            return bot.WorkflowRun(run_id=None, html_url="https://example.test/workflow")

    telegram = Telegram()
    github = ManualGitHub()
    lock = _SpyLock()
    request = bot.RunRequest(suite_key="smoke", server_key="smartup")

    bot.start_run(telegram, github, "42", 7, request, _ActiveStore(), lock)

    assert lock.entered == 1
    assert github.dispatched == [(request, 7)]


def test_daily_workflow_uses_server_dispatched_all_suite_without_github_cron():
    workflow = (ROOT / ".github" / "workflows" / "daily-smoke.yml").read_text(encoding="utf-8")

    assert "\n  schedule:" not in workflow
    assert "          - all\n" in workflow
    assert workflow.count("inputs.suite == 'all'") == 3
    assert "needs: smoke" in workflow
