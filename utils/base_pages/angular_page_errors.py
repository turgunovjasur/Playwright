"""Keep errors observed during A2 page readiness available to the next UI action."""

from functools import wraps

from utils.base_pages.page_diagnostics import expectation_gate
from utils.base_pages.page_reporting import report_web_action


ERROR_ELEMENTS = (
    ".alert-danger, [role='dialog'] [data-testid*='error' i], "
    "smt-alert-dialog:has(.bg-error-100), main app-page-model-load-error [role='alert']"
)
ERROR_MARKER = "html[data-smartup-test-page-error]"


def watch_errors(page):
    # A transient error may have disappeared by the next Playwright call.
    page.evaluate("""selector => {
        if (window.__smartupTestErrorObserver) return;
        const root = document.documentElement;
        const capture = () => {
            if (root.hasAttribute('data-smartup-test-page-error')) return;
            for (const node of document.querySelectorAll(selector)) {
                const rect = node.getBoundingClientRect();
                if (rect.width && rect.height && getComputedStyle(node).visibility === 'visible') {
                    root.setAttribute('data-smartup-test-page-error', node.innerText.trim() || '(empty)');
                    return;
                }
            }
        };
        const observer = new MutationObserver(capture);
        observer.observe(root, {subtree: true, childList: true, attributes: true, characterData: true});
        window.__smartupTestErrorObserver = observer;
        capture();
    }""", ERROR_ELEMENTS)
    page._smartup_watching_page_errors = True


def stop_watching(page):
    if getattr(page, "_smartup_watching_page_errors", False):
        page.evaluate("""() => {
            window.__smartupTestErrorObserver?.disconnect();
            delete window.__smartupTestErrorObserver;
            document.documentElement.removeAttribute('data-smartup-test-page-error');
        }""")
        page._smartup_watching_page_errors = False


def check_observed_error(page):
    if getattr(page, "_smartup_watching_page_errors", False) and not page.is_closed():
        message = page.evaluate("() => document.documentElement.getAttribute('data-smartup-test-page-error')")
        if message is not None:
            expectation_gate(page, "application_error")
            raise AssertionError(f"Smartup application error: {message}, url={page.url}")


def angular_action(method):
    @wraps(method)
    def guarded(self, *args, **kwargs):
        page = self.page
        if method.__name__ == "expect_page" and not kwargs.get("check_no_error", True):
            stop_watching(page)
        elif method.__name__ == "close_biruni_alert":
            # This operation asserts the expected error text itself.
            result = method(self, *args, **kwargs)
            stop_watching(page)
            return result
        else:
            check_observed_error(page)
        try:
            return method(self, *args, **kwargs)
        except Exception:
            check_observed_error(page)
            raise

    return report_web_action(guarded)
