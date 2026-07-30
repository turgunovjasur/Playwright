import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import utils.base_page as base_page_module


BasePage = base_page_module.BasePage


class _FakeRow:
    pass


class _FakeRows:
    def __init__(self, row):
        self.row = row
        self.has_text = None

    def filter(self, *, has_text):
        self.has_text = has_text
        return self

    @property
    def first(self):
        return self.row


class _FakeGrid:
    def __init__(self, rows):
        self.rows = rows

    def locator(self, selector):
        assert selector == ".tbl-row"
        return self.rows


class _FakePage:
    def __init__(self, grid):
        self.grid = grid

    def locator(self, selector):
        assert selector == "b-grid"
        return self.grid


class _FakeExpectation:
    def __init__(self, target, assertions):
        self.target = target
        self.assertions = assertions

    def to_be_visible(self):
        self.assertions.append(("visible", self.target))

    def to_contain_text(self, value):
        self.assertions.append(("contains", self.target, value))


def test_grid_ignores_whitespace_by_default(monkeypatch):
    row = _FakeRow()
    rows = _FakeRows(row)
    assertions = []
    base = BasePage(_FakePage(_FakeGrid(rows)))
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target, assertions),
    )

    result = base.grid("28.07.2026", "10000")

    assert result is row
    assert isinstance(rows.has_text, re.Pattern)
    assert rows.has_text.search("28. 07. 2026")
    contains_pattern = assertions[1][2]
    assert isinstance(contains_pattern, re.Pattern)
    assert contains_pattern.search("10 000")
    assert contains_pattern.search("10\u00a0000")
    assert not contains_pattern.search("10 001")


def test_grid_can_keep_whitespace_sensitive_matching(monkeypatch):
    row = _FakeRow()
    rows = _FakeRows(row)
    assertions = []
    base = BasePage(_FakePage(_FakeGrid(rows)))
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target, assertions),
    )

    base.grid("28.07.2026", "10000", remove_spaces=False)

    assert rows.has_text == "28.07.2026"
    assert assertions[1] == ("contains", row, "10000")


def test_grid_rejects_non_boolean_remove_spaces():
    base = BasePage(page=object())

    with pytest.raises(TypeError, match="remove_spaces"):
        base.grid("row", remove_spaces="yes")
