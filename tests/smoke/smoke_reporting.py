"""Smoke test progressi, xato diagnostikasi va Allure report boshqaruvi."""

import json
import re
import shutil
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit

import allure
import pytest

from scripts.report_lifecycle import ALLURE_RESULTS_DIR, TRACE_DIR
from tests.smoke.progress import emit_progress_event
from tests.smoke.smoke_config import env_flag
from tests.smoke.web_context_reporting import record_report as record_web_context_report
from utils.report_safety import safe_payload, safe_url
from utils.screenshot_masking import masked_page_screenshot


_PROGRESS_STARTED_ATTR = "_smartup_progress_started"
_PROGRESS_FINISHED_ATTR = "_smartup_progress_finished"
PROGRESS_TOTALS_ATTR = "_smartup_progress_totals"
_FINAL_RESULT_ATTR = "_smartup_final_result"
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


def form_case_from_item(item):
    """Parametrized Forms itemidagi structured case metadata'ni qaytaradi."""
    callspec = getattr(item, "callspec", None)
    params = getattr(callspec, "params", None)
    if not isinstance(params, Mapping):
        return None
    form_case = params.get("form_case")
    return form_case if isinstance(form_case, Mapping) else None


def _form_progress_context(item):
    """Telegram progress uchun user-readable forma kontekstini normalize qiladi."""
    form_case = form_case_from_item(item)
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
    }
    totals = getattr(getattr(item, "session", None), PROGRESS_TOTALS_ATTR, None)
    if totals is not None:
        metadata["test_total"] = totals["test_total"]
    form_context = _form_progress_context(item)
    if form_context is not None:
        display = _form_progress_display(form_context)
        metadata.update(
            title=display,
            display=display,
            form=form_context,
        )
        if totals is not None:
            metadata["form_total"] = totals["form_total"]
    return metadata


def reporting_warning(nodeid, action, error):
    """Diagnostika xatosini ko'rsatadi; asl test natijasiga tegmaydi."""
    message = f"[REPORTING] {nodeid}: {action} bajarilmadi ({type(error).__name__}). Test natijasi saqlandi."
    try:
        print(message)
    except OSError:
        pass


def emit_item_progress(item, event, **details):
    """Progress yozishdagi xato pytest hookini to'xtatmasligini ta'minlaydi."""
    try:
        metadata = _progress_metadata(item)
        if not metadata:
            return False
        emit_progress_event(event=event, **details, **metadata)
        return True
    except Exception as error:
        reporting_warning(item.nodeid, "Progress yozish", error)
        return False


def start_progress(item):
    """Test uchun `started` progress eventini faqat bir marta chiqaradi."""
    if getattr(item, _PROGRESS_STARTED_ATTR, False):
        return
    if emit_item_progress(item, "started"):
        setattr(item, _PROGRESS_STARTED_ATTR, True)


def finish_progress(item, event, *, error_type=None, message=None):
    """Test yakuniy progress eventini faqat bir marta chiqaradi."""
    if getattr(item, _PROGRESS_FINISHED_ATTR, False):
        return
    if emit_item_progress(item, event, error_type=error_type, message=message):
        setattr(item, _PROGRESS_FINISHED_ATTR, True)


