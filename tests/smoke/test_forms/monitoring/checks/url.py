"""FormMonitor uchun browser-aware URL gate va direct-route diagnostikasi."""

from __future__ import annotations

import time
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import company_url


DEFAULT_URL_TIMEOUT = 15_000
EXPECTED_URL_NOT_REACHED = "EXPECTED_URL_NOT_REACHED"
SHELL_NOT_DETECTED = "SHELL_NOT_DETECTED"


def canonical_form_path(url):
    """Legacy token/query va A2 prefiksini olib, forma pathini qaytaradi."""
    parsed = urlsplit(str(url or ""))
    fragment = parsed.fragment.lstrip("/")
    if fragment.startswith("!"):
        parts = fragment.split("/", 1)
        fragment = parts[1] if len(parts) == 2 else ""
    if not fragment and "/a2/" in parsed.path:
        fragment = parsed.path.split("/a2/", 1)[1]
    return fragment.split("?", 1)[0].strip("/")


def normalize_expected_path(expected_path):
    return str(expected_path or "").split("?", 1)[0].strip("/")


def detect_shell(url):
    """Actual browser URLidan destination shellni aniqlaydi."""
    actual_url = str(url or "")
    if "/a2/" in actual_url:
        return "a2"
    fragment = urlsplit(actual_url).fragment.lstrip("/")
    if fragment.startswith("!"):
        return "legacy"
    return None


def _url_contains_path(url, expected_path):
    return bool(expected_path) and expected_path in str(url or "")


def _wait_for_expected_path(page, expected_path, *, timeout):
    if _url_contains_path(getattr(page, "url", ""), expected_path):
        return True
    try:
        page.wait_for_url(lambda value: _url_contains_path(value, expected_path), timeout=timeout)
    except (PlaywrightTimeoutError, PlaywrightError, AssertionError, AttributeError, TypeError):
        return _url_contains_path(getattr(page, "url", ""), expected_path)
    return _url_contains_path(getattr(page, "url", ""), expected_path)


def build_direct_form_url(current_url, expected_path, *, shell):
    """Joriy authenticated shell kontekstidan direct forma URLini quradi."""
    expected = normalize_expected_path(expected_path)
    base_url = company_url()
    if str(shell or "").strip().lower() == "a2":
        return f"{base_url}/a2/{expected}"

    fragment = urlsplit(str(current_url or "")).fragment.lstrip("/")
    token = fragment.split("/", 1)[0]
    if not token.startswith("!") or len(token) == 1:
        return ""
    return f"{base_url}/#/{token}/{expected}"


def _capture_evidence(capture_evidence, stage, result):
    if capture_evidence is None:
        return
    evidence = capture_evidence(stage, result)
    if evidence:
        result["evidence"].append(evidence)


def _direct_probe(page, result, *, expected_path, shell, timeout, capture_evidence):
    result["direct_probe_executed"] = True
    try:
        direct_url = build_direct_form_url(result["actual_url"], expected_path, shell=shell)
    except (AssertionError, ValueError, TypeError) as exc:
        direct_url = ""
        result["direct_error"] = str(exc)
    result["direct_expected_url"] = direct_url

    deadline = time.monotonic() + (timeout / 1000)
    if direct_url:
        try:
            page.goto(direct_url, wait_until="domcontentloaded", timeout=timeout)
        except (PlaywrightTimeoutError, PlaywrightError, AssertionError, AttributeError, TypeError) as exc:
            result["direct_error"] = str(exc)
        remaining = max(0, int((deadline - time.monotonic()) * 1000))
        result["direct_url_reached"] = _url_contains_path(getattr(page, "url", ""), expected_path)
        if not result["direct_url_reached"] and remaining:
            result["direct_url_reached"] = _wait_for_expected_path(page, expected_path, timeout=remaining)
    elif not result["direct_error"]:
        result["direct_error"] = "Direct URL uchun authenticated legacy token topilmadi."

    result["direct_actual_url"] = str(getattr(page, "url", "") or "")
    result["direct_summary"] = (
        "Forma route'da mavjud, lekin menu navigatsiyasi target route'ga olib bormadi."
        if result["direct_url_reached"]
        else "Expected forma menu va direct URL orqali ham ochilmadi."
    )
    _capture_evidence(capture_evidence, "direct", result)


def check_url(page, expected_path, *, timeout=DEFAULT_URL_TIMEOUT, try_direct_url=True, capture_evidence=None):
    """Expected pathni actual URL ichidan kutadi va destination shellni qaytaradi."""
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("check_url timeout musbat int bo'lishi kerak")
    if not isinstance(try_direct_url, bool):
        raise ValueError("check_url try_direct_url bool bo'lishi kerak")

    expected = normalize_expected_path(expected_path)
    if not expected:
        raise ValueError("check_url expected_path bo'sh bo'lmasligi kerak")

    path_found = _wait_for_expected_path(page, expected, timeout=timeout)
    actual_url = str(getattr(page, "url", "") or "")
    actual_path = canonical_form_path(actual_url)
    shell = detect_shell(actual_url)
    passed = path_found and shell is not None
    reason_code = (
        ""
        if passed
        else SHELL_NOT_DETECTED
        if path_found
        else EXPECTED_URL_NOT_REACHED
    )
    reason_summary = (
        ""
        if passed
        else "Actual forma URLidan A2 yoki legacy shell aniqlanmadi."
        if reason_code == SHELL_NOT_DETECTED
        else "Belgilangan vaqt ichida kutilgan forma URLi ochilmadi."
    )
    result = {
        "name": "url",
        "enabled": True,
        "execution_status": "PASSED" if passed else "FAILED",
        "passed": passed,
        "reason_code": reason_code,
        "reason_summary": reason_summary,
        "expected": expected,
        "actual": actual_path,
        "expected_url": expected,
        "actual_url": actual_url,
        "actual_path": actual_path,
        "timeout_ms": timeout,
        "detail": "" if passed else f"Markaziy URL check [{reason_code}]: timeout={timeout} ms, expected={expected}, actual={actual_url or '—'}",
        "status": "" if passed else "NOT_OPENED",
        "opened": passed,
        "direct_probe_enabled": try_direct_url,
        "direct_probe_executed": False,
        "direct_expected_url": "",
        "direct_actual_url": "",
        "direct_url_reached": False,
        "direct_error": "",
        "direct_summary": "",
        "evidence": [],
    }
    if passed:
        return result, shell

    _capture_evidence(capture_evidence, "menu", result)
    if try_direct_url and shell is not None:
        _direct_probe(page, result, expected_path=expected, shell=shell, timeout=timeout, capture_evidence=capture_evidence)
    elif try_direct_url:
        result["direct_error"] = "Actual URLdan shell aniqlanmagani uchun direct URL qurilmadi."
    return result, shell
