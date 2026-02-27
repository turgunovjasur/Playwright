import os

import pytest_asyncio
from playwright.async_api import async_playwright, Browser, Page

TRACE_DIR = "test-results/traces"


@pytest_asyncio.fixture
async def browser():
    """Bitta browser instance, to'liq ekranda ochiladi."""
    async with async_playwright() as p:
        browser_obj = await p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        yield browser_obj
        await browser_obj.close()


@pytest_asyncio.fixture
async def page(browser: Browser) -> Page:
    """Har bir test uchun yangi sahifa, to'liq ekran (no_viewport + --start-maximized). Trace yoziladi."""
    context = await browser.new_context(no_viewport=True)  # viewport cheklovini olib tashlaydi
    await context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page_obj = await context.new_page()
    # page.set_default_timeout(30_000)  # barcha operatsiyalar uchun 60s

    yield page_obj
    os.makedirs(TRACE_DIR, exist_ok=True)
    await context.tracing.stop(path=os.path.join(TRACE_DIR, "trace.zip"))
    await page_obj.close()
    await context.close()
