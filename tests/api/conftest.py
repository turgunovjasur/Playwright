"""API-only fixtures: no page, browser, storage-state or UI runner dependency."""

import hashlib
import json
import os
import random
import re
import time
from pathlib import Path

import pytest

from scripts.api_setup_bridge import _expected_steps, record_setup_success
from scripts.report_lifecycle import generate_report
from tests.api.state import SetupState
from tests.shared import config as run_config
from utils.report_safety import safe_text


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
    config._api_failure_summary = ""
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
    if config.option.collectonly or config._api_external_run:
        return
    if session.exitstatus == 0 and config._api_default_baseline:
        _record_completed_setup(session)

    if run_config.env_flag("SMARTUP_RUNNER"):
        return
    if (session.testscollected and run_config.env_flag("OPEN_REPORT")
            and not run_config.env_flag("DEFER_ALLURE_REPORT")):
        results = Path(config.option.allure_report_dir).resolve()
        report_dir = ROOT / "test-results/api/allure-report"
        env = os.environ.copy()
        env.setdefault("ALLURE_HISTORY_PATH", str(ROOT / "test-results/api/allure-history/history.jsonl"))
        if results.is_relative_to(report_dir.resolve()):
            print("[ALLURE] Natijalar va HTML hisobot uchun alohida kataloglar kerak.")
        else:
            generate_report(ROOT, env, results_dir=results, report_dir=report_dir,
                            open_report=True, background=True)
    # PyCharm passes --no-summary, so pytest_terminal_summary is never called.
    if config._api_failure_summary:
        terminal = config.pluginmanager.getplugin("terminalreporter")
        if terminal:
            terminal.write_sep("=", "API setup xatosi", red=True)
            terminal.write_line(config._api_failure_summary)


def _is_complete_setup(session):
    runner, expected = _expected_steps(ROOT, session.config._api_setup_environment)
    names = [item.name for item in session.items]
    return (len(names) == len(expected) and set(names) == expected
            and all(item.path.resolve() == runner for item in session.items))


def _record_completed_setup(session):
    config = session.config
    if not _is_complete_setup(session):
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
        if not item.config._api_external_run and not run_config.env_flag("SMARTUP_RUNNER"):
            item.config._api_failure_summary = _failure_summary(item, call, report)


def _failure_summary(item, call, report):
    listener = item.config.pluginmanager.getplugin("allure_listener")
    result = listener.allure_logger.get_test(None) if listener else None
    title = result.name if result and result.name else item.name
    phases = {"setup": "Testni tayyorlash", "call": "Testni bajarish", "teardown": "Testni yakunlash"}
    path = []
    steps = result.steps if result and report.when == "call" else []
    while steps:
        failed = next((step for step in reversed(steps) if step.status in {"failed", "broken"}), None)
        if failed is None:
            break
        path.append(failed.name)
        steps = failed.steps
    if call.excinfo:
        reason = str(call.excinfo.value) or call.excinfo.typename
    else:
        reason = report.longreprtext
    http_error = re.fullmatch(r"POST (\S+): HTTP (\d{3})(.*)", reason)
    if http_error:
        endpoint, status, detail = http_error.groups()
        reason = f"Server POST {endpoint} so‘roviga HTTP {status} qaytardi.{detail}"
    step = " → ".join(path) or phases[report.when]
    return f"Test: {safe_text(title)}\nQadam: {safe_text(step)}\nXato: {safe_text(reason).strip()[:800]}"


def pytest_runtest_setup(item):
    if item.config._api_setup_failure:
        pytest.skip(f"Previous API setup step failed: {item.config._api_setup_failure}")


@pytest.fixture(scope="session")
def api_setup(pytestconfig, request):
    path = Path(pytestconfig.getoption("--api-data-file")).resolve()
    ui_store = (ROOT / "test-results/data/data_store.json").resolve()
    if path == ui_store:
        raise pytest.UsageError("--api-data-file must not overwrite the UI data_store.json")
    url = os.environ["COMPANY_URL"].rstrip("/")
    company = os.environ["COMPANY_CODE"]
    if run_config.env_flag("NEW_CODE") or _is_complete_setup(request.session):
        if path.exists():
            previous = path.read_bytes()
            backups = path.parent / "baseline-backups"
            backups.mkdir(parents=True, exist_ok=True)
            (backups / f"{hashlib.sha256(previous).hexdigest()}.json").write_bytes(previous)
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
