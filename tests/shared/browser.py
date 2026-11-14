"""Browser context va page uchun umumiy yaratish/yopish tartibi."""

import sys
from contextlib import contextmanager
from pathlib import Path

from tests.shared import config, reporting
from utils.base_pages import UI_TIMEOUT_MS


@contextmanager
def browser_context(browser, trace_path, *, storage_state=None):
    """Contextni tayyorlaydi; trace xatosida ham contextni yopadi."""
    options = config.browser_context_options()
    if storage_state is not None:
        options["storage_state"] = storage_state
    context = browser.new_context(**options)
    trace_started = False
    try:
        context.set_default_timeout(UI_TIMEOUT_MS)
        context.set_default_navigation_timeout(UI_TIMEOUT_MS)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        trace_started = True
        yield context
    finally:
        original_error = sys.exc_info()[0] is not None
        cleanup_errors = []
        try:
            if trace_started:
                try:
                    trace_path = Path(trace_path)
                    trace_path.parent.mkdir(parents=True, exist_ok=True)
                    context.tracing.stop(path=str(trace_path))
                except Exception as error:
                    cleanup_errors.append(("Trace saqlanmadi", error))
        finally:
            try:
                context.close()
            except Exception as error:
                cleanup_errors.append(("Browser context yopilmadi", error))
        if cleanup_errors:
            message = "; ".join(f"{action} ({type(error).__name__})" for action, error in cleanup_errors)
            if original_error:
                print(f"[CLEANUP] {message}. Asl xato saqlandi.")
            else:
                raise RuntimeError(message) from cleanup_errors[0][1]


@contextmanager
def browser_page(context):
    """Diagnostikali page ochadi va foydalanish tugagach yopadi."""
    page = context.new_page()
    try:
        reporting.install_auth_diagnostics(page)
        yield page
    finally:
        original_error = sys.exc_info()[0] is not None
        try:
            page.close()
        except Exception as error:
            if original_error:
                print(f"[CLEANUP] Page yopilmadi ({type(error).__name__}). Asl xato saqlandi.")
            else:
                raise
