"""Smoke test progressi, xato diagnostikasi va Allure report boshqaruvi."""

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import allure
import pytest

from tests.smoke.progress import emit_progress_event
from tests.smoke.smoke_config import env_flag, is_headless
from utils.logger import write_failure_log


TRACE_DIR = "test-results/traces"
ALLURE_RESULTS_DIR = "test-results/allure-results"
ALLURE_REPORT_DIR = "test-results/allure-report"
ALLURE_SERVER_LOG = "test-results/logs/allure-report-server.log"

_PROGRESS_STARTED_ATTR = "_smartup_progress_started"
_PROGRESS_FINISHED_ATTR = "_smartup_progress_finished"


def smoke_group_name(item):
    """Test itemidagi `smoke_group` markeridan group nomini qaytaradi."""
    marker = item.get_closest_marker("smoke_group")
    if not marker:
        return None
    if not marker.args:
        raise pytest.UsageError(
            "smoke_group marker group nomini talab qiladi: "
            "@pytest.mark.smoke_group('A')"
        )
    return str(marker.args[0])


def smoke_group_independent(item):
    """Group ichidagi testlar bir-biridan mustaqil belgilanganini tekshiradi."""
    marker = item.get_closest_marker("smoke_group")
    return bool(marker and marker.kwargs.get("independent", False))


def is_user_setup(item):
    """Test item `user_setup` chainiga tegishli ekanini tekshiradi."""
    return item.get_closest_marker("user_setup") is not None


def _progress_metadata(item):
    """Progress event uchun test groupi, runneri va ko'rinadigan nomini yig'adi."""
    if is_user_setup(item):
        group = "Setup"
    else:
        group_name = smoke_group_name(item)
        if not group_name:
            return None
        group = f"{group_name} group"

    title = (
        getattr(getattr(item, "obj", None), "__allure_display_name__", None)
        or item.name
    )
    return {
        "group": group,
        "runner": Path(str(item.path)).name,
        "test_id": item.name,
        "title": title,
    }


def start_progress(item):
    """Test uchun `started` progress eventini faqat bir marta chiqaradi."""
    metadata = _progress_metadata(item)
    if not metadata or getattr(item, _PROGRESS_STARTED_ATTR, False):
        return
    setattr(item, _PROGRESS_STARTED_ATTR, True)
    emit_progress_event(event="started", **metadata)


def finish_progress(item, event, *, error_type=None, message=None):
    """Test yakuniy progress eventini faqat bir marta chiqaradi."""
    metadata = _progress_metadata(item)
    if not metadata or getattr(item, _PROGRESS_FINISHED_ATTR, False):
        return
    setattr(item, _PROGRESS_FINISHED_ATTR, True)
    emit_progress_event(
        event=event,
        error_type=error_type,
        message=message,
        **metadata,
    )


def report_message(report):
    """Pytest reportdan birinchi foydali xato yoki skip qatorini oladi."""
    report_text = str(report.longrepr or "").strip()
    if not report_text:
        return ""
    return next(
        (
            line.strip()
            for line in report_text.splitlines()
            if line.strip()
        ),
        "",
    )


def prepare_allure_results(config, run_info, root_dir):
    """Run boshida Allure history, environment, categories va executorni tayyorlaydi."""
    root_dir = Path(root_dir)
    results_dir = root_dir / ALLURE_RESULTS_DIR
    report_dir = root_dir / ALLURE_REPORT_DIR
    results_dir.mkdir(parents=True, exist_ok=True)

    history_source = report_dir / "history"
    history_destination = results_dir / "history"
    if history_source.exists():
        shutil.rmtree(history_destination, ignore_errors=True)
        try:
            shutil.copytree(
                history_source,
                history_destination,
                dirs_exist_ok=True,
            )
        except FileNotFoundError:
            pass

    environment_path = results_dir / "environment.properties"
    with environment_path.open("w", encoding="utf-8") as environment_file:
        environment_file.write("Browser=Chromium\n")
        environment_file.write(
            f"Browser.Headless={is_headless(config)}\n"
        )
        environment_file.write(f"Company.URL={run_info['company_url']}\n")
        environment_file.write(
            f"Company.Create={run_info['create_company']}\n"
        )
        if not run_info["create_company"]:
            environment_file.write(
                f"Company.Code={run_info['company_code']}\n"
            )
        environment_file.write("Framework=Playwright\n")
        environment_file.write("Language=Python 3.11\n")
        environment_file.write("Environment=Staging\n")
        environment_file.write(f"Host={socket.gethostname()}\n")

    categories_source = root_dir / "allure" / "categories.json"
    categories_destination = results_dir / "categories.json"
    if categories_source.exists():
        shutil.copy(categories_source, categories_destination)

    executor_path = results_dir / "executor.json"
    executor_data = {
        "name": socket.gethostname(),
        "type": "local",
        "buildName": "Smoke Tests",
        "reportName": "Allure Report",
    }
    with executor_path.open("w", encoding="utf-8") as executor_file:
        json.dump(executor_data, executor_file, indent=2)


