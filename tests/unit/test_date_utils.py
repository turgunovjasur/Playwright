import sys
from calendar import monthrange
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from utils.date_utils import format_date, resolve_date


def test_format_date_returns_tashkent_today_by_default():
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    assert format_date() == today.strftime("%d.%m.%Y")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("28.07.2026", date(2026, 7, 28)),
        ("2026-07-28", date(2026, 7, 28)),
        ("28/07/2026", date(2026, 7, 28)),
        ("28-07-2026", date(2026, 7, 28)),
        (date(2026, 7, 28), date(2026, 7, 28)),
        (datetime(2026, 7, 28, 10, 30), date(2026, 7, 28)),
    ],
)
def test_resolve_date_accepts_supported_date_values(value, expected):
    assert resolve_date(value) == expected


def test_resolve_date_supports_relative_days():
    assert resolve_date("2026-07-28", days=3) == date(2026, 7, 31)
    assert resolve_date("2026-07-28", days=-1) == date(2026, 7, 27)


def test_resolve_date_supports_month_boundaries():
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    assert resolve_date("first_day") == today.replace(day=1)
    assert resolve_date("month_start") == today.replace(day=1)
    assert resolve_date("last_day") == today.replace(
        day=monthrange(today.year, today.month)[1]
    )
    assert resolve_date("month_end") == today.replace(
        day=monthrange(today.year, today.month)[1]
    )


def test_resolve_date_supports_named_relative_days():
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    assert resolve_date("yesterday") == today - timedelta(days=1)
    assert resolve_date("tomorrow") == today + timedelta(days=1)


@pytest.mark.parametrize("date_format", ["%Y-%m-%d", "YYYY-MM-DD"])
def test_format_date_supports_custom_output_format(date_format):
    assert format_date("28.07.2026", date_format=date_format) == "2026-07-28"


@pytest.mark.parametrize("days", [True, 1.5, "1"])
def test_resolve_date_rejects_non_integer_days(days):
    with pytest.raises(TypeError, match="days int"):
        resolve_date(days=days)
