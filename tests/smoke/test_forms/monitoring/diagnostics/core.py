"""FormMonitor diagnostika registry'si va browser state snapshot'i."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError

from tests.smoke.test_forms.monitoring.checks import (
    canonical_form_path,
    clean_text,
    normalize_enabled_names,
)
from tests.smoke.test_forms.monitoring.diagnostics.failed_requests import (
    FailedRequestsDiagnostic,
)


DIAGNOSTIC_FACTORIES = {
    "failed_requests": FailedRequestsDiagnostic,
}
DIAGNOSTIC_NAMES = tuple(DIAGNOSTIC_FACTORIES)


class FormDiagnostics:
    """Registered diagnostikalar lifecycle'ini FormMonitor uchun boshqaradi."""

    def __init__(self, page, *, enabled_names=None):
        self.enabled_names = normalize_enabled_names(
            enabled_names,
            available=DIAGNOSTIC_NAMES,
            option_name="diagnostics",
        )
        self._instances = {
            name: DIAGNOSTIC_FACTORIES[name](page)
            for name in self.enabled_names
        }
        for diagnostic in self._instances.values():
            diagnostic.start()

    def reset(self):
        for diagnostic in self._instances.values():
            diagnostic.reset()

    def evaluate(self, *, run=True):
        results = {}
        for name in DIAGNOSTIC_NAMES:
            diagnostic = self._instances.get(name)
            if diagnostic is None:
                result = {
                    "enabled": False,
                    "execution_status": "DISABLED",
                }
            elif not run:
                result = {
                    "enabled": True,
                    "execution_status": "NOT_RUN",
                    "blocked_by": "url",
                }
            else:
                result = diagnostic.snapshot()
            results[name] = result
        return results

    def close(self):
        for diagnostic in self._instances.values():
            diagnostic.close()


def _safe_page_title(page):
    try:
        return clean_text(page.title())
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def _safe_locator_visible(locator):
    """``is_visible`` kutmaydi — bu ataylab lahzalik snapshot."""
    try:
        return bool(locator.is_visible())
    except (PlaywrightError, AttributeError, TypeError):
        return False


def _safe_visible_headings(page):
    try:
        headings = page.get_by_role("heading").filter(visible=True).all_inner_texts()
    except (PlaywrightError, AttributeError, TypeError):
        return []
    return [clean_text(heading) for heading in headings if clean_text(heading)]


def capture_form_state(page):
    """Hard-check natijalarini boyitadigan kutishsiz browser snapshot'i."""
    actual_url = getattr(page, "url", "") or ""
    loader_visible = any(
        _safe_locator_visible(page.locator(selector).first)
        for selector in (
            ".block-ui-overlay:visible",
            ".smt-skeleton:visible",
        )
    )

    document_title = _safe_page_title(page)
    is_a2 = "/a2/" in actual_url
    title_candidates = [document_title] if is_a2 and document_title else []
    if not is_a2:
        title_candidates = _safe_visible_headings(page)
    actual_form_title = " | ".join(title_candidates) or document_title

    return {
        "actual_url": actual_url,
        "actual_title": actual_form_title,
        "document_title": document_title,
        "title_candidates": title_candidates,
        "title_source": "document_title" if is_a2 else "visible_heading",
        "canonical_path": canonical_form_path(actual_url),
        "loader_visible": loader_visible,
    }
