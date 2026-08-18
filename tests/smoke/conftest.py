"""Pytest smoke hooklari va umumiy fixture'lar uchun yagona kirish nuqtasi."""

import json
import os
import random
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

from tests.smoke import smoke_config, smoke_reporting
from tests.smoke.flows.flow_authorization import authorization
from utils.logger import get_logger


ROOT_DIR = smoke_config.ROOT_DIR
TRACE_DIR = smoke_reporting.TRACE_DIR
DATA_DIR = "test-results/data"

_USER_SETUP_FAILED = False
_FAILED_SMOKE_GROUPS = set()


# Lokal run profili pytest hooklari ishlashidan oldin yuklanishi kerak.
smoke_config.load_local_dotenv()


# Pytest konfiguratsiyasi
# ----------------------------------------------------------------------------------------------------------------------

def pytest_addoption(parser):
    """Smartup smoke uchun CLI optionlarini pytestga ro'yxatdan o'tkazadi."""
    smoke_config.add_pytest_options(parser)


def pytest_collection_modifyitems(config, items):
    """Directory runlarda faqat mos runnerlarni kerakli tartibda qoldiradi."""
    smoke_config.modify_collected_items(config, items)


def pytest_deselected(items):
    """Collectiondan chiqarilgan test nomlarini progress consumeriga uzatadi."""
    smoke_reporting.report_deselected(items)


def pytest_configure(config):
    """Run environmentini tekshiradi va Allure metadata fayllarini tayyorlaydi."""
    expect.set_options(timeout=10_000)
    run_info = smoke_config.configure_environment(config, _load_data_file)
    smoke_reporting.prepare_allure_results(config, run_info, ROOT_DIR)


# Data-store helperlari
# ----------------------------------------------------------------------------------------------------------------------

def _data_file(file_name="data_store"):
    """Berilgan data-store nomi uchun JSON fayl pathini qaytaradi."""
    return Path(DATA_DIR) / f"{file_name}.json"


def _load_data_file(file_name="data_store"):
    """Data-store JSON objectini o'qiydi; yo'q yoki bo'sh fayl uchun `{}` beradi."""
    path = _data_file(file_name)
    if not path.exists():
        return {}

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path} buzilgan JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{path} ichida JSON object bo'lishi kerak")
    return data


def _write_data_file(data, file_name="data_store"):
    """Data-store objectini vaqtinchalik fayl orqali atomik tarzda yozadi."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _data_file(file_name)
    temporary_path = path.with_suffix(".json.tmp")
    with temporary_path.open("w", encoding="utf-8") as data_file:
        json.dump(data, data_file, indent=4, ensure_ascii=False)
    temporary_path.replace(path)


# Browser va page fixture'lari
# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_browser(request):
    """Smoke testlar uchun umumiy Chromium browserini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: `session_context`, `group_session_page` va `page` fixture'lari.
    Nima qaytaradi: bir marta ishga tushirilgan Playwright `Browser` obyekti.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            **smoke_config.browser_launch_options(request.config)
        )
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def session_context(session_browser, request):
    """Setup chain uchun umumiy browser profilini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: `session_page` orqali barcha setup runner testlari.
    Nima qaytaradi: login, cookie va holatni saqlaydigan bitta `BrowserContext`.
    """
    context = session_browser.new_context(
        **smoke_config.browser_context_options(request.config)
    )
    context.set_default_timeout(10_000)
    context.set_default_navigation_timeout(20_000)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    os.makedirs(TRACE_DIR, exist_ok=True)
    context.tracing.stop(path=os.path.join(TRACE_DIR, "smoke_trace.zip"))
    context.close()


@pytest.fixture(scope="session")
def session_page(session_context):
    """Setup runner testlari uchun umumiy browser tabini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: setup runner ichidagi barcha ketma-ket testlar.
    Nima qaytaradi: `session_context` ichida ochilgan bitta umumiy `Page`.
    """
    page = session_context.new_page()
    smoke_reporting.install_auth_diagnostics(page)
    yield page
    page.close()


