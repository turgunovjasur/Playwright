"""Pytest smoke hooklari va umumiy fixture'lar uchun yagona kirish nuqtasi."""

import random
import time
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

from tests.smoke import smoke_config, smoke_reporting
from tests.smoke.smoke_browser import browser_context, browser_page
from tests.smoke.flows.flow_authorization import authorization
from utils.data_store import data_file, load_data_file
from utils.logger import get_logger


ROOT_DIR = smoke_config.ROOT_DIR
TRACE_DIR = smoke_reporting.TRACE_DIR

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
    """Company yaratish testini joriy company rejimiga qarab ro'yxatdan chiqaradi."""
    smoke_config.modify_collected_items(config, items)


def pytest_deselected(items):
    """Collectiondan chiqarilgan test nomlarini progress consumeriga uzatadi."""
    smoke_reporting.report_deselected(items)


def pytest_collection_finish(session):
    """Filtrlardan keyin progress uchun yakuniy test sonlarini bir marta hisoblaydi."""
    smoke_reporting.prepare_progress_totals(session)


def pytest_configure(config):
    """Run environmentini tekshiradi va Allure metadata fayllarini tayyorlaydi."""
    global _USER_SETUP_FAILED
    config._smartup_started_at = time.time()
    _USER_SETUP_FAILED = False
    _FAILED_SMOKE_GROUPS.clear()
    expect.set_options(timeout=10_000)
    run_info = smoke_config.configure_environment(config)
    smoke_reporting.prepare_allure_results(run_info, ROOT_DIR)


# Browser va page fixture'lari
# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_browser():
    """Smoke testlar uchun umumiy Chromium browserini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: `session_context`, `group_session_page` va `page` fixture'lari.
    Nima qaytaradi: bir marta ishga tushirilgan Playwright `Browser` obyekti.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            **smoke_config.browser_launch_options()
        )
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture(scope="session")
def session_context(session_browser):
    """Setup chain uchun umumiy browser profilini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: `session_page` orqali barcha setup runner testlari.
    Nima qaytaradi: login, cookie va holatni saqlaydigan bitta `BrowserContext`.
    """
    with browser_context(session_browser, Path(TRACE_DIR) / "smoke_trace.zip") as context:
        yield context


@pytest.fixture(scope="session")
def session_page(session_context):
    """Setup runner testlari uchun umumiy browser tabini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: setup runner ichidagi barcha ketma-ket testlar.
    Nima qaytaradi: `session_context` ichida ochilgan bitta umumiy `Page`.
    """
    with browser_page(session_context) as page:
        yield page


@pytest.fixture(scope="module")
def group_session_page(session_browser, request):
    """Bitta runner moduli uchun umumiy context va browser tabini boshqaradi.

    Qancha yashaydi: bitta runner moduli davomida (`scope="module"`).
    Kim ishlatadi: group/form runner testlari va `group_user_page` kabi wrapperlar.
    Nima qaytaradi: alohida contextdagi, avtomatik login qilinmagan umumiy `Page`.
    """
    safe_name = request.module.__name__.replace(".", "_")
    with browser_context(session_browser, Path(TRACE_DIR) / f"{safe_name}.zip") as context:
        with browser_page(context) as page:
            yield page


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
    safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
    with browser_context(session_browser, Path(TRACE_DIR) / f"{safe_name}.zip") as context:
        with browser_page(context) as isolated_page:
            yield isolated_page


# Test data va logger fixture'lari
# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def code():
    """Yangi 6 xonali code yaratadi yoki saqlangan `code` qiymatini qaytaradi."""
    if smoke_config.env_flag("NEW_CODE"):
        return str(random.randint(100000, 999999))

    saved = load_data_file().get("code")
    if saved:
        return saved

    pytest.exit(
        "Yakka test uchun saqlangan 'code' topilmadi. "
        "Avval test_0_setup_runner ni ishga tushiring."
    )


@pytest.fixture
def logger(request):
    """Har bir test uchun alohida loyiha loggerini ochadi va yakunda yopadi."""
    test_logger = get_logger(request.node.nodeid)
    try:
        yield test_logger
    finally:
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
    """Avval dependency holatini yangilaydi, keyin natija va diagnostikani yozadi."""
    global _USER_SETUP_FAILED
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        if smoke_reporting.is_user_setup(item):
            _USER_SETUP_FAILED = True

        group_name = smoke_reporting.smoke_group_name(item)
        if (
            group_name
            and not smoke_reporting.smoke_group_independent(item)
        ):
            _FAILED_SMOKE_GROUPS.add(group_name)

    smoke_reporting.record_test_report(item, report, call, data_file())


def pytest_runtest_logreport(report):
    """Failed pytest fazasi uchun diskka diagnostika logini yozadi."""
    smoke_reporting.log_failed_report(report)


def pytest_terminal_summary(terminalreporter):
    """Forms runnerning strukturali natijalarini capture yopilgach chiqaradi."""
    reports = getattr(terminalreporter, "_smartup_forms_reports", [])
    for summary in reports:
        terminalreporter.write_sep("=", "FORMS — MARKAZIY MONITORING HISOBOTI")
        for line in summary.splitlines():
            terminalreporter.write_line(line)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Direct pytest run tugaganda so'ralgan trace yoki Allure reportni ochadi."""
    smoke_reporting.finish_session(ROOT_DIR, exitstatus, started_at=session.config._smartup_started_at)
