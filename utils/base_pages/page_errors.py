"""Page-objectlar uchun ko'rinadigan application error tekshiruvi."""

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


APPLICATION_ERROR_OBSERVATION_MS = 2_400


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
        error_text = " ".join(error.inner_text(timeout=1000).split())
    except PlaywrightError:
        error_text = ""
    raise AssertionError(
        f"expect_page: application error ko'rindi; "
        f"error={error_text or '(matn bo‘sh yoki olinmadi)'}, "
        f"selector={selector}, url={page.url}"
    )
