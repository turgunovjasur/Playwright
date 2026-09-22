"""Relay test subprocess output and consume structured progress events."""

from __future__ import annotations

import json
import subprocess
import sys
import time

from .constants import EVENT_PREFIX
from .formatting import _utc_now_text, now_tashkent
from .paths import ROOT
from .progress_delivery import edit_progress
from .progress_state import load_state, save_state, sync_run_code_from_data_store, update_from_event
from .summaries import enrich_failed_result_from_summary, sync_summary_metrics


def command_run(args):
    command = args.command
    if not command:
        print("telegram_progress.py run: command is required", file=sys.stderr)
        return 2

    state = load_state()
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
    for line in process.stdout:
        print(line, end="", flush=True)
        if not line.startswith(EVENT_PREFIX):
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
