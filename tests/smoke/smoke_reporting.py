"""Smoke test progressi, xato diagnostikasi va Allure report boshqaruvi."""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit

import allure
import pytest

from scripts.allure_report_cli import (
    AllureCliNotInstalled,
    build_generate_command,
    generate_report,
)
from tests.smoke.progress import emit_progress_event
from tests.smoke.screenshot_masking import masked_page_screenshot
from tests.smoke.smoke_config import env_flag, is_headless
from utils.logger import write_failure_log


TRACE_DIR = "test-results/traces"
ALLURE_RESULTS_DIR = "test-results/allure-results"
ALLURE_REPORT_DIR = "test-results/allure-report"
ALLURE_CONFIG_PATH = "allurerc.mjs"
ALLURE_SERVER_LOG = "test-results/logs/allure-report-server.log"

_PROGRESS_STARTED_ATTR = "_smartup_progress_started"
_PROGRESS_FINISHED_ATTR = "_smartup_progress_finished"
_AUTH_LISTENER_ATTR = "_smartup_auth_diagnostics_installed"
_AUTH_RESPONSE_ATTR = "_smartup_first_unauthorized_response"
_LICENSE_401_MESSAGE = "Нет лицензии для входа в систему!"


def safe_page_url(value):
    """Smartup session tokenini URL diagnostikasidan yashiradi."""
    return re.sub(r"(#/)[^/]+", r"\1<session>", str(value or ""), count=1)


def safe_page_screenshot(page, *, full_page=True, mask_profile=None):
    """Secretlar va explicit forma profilini masklab screenshot oladi."""
    return masked_page_screenshot(
        page,
        full_page=full_page,
        profile_name=mask_profile,
    )


def page_from_item(item):
    """Test item ishlatayotgan asosiy Playwright page'ini qaytaradi."""
    for fixture_name in (
        "session_page",
        "group_user_page",
        "group_session_page",
        "page",
    ):
        page = item.funcargs.get(fixture_name)
        if page is not None:
            return page
    return None


def install_auth_diagnostics(page):
    """Page'dagi birinchi HTTP 401 response'ni failure diagnostikasi uchun saqlaydi."""
    if getattr(page, _AUTH_LISTENER_ATTR, False):
        return

    setattr(page, _AUTH_LISTENER_ATTR, True)
    setattr(page, _AUTH_RESPONSE_ATTR, None)

    def remember_first_unauthorized(response):
        try:
            status = int(response.status)
        except (AttributeError, TypeError, ValueError):
            return
        if status != 401 or getattr(page, _AUTH_RESPONSE_ATTR, None) is not None:
            return
        try:
            response_host = urlsplit(str(response.url or "")).netloc
            page_host = urlsplit(str(page.url or "")).netloc
        except Exception:
            response_host = page_host = ""
        if response_host and page_host and response_host != page_host:
            return
        setattr(page, _AUTH_RESPONSE_ATTR, response)

    page.on("response", remember_first_unauthorized)


def reset_auth_diagnostics(item):
    """Keyingi test avvalgi testning 401 holatini meros qilib olmasligini ta'minlaydi."""
    page = page_from_item(item)
    if page is not None and getattr(page, _AUTH_LISTENER_ATTR, False):
        setattr(page, _AUTH_RESPONSE_ATTR, None)


def _safe_response_message(response):
    try:
        text = response.text()
    except Exception:
        return ""

    clean = " ".join(str(text or "").split())
    if not clean:
        return ""
    if _LICENSE_401_MESSAGE.casefold() in clean.casefold():
        return _LICENSE_401_MESSAGE
    if clean.casefold() in {"unauthorized", "401 unauthorized"}:
        return clean
    return ""


def _auth_ui_state(page):
    try:
        current_path = urlsplit(page.url).path
    except Exception:
        current_path = ""
    if current_path.endswith("/login.html"):
        return "login_redirect"

    try:
        lock = page.locator("#closing-session .cs-lock.open").first
        if lock.is_visible():
            return "session_lock"
    except Exception:
        pass
    return "current_page"


