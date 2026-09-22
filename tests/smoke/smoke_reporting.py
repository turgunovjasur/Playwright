"""Smoke group/Forms metadata; umumiy diagnostika tests.shared ichida."""

from collections.abc import Mapping
from pathlib import Path

import pytest

# Eski consumerlar uchun public diagnostika API manzili saqlanadi.
from tests.shared.reporting import (
    PROGRESS_TOTALS_ATTR as PROGRESS_TOTALS_ATTR,
    auth_diagnostic_for_item as auth_diagnostic_for_item,
    reset_auth_diagnostics as reset_auth_diagnostics,
    safe_page_screenshot as safe_page_screenshot,
)

__all__ = [
    "PROGRESS_TOTALS_ATTR", "auth_diagnostic_for_item", "reset_auth_diagnostics",
    "safe_page_screenshot", "smoke_group_name", "smoke_group_independent",
    "smoke_group_setup_independent", "is_user_setup", "form_case_from_item",
    "progress_metadata",
]


def smoke_group_name(item):
    """Test itemidagi `smoke_group` markeridan group nomini qaytaradi."""
    marker = item.get_closest_marker("smoke_group")
    if not marker:
        return None
    if not marker.args:
        raise pytest.UsageError(
            "smoke_group marker group nomini talab qiladi: "
            "@pytest.mark.smoke_group('A')"
        )
    return str(marker.args[0])


def smoke_group_independent(item):
    """Group ichidagi testlar bir-biridan mustaqil belgilanganini tekshiradi."""
    marker = item.get_closest_marker("smoke_group")
    return bool(marker and marker.kwargs.get("independent", False))


def smoke_group_setup_independent(item):
    """Setup failed bo'lsa ham group ishlashi kerakligini tekshiradi."""
    marker = item.get_closest_marker("smoke_group")
    return bool(marker and marker.kwargs.get("setup_independent", False))


def is_user_setup(item):
    """Test item `user_setup` chainiga tegishli ekanini tekshiradi."""
    return item.get_closest_marker("user_setup") is not None


def form_case_from_item(item):
    """Parametrized Forms itemidagi structured case metadata'ni qaytaradi."""
    callspec = getattr(item, "callspec", None)
    params = getattr(callspec, "params", None)
    if not isinstance(params, Mapping):
        return None
    form_case = params.get("form_case")
    return form_case if isinstance(form_case, Mapping) else None


def _form_progress_context(item):
    """Telegram progress uchun user-readable forma kontekstini normalize qiladi."""
    form_case = form_case_from_item(item)
    if form_case is None:
        return None

    try:
        number = int(form_case.get("global_number"))
    except (TypeError, ValueError):
        number = 0

    return {
        "number": number,
        "navbar": str(form_case.get("navbar_tab") or "").strip(),
        "menu": str(form_case.get("menu_column") or "").strip(),
        "title": str(
            form_case.get("label")
            or form_case.get("title")
            or form_case.get("menu_item")
            or item.name
        ).strip(),
        "filial": str(form_case.get("filial") or "").strip(),
        "expected_url": str(form_case.get("expected_path") or "").strip(),
    }


def _form_progress_display(context):
    """Forma raqami va UI yo'lidan Telegramda ko'rinadigan nom yasaydi."""
    path = " → ".join(
        value
        for value in (
            context.get("navbar"),
            context.get("menu"),
            context.get("title"),
        )
        if value
    )
    number = int(context.get("number") or 0)
    return f"{number:03d} | {path or 'Noma’lum forma'}"


def progress_metadata(item):
    """Progress event uchun test groupi, runneri va ko'rinadigan nomini yig'adi."""
    if is_user_setup(item):
        group = "Setup"
    else:
        group_name = smoke_group_name(item)
        if not group_name:
            return None
        group = f"{group_name} group"

    allure_title = (
        getattr(getattr(item, "obj", None), "__allure_display_name__", None)
        or item.name
    )
    metadata = {
        "group": group,
        "runner": Path(str(item.path)).name,
        "test_id": item.name,
        "title": allure_title,
    }
    form_context = _form_progress_context(item)
    if form_context is not None:
        display = _form_progress_display(form_context)
        metadata.update(
            title=display,
            display=display,
            form=form_context,
        )
    return metadata
