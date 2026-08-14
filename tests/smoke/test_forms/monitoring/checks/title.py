"""FormMonitor uchun browser-aware shell-specific title gate."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.test_forms.monitoring.checks.core import (
    OPENED_WITH_DEFECT,
    clean_text,
    reason_description,
)


DEFAULT_TITLE_TIMEOUT = 15_000
TITLE_NOT_REACHED = "TITLE_NOT_REACHED"
TITLE_SOURCES = {
    "legacy": "visible_heading",
    "a2": "document_title",
}
A2_EXPECTED_TITLE_SCRIPT = """
(expectedTitle) => {
  const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim();
  return normalize(document.title) === expectedTitle;
}
"""
LEGACY_EXPECTED_TITLE_SCRIPT = """
(expectedTitle) => {
  const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim();
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
  const headings = document.querySelectorAll(
    "h1, h2, h3, h4, h5, h6, [role='heading']"
  );
  return Array.from(headings).some(
    (heading) => isVisible(heading) && normalize(heading.innerText) === expectedTitle
  );
}
"""


class TitleContractError(RuntimeError):
    """Playwright title API ishlamaganidagi test-contract xatosi."""


def _validate_contract(expected_title, shell, timeout):
    expected = clean_text(expected_title)
    if not expected:
        raise ValueError("check_title expected_title bo'sh bo'lmasligi kerak")

    normalized_shell = clean_text(shell).lower()
    if normalized_shell not in TITLE_SOURCES:
        raise ValueError("check_title shell faqat 'legacy' yoki 'a2' bo'lishi kerak")

    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("check_title timeout musbat int bo'lishi kerak")
    return expected, normalized_shell


def _safe_document_title(page):
    try:
        return clean_text(page.title())
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def _safe_visible_headings(page):
    try:
        headings = (
            page.get_by_role("heading")
            .filter(visible=True)
            .all_inner_texts()
        )
    except (PlaywrightError, AttributeError, TypeError):
        return []
    return [clean_text(heading) for heading in headings if clean_text(heading)]


def _wait_for_expected_title(page, *, expected_title, shell, timeout):
    if shell == "a2":
        page.wait_for_function(
            A2_EXPECTED_TITLE_SCRIPT,
            arg=expected_title,
            timeout=timeout,
        )
        return

    page.wait_for_function(
        LEGACY_EXPECTED_TITLE_SCRIPT,
        arg=expected_title,
        timeout=timeout,
    )


def check_title(page, *, expected_title, shell, timeout=DEFAULT_TITLE_TIMEOUT):
    """Expected forma nomini shellga mos signaldan exact kutadi."""
    expected, normalized_shell = _validate_contract(
        expected_title,
        shell,
        timeout,
    )
    title_source = TITLE_SOURCES[normalized_shell]
    actual_url = str(getattr(page, "url", "") or "")

    try:
        _wait_for_expected_title(
            page,
            expected_title=expected,
            shell=normalized_shell,
            timeout=timeout,
        )
    except PlaywrightTimeoutError:
        passed = False
    except PlaywrightError as exc:
        raise TitleContractError(
            f"check_title contract xatosi: {clean_text(exc)}"
        ) from exc
    except (AttributeError, TypeError) as exc:
        raise TitleContractError(
            f"check_title browser API xatosi: {clean_text(exc)}"
        ) from exc
    else:
        passed = True

    document_title = _safe_document_title(page)
    title_candidates = (
        [document_title]
        if normalized_shell == "a2" and document_title
        else _safe_visible_headings(page)
        if normalized_shell == "legacy"
        else []
    )
    actual_title = (
        document_title
        if normalized_shell == "a2"
        else " | ".join(title_candidates)
    )
    if passed and not actual_title:
        actual_title = expected
        title_candidates = [expected]

    detail = (
        ""
        if passed
        else (
            f"Markaziy title check [{TITLE_NOT_REACHED}]: "
            f"timeout={timeout} ms, shell={normalized_shell}, "
            f"title_source={title_source}, expected={expected}, "
            f"actual={actual_title or '—'}, "
            f"candidates={title_candidates or ['—']}, "
            f"actual_url={actual_url or '—'}"
        )
    )
    return {
        "name": "title",
        "enabled": True,
        "execution_status": "PASSED" if passed else "FAILED",
        "passed": passed,
        "reason_code": "" if passed else TITLE_NOT_REACHED,
        "reason_summary": (
            "" if passed else reason_description(TITLE_NOT_REACHED)
        ),
        "expected": expected,
        "actual": actual_title,
        "timeout_ms": timeout,
        "title_source": title_source,
        "expected_title": expected,
        "actual_title": actual_title,
        "title_candidates": title_candidates,
        "document_title": document_title,
        "actual_url": actual_url,
        "detail": detail,
        "status": "" if passed else OPENED_WITH_DEFECT,
        "opened": True,
    }
