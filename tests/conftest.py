"""
Playwright async testlar uchun fixture'lar.
page – har bir test uchun yangi browser sahifa (async).

NIMA UCHUN O'Z FIXTURE'IMIZ?
pytest-playwright plugin o'zining sync "page" fixture'ini beradi va ichida event loop
ishg'a tushiradi. test_login esa async (pytest-asyncio). Ikki loop bir-biriga
kirib ketadi → "Runner.run() cannot be called from a running event loop".
Bu yerda o'zimiz async_playwright + pytest_asyncio.fixture ishlatamiz – hammasi
BITTA asyncio loop'da ishlaydi, conflict bo'lmaydi.
"""
import pytest_asyncio
from playwright.async_api import async_playwright, Browser, Page


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
    """Har bir test uchun yangi sahifa, to'liq ekran (no_viewport + --start-maximized)."""
    context = await browser.new_context(no_viewport=True)  # viewport cheklovini olib tashlaydi
    page_obj = await context.new_page()
    yield page_obj
    await page_obj.close()
    await context.close()
