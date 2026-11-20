"""Browser context va page uchun umumiy yaratish/yopish tartibi."""

import os
import sys
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.shared import config, reporting
from tests.shared.angular_asset_cache import enable_asset_cache
from utils.base_pages import UI_TIMEOUT_MS


_ZOOM_SETTINGS = "chrome://settings/appearance"
_pending_zoom_settings = {}


@contextmanager
def chromium_session(chromium):
    options = config.browser_launch_options()
    if options["headless"]:
        with chromium.launch(**options) as browser:
            yield browser
    else:
        # The temporary default profile owns Chromium's native zoom preference.
        # Test data still lives in separate contexts created by browser_context().
        with chromium.launch_persistent_context("", no_viewport=True, **options) as profile:
            settings = profile.pages[0]
            settings.goto(_ZOOM_SETTINGS)
            browser = profile.browser
            _pending_zoom_settings[browser] = settings
            try:
                yield browser
            finally:
                _pending_zoom_settings.pop(browser, None)


def _enter_fullscreen(page):
    page.bring_to_front()
    session = page.context.new_cdp_session(page)
    try:
        window = session.send("Browser.getWindowForTarget")
        # macOS may ignore the first request while it is closing the previous window.
        for attempt in range(3):
            session.send("Browser.setWindowBounds", {
                "windowId": window["windowId"],
                "bounds": {"windowState": "fullscreen"},
            })
            try:
                page.wait_for_function(
                    "matchMedia('(display-mode: fullscreen)').matches && outerWidth >= screen.width",
                    timeout=2000,
                )
                break
            except PlaywrightTimeoutError:
                if attempt == 2:
                    raise
    finally:
        session.detach()


def _fit_profile_zoom(page, settings):
    width, height = page.evaluate("[innerWidth, innerHeight]")
    if width >= config.DESKTOP_WIDTH and height >= config.DESKTOP_HEIGHT:
        return
    current_zoom = settings.evaluate("chrome.settingsPrivate.getDefaultZoom()")
    zoom = min(
        1,
        width * current_zoom / config.DESKTOP_WIDTH,
        height * current_zoom / config.DESKTOP_HEIGHT,
    )
    if zoom != current_zoom:
        settings.evaluate("zoom => chrome.settingsPrivate.setDefaultZoom(zoom)", zoom)
    page.wait_for_function(
        "([w, h]) => innerWidth >= w && innerHeight >= h",
        arg=[config.DESKTOP_WIDTH, config.DESKTOP_HEIGHT],
        timeout=UI_TIMEOUT_MS,
    )


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
        server = os.environ.get("COMPANY_URL")
        if server and os.environ.get("GITHUB_ACTIONS") != "true":
            enable_asset_cache(page, server, config.ROOT_DIR / "test-results" / "angular-cache")
        if page.viewport_size is None:
            _enter_fullscreen(page)
            browser = context.browser
            settings = _pending_zoom_settings.get(browser)
            if settings is not None:
                _fit_profile_zoom(page, settings)
                settings.close()
                del _pending_zoom_settings[browser]
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
