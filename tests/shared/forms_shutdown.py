"""Limit final Forms cleanup even when the pytest interpreter is stuck."""

import os
from pathlib import Path
import signal
import subprocess
import sys
import threading


FORMS_SHUTDOWN_SECONDS = 120


def arm_forms_shutdown(config):
    if getattr(config, "_smartup_forms_shutdown_armed", False):
        return
    watcher = subprocess.Popen(
        [sys.executable, "-I", str(Path(__file__).resolve()),
         str(os.getpid()), str(FORMS_SHUTDOWN_SECONDS)],
        stdin=subprocess.PIPE,
        start_new_session=(os.name == "posix"),
    )
    config._smartup_forms_shutdown_armed = True

    def disarm():
        watcher.stdin.close()
        watcher.wait()

    config.add_cleanup(disarm)


def watch_pytest(parent_pid, seconds):
    # The private pipe closes on clean teardown or if the parent already exited.
    def stop_stuck_run():
        if os.getppid() == parent_pid:
            # The Playwright driver closes its browsers when its parent pipe closes.
            os.kill(parent_pid, getattr(signal, "SIGKILL", signal.SIGTERM))
            print(f"[Forms] Pytest cleanup exceeded {seconds:g}s (PID {parent_pid}).",
                  file=sys.stderr, flush=True)

    deadline = threading.Timer(seconds, stop_stuck_run)
    deadline.start()
    try:
        os.read(0, 1)
    finally:
        deadline.cancel()
        deadline.join()


if __name__ == "__main__":
    watch_pytest(int(sys.argv[1]), float(sys.argv[2]))
