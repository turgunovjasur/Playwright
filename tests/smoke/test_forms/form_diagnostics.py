"""Browser state capture va observation-only forma diagnostikalari."""

from __future__ import annotations

from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError

from tests.smoke.test_forms.flow import canonical_form_path
from tests.smoke.test_forms.form_checks import clean_text, normalize_enabled_names


ALERT_SELECTORS = (
    "#biruniAlertExtended:visible",
    "#biruniAlert:visible",
    "[role='alert']:visible",
    ".alert-danger:visible",
    "[role='dialog']:visible .alert-danger:visible",
    "[role='dialog']:visible [data-testid*='error' i]",
)

ALERT_WAIT_MS = 1200
MAX_PAGE_EVENTS = 20

CAPTURE_JS_ERROR_SCRIPT = """
(() => {
  if (window.__formMonitorCaptureInstalled) {
    return;
  }
  window.__formMonitorCaptureInstalled = true;
  window.__formMonitorCaptureErrors = [];
  window.__formMonitorCaptureCount = 0;
  window.__formMonitorResourceErrors = [];
  window.__formMonitorResourceCount = 0;
  window.__formMonitorPromiseRejections = [];
  window.__formMonitorPromiseRejectionCount = 0;
  const SAMPLE_LIMIT = 50;
  const withoutQuery = (value) => String(value || "").split("?")[0];
  window.addEventListener(
    "error",
    (event) => {
      // Capture fazasi resurs yuklanish xatosini ham beradi (img/script/link).
      // Ular JS exception emas va network kanali ularni allaqachon qamraydi,
      // shuning uchun alohida ro'yxatga tushadi.
      const target = event && event.target;
      if (target && target !== window && target.tagName) {
        window.__formMonitorResourceCount += 1;
        if (window.__formMonitorResourceErrors.length < SAMPLE_LIMIT) {
          window.__formMonitorResourceErrors.push(
            target.tagName + " " + withoutQuery(target.src || target.href)
          );
        }
        return;
      }
      const error = event && event.error;
      const message =
        (event && event.message) ||
        (error && error.message) ||
        (event && event.type) ||
        "noma'lum error eventi";
      let label = String(message);
      if (event && event.filename) {
        label += " @ " + withoutQuery(event.filename) + ":" + event.lineno;
      }
      window.__formMonitorCaptureCount += 1;
      if (window.__formMonitorCaptureErrors.length < SAMPLE_LIMIT) {
        window.__formMonitorCaptureErrors.push(label);
      }
    },
    true
  );
  window.addEventListener(
    "unhandledrejection",
    (event) => {
      const reason = event && event.reason;
      const message =
        (reason && reason.message) ||
        String(reason || "noma'lum promise rejection");
      window.__formMonitorPromiseRejectionCount += 1;
      if (window.__formMonitorPromiseRejections.length < SAMPLE_LIMIT) {
        window.__formMonitorPromiseRejections.push(message);
      }
    },
    true
  );
})();
"""

CAPTURE_READ_SCRIPT = """
({
  js: window.__formMonitorCaptureErrors || [],
  jsCount: window.__formMonitorCaptureCount || 0,
  resources: window.__formMonitorResourceErrors || [],
  resourceCount: window.__formMonitorResourceCount || 0,
  promiseRejections: window.__formMonitorPromiseRejections || [],
  promiseRejectionCount: window.__formMonitorPromiseRejectionCount || 0,
})
"""

CAPTURE_RESET_SCRIPT = """
(() => {
  window.__formMonitorCaptureErrors = [];
  window.__formMonitorCaptureCount = 0;
  window.__formMonitorResourceErrors = [];
  window.__formMonitorResourceCount = 0;
  window.__formMonitorPromiseRejections = [];
  window.__formMonitorPromiseRejectionCount = 0;
})()
"""