def record_test_report(item, report, call, data_path):
    """Faza natijasini saqlaydi; teardown oxirida bitta yakuniy progress chiqaradi.

    Failed skipped'dan ustun. Bir nechta faza yiqilsa birinchi xato asosiy
    sabab bo'lib qoladi; har fazaning xatosi pytest/Allure reportida saqlanadi.
    """
    try:
        record_web_context_report(item, report, page_from_item(item))
    except Exception as error:
        reporting_warning(item.nodeid, "Webda tekshirish kontekstini yozish", error)
    result = getattr(item, _FINAL_RESULT_ATTR, {"event": "passed"})
    if report.failed or report.skipped:
        try:
            allure.attach(
                json.dumps({
                    "nodeid": item.nodeid,
                    "phase": report.when,
                    "started_at": int(call.start * 1000),
                    "finished_at": int(call.stop * 1000),
                    "blocked_by": getattr(item, "_smartup_blocked_by", ""),
                    "skip_kind": (
                        "dependency" if getattr(item, "_smartup_blocked_by", "") else
                        "intentional" if report.skipped and (
                            item.get_closest_marker("skip") or item.get_closest_marker("skipif")
                        ) else
                        "other" if report.skipped else ""
                    ),
                }, ensure_ascii=False),
                name="test-outcome-context",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception as error:
            reporting_warning(item.nodeid, "Test fazasi diagnostikasi", error)
    if report.failed:
        failure = {
            "event": "failed",
            "error_type": call.excinfo.typename if call.excinfo else "Failed",
            "message": str(call.excinfo.value).strip() if call.excinfo else report_message(report),
        }
        auth_diagnostic = None
        try:
            auth_diagnostic = auth_diagnostic_for_item(item)
            if auth_diagnostic:
                failure["error_type"] = auth_diagnostic["error_type"]
                failure["message"] = auth_diagnostic["summary"]
                report.user_properties.append(("auth_diagnostic", auth_diagnostic["summary"]))
        except Exception as error:
            reporting_warning(item.nodeid, "Authorization diagnostikasi", error)
        if result["event"] != "failed":
            result = failure
        # Natijani optional artefaktlardan oldin saqlaymiz.
        setattr(item, _FINAL_RESULT_ATTR, result)
        try:
            attach_failure_artifacts(item, data_path, auth_diagnostic=auth_diagnostic)
        except Exception as error:
            reporting_warning(item.nodeid, "Failure artefaktlarini yig'ish", error)
    elif report.skipped and result["event"] == "passed":
        result = {"event": "skipped", "error_type": "Skipped", "message": report_message(report)}
    setattr(item, _FINAL_RESULT_ATTR, result)

    if report.when == "teardown":
        try:
            reset_auth_diagnostics(item)
        except Exception as error:
            reporting_warning(item.nodeid, "Authorization diagnostikasini tozalash", error)
        finish_progress(item, **result)


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


def prepare_allure_results(run_info, root_dir):
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
            f"Browser.Headless={env_flag('HEADLESS')}\n"
        )
        environment_file.write(f"Server={run_info['company_url']}\n")
        run_mode = "Create company" if run_info["create_company"] else "Existing company"
        environment_file.write(f"Run.Mode={run_mode}\n")
        environment_file.write("Environment=Staging\n")

    executor_path = results_dir / "executor.json"
    executor_data = {
        "name": "Local runner",
        "type": "local",
        "buildName": "Smartup smoke run",
        "reportName": "Smartup test hisoboti",
    }
    with executor_path.open("w", encoding="utf-8") as executor_file:
        json.dump(executor_data, executor_file, indent=2)


def _visible_texts(page, selector, *, limit=20, errors=None, field="matn"):
    """Ko'rinadigan diagnostika matnlarini takrorsiz va cheklangan holda oladi."""
    try:
        raw_texts = page.locator(selector).all_inner_texts()
    except Exception:
        if errors is not None:
            errors.append(field)
        return None

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
    errors = []
    try:
        current_url = safe_url(page.url)
    except Exception:
        current_url = None
        errors.append("current_url")
    try:
        document_title = str(page.title() or "")
    except Exception:
        document_title = None
        errors.append("document_title")
    try:
        visible_loader_count = page.locator(
            ".block-ui-overlay:visible, .smt-skeleton:visible"
        ).count()
    except Exception:
        visible_loader_count = None
        errors.append("visible_loader_count")

    try:
        content = page.evaluate("""() => ({
            ready_state: document.readyState,
            body_text_length: (document.body?.innerText || '').trim().length,
            main_count: document.querySelectorAll('main').length
        })""")
    except Exception:
        content = {}
        errors.append("content")

    state = {
        "current_url": current_url,
        "document_title": document_title,
        "visible_headings": _visible_texts(
            page,
            "h1:visible, h2:visible, h3:visible, h4:visible, "
            "h5:visible, h6:visible, [role='heading']:visible",
            errors=errors, field="visible_headings",
        ),
        "visible_alerts": _visible_texts(
            page,
            "#biruniAlert:visible, #biruniAlertExtended:visible, "
            "[role='alert']:visible",
            errors=errors, field="visible_alerts",
        ),
        "visible_loader_count": visible_loader_count,
        "content": content,
        "observation_errors": errors,
    }
    return safe_payload(state)


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
                state["current_url"] or "O'qib bo'lmadi",
                name="04 - Current URL",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                state["document_title"] or "O'qib bo'lmadi",
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
