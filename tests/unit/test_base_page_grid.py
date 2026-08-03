import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import utils.base_page as base_page_module


BasePage = base_page_module.BasePage


class _FakeRow:
    def __init__(self, visible=True, cells=None):
        self.visible = visible
        self.cells = cells

    def is_visible(self):
        return self.visible

    def locator(self, selector):
        assert selector == ".tbl-cell"
        return self.cells


class _FakeCell:
    def __init__(self, text):
        self.text = text

    def inner_text(self):
        return self.text


class _FakeCells:
    def __init__(self, cells):
        self.cells = cells
        self.index = None

    def nth(self, index):
        self.index = index
        return self.cells[index]


class _FakeNoData:
    def __init__(self, visible):
        self.visible = visible

    def is_visible(self):
        return self.visible


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
    def __init__(self, rows, no_data=None):
        self.rows = rows
        self.no_data = no_data

    def filter(self, *, visible):
        assert visible is True
        return self

    @property
    def first(self):
        return self

    def locator(self, selector):
        assert selector == ".tbl-row"
        return self.rows

    def get_by_text(self, text, *, exact):
        assert (text, exact) == ("нет данных", True)
        return self.no_data


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


def test_grid_empty_state_asserts_with_playwright_expect(monkeypatch):
    row = _FakeRow()
    no_data = _FakeNoData(visible=True)
    grid = _FakeGrid(_FakeRows(row), no_data=no_data)
    assertions = []
    base = BasePage(_FakePage(grid))
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target, assertions),
    )

    result = base.grid(state="empty")

    assert result is grid
    assert assertions == [("visible", no_data)]


@pytest.mark.parametrize("visible", [True, False])
def test_grid_empty_state_can_return_bool(visible):
    row = _FakeRow()
    grid = _FakeGrid(_FakeRows(row), no_data=_FakeNoData(visible))
    base = BasePage(_FakePage(grid))

    assert base.grid(state="empty", return_bool=True) is visible


@pytest.mark.parametrize("visible", [True, False])
def test_grid_row_visibility_can_return_bool(visible):
    row = _FakeRow(visible=visible)
    base = BasePage(_FakePage(_FakeGrid(_FakeRows(row))))

    assert base.grid("Акция", return_bool=True) is visible


def test_grid_rejects_bool_mode_with_row_action():
    base = BasePage(page=object())

    with pytest.raises(ValueError, match="return_bool"):
        base.grid("Акция", click=True, return_bool=True)


def test_grid_cell_asserts_and_returns_value_without_spaces(monkeypatch):
    cell = _FakeCell("  7\u00a0000  ")
    cells = _FakeCells([cell])
    row = _FakeRow(cells=cells)
    assertions = []
    base = BasePage(page=object())
    monkeypatch.setattr(base_page_module, "expect", lambda target: _FakeExpectation(target, assertions))

    result = base.grid_cell(row, 0, expect_value=7000, return_value=True, remove_spaces=True)

    assert result == "7000"
    assert cells.index == 0
    assert assertions[0] == ("visible", cell)
    expected_pattern = assertions[1][2]
    assert isinstance(expected_pattern, re.Pattern)
    assert expected_pattern.search("7 000")
    assert expected_pattern.search("7\u00a0000")


@pytest.mark.parametrize("index", [-1, "1"])
def test_grid_cell_rejects_invalid_index(index):
    base = BasePage(page=object())

    with pytest.raises(ValueError, match=r"grid_cell\(index"):
        base.grid_cell(_FakeRow(), index)
