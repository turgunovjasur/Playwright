import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import utils.base_page as base_page_module


BasePage = base_page_module.BasePage


class _FakeTarget:
    def __init__(self):
        self.clicked = False

    def click(self):
        self.clicked = True


class _FakeCandidates:
    def __init__(self, target):
        self.target = target
        self.index = None

    def nth(self, index):
        self.index = index
        return self.target


class _FakeRoot:
    def __init__(self, candidates):
        self.candidates = candidates
        self.role_call = None

    def get_by_role(self, role, *, name, exact):
        self.role_call = (role, name, exact)
        return self.candidates


class _FakePage:
    def __init__(self, root):
        self.root = root
        self.selector = None

    def locator(self, selector):
        self.selector = selector
        return self.root


class _FakeExpectation:
    def __init__(self, target, assertions):
        self.target = target
        self.assertions = assertions

    def to_be_visible(self, *, timeout):
        self.assertions.append(("visible", self.target, timeout))


def test_click_uses_semantic_role_name_and_optional_scope(monkeypatch):
    target = _FakeTarget()
    candidates = _FakeCandidates(target)
    root = _FakeRoot(candidates)
    page = _FakePage(root)
    assertions = []
    base = BasePage(page)

    monkeypatch.setattr(
        base_page_module,
        "expect",
        lambda locator: _FakeExpectation(locator, assertions),
    )

    result = base.click(
        name="Доступные",
        index=2,
        root=".modal.show",
        timeout=1234,
    )

    assert result is target
    assert page.selector == ".modal.show"
    assert root.role_call == ("button", "Доступные", False)
    assert candidates.index == 2
    assert assertions == [("visible", target, 1234)]
    assert target.clicked