def attach_failure_artifacts(item, data_path):
    """Failed testning URL, title, screenshot va data-store holatini Allurega qo'shadi."""
    page = (
        item.funcargs.get("session_page")
        or item.funcargs.get("group_user_page")
        or item.funcargs.get("group_session_page")
        or item.funcargs.get("page")
    )
    if page:
        try:
            allure.attach(
                page.url,
                name="current-url",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                page.title(),
                name="page-title",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name="failure-hook-error",
                attachment_type=allure.attachment_type.TEXT,
            )

    data_path = Path(data_path)
    if data_path.exists():
        allure.attach(
            data_path.read_text(encoding="utf-8"),
            name="data-store",
            attachment_type=allure.attachment_type.JSON,
        )


def log_failed_report(report):
    """Failed pytest fazasini `test-results/logs` ichidagi matn logiga yozadi."""
    if not report.failed:
        return
    longrepr_text = str(report.longrepr) if report.longrepr else "Xabar yo'q"
    log_path = write_failure_log(report.nodeid, report.when, longrepr_text)
    print(f"\n[LOG] Xato logi saqlandi: {log_path}")


def finish_session(root_dir):
    """Direct pytest run tugaganda so'ralgan trace viewer yoki Allure reportni ochadi."""
    if env_flag("SMARTUP_RUNNER"):
        return

    root_dir = Path(root_dir)
    if env_flag("SHOW_TRACE"):
        _open_latest_trace(root_dir)

    if env_flag("OPEN_REPORT"):
        _generate_and_open_allure_report(root_dir)


def _open_latest_trace(root_dir):
    """Eng oxirgi Playwright trace faylini CLI viewerda ochadi."""
    playwright_bin = shutil.which("playwright")
    if not playwright_bin:
        virtualenv_playwright = Path(sys.executable).with_name("playwright")
        if virtualenv_playwright.is_file():
            playwright_bin = str(virtualenv_playwright)

    trace_dir = root_dir / TRACE_DIR
    traces = (
        sorted(
            trace_dir.glob("*.zip"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        if trace_dir.exists()
        else []
    )
    if not playwright_bin:
        print("\n[TRACE] SHOW_TRACE=1, lekin playwright CLI topilmadi")
    elif not traces:
        print("\n[TRACE] SHOW_TRACE=1, lekin trace fayli topilmadi")
    else:
        print(f"\n[TRACE] Trace ochilmoqda: {traces[0]}")
        subprocess.Popen(
            [playwright_bin, "show-trace", str(traces[0])],
            cwd=root_dir,
        )


def _generate_and_open_allure_report(root_dir):
    """Allure HTML reportini generatsiya qiladi va lokal serverda ochadi."""
    allure_bin = shutil.which("allure")
    if not allure_bin:
        print("\n[ALLURE] OPEN_REPORT=1, lekin allure CLI topilmadi")
        return

    generate_command = [
        allure_bin,
        "generate",
        str(root_dir / ALLURE_RESULTS_DIR),
        "-o",
        str(root_dir / ALLURE_REPORT_DIR),
        "--clean",
    ]
    open_command = [
        sys.executable,
        str(root_dir / "scripts" / "open_allure_report.py"),
        str(root_dir / ALLURE_REPORT_DIR),
    ]

    print("\n[ALLURE] Report generate qilinmoqda...")
    generate_result = subprocess.call(generate_command, cwd=root_dir)
    if generate_result != 0:
        print(f"[ALLURE] Report generate failed: exit_code={generate_result}")
        return

    print("[ALLURE] Report ochilmoqda...")
    server_log_path = root_dir / ALLURE_SERVER_LOG
    server_log_path.parent.mkdir(parents=True, exist_ok=True)
    detach_options = (
        {"start_new_session": True}
        if os.name == "posix"
        else {
            "creationflags": (
                subprocess.CREATE_NEW_PROCESS_GROUP
                | subprocess.DETACHED_PROCESS
            )
        }
    )
    try:
        with server_log_path.open("a", encoding="utf-8") as server_log:
            subprocess.Popen(
                open_command,
                cwd=root_dir,
                stdout=server_log,
                stderr=subprocess.STDOUT,
                close_fds=True,
                **detach_options,
            )
    except OSError as exc:
        print(f"[ALLURE] Lokal serverni ishga tushirib bo'lmadi: {exc}")
        return
    print(f"[ALLURE] Server log: {server_log_path}")
