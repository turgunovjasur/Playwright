"""External-service tests reuse a completed baseline without creating another user."""
from copy import deepcopy
import os
from pathlib import Path
import pytest
from scripts.api_setup_bridge import validate_api_baseline
from tests.api.state import SetupState


@pytest.fixture
def currency_baseline(tmp_path):
    root = Path(__file__).resolve().parents[3]
    baseline = validate_api_baseline(root, os.environ)
    state = SetupState(tmp_path / "currency-state.json", deepcopy(baseline))
    try:
        yield state
    finally:
        state.close()
