"""FormMonitor uchun browser-aware content-ready gate."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.test_forms.monitoring.checks.core import (
    NOT_OPENED,
    clean_text,
    reason_description,
)


DEFAULT_CONTENT_READY_TIMEOUT = 15_000
LEGACY_DEFAULT_READY_SELECTORS = (
    "b-page:visible",
    ".subheader:visible",
)
LEGACY_DEFAULT_READY_SELECTOR = ", ".join(LEGACY_DEFAULT_READY_SELECTORS)
A2_DEFAULT_READY_DESCRIPTION = "main:visible with text or visible child"
A2_CONTENT_READY_SCRIPT = """
() => {
  const main = document.querySelector("main");
  if (!main) {
    return false;
  }
  const isVisible = (element) => {
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return (
      style.visibility !== "hidden" &&
      style.display !== "none" &&
      rect.width > 0 &&
      rect.height > 0
    );
  };
  if (!isVisible(main)) {
    return false;
  }
  if (String(main.innerText || "").trim()) {
    return true;
  }
  return Array.from(main.children).some(isVisible);
}
"""


class ContentReadyContractError(RuntimeError):
    """Noto'g'ri selector yoki Playwright API kontrakti xatosi."""


def _validate_timeout(timeout):
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("check_content_ready timeout musbat int bo'lishi kerak")


def _normalize_ready(ready):
    if ready is None:
        return None
    if not isinstance(ready, str) or not ready.strip():
        raise ValueError("check_content_ready ready non-empty CSS selector bo'lishi kerak")
    return ready.strip()


def _ready_contract(shell, ready):
    if ready is not None:
        return "explicit", ready
    if shell == "a2":
        return "a2_default", A2_DEFAULT_READY_DESCRIPTION
    return "legacy_default", LEGACY_DEFAULT_READY_SELECTOR


def _matched_legacy_selector(page):
    for selector in LEGACY_DEFAULT_READY_SELECTORS:
        if page.locator(selector).first.is_visible():
            return selector
    return ""


def check_content_ready(page, *, shell, ready=None, timeout=DEFAULT_CONTENT_READY_TIMEOUT):
    """Forma kontenti timeout ichida tayyor bo'lishini kutadi."""
    _validate_timeout(timeout)
    normalized_shell = clean_text(shell).lower()
    if normalized_shell not in {"legacy", "a2"}:
        raise ValueError("check_content_ready shell faqat 'legacy' yoki 'a2' bo'lishi kerak")
    ready = _normalize_ready(ready)
    ready_source, expected_ready = _ready_contract(normalized_shell, ready)
    actual_url = str(getattr(page, "url", "") or "")
    matched_selector = ""

    try:
        if ready_source == "a2_default":
            page.wait_for_function(A2_CONTENT_READY_SCRIPT, timeout=timeout)
            matched_selector = "main:visible"
        else:
            selector = ready or LEGACY_DEFAULT_READY_SELECTOR
            page.locator(selector).first.wait_for(
                state="visible",
                timeout=timeout,
            )
            matched_selector = ready or _matched_legacy_selector(page)
    except PlaywrightTimeoutError:
        passed = False
    except PlaywrightError as exc:
        raise ContentReadyContractError(
            f"check_content_ready contract xatosi: {clean_text(exc)}"
        ) from exc
    else:
        passed = True

    content_observation = (
        f"{matched_selector or expected_ready} visible"
        if passed
        else f"{timeout} ms ichida forma kontenti tayyor bo'lmadi"
    )
    detail = (
        ""
        if passed
        else (
            "Markaziy content-ready check [CONTENT_NOT_READY]: "
            f"timeout={timeout} ms, actual_url={actual_url or '—'}, "
            f"ready_source={ready_source}, expected_ready={expected_ready}, "
            f"observation={content_observation}"
        )
    )
    return {
        "name": "content_ready",
        "enabled": True,
        "execution_status": "PASSED" if passed else "FAILED",
        "passed": passed,
        "reason_code": "" if passed else "CONTENT_NOT_READY",
        "reason_summary": (
            "" if passed else reason_description("CONTENT_NOT_READY")
        ),
        "expected": expected_ready,
        "actual": matched_selector or content_observation,
        "timeout_ms": timeout,
        "ready_source": ready_source,
        "expected_ready": expected_ready,
        "matched_selector": matched_selector,
        "content_observation": clean_text(content_observation),
        "actual_url": actual_url,
        "detail": detail,
        "status": "" if passed else NOT_OPENED,
        "opened": True,
    }
