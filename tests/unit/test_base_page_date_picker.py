import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import utils.base_page as base_page_module

BasePage = base_page_module.BasePage


def test_base_page_date_returns_formatted_relative_date():
    assert BasePage.date(
        "2026-07-28",
        days=1,
        date_format="%Y-%m-%d",
    ) == "2026-07-29"


class _FakeInput:
    def __init__(self):
        self.click_count = 0

    def click(self):
        self.click_count += 1


class _FakeExpectation:
    def __init__(self, target, assertions):
        self.target = target
        self.assertions = assertions

    def to_be_visible(self, *, timeout):
        self.assertions.append(("visible", self.target, timeout))

    def to_have_value(self, value, *, timeout):
        self.assertions.append(("value", self.target, value, timeout))


def test_date_picker_auto_fill_checks_existing_date_without_opening_calendar(monkeypatch):
    input_el = _FakeInput()
    assertions = []
    base = BasePage(page=object())

    monkeypatch.setattr(base, "_resolve_root", lambda root: root)
    monkeypatch.setattr(
        base,
        "_field_locator_by_label",
        lambda label, *, index, root, target: input_el,
    )
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target, assertions),
    )

    result = base.date_picker(
        "Дата курса",
        date="today",
        auto_fill=True,
        root="modal",
        timeout=1234,
    )

    assert result is input_el
    assert input_el.click_count == 0
    assert assertions == [
        ("visible", input_el, 1234),
        ("value", input_el, BasePage.date("today"), 1234),
    ]


def test_date_picker_rejects_non_boolean_auto_fill():
    base = BasePage(page=object())

    with pytest.raises(TypeError, match="auto_fill bool"):
        base.date_picker("Дата курса", auto_fill="yes")


def test_date_picker_parses_shown_days_when_navigating_to_another_month(monkeypatch):
    state = {
        "target_visible": False,
        "navigation_clicks": 0,
        "day_clicks": 0,
    }
    input_el = _FakeInput()
    assertions = []

    class _TargetDay:
        @property
        def first(self):
            return self

        def count(self):
            return int(state["target_visible"])

        def get_attribute(self, name):
            assert name == "class"
            return ""

        def click(self):
            state["day_clicks"] += 1

    class _ShownDay:
        def get_attribute(self, name):
            assert name == "data-day"
            return "01.08.2026"

    class _ShownDays:
        def count(self):
            return 1

        def nth(self, index):
            assert index == 0
            return _ShownDay()

    class _Navigation:
        @property
        def first(self):
            return self

        def get_attribute(self, name):
            assert name == "class"
            return ""

        def click(self):
            state["navigation_clicks"] += 1
            state["target_visible"] = True

    class _Picker:
        def locator(self, selector):
            if selector == '[data-action="selectDay"][data-day="01.07.2026"]':
                return _TargetDay()
            if selector == '[data-action="selectDay"]':
                return _ShownDays()
            if selector == "th.prev":
                return _Navigation()
            raise AssertionError(f"Unexpected selector: {selector}")

    class _PickerLocator:
        @property
        def last(self):
            return _Picker()

    class _Page:
        def locator(self, selector):
            assert selector == ".bootstrap-datetimepicker-widget:visible"
            return _PickerLocator()

    base = BasePage(page=_Page())
    monkeypatch.setattr(base, "_resolve_root", lambda root: root)
    monkeypatch.setattr(
        base,
        "_field_locator_by_label",
        lambda label, *, index, root, target: input_el,
    )
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target, assertions),
    )

    result = base.date_picker(
        "Дата курса",
        date="01.07.2026",
        root="modal",
        timeout=1234,
    )

    assert result is input_el
    assert input_el.click_count == 1
    assert state == {
        "target_visible": True,
        "navigation_clicks": 1,
        "day_clicks": 1,
    }
    assert assertions[-1] == ("value", input_el, "01.07.2026", 1234)
