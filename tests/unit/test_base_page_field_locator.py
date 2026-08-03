import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import utils.base_page as base_page_module


BasePage = base_page_module.BasePage


class _FakeElement:
    def __init__(self, *, text="", box=None):
        self.text = text
        self.box = box

    def inner_text(self):
        return self.text

    def bounding_box(self):
        return self.box


class _FakeCollection:
    def __init__(self, items):
        self.items = items

    @property
    def first(self):
        return self.items[0] if self.items else self

    def count(self):
        return len(self.items)

    def nth(self, index):
        return self.items[index]


class _FakeGrid:
    def __init__(self, headers, candidates):
        self.headers = _FakeCollection(headers)
        self.candidates = _FakeCollection(candidates)

    def locator(self, selector):
        if selector == "b-pg-grid:visible":
            return _FakeCollection([])
        if selector == ".tbl-header-cell":
            return self.headers
        if selector == "b-input:visible":
            return self.candidates
        raise AssertionError(f"Kutilmagan selector: {selector}")


class _FakeExpectation:
    def __init__(self, target):
        self.target = target

    def to_be_visible(self, *, timeout):
        assert timeout in {1_000, 10_000}


def test_grid_header_locator_normalizes_nbsp_before_matching(monkeypatch):
    product_input = _FakeElement(
        box={"x": 20, "y": 50, "width": 200, "height": 30}
    )
    grid = _FakeGrid(
        headers=[
            _FakeElement(
                text="Название\xa0",
                box={"x": 10, "y": 10, "width": 300, "height": 30},
            ),
            _FakeElement(
                text="Цена\xa0",
                box={"x": 310, "y": 10, "width": 100, "height": 30},
            ),
        ],
        candidates=[product_input],
    )
    base = BasePage(page=object())
    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda target: _FakeExpectation(target),
    )

    result = base._field_locator_by_grid_header(
        "Название",
        root=grid,
        target="b-input",
    )

    assert result is product_input
