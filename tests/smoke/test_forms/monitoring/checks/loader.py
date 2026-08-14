"""FormMonitor uchun browser-aware blocking-loader gate."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from tests.smoke.test_forms.monitoring.checks.core import OPENED_WITH_DEFECT, reason_description


DEFAULT_LOADER_TIMEOUT = 60_000
LOADER_NOT_FINISHED = "LOADER_NOT_FINISHED"
BLOCKING_LOADER_SELECTORS = (
    ".block-ui-overlay:visible",
    ".smt-skeleton:visible",
)
BLOCKING_LOADER_SELECTOR = ", ".join(BLOCKING_LOADER_SELECTORS)
LOADER_SELECTORS_BY_SHELL = {
    "legacy": (
        ".block-ui-overlay:visible",
        ".smt-skeleton:visible",
    ),
    "a2": (
        ".smt-skeleton:visible",
        ".block-ui-overlay:visible",
    ),
}


def _safe_count(page, selector):
    try:
        return int(page.locator(selector).count())
    except (PlaywrightError, AttributeError, TypeError, ValueError):
        return 0


def _visible_loaders(page, selectors):
    return [
        selector
        for selector in selectors
        if _safe_count(page, selector) > 0
    ]


def check_loader(page, *, shell, timeout=DEFAULT_LOADER_TIMEOUT):
    """Blocking loaderlar yo'qolishini kutadi va structured hard-check qaytaradi."""
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("check_loader timeout musbat int bo'lishi kerak")
    normalized_shell = str(shell or "").strip().lower()
    if normalized_shell not in LOADER_SELECTORS_BY_SHELL:
        raise ValueError("check_loader shell faqat 'legacy' yoki 'a2' bo'lishi kerak")

    selectors = LOADER_SELECTORS_BY_SHELL[normalized_shell]
    selector = ", ".join(selectors)
    loader = page.locator(selector)
    try:
        expect(loader).to_have_count(0, timeout=timeout)
        passed = True
    except (AssertionError, PlaywrightTimeoutError):
        passed = False

    visible_loaders = _visible_loaders(page, selectors)
    loader_count = _safe_count(page, selector)
    actual_url = str(getattr(page, "url", "") or "")
    detail = (
        ""
        if passed
        else (
            f"Markaziy loader check [{LOADER_NOT_FINISHED}]: "
            f"timeout={timeout} ms, actual_url={actual_url or '—'}, "
            f"loader_count={loader_count}, "
            f"visible_loaders={visible_loaders or ['—']}"
        )
    )
    return {
        "name": "loader",
        "enabled": True,
        "execution_status": "PASSED" if passed else "FAILED",
        "passed": passed,
        "reason_code": "" if passed else LOADER_NOT_FINISHED,
        "reason_summary": "" if passed else reason_description(LOADER_NOT_FINISHED),
        "expected": "blocking loader count=0",
        "actual": visible_loaders,
        "timeout_ms": timeout,
        "visible_loaders": visible_loaders,
        "loader_count": loader_count,
        "actual_url": actual_url,
        "detail": detail,
        "status": "" if passed else OPENED_WITH_DEFECT,
        "opened": True,
    }