def auth_diagnostic_for_item(item):
    """Saqlangan 401'ni credentiallarsiz, user-facing diagnostikaga aylantiradi."""
    page = page_from_item(item)
    if page is None:
        return None

    response = getattr(page, _AUTH_RESPONSE_ATTR, None)
    if response is None:
        return None

    try:
        request_method = str(response.request.method or "REQUEST").upper()
    except Exception:
        request_method = "REQUEST"
    try:
        request_path = urlsplit(str(response.url or "")).path or "/"
    except Exception:
        request_path = "/"

    server_message = _safe_response_message(response)
    ui_state = _auth_ui_state(page)
    is_license_401 = _LICENSE_401_MESSAGE.casefold() in server_message.casefold()
    kind = (
        "license_session_unauthorized"
        if is_license_401
        else "auth_session_unauthorized"
    )
    error_type = (
        "LicenseSessionUnauthorized"
        if is_license_401
        else "AuthSessionUnauthorized"
    )
    cause = (
        "Backend license/session kirishini rad etdi"
        if is_license_401
        else "Backend sessiya so'rovini rad etdi"
    )
    ui_labels = {
        "login_redirect": "login sahifasiga redirect",
        "session_lock": "qayta login lock oynasi",
        "current_page": "joriy sahifa",
    }
    summary = f"{cause}: {request_method} {request_path} → HTTP 401"
    if server_message:
        summary += f'; server="{server_message}"'
    summary += f"; UI={ui_labels[ui_state]}"

    return {
        "kind": kind,
        "error_type": error_type,
        "method": request_method,
        "path": request_path,
        "status": 401,
        "server_message": server_message,
        "ui_state": ui_state,
        "summary": summary,
    }


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


def smoke_group_setup_independent(item):
    """Setup failed bo'lsa ham group ishlashi kerakligini tekshiradi."""
    marker = item.get_closest_marker("smoke_group")
    return bool(marker and marker.kwargs.get("setup_independent", False))


def is_user_setup(item):
    """Test item `user_setup` chainiga tegishli ekanini tekshiradi."""
    return item.get_closest_marker("user_setup") is not None


def _form_case_from_item(item):
    """Parametrized Forms itemidagi structured case metadata'ni qaytaradi."""
    callspec = getattr(item, "callspec", None)
    params = getattr(callspec, "params", None)
    if not isinstance(params, Mapping):
        return None
    form_case = params.get("form_case")
    return form_case if isinstance(form_case, Mapping) else None


def _form_progress_context(item):
    """Telegram progress uchun user-readable forma kontekstini normalize qiladi."""
    form_case = _form_case_from_item(item)
    if form_case is None:
        return None

    try:
        number = int(form_case.get("global_number"))
    except (TypeError, ValueError):
        number = 0

    return {
        "number": number,
        "navbar": str(form_case.get("navbar_tab") or "").strip(),
        "menu": str(form_case.get("menu_column") or "").strip(),
        "title": str(
            form_case.get("label")
            or form_case.get("title")
            or form_case.get("menu_item")
            or item.name
        ).strip(),
        "filial": str(form_case.get("filial") or "").strip(),
        "expected_url": str(form_case.get("expected_path") or "").strip(),
    }


def _form_progress_display(context):
    """Forma raqami va UI yo'lidan Telegramda ko'rinadigan nom yasaydi."""
    path = " → ".join(
        value
        for value in (
            context.get("navbar"),
            context.get("menu"),
            context.get("title"),
        )
        if value
    )
    number = int(context.get("number") or 0)
    return f"{number:03d} | {path or 'Noma’lum forma'}"


def _form_progress_total(item):
    """Joriy pytest collectiondagi parametrized Forms itemlar sonini qaytaradi."""
    session = getattr(item, "session", None)
    items = getattr(session, "items", ())
    return sum(_form_case_from_item(candidate) is not None for candidate in items)


def _progress_test_total(item):
    """Joriy collectiondagi Telegram progress testlari sonini qaytaradi."""
    session = getattr(item, "session", None)
    items = getattr(session, "items", ())
    return sum(
        is_user_setup(candidate) or bool(smoke_group_name(candidate))
        for candidate in items
    )


