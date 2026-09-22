"""Hourly scheduling and active-run checks before dispatch."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import time

from .models import RunRequest
from .runs import find_busy_run


class HourlyScheduler:
    def __init__(self, config, *, dispatch_slot, now_provider=None, wait=None, logger=None):
        self.config = config
        self.timezone = ZoneInfo(config.timezone_name)
        self.dispatch_slot = dispatch_slot
        self.now_provider = now_provider or datetime.now
        self.wait = wait or time.sleep
        self.logger = logger or print
        self._last_slot = None

    def tick(self):
        if not self.config.enabled:
            return "disabled"

        now = self.now_provider(self.timezone)
        if now.minute != self.config.minute:
            return "waiting"

        slot = now.strftime("%Y-%m-%dT%H")
        if slot == self._last_slot:
            return "already-checked"

        self._last_slot = slot
        return self.dispatch_slot(slot)

    def run_forever(self):
        while True:
            try:
                self.tick()
            except Exception as exc:
                self.logger(
                    f"Hourly scheduler error: {exc.__class__.__name__}",
                    file=sys.stderr,
                )
            self.wait(15)


def dispatch_hourly_slot(github, active_store, dispatch_lock, config, slot):
    with dispatch_lock:
        busy_run, _local_active = find_busy_run(github, active_store)
        if busy_run is not None:
            print(f"Hourly scheduler slot={slot} skipped-active run_id={busy_run.run_id}")
            return "skipped-active"

        workflow_run = github.dispatch(
            RunRequest(suite_key="all", server_key=config.server_key)
        )

    print(
        f"Hourly scheduler slot={slot} dispatched run_id={workflow_run.run_id} "
        f"url={workflow_run.html_url}"
    )
    return "dispatched"
