"""Publish the current pytest item for CI without changing pytest output capture."""

import os
from pathlib import Path

import pytest


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    path = Path(os.environ["SMARTUP_CURRENT_TEST_FILE"])
    title = getattr(item.obj, "__allure_display_name__", None) or item.name
    items = item.session.items
    display = f"{items.index(item) + 1}/{len(items)} · {item.path.stem} · {title}"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(display, encoding="utf-8")
    temporary.replace(path)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)