@pytest.fixture(scope="module")
def group_session_page(session_browser, request):
    """Bitta runner moduli uchun umumiy context va browser tabini boshqaradi.

    Qancha yashaydi: bitta runner moduli davomida (`scope="module"`).
    Kim ishlatadi: group/form runner testlari va `group_user_page` kabi wrapperlar.
    Nima qaytaradi: alohida contextdagi, avtomatik login qilinmagan umumiy `Page`.
    """
    context = session_browser.new_context(
        **smoke_config.browser_context_options(request.config)
    )
    context.set_default_timeout(10_000)
    context.set_default_navigation_timeout(20_000)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    smoke_reporting.install_auth_diagnostics(page)

    yield page

    os.makedirs(TRACE_DIR, exist_ok=True)
    safe_name = request.module.__name__.replace(".", "_")
    context.tracing.stop(path=os.path.join(TRACE_DIR, f"{safe_name}.zip"))
    page.close()
    context.close()


@pytest.fixture(scope="module")
def group_user_page(group_session_page, code):
    """Runner testlariga oddiy Smartup user sessiyasini beradi.

    Qancha yashaydi: bitta runner moduli davomida (`scope="module"`).
    Kim ishlatadi: oddiy user huquqi bilan bajariladigan group runner testlari.
    Nima qaytaradi: user bilan login qilingan o'sha `group_session_page` obyekti.
    """
    authorization(group_session_page, who="user", code=code)
    return group_session_page


@pytest.fixture
def page(session_browser, request):
    """Standalone test uchun toza browser profili va tabini boshqaradi.

    Qancha yashaydi: faqat bitta test funksiyasi davomida (`scope="function"`).
    Kim ishlatadi: boshqa testlardan izolyatsiya talab qiladigan standalone test.
    Nima qaytaradi: yangi alohida context ichida ochilgan toza `Page`.
    """
    context = session_browser.new_context(
        **smoke_config.browser_context_options(request.config)
    )
    context.set_default_timeout(10_000)
    context.set_default_navigation_timeout(20_000)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    isolated_page = context.new_page()
    smoke_reporting.install_auth_diagnostics(isolated_page)

    yield isolated_page

    os.makedirs(TRACE_DIR, exist_ok=True)
    safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
    context.tracing.stop(path=os.path.join(TRACE_DIR, f"{safe_name}.zip"))
    isolated_page.close()
    context.close()


# Test data va logger fixture'lari
# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def code(request):
    """Yangi 6 xonali code yaratadi yoki saqlangan `code` qiymatini qaytaradi."""
    new_code = smoke_config.option_flag_or_env(
        request.config,
        "--new-code",
        "NEW_CODE",
    )
    if new_code:
        return str(random.randint(100000, 999999))

    saved = _load_data_file().get("code")
    if saved:
        return saved

    pytest.exit(
        "Yakka test uchun saqlangan 'code' topilmadi. "
        "Avval test_0_setup_runner ni ishga tushiring."
    )


@pytest.fixture(scope="session")
def save_data():
    """Testlarga data-store ichiga key/value saqlash funksiyasini beradi."""
    os.makedirs(DATA_DIR, exist_ok=True)

    def _save(key, value, file_name="data_store"):
        """Bitta key/value qiymatini tanlangan data-store fayliga saqlaydi."""
        data = _load_data_file(file_name)
        data[key] = value
        _write_data_file(data, file_name)

    return _save


@pytest.fixture(scope="session")
def load_data():
    """Testlarga data-store ichidan optional qiymat o'qish funksiyasini beradi."""

    def _load(key, file_name="data_store"):
        """Key topilsa qiymatini, topilmasa `None` qaytaradi."""
        return _load_data_file(file_name).get(key)

    return _load