EMPTY_CAPTURE_SIGNALS = {
    "js_errors": [],
    "js_error_count": 0,
    "resource_errors": [],
    "resource_error_count": 0,
    "promise_rejections": [],
    "promise_rejection_count": 0,
}

DIAGNOSTIC_NAMES = (
    "busy",
    "resource_errors",
    "promise_rejections",
    "failed_requests",
    "title_metadata",
)


def safe_page_title(page):
    try:
        return clean_text(page.title())
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def safe_locator_visible(locator):
    """``is_visible`` kutmaydi — bu ataylab lahzalik surat."""
    try:
        return bool(locator.is_visible())
    except (PlaywrightError, AttributeError, TypeError):
        return False


def safe_locator_count(locator):
    try:
        return int(locator.count())
    except (PlaywrightError, AttributeError, TypeError, ValueError):
        return 0


def safe_inner_text(locator, *, timeout=750):
    try:
        return clean_text(locator.inner_text(timeout=timeout))
    except (PlaywrightError, AttributeError, TypeError):
        return ""


def safe_visible_headings(page):
    try:
        headings = page.get_by_role("heading").filter(visible=True).all_inner_texts()
    except (PlaywrightError, AttributeError, TypeError):
        return []
    return [clean_text(heading) for heading in headings if clean_text(heading)]


def failed_request_label(response):
    """4xx/5xx javobni qisqa yorliqqa aylantiradi; query string yozilmaydi."""
    try:
        status = int(response.status)
        if status < 400:
            return ""
        parts = urlsplit(str(response.url or ""))
    except (AttributeError, TypeError, ValueError):
        return ""
    return f"{status} {parts.netloc}{parts.path}"


def js_error_label(error):
    message = clean_text(getattr(error, "message", None) or error)
    return message[:300]


def read_capture_signals(page):
    """A2 JS xatosi va observation-only browser signallarini o'qiydi."""
    try:
        raw = page.evaluate(CAPTURE_READ_SCRIPT)
    except (PlaywrightError, AttributeError, TypeError):
        return dict(EMPTY_CAPTURE_SIGNALS)
    if not isinstance(raw, dict):
        return dict(EMPTY_CAPTURE_SIGNALS)

    def labels(values):
        return [
            text
            for text in (clean_text(item)[:300] for item in values or [])
            if text
        ]

    return {
        "js_errors": labels(raw.get("js")),
        "js_error_count": int(raw.get("jsCount") or 0),
        "resource_errors": labels(raw.get("resources")),
        "resource_error_count": int(raw.get("resourceCount") or 0),
        "promise_rejections": labels(raw.get("promiseRejections")),
        "promise_rejection_count": int(raw.get("promiseRejectionCount") or 0),
    }


def reset_capture_signals(page):
    try:
        page.evaluate(CAPTURE_RESET_SCRIPT)
    except (PlaywrightError, AttributeError, TypeError):
        pass


def wait_for_any_visible(page, selectors, *, timeout):
    """Birinchi ko'rinadigan selektorni kutadi; hech biri chiqmasa jim qaytadi."""
    try:
        page.locator(", ".join(selectors)).first.wait_for(
            state="visible",
            timeout=timeout,
        )
    except (PlaywrightError, AttributeError, TypeError):
        return


def visible_error_text(page):
    """Faqat aniq error komponentlarini o'qiydi; oddiy dialog xato emas."""
    wait_for_any_visible(page, ALERT_SELECTORS, timeout=ALERT_WAIT_MS)
    for selector in ALERT_SELECTORS:
        locator = page.locator(selector).first
        if not safe_locator_visible(locator):
            continue
        text = safe_inner_text(locator, timeout=500)
        if text:
            return text
    return ""


def generic_a2_content_ready(page):
    main = page.locator("main").first
    if not safe_locator_visible(main):
        return False
    if safe_inner_text(main):
        return True
    try:
        child = main.locator(":scope > *").filter(visible=True).first
    except (PlaywrightError, AttributeError, TypeError):
        return False
    return safe_locator_visible(child)


