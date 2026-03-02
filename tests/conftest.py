import os
import json
import random
import pytest
from typing import Any, Generator
from playwright.sync_api import sync_playwright, Browser, Page

TRACE_DIR = "test-results/traces"
DATA_DIR = "test-results/data"

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

@pytest.fixture(scope="session")
def random_code():
    """Test sessiyasi uchun yagona cod qiymati"""
    return str(random.randint(1000, 9999))

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def save_data():
    """JSON faylga ma'lumot saqlash."""
    os.makedirs(DATA_DIR, exist_ok=True)

    def _save(key, value, file_name="data_store"):
        path = os.path.join(DATA_DIR, f"{file_name}.json")
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        data[key] = value
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    return _save

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def load_data():
    """JSON fayldan ma'lumot o'qish."""
    def _load(key, file_name="data_store"):
        path = os.path.join(DATA_DIR, f"{file_name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f).get(key)
                except json.JSONDecodeError:
                    return None
        return None

    return _load

# ----------------------------------------------------------------------------------------------------------------------
