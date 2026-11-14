"""Opening a form from a list is safe to repeat before any data is entered."""
import re

import allure

from utils.base_pages import UI_TIMEOUT_MS
from utils.base_pages.auto_base_page import AutoBasePage
from utils.report_safety import safe_text
from utils.base_pages.page_errors import is_module_load_error


def open_form_from_list(page, *, heading, url, button="Создать", timeout=UI_TIMEOUT_MS):
    """Click a navigation button, verify the destination, recover one failed JS import."""
    base = AutoBasePage(page)
    source = page.url
    for attempt in range(2):
        base.click(name=button, exact=True, timeout=timeout)
        state = page.wait_for_function("""source => {
            if (location.href !== source) return {navigated: true};
            const dialog = document.querySelector('[role="dialog"] smt-alert-dialog');
            if (dialog?.getClientRects().length) return {error: dialog.innerText};
        }""", arg=source, timeout=timeout).json_value()
        if state.get("navigated"):
            base.expect_page(heading=heading, url=url, timeout=timeout)
            return
        message = state["error"]
        if attempt or page.url != source or not is_module_load_error(message, source):
            raise AssertionError(f"{heading}: {safe_text(message)}")
        with allure.step("Forma moduli yuklanmadi — ro‘yxatni bir marta qayta ochish"):
            page.reload(wait_until="domcontentloaded", timeout=timeout)
            base.expect_page(url=re.compile("^" + re.escape(source) + "$"), timeout=timeout)
