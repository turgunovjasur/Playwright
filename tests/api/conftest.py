"""API-only fixtures: no page, browser, storage-state or UI runner dependency."""

import json
import os
import random
import time
from pathlib import Path

import pytest

from scripts.api_setup_bridge import _expected_steps, record_setup_success
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


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    run_config.configure_environment(config)
    if getattr(config.option, "numprocesses", 0):
        raise pytest.UsageError("API setup is sequential; run without pytest-xdist workers")
    config.addinivalue_line("markers", "api_setup: sequential HTTP setup chain")
    config.addinivalue_line("markers", "api_external: external-service API integration")
    integration_root = (ROOT / "tests/api/integrations").resolve()
    selected_paths = [Path(str(arg).split("::", 1)[0]).resolve() for arg in config.args]
    config._api_external_run = bool(selected_paths) and all(
        path == integration_root or integration_root in path.parents for path in selected_paths
    )
    includes_integration = any(
        path == integration_root or integration_root in path.parents
        or path in integration_root.parents for path in selected_paths
    )
    if includes_integration and not config._api_external_run:
        # Reject before sessionstart invalidates the baseline or Allure cleans
        # setup results. A broad tests/api selection is deliberately ambiguous.
        raise pytest.UsageError("Setup va tashqi kurs integratsiyasini alohida runnerlarda Run qiling")
    config._api_setup_failure = None
    config._api_default_baseline = (
        Path(config.getoption("--api-data-file")).resolve()
        == (ROOT / "test-results/api/data_store.json").resolve()
        and not config._api_external_run
    )
    if config._api_external_run:
        # Integration runs must never clean setup results, overwrite its JUnit,
        # or invalidate the successful baseline used by regression.
        if config.option.xmlpath and Path(config.option.xmlpath).resolve() == (ROOT / "test-results/api/setup-runner.xml").resolve():
            raise pytest.UsageError("Tashqi kurs testi setup JUnit faylini almashtira olmaydi")
        if not config.option.xmlpath:
            config.option.xmlpath = str(ROOT / "test-results/api/external-currency.xml")
        if Path(config.option.allure_report_dir).resolve() == (ROOT / "test-results/api/allure-results").resolve():
            config.option.allure_report_dir = str(ROOT / "test-results/api/external-currency-results")
    # Collection/custom baseline eski regression dalilini almashtirmasin.
    if not config.option.collectonly and config._api_default_baseline:
        if not config.pluginmanager.hasplugin("junitxml"):
            raise pytest.UsageError(
                "API setup tasdig‘i uchun JUnit plugini kerak; -p no:junitxml ni olib tashlang"
            )
        if not config.option.xmlpath:
            config.option.xmlpath = str(ROOT / "test-results/api/setup-runner.xml")


def pytest_sessionstart(session):
    config = session.config
    config._api_setup_started_at = time.time()
    config._api_setup_environment = dict(os.environ)
    if not config.option.collectonly and config._api_default_baseline:
        # Yangi yoki qisman setup oldingi muvaffaqiyat bilan tasdiqlanmasin.
        (ROOT / "test-results/api/setup-success.json").unlink(missing_ok=True)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    # JUnit pluginining sessionfinish'i faylni yozib bo‘lishini kutamiz.
    outcome = yield
    outcome.get_result()
    config = session.config
    if config.option.collectonly or session.exitstatus != 0 or not config._api_default_baseline:
        return
    runner, expected = _expected_steps(ROOT, config._api_setup_environment)
    names = [item.name for item in session.items]
    if (len(names) != len(expected) or set(names) != expected
            or any(item.path.resolve() != runner.resolve() for item in session.items)):
        # Leaf yoki tanlangan qadamlarni run qilish mumkin, lekin ular to‘liq setup emas.
        return
    try:
        record_setup_success(
            ROOT, config._api_setup_environment,
            started_at=config._api_setup_started_at,
            junit_path=config.option.xmlpath,
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        terminal = config.pluginmanager.getplugin("terminalreporter")
        if terminal:
            terminal.write_line(f"API setup tasdiq fayli yozilmadi: {error}", red=True)


def pytest_collection_modifyitems(config, items):
    external_items = [item for item in items if item.get_closest_marker("api_external")]
    if external_items and (len(external_items) != len(items) or not config._api_external_run):
        raise pytest.UsageError("Tashqi kurs integratsiyasini o‘z runnerida setupdan alohida Run qiling")
    api_items = [item for item in items if item.get_closest_marker("api_setup") or item.get_closest_marker("api_external")]
    if len(api_items) != len(items):
        raise pytest.UsageError("Run tests/api separately from the UI suites")
    # A directory selection sees both reusable leaf wrappers and the runner.
    # Keep a single execution of each step; an explicit leaf path still works.
    runner_present = any(item.path.name in {"test_0_setup_runner.py", "test_0_currency_runner.py"} for item in items)
    deselected = [item for item in items if
                  (runner_present and item.path.name not in {"test_0_setup_runner.py", "test_0_currency_runner.py"}) or
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
