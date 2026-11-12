"""Page-objectlar uchun ko'rinadigan application error tekshiruvi."""

import re
from contextlib import contextmanager
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


APPLICATION_ERROR_OBSERVATION_MS = 4_800


def expect_no_application_error(page, selector, *, timeout):
    """Qisqa kuzatishda error ko'rinsa, uni yopmasdan matni bilan yiqiladi."""
    error = page.locator(selector).first
    if timeout == 0:
        if not error.is_visible():
            return
    else:
        try:
            error.wait_for(
                state="visible",
                timeout=min(timeout, APPLICATION_ERROR_OBSERVATION_MS),
            )
        except PlaywrightTimeoutError:
            return

    try:
        error_text = " ".join(error.inner_text(timeout=2_000).split())
    except PlaywrightError:
        error_text = ""
    raise AssertionError(
        f"expect_page: application error ko'rindi; "
        f"error={error_text or '(matn bo‘sh yoki olinmadi)'}, "
        f"selector={selector}, url={page.url}"
    )


def is_module_load_error(message, source_url):
    match = re.search(r"Failed to fetch dynamically imported module:\s*(https?://[^\s]+)", message)
    if not match:
        return False
    module, source = urlsplit(match[1]), urlsplit(source_url)
    return ((module.scheme, module.netloc) == (source.scheme, source.netloc)
            and re.search(r"/a2/chunk-[\w-]+\.js$", module.path) is not None)


@contextmanager
def observe_module_load_errors(page, source_url):
    """Record failed dynamic imports only while navigating to this application."""
    failures = []
    def capture(message):
        if message.type == "error" and is_module_load_error(message.text, source_url):
            failures.append(message.text)
    page.on("console", capture)
    try:
        yield failures
    finally:
        page.remove_listener("console", capture)