@pytest.fixture(scope="session")
def require_data(load_data):
    """Testlarga data-store ichidan majburiy qiymat o'qish funksiyasini beradi."""

    def _require(key, file_name="data_store"):
        """Key yo'q bo'lsa aniq dependency xatosi ko'taradi."""
        value = load_data(key, file_name=file_name)
        if value in (None, ""):
            raise AssertionError(
                f"{file_name}.json ichida majburiy key topilmadi: {key}"
            )
        return value

    return _require


@pytest.fixture
def logger(request):
    """Har bir test uchun alohida loyiha loggerini ochadi va yakunda yopadi."""
    test_logger = get_logger(request.node.nodeid)
    yield test_logger
    test_logger.close()


# Test lifecycle va dependency hooklari
# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Setup/group dependency qoidalarini tekshiradi va progressni boshlaydi."""
    if smoke_reporting.is_user_setup(item):
        if _USER_SETUP_FAILED:
            pytest.skip(
                "Oldingi user_setup testi failed bo'lgani uchun qolgan "
                "user_setup testlari skip qilindi"
            )
        smoke_reporting.start_progress(item)
        return

    group_name = smoke_reporting.smoke_group_name(item)
    if not group_name:
        return

    if (
        _USER_SETUP_FAILED
        and not smoke_reporting.smoke_group_setup_independent(item)
    ):
        pytest.skip(
            "User setup failed bo'lgani uchun setupga bog'liq group test skip qilindi"
        )

    if (
        group_name in _FAILED_SMOKE_GROUPS
        and not smoke_reporting.smoke_group_independent(item)
    ):
        pytest.skip(
            f"{group_name} group ichidagi oldingi test failed bo'lgani "
            "uchun skip qilindi"
        )

    smoke_reporting.start_progress(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test natijasini progress, screenshot va dependency statusiga aylantiradi."""
    global _USER_SETUP_FAILED
    outcome = yield
    report = outcome.get_result()
    auth_diagnostic = (
        smoke_reporting.auth_diagnostic_for_item(item)
        if report.failed
        else None
    )

    if report.failed:
        error_type = (
            auth_diagnostic["error_type"]
            if auth_diagnostic
            else call.excinfo.typename if call.excinfo else "Failed"
        )
        exception_message = (
            str(call.excinfo.value).strip() if call.excinfo else ""
        )
        smoke_reporting.finish_progress(
            item,
            "failed",
            error_type=error_type,
            message=(
                auth_diagnostic["summary"]
                if auth_diagnostic
                else exception_message
                or smoke_reporting.report_message(report)
            ),
        )
        if auth_diagnostic:
            report.user_properties.append(
                ("auth_diagnostic", auth_diagnostic["summary"])
            )
    elif report.skipped:
        smoke_reporting.finish_progress(
            item,
            "skipped",
            error_type="Skipped",
            message=smoke_reporting.report_message(report),
        )
    elif report.when == "teardown":
        smoke_reporting.finish_progress(item, "passed")

    if report.failed:
        smoke_reporting.attach_failure_artifacts(
            item,
            _data_file(),
            auth_diagnostic=auth_diagnostic,
        )
    elif report.when == "teardown":
        smoke_reporting.reset_auth_diagnostics(item)

    if report.failed:
        if smoke_reporting.is_user_setup(item):
            _USER_SETUP_FAILED = True

        group_name = smoke_reporting.smoke_group_name(item)
        if (
            group_name
            and not smoke_reporting.smoke_group_independent(item)
        ):
            _FAILED_SMOKE_GROUPS.add(group_name)


def pytest_runtest_logreport(report):
    """Failed pytest fazasi uchun diskka diagnostika logini yozadi."""
    smoke_reporting.log_failed_report(report)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Forms runnerning strukturali natijalarini capture yopilgach chiqaradi."""
    reports = getattr(terminalreporter, "_smartup_forms_reports", [])
    for summary in reports:
        terminalreporter.write_sep("=", "FORMS — MARKAZIY MONITORING HISOBOTI")
        for line in summary.splitlines():
            terminalreporter.write_line(line)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Direct pytest run tugaganda so'ralgan trace yoki Allure reportni ochadi."""
    smoke_reporting.finish_session(ROOT_DIR)
