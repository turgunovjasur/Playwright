"""API-only fixtures: no page, browser, storage-state or UI runner dependency."""

import json
import os
import random
from pathlib import Path

import pytest

from tests.api.state import SetupState
from tests.shared import config as run_config


ROOT = Path(__file__).resolve().parents[2]
run_config.load_local_dotenv()


def pytest_addoption(parser):
    options = parser.getgroup("smartup-api")
    for name in ("url", "company-code", "company-password", "head-email", "head-password"):
        options.addoption("--" + name, default="")
    for name in ("headless", "new-code", "disable-license-policy"):
        options.addoption("--" + name, action="store_true", default=False)
    options.addoption("--api-data-file", default=str(ROOT / "test-results/api/data_store.json"))


def pytest_configure(config):
    run_config.configure_environment(config)
    if getattr(config.option, "numprocesses", 0):
        raise pytest.UsageError("API setup is sequential; run without pytest-xdist workers")
    config.addinivalue_line("markers", "api_setup: sequential HTTP setup chain")
    config._api_setup_failure = None


def pytest_collection_modifyitems(config, items):
    api_items = [item for item in items if item.get_closest_marker("api_setup")]
    if len(api_items) != len(items):
        raise pytest.UsageError("Run tests/api separately from the UI suites")
    # A directory selection sees both reusable leaf wrappers and the runner.
    # Keep a single execution of each step; an explicit leaf path still works.
    runner_present = any(item.path.name == "test_0_setup_runner.py" for item in items)
    deselected = [item for item in items if
                  (runner_present and item.path.name != "test_0_setup_runner.py") or
                  (os.environ["COMPANY_CODE"] != "1" and item.name == "test_00_company")]
    items[:] = [item for item in items if item not in deselected]
    if deselected:
        config.hook.pytest_deselected(items=deselected)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed and item.config._api_setup_failure is None:
        item.config._api_setup_failure = item.nodeid


def pytest_runtest_setup(item):
    if item.config._api_setup_failure:
        pytest.skip(f"Previous API setup step failed: {item.config._api_setup_failure}")


@pytest.fixture(scope="session")
def api_setup(pytestconfig):
    path = Path(pytestconfig.getoption("--api-data-file")).resolve()
    ui_store = (ROOT / "test-results/data/data_store.json").resolve()
    if path == ui_store:
        raise pytest.UsageError("--api-data-file must not overwrite the UI data_store.json")
    url = os.environ["COMPANY_URL"].rstrip("/")
    company = os.environ["COMPANY_CODE"]
    if run_config.env_flag("NEW_CODE"):
        values = {"code": str(random.SystemRandom().randint(100000, 999999)),
                  "url": url, "company_code": company, "suite": "api_setup"}
    else:
        try:
            values = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except (OSError, ValueError):
            raise pytest.UsageError(f"API baseline is not readable JSON: {path}") from None
        if not isinstance(values, dict):
            raise pytest.UsageError("API baseline must contain a JSON object")
        if not values or values.get("suite") != "api_setup":
            raise pytest.UsageError("API baseline missing; use NEW_CODE=1 for the complete API setup")
        if values.get("url") != url or (company != "1" and values.get("company_code") != company):
            raise pytest.UsageError("Saved API baseline belongs to a different server/company")
    state = SetupState(path, values)
    state.save()
    try:
        yield state
    finally:
        state.close()