def _progress_metadata(item):
    """Progress event uchun test groupi, runneri va ko'rinadigan nomini yig'adi."""
    if is_user_setup(item):
        group = "Setup"
    else:
        group_name = smoke_group_name(item)
        if not group_name:
            return None
        group = f"{group_name} group"

    allure_title = (
        getattr(getattr(item, "obj", None), "__allure_display_name__", None)
        or item.name
    )
    metadata = {
        "group": group,
        "runner": Path(str(item.path)).name,
        "test_id": item.name,
        "title": allure_title,
        "test_total": _progress_test_total(item),
    }
    form_context = _form_progress_context(item)
    if form_context is not None:
        display = _form_progress_display(form_context)
        metadata.update(
            title=display,
            display=display,
            form=form_context,
            form_total=_form_progress_total(item),
        )
    return metadata


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


def report_deselected(items):
    """Collectiondan ataylab chiqarilgan testlarni nomi bilan progressga yozadi."""
    for item in items:
        metadata = _progress_metadata(item)
        if metadata:
            emit_progress_event(event="deselected", **metadata)


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


def _clean_current_allure_results(results_dir):
    """Explicit resetda raw resultlarni o'chiradi; JSONL history alohida."""
    results_dir.mkdir(parents=True, exist_ok=True)
    for item in results_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)


def prepare_allure_results(config, run_info, root_dir):
    """Run boshida Allure environment va executor metadata fayllarini tayyorlaydi."""
    root_dir = Path(root_dir)
    results_dir = root_dir / ALLURE_RESULTS_DIR
    if env_flag("CLEAN_ALLURE_RESULTS"):
        _clean_current_allure_results(results_dir)
    else:
        results_dir.mkdir(parents=True, exist_ok=True)

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

    executor_path = results_dir / "executor.json"
    executor_data = {
        "name": socket.gethostname(),
        "type": "local",
        "buildName": "Smoke Tests",
        "reportName": "Allure Report",
    }
    with executor_path.open("w", encoding="utf-8") as executor_file:
        json.dump(executor_data, executor_file, indent=2)


def _visible_texts(page, selector, *, limit=20):
    """Ko'rinadigan diagnostika matnlarini takrorsiz va cheklangan holda oladi."""
    try:
        raw_texts = page.locator(selector).all_inner_texts()
    except Exception:
        return []

    texts = []
    for raw_text in raw_texts:
        text = " ".join(str(raw_text or "").split())
        if text and text not in texts:
            texts.append(text[:500])
        if len(texts) >= limit:
            break
    return texts


def browser_state(page):
    """Failure paytidagi browser holatini machine-readable payloadga aylantiradi."""
    try:
        current_url = safe_page_url(page.url)
    except Exception:
        current_url = ""
    try:
        document_title = str(page.title() or "")
    except Exception:
        document_title = ""
    try:
        visible_loader_count = page.locator(
            ".block-ui-overlay:visible, .smt-skeleton:visible"
        ).count()
    except Exception:
        visible_loader_count = 0

    return {
        "current_url": current_url,
        "document_title": document_title,
        "visible_headings": _visible_texts(
            page,
            "h1:visible, h2:visible, h3:visible, h4:visible, "
            "h5:visible, h6:visible, [role='heading']:visible",
        ),
        "visible_alerts": _visible_texts(
            page,
            "#biruniAlert:visible, #biruniAlertExtended:visible, "
            "[role='alert']:visible",
        ),
        "visible_loader_count": visible_loader_count,
    }


def trace_reference_for_item(item):
    """Testni qamrab olgan trace faylining run tugagach paydo bo'ladigan pathini qaytaradi."""
    fixture_names = getattr(item, "funcargs", {})
    if fixture_names.get("page") is not None:
        safe_name = item.nodeid.replace("/", "_").replace("::", "__")
        return {
            "path": f"{TRACE_DIR}/{safe_name}.zip",
            "scope": "test",
        }
    if (
        fixture_names.get("group_session_page") is not None
        or fixture_names.get("group_user_page") is not None
    ):
        module_name = item.module.__name__.replace(".", "_")
        return {
            "path": f"{TRACE_DIR}/{module_name}.zip",
            "scope": "module",
        }
    if fixture_names.get("session_page") is not None:
        return {
            "path": f"{TRACE_DIR}/smoke_trace.zip",
            "scope": "session",
        }
    return {}


