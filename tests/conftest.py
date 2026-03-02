import os
import pytest
from typing import Any, Generator
from playwright.sync_api import sync_playwright, Browser, Page

TRACE_DIR = "test-results/traces"

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture
def browser():
    """Bitta browser instance, to'liq ekranda ochiladi."""
    with sync_playwright() as p:
        browser_obj = p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        yield browser_obj
        browser_obj.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture
def page(browser: Browser) -> Generator[Page, Any, None]:
    """Har bir test uchun yangi sahifa, to'liq ekran (no_viewport + --start-maximized). Trace yoziladi."""
    context = browser.new_context(no_viewport=True)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page_obj = context.new_page()

    yield page_obj

    os.makedirs(TRACE_DIR, exist_ok=True)
    context.tracing.stop(path=os.path.join(TRACE_DIR, "trace.zip"))
    page_obj.close()
    context.close()

# ----------------------------------------------------------------------------------------------------------------------
