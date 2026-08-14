"""FormMonitor uchun browser-aware application-error gate."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.test_forms.monitoring.checks.core import OPENED_WITH_DEFECT, clean_text, reason_description


DEFAULT_APPLICATION_ERROR_TIMEOUT = 1_200
HARD_ERROR_SELECTORS = (
    "#biruniAlertExtended:visible",
    "#biruniAlert:visible",
    ".alert-danger:visible",
    "[role='dialog']:visible [data-testid*='error' i]",
)
HARD_ERROR_SELECTOR = ", ".join(HARD_ERROR_SELECTORS)
ERROR_SELECTORS_BY_SHELL = {
    "legacy": (
        "#biruniAlertExtended:visible",
        "#biruniAlert:visible",
        ".alert-danger:visible",
    ),
    "a2": (
        ".alert-danger:visible",
        "[role='dialog']:visible [data-testid*='error' i]",
    ),
}
BIRUNI_ERROR_BASE_SELECTORS = {
    "#biruniAlertExtended:visible": "#biruniAlertExtended",
    "#biruniAlert:visible": "#biruniAlert",
}


def _positive_timeout(value, *, name):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} musbat int bo'lishi kerak")


def _matched_error(page, selectors):
    for selector in selectors:
        locator = page.locator(selector).first
        if not locator.is_visible():
            continue
        try:
            error_text = clean_text(locator.inner_text(timeout=500))
        except PlaywrightError:
            error_text = ""
        return selector, error_text
    return HARD_ERROR_SELECTOR, ""


def check_application_error(page, *, shell, timeout=DEFAULT_APPLICATION_ERROR_TIMEOUT):
    """Aniq UI errorni kutadi va structured hard-check natijasini qaytaradi."""
    _positive_timeout(timeout, name="check_application_error timeout")
    normalized_shell = str(shell or "").strip().lower()
    if normalized_shell not in ERROR_SELECTORS_BY_SHELL:
        raise ValueError("check_application_error shell faqat 'legacy' yoki 'a2' bo'lishi kerak")
    selectors = ERROR_SELECTORS_BY_SHELL[normalized_shell]
    selector = ", ".join(selectors)

    try:
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError:
        return {
            "name": "application_error",
            "enabled": True,
            "execution_status": "PASSED",
            "passed": True,
            "reason_code": "",
            "reason_summary": "",
            "expected": "visible hard application error yo'q",
            "actual": "",
            "timeout_ms": timeout,
            "matched_selector": "",
            "error_text": "",
            "actual_url": str(getattr(page, "url", "") or ""),
            "detail": "",
            "status": "",
            "opened": True,
        }

    matched_selector, error_text = _matched_error(page, selectors)
    actual_url = str(getattr(page, "url", "") or "")
    detail = (
        "Markaziy application-error check [APPLICATION_ERROR]: "
        f"timeout={timeout} ms, actual_url={actual_url or '—'}, "
        f"matched_selector={matched_selector or '—'}, "
        f"error_text={error_text or '—'}"
    )
    return {
        "name": "application_error",
        "enabled": True,
        "execution_status": "FAILED",
        "passed": False,
        "reason_code": "APPLICATION_ERROR",
        "reason_summary": reason_description("APPLICATION_ERROR"),
        "expected": "visible hard application error yo'q",
        "actual": error_text or matched_selector,
        "timeout_ms": timeout,
        "matched_selector": matched_selector,
        "error_text": error_text,
        "actual_url": actual_url,
        "detail": detail,
        "status": OPENED_WITH_DEFECT,
        "opened": True,
    }


def dismiss_application_error(page, check_result, *, timeout=2_000):
    """Screenshotdan keyin faqat ma'lum Biruni error modalini yopishga urinadi."""
    _positive_timeout(timeout, name="dismiss_application_error timeout")
    matched_selector = str((check_result or {}).get("matched_selector") or "")
    base_selector = BIRUNI_ERROR_BASE_SELECTORS.get(matched_selector)
    if not base_selector:
        return {
            "modal_cleanup_attempted": False,
            "modal_cleanup_succeeded": False,
            "modal_cleanup_error": "",
        }

    try:
        alert = page.locator(base_selector).first
        if not alert.is_visible():
            return {
                "modal_cleanup_attempted": True,
                "modal_cleanup_succeeded": True,
                "modal_cleanup_error": "",
            }
        close_button = alert.locator("button.close").first
        if not close_button.is_visible():
            raise AssertionError("Biruni error modalida visible button.close topilmadi")
        close_button.click()
        alert.wait_for(state="hidden", timeout=timeout)
    except (AssertionError, PlaywrightError, AttributeError, TypeError) as exc:
        return {
            "modal_cleanup_attempted": True,
            "modal_cleanup_succeeded": False,
            "modal_cleanup_error": clean_text(exc),
        }
    return {
        "modal_cleanup_attempted": True,
        "modal_cleanup_succeeded": True,
        "modal_cleanup_error": "",
    }