def attach_failure_artifacts(item, data_path, auth_diagnostic=None):
    """Failed testning browser holati va strukturali diagnostikasini Allurega qo'shadi."""
    page = page_from_item(item)
    auth_diagnostic = auth_diagnostic or auth_diagnostic_for_item(item)
    if auth_diagnostic:
        allure.attach(
            json.dumps(auth_diagnostic, ensure_ascii=False, indent=2),
            name="auth-diagnostic",
            attachment_type=allure.attachment_type.JSON,
        )

    if page is not None:
        try:
            state = browser_state(page)
            allure.attach(
                json.dumps(state, ensure_ascii=False, indent=2),
                name="01 - Browser State",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                state["current_url"],
                name="04 - Current URL",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                page.title(),
                name="05 - Page Title",
                attachment_type=allure.attachment_type.TEXT,
            )
            is_forms_runner = smoke_group_name(item) == "Forms"
            screenshot_name = (
                "pytest-final-page-context — failed-form dalili emas"
                if is_forms_runner
                else "failure-screenshot — sensitive qiymatlar yashirilgan"
            )
            allure.attach(
                safe_page_screenshot(page, full_page=True),
                name=f"02 - {screenshot_name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name="failure-hook-error",
                attachment_type=allure.attachment_type.TEXT,
            )

    trace_reference = trace_reference_for_item(item)
    if trace_reference:
        allure.attach(
            json.dumps(trace_reference, ensure_ascii=False, indent=2),
            name="trace-reference",
            attachment_type=allure.attachment_type.JSON,
        )

    data_path = Path(data_path)
    if data_path.exists():
        allure.attach(
            data_path.read_text(encoding="utf-8"),
            name="06 - Data Store",
            attachment_type=allure.attachment_type.JSON,
        )


def log_failed_report(report):
    """Failed pytest fazasini `test-results/logs` ichidagi matn logiga yozadi."""
    if not report.failed:
        return
    longrepr_text = str(report.longrepr) if report.longrepr else "Xabar yo'q"
    auth_diagnostic = next(
        (
            value
            for key, value in getattr(report, "user_properties", [])
            if key == "auth_diagnostic"
        ),
        "",
    )
    if auth_diagnostic:
        longrepr_text += f"\n\n[AUTH DIAGNOSTIKA]\n{auth_diagnostic}"
    log_path = write_failure_log(report.nodeid, report.when, longrepr_text)
    print(f"\n[LOG] Xato logi saqlandi: {log_path}")


def _generate_test_summary(root_dir, exitstatus):
    """Direct pytest run uchun Allure generatsiyasidan oldin summary yaratadi."""
    command = [
        sys.executable,
        str(root_dir / "scripts" / "analyze_test_result.py"),
        "--exit-code",
        str(exitstatus),
        "--command",
        "direct pytest run",
        "--started-at",
        "0",
    ]
    subprocess.call(command, cwd=root_dir)


def finish_session(root_dir, exitstatus):
    """Direct pytest run tugaganda so'ralgan trace viewer yoki Allure reportni ochadi."""
    if env_flag("SMARTUP_RUNNER"):
        return

    root_dir = Path(root_dir)
    _generate_test_summary(root_dir, exitstatus)
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
    """Shared Allure 3 helper bilan report yaratib, keyin lokal serverni ochadi."""
    results_dir = root_dir / ALLURE_RESULTS_DIR
    report_dir = root_dir / ALLURE_REPORT_DIR
    config_path = root_dir / ALLURE_CONFIG_PATH
    open_command = [
        sys.executable,
        str(root_dir / "scripts" / "open_allure_report.py"),
        str(report_dir),
    ]

    print("\n[ALLURE] Report generate qilinmoqda...")
    try:
        command = build_generate_command(
            results_dir,
            report_dir,
            config_path,
            project_root=root_dir,
        )
        print(" ".join(command))
        result = generate_report(
            results_dir,
            report_dir,
            config_path,
            project_root=root_dir,
            env=os.environ,
        )
    except (AllureCliNotInstalled, OSError, ValueError) as error:
        print(f"[ALLURE] Report generate failed: {error}")
        return
    if result.returncode != 0:
        print(f"[ALLURE] Report generate failed: exit_code={result.returncode}")
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