def capture_form_state(page, *, ready=None):
    """Check va diagnostika uchun bitta yakuniy browser state'ni o'qiydi."""
    actual_url = getattr(page, "url", "") or ""
    ready_visible = False

    if ready:
        ready_visible = safe_locator_visible(page.locator(ready).first)
        content_ready = ready_visible
    elif "/a2/" in actual_url:
        content_ready = generic_a2_content_ready(page)
    else:
        content_ready = any(
            safe_locator_visible(page.locator(selector).first)
            for selector in ("b-page:visible", ".subheader:visible")
        )

    loader_visible = any(
        safe_locator_visible(page.locator(selector).first)
        for selector in (
            ".block-ui-overlay:visible",
            ".smt-skeleton:visible",
        )
    )
    busy_visible_count = safe_locator_count(
        page.locator("[aria-busy='true']:visible")
    )

    document_title = safe_page_title(page)
    is_a2 = "/a2/" in actual_url
    title_candidates = [document_title] if is_a2 and document_title else []
    if not is_a2:
        title_candidates = safe_visible_headings(page)
    actual_form_title = " | ".join(title_candidates) or document_title

    return {
        "actual_url": actual_url,
        "actual_title": actual_form_title,
        "js_errors": [],
        "capture_signals": read_capture_signals(page),
        "document_title": document_title,
        "title_candidates": title_candidates,
        "title_source": "document" if is_a2 else "visible_heading",
        "canonical_path": canonical_form_path(actual_url),
        "visible_error": visible_error_text(page),
        "ready_required": bool(ready),
        "ready_visible": ready_visible,
        "content_ready": content_ready,
        "loader_visible": loader_visible,
        "busy_visible": busy_visible_count > 0,
        "busy_visible_count": busy_visible_count,
    }


def diagnose_busy(state):
    return {
        "enabled": True,
        "visible": bool(state.get("busy_visible")),
        "count": int(state.get("busy_visible_count") or 0),
    }


def diagnose_resource_errors(state):
    capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
    return {
        "enabled": True,
        "count": int(capture.get("resource_error_count") or 0),
        "samples": list(capture.get("resource_errors") or [])[:MAX_PAGE_EVENTS],
    }


def diagnose_promise_rejections(state):
    capture = state.get("capture_signals") or EMPTY_CAPTURE_SIGNALS
    return {
        "enabled": True,
        "count": int(capture.get("promise_rejection_count") or 0),
        "samples": list(capture.get("promise_rejections") or [])[:MAX_PAGE_EVENTS],
    }


def diagnose_failed_requests(page_events):
    return {
        "enabled": True,
        "count": int(page_events.get("failed_request_count") or 0),
        "samples": list(page_events.get("failed_requests") or [])[:MAX_PAGE_EVENTS],
    }


def diagnose_title_metadata(state):
    return {
        "enabled": True,
        "source": state.get("title_source") or "",
        "document_title": state.get("document_title") or "",
    }


DIAGNOSTIC_FUNCTIONS = {
    "busy": lambda state, page_events: diagnose_busy(state),
    "resource_errors": lambda state, page_events: diagnose_resource_errors(state),
    "promise_rejections": (
        lambda state, page_events: diagnose_promise_rejections(state)
    ),
    "failed_requests": (
        lambda state, page_events: diagnose_failed_requests(page_events)
    ),
    "title_metadata": lambda state, page_events: diagnose_title_metadata(state),
}


def evaluate_diagnostics(state, page_events, *, enabled_names=None):
    enabled = set(
        normalize_enabled_names(
            enabled_names,
            available=DIAGNOSTIC_NAMES,
            option_name="diagnostics",
        )
    )
    return {
        name: (
            DIAGNOSTIC_FUNCTIONS[name](state, page_events)
            if name in enabled
            else {"enabled": False}
        )
        for name in DIAGNOSTIC_NAMES
    }
