from types import SimpleNamespace

import pytest

from tests.smoke import conftest as smoke_conftest
from tests.smoke import smoke_reporting


class _FakeItem:
    def __init__(self, *, group, **kwargs):
        self._marker = SimpleNamespace(args=(group,), kwargs=kwargs)

    def get_closest_marker(self, name):
        if name == "smoke_group":
            return self._marker
        return None


def test_setup_independent_forms_run_after_setup_failure(monkeypatch):
    item = _FakeItem(
        group="Forms",
        independent=True,
        setup_independent=True,
    )
    monkeypatch.setattr(smoke_conftest, "_USER_SETUP_FAILED", True)
    monkeypatch.setattr(smoke_reporting, "start_progress", lambda _item: None)

    smoke_conftest.pytest_runtest_setup(item)

    assert smoke_reporting.smoke_group_setup_independent(item) is True


def test_regular_group_is_still_skipped_after_setup_failure(monkeypatch):
    item = _FakeItem(group="0")
    monkeypatch.setattr(smoke_conftest, "_USER_SETUP_FAILED", True)
    monkeypatch.setattr(smoke_reporting, "start_progress", lambda _item: None)

    with pytest.raises(pytest.skip.Exception, match="User setup failed"):
        smoke_conftest.pytest_runtest_setup(item)

    assert smoke_reporting.smoke_group_setup_independent(item) is False
