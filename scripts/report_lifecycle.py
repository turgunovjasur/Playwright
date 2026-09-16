"""Runner va direct pytest uchun summary, Allure va trace boshqaruvi."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

if __package__:
    from .allure_report_cli import AllureCliNotInstalled, build_generate_command, generate_report as generate_allure_report
else:
    from allure_report_cli import AllureCliNotInstalled, build_generate_command, generate_report as generate_allure_report


TRACE_DIR = "test-results/traces"
ALLURE_RESULTS_DIR = "test-results/allure-results"
ALLURE_REPORT_DIR = "test-results/allure-report"
ALLURE_CONFIG_PATH = "allurerc.mjs"
ALLURE_SERVER_LOG = "test-results/logs/allure-report-server.log"


def generate_test_summary(root_dir, env, *, test_exit, command_text, started_at, dry_run=False):
    """Faqat joriy run natijalari uchun analyzerni chaqiradi."""
    root_dir = Path(root_dir)
    command = [
        sys.executable, str(root_dir / "scripts" / "analyze_test_result.py"),
        "--exit-code", str(test_exit), "--command", command_text,
        "--started-at", str(started_at),
    ]
    print(" ".join(command))
    if dry_run:
        return 0
    return subprocess.call(command, cwd=root_dir, env=env)


def show_trace(root_dir, env, *, dry_run=False, background=False):
    """Oxirgi traceni runnerda kutib, direct pytestda fonda ochadi."""
    root_dir = Path(root_dir)
    playwright_bin = shutil.which("playwright")
    if not playwright_bin:
        executable = "playwright.exe" if os.name == "nt" else "playwright"
        virtualenv_playwright = Path(sys.executable).with_name(executable)
        if virtualenv_playwright.is_file():
            playwright_bin = str(virtualenv_playwright)
    if not playwright_bin:
        print("[TRACE] Playwright CLI topilmadi")
        return
    trace = max((root_dir / TRACE_DIR).glob("*.zip"), key=lambda path: path.stat().st_mtime, default=None)
    if trace is None:
        print("[TRACE] Trace fayli topilmadi")
        return
    command = [playwright_bin, "show-trace", str(trace)]
    print(" ".join(command))
    if dry_run:
        return
    if background:
        subprocess.Popen(command, cwd=root_dir, env=env)
    else:
        subprocess.call(command, cwd=root_dir, env=env)


def _open_report(root_dir, report_dir, env, *, dry_run, background):
    command = [sys.executable, str(root_dir / "scripts" / "open_allure_report.py"), str(report_dir)]
    print(" ".join(command))
    if dry_run:
        return 0
    if not background:
        return subprocess.call(command, cwd=root_dir, env=env)

    log_path = root_dir / ALLURE_SERVER_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)
    detach_options = (
        {"start_new_session": True}
        if os.name == "posix"
        else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
    )
    try:
        with log_path.open("a", encoding="utf-8") as server_log:
            subprocess.Popen(
                command, cwd=root_dir, env=env, stdout=server_log,
                stderr=subprocess.STDOUT, close_fds=True, **detach_options,
            )
    except OSError as error:
        print(f"[ALLURE] Lokal serverni ishga tushirib bo'lmadi: {error}")
        return 2
    print(f"[ALLURE] Server log: {log_path}")
    return 0


def generate_report(root_dir, env, *, open_report=False, dry_run=False, background=False):
    """Allure report yaratadi va so'ralganda mavjud ochish rejimida ko'rsatadi."""
    root_dir = Path(root_dir)
    results_dir = root_dir / ALLURE_RESULTS_DIR
    report_dir = root_dir / ALLURE_REPORT_DIR
    config_path = root_dir / ALLURE_CONFIG_PATH
    try:
        command = build_generate_command(results_dir, report_dir, config_path, project_root=root_dir)
        print(" ".join(command))
        result = generate_allure_report(
            results_dir, report_dir, config_path, project_root=root_dir,
            env=env, dry_run=dry_run,
        )
    except (AllureCliNotInstalled, OSError, ValueError) as error:
        print(f"[ALLURE] Report generate failed: {error}")
        return 2
    if result.returncode != 0:
        print(f"[ALLURE] Report generate failed: exit_code={result.returncode}")
        return result.returncode
    if open_report:
        return _open_report(root_dir, report_dir, env, dry_run=dry_run, background=background)
    return 0
