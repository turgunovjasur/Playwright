"""Smoke suite'ga xos metadata va setup/group dependency qoidalari."""

from pathlib import Path

import pytest

from tests.smoke import smoke_reporting

SMOKE_DIR = Path(__file__).resolve().parent
_USER_SETUP_FAILED = False
_FAILED_SMOKE_GROUPS = {}


def pytest_configure(config):
    global _USER_SETUP_FAILED
    _USER_SETUP_FAILED = False
    _FAILED_SMOKE_GROUPS.clear()


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Collection hooklari global: metadata faqat smoke itemlariga tegishli."""
    for item in items:
        if not Path(str(item.path)).is_relative_to(SMOKE_DIR):
            continue
        item._smartup_progress_context = smoke_reporting.progress_metadata(item)
        item._smartup_forms_runner = smoke_reporting.smoke_group_name(item) == "Forms"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Smoke setup/group dependency qoidalarini tekshiradi."""
    if smoke_reporting.is_user_setup(item):
        if _USER_SETUP_FAILED:
            item._smartup_blocked_by = _USER_SETUP_FAILED
            pytest.skip(
                "Oldingi user_setup testi failed bo'lgani uchun qolgan "
                "user_setup testlari skip qilindi"
            )
        return

    group_name = smoke_reporting.smoke_group_name(item)
    if not group_name:
        return

    if (
        _USER_SETUP_FAILED
        and not smoke_reporting.smoke_group_setup_independent(item)
    ):
        item._smartup_blocked_by = _USER_SETUP_FAILED
        pytest.skip(
            "User setup failed bo'lgani uchun setupga bog'liq group test skip qilindi"
        )

    if (
        group_name in _FAILED_SMOKE_GROUPS
        and not smoke_reporting.smoke_group_independent(item)
    ):
        item._smartup_blocked_by = _FAILED_SMOKE_GROUPS[group_name]
        pytest.skip(
            f"{group_name} group ichidagi oldingi test failed bo'lgani "
            "uchun skip qilindi"
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Smoke setup/group failure holatini yangilaydi; reporting parent hookda."""
    global _USER_SETUP_FAILED
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        if smoke_reporting.is_user_setup(item):
            _USER_SETUP_FAILED = _USER_SETUP_FAILED or item.nodeid

        group_name = smoke_reporting.smoke_group_name(item)
        if (
            group_name
            and not smoke_reporting.smoke_group_independent(item)
        ):
            _FAILED_SMOKE_GROUPS.setdefault(group_name, item.nodeid)


def pytest_terminal_summary(terminalreporter):
    """Forms runnerning strukturali natijalarini capture yopilgach chiqaradi."""
    reports = getattr(terminalreporter, "_smartup_forms_reports", [])
    for summary in reports:
        terminalreporter.write_sep("=", "FORMS — MARKAZIY MONITORING HISOBOTI")
        for line in summary.splitlines():
            terminalreporter.write_line(line)
