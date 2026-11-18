"""Relay test subprocess output and consume structured progress events."""

from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time

from .constants import EVENT_PREFIX, NIGHTLY_TARGETS, PROGRESS_EDIT_INTERVAL_SECONDS
from .formatting import _utc_now_text, now_tashkent
from .paths import ROOT
from .progress_delivery import edit_progress
from .progress_state import load_state, save_state, sync_run_code_from_data_store, update_from_event
from .summaries import enrich_failed_result_from_summary, sync_summary_metrics


def run_phase(command, phase, state):
    """Sample an atomic pytest snapshot, including tests shorter than a poll."""
    phases = state.setdefault("phases", {})
    progress = {"outcome": "running", "total": phases.get(phase, {}).get("total", 0)}
    phases[phase] = progress
    state["status"] = phase

    def publish(path, *, boundary=False):
        if path.is_file():
            progress.update(json.loads(path.read_text(encoding="utf-8")))
            if phase == "API setup" and "Order regression" not in phases:
                from tests.regression.test_orders.helpers.ordering import GROUP_NAMES
                from tests.regression.test_orders.helpers.reporting import group_test_numbers

                phases["Order regression"] = {
                    "outcome": "pending",
                    "total": sum(len(group_test_numbers(group)) for group in GROUP_NAMES),
                }
        save_state(state)
        if time.time() >= float(state.get("telegram_backoff_until") or 0):
            edit_progress(state, force=boundary)

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "current-test"
        publish(path, boundary=True)
        env = os.environ.copy()
        env.pop("TELEGRAM_BOT_TOKEN", None)
        env.pop("TELEGRAM_CHAT_ID", None)
        env["SMARTUP_CURRENT_TEST_FILE"] = str(path)
        env["PYTEST_ADDOPTS"] = (env.get("PYTEST_ADDOPTS", "") + " -p tests.shared.telegram_current_test").strip()
        with subprocess.Popen(command, cwd=ROOT, env=env) as process:
            while True:
                try:
                    code = process.wait(timeout=PROGRESS_EDIT_INTERVAL_SECONDS)
                    break
                except subprocess.TimeoutExpired:
                    publish(path)
        progress["outcome"] = "failed" if code else "passed"
        publish(path, boundary=True)
    return code


def progress_lines(output):
    """Flush throttled edits even while a long-running test produces no output."""
    events = queue.Queue()

    def relay():
        try:
            for line in output:
                print(line, end="", flush=True)
                if line.startswith(EVENT_PREFIX):
                    events.put(line)
        finally:
            events.put(None)

    threading.Thread(target=relay, daemon=True).start()
    while True:
        try:
            line = events.get(timeout=PROGRESS_EDIT_INTERVAL_SECONDS)
        except queue.Empty:
            yield ""
            continue
        if line is None:
            return
        yield line


def command_run(args):
    command = args.command
    if not command:
        print("telegram_progress.py run: command is required", file=sys.stderr)
        return 2

    state = load_state()
    if args.phase:
        return run_phase(command, args.phase, state)
    now = now_tashkent()
    state["status"] = "Testlar boshlanmoqda"
    state["test_started_at"] = now.strftime("%Y-%m-%d %H:%M:%S UZT")
    state["test_started_at_utc"] = _utc_now_text()
    state["test_started_epoch"] = time.time()
    save_state(state)
    edit_progress(state, force=True)
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in progress_lines(process.stdout):
        if not line:
            if state.get("target") in NIGHTLY_TARGETS:
                edit_progress(state)
            continue
        try:
            event = json.loads(line[len(EVENT_PREFIX):])
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        update_from_event(state, event)
        sync_run_code_from_data_store(state)
        save_state(state)
        edit_progress(state)

    exit_code = process.wait()
    sync_summary_metrics(state)
    if exit_code:
        enrich_failed_result_from_summary(state)
    save_state(state)
    edit_progress(state)
    return exit_code
