"""Smoke va regression uchun umumiy pytest fixture va lifecycle hooklari."""

import os
import random
import time
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

from scripts.report_lifecycle import generate_report, generate_test_summary, show_trace
from tests.shared import config as run_config, reporting
from tests.shared.authorization import authorization
from tests.shared.browser import browser_context, browser_page
from utils.data_store import data_file, load_data_file
from utils.logger import get_logger, write_failure_log
from utils.report_context import begin_test, end_test

ROOT_DIR = run_config.ROOT_DIR
TRACE_DIR = reporting.TRACE_DIR

# API has its own config/options and HTTP-only lifecycle. Run it separately
# with -c tests/api/pytest.ini; do not include it in the default UI collection.
collect_ignore = ["api"]

# CLI/environment precedence avvalgidek: lokal .env ustun.
run_config.load_local_dotenv()


def pytest_addoption(parser):
    """Smartup uchun CLI optionlarini pytestga ro'yxatdan o'tkazadi."""
    smartup = parser.getgroup("smartup")
    smartup.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Chromium ni headless rejimda ishga tushiradi",
    )
    smartup.addoption(
        "--new-code",
        action="store_true",
        default=False,
        help=(
            "Setup tanlangan bo'lsa yangi 6 xonali code yaratadi; setupsiz "
            "testlar har doim data_store.json dagi mavjud code ni ishlatadi"
        ),
    )
    smartup.addoption("--url", default="", help="Majburiy server URL")
    smartup.addoption(
        "--company-code",
        default="",
        help="Majburiy: 1 — yangi company yaratish; boshqa kod — mavjud company.",
    )
    smartup.addoption(
        "--company-password",
        default="",
        help="Mavjud company admin paroli; company code 1 bo'lmasa majburiy.",
    )
    smartup.addoption(
        "--head-email",
        default="",
        help="--company-code 1 bilan head profil emaili.",
    )
    smartup.addoption(
        "--head-password",
        default="",
        help="--company-code 1 bilan head profil paroli.",
    )
    smartup.addoption(
        "--disable-license-policy",
        action="store_true",
        default=False,
        help=(
            "--company-code 1 bilan yangi companyda Политика лицензирования "
            "ni o'chiradi."
        ),
    )


def pytest_configure(config):
    """Run environmentini tekshiradi va Allure metadata fayllarini tayyorlaydi."""
    config._smartup_started_at = time.time()
    expect.set_options(timeout=20_000)
    run_info = run_config.configure_environment(config)
    reporting.prepare_allure_results(run_info, ROOT_DIR)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Company yaratish testini joriy company rejimiga qarab ro'yxatdan chiqaradi."""
    if os.environ["COMPANY_CODE"] != "1":
        company_items = [
            item
            for item in items
            if (
                (Path(str(item.path)).name == "test_0_setup_runner.py"
                 or item.get_closest_marker("regression_setup") is not None)
                and item.name == "test_00_company"
            ) or (
                Path(str(item.path)).name == "test_00_company.py"
                and item.name == "test_company"
            )
        ]
        if company_items:
            items[:] = [item for item in items if item not in company_items]
            config.hook.pytest_deselected(items=company_items)

    smoke_setup = any(item.get_closest_marker("user_setup") for item in items)
    regression_setup = any(item.get_closest_marker("regression_setup") for item in items)
    if smoke_setup and regression_setup:
        raise pytest.UsageError(
            "Smoke va regression setup bitta code/data_store ishlatadi. "
            "Ularni alohida sessiyalarda ketma-ket run qiling: setup va regression-setup."
        )


def pytest_deselected(items):
    """Collectiondan chiqarilgan test nomlarini progress consumeriga uzatadi."""
    for item in items:
        reporting.emit_item_progress(item, "deselected")


def pytest_collection_finish(session):
    """Filtrlardan keyin progress uchun yakuniy test sonlarini bir marta hisoblaydi."""
    test_total = 0
    form_total = 0
    for item in session.items:
        if getattr(item, "_smartup_progress_context", None) is not None:
            test_total += 1
        if "form" in (getattr(item, "_smartup_progress_context", None) or {}):
            form_total += 1
    setattr(
        session,
        reporting.PROGRESS_TOTALS_ATTR,
        {"test_total": test_total, "form_total": form_total},
    )


@pytest.fixture(scope="session")
def session_browser():
    """Smartup testlar uchun umumiy Chromium browserini boshqaradi.

    Qancha yashaydi: butun pytest run davomida (`scope="session"`).
    Kim ishlatadi: `session_context`, `group_session_page` va `page` fixture'lari.
    Nima qaytaradi: bir marta ishga tushirilgan Playwright `Browser` obyekti.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            **run_config.browser_launch_options()
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


@pytest.fixture(scope="session")
def code(request):
    """Setup NEW_CODE'ni qo'llaydi; setupsiz run saqlangan code'ni oladi.

    Final tanlov tekshiriladi: -k/-m/node ID orqali setup chiqarib tashlansa
    yangi code yaratilmaydi. Setup + group run bitta session code'ni bo'lishadi.
    """
    setup_dirs = (ROOT_DIR / "tests/smoke/test_setup", ROOT_DIR / "tests/regression/test_setup")
    setup_selected = any(
        "code" in item.fixturenames and (
            item.get_closest_marker("user_setup") is not None
            or item.get_closest_marker("regression_setup") is not None
            or any(Path(str(item.path)).is_relative_to(directory) for directory in setup_dirs)
        )
        for item in request.session.items
    )
    if setup_selected and run_config.env_flag("NEW_CODE"):
        return str(random.randint(100000, 999999))

    saved = load_data_file().get("code")
    if saved:
        return saved

    pytest.exit(
        "test-results/data/data_store.json ichida saqlangan 'code' topilmadi. "
        "Avval setupni bajaring yoki API setup baseline'ni umumiy data_store.json ga ko'chiring."
    )


@pytest.fixture
def logger(request):
    """Har bir test uchun alohida loyiha loggerini ochadi va yakunda yopadi."""
    test_logger = get_logger(request.node.nodeid)
    try:
        yield test_logger
    finally:
        test_logger.close()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Skip/setup failure ham kiradigan testcase chegarasida kontekstni ajratadi."""
    token = begin_test(item.nodeid)
    try:
        yield
    finally:
        end_test(token)


def pytest_runtest_logreport(report):
    """Failed pytest fazasi uchun diskka diagnostika logini yozadi."""
    if not report.failed:
        return
    longrepr_text = str(report.longrepr) if report.longrepr else "Xabar yo'q"
    auth_diagnostic = next(
        (
            value
            for key, value in getattr(report, "user_properties", [])
            if key == "auth_diagnostic"
        ),
        "",
    )
    if auth_diagnostic:
        longrepr_text += f"\n\n[AUTH DIAGNOSTIKA]\n{auth_diagnostic}"
    try:
        log_path = write_failure_log(report.nodeid, report.when, longrepr_text)
        print(f"\n[LOG] Xato logi saqlandi: {log_path}")
    except Exception as error:
        reporting.reporting_warning(report.nodeid, "Xato logini saqlash", error)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Direct pytest summarysini yaratadi va so'ralgan trace/Allure reportni ochadi."""
    if run_config.env_flag("SMARTUP_RUNNER"):
        return

    generate_test_summary(
        ROOT_DIR,
        os.environ,
        test_exit=exitstatus,
        command_text="direct pytest run",
        started_at=session.config._smartup_started_at,
    )
    if run_config.env_flag("SHOW_TRACE"):
        show_trace(ROOT_DIR, os.environ, background=True)
    if run_config.env_flag("OPEN_REPORT"):
        generate_report(ROOT_DIR, os.environ, open_report=True, background=True)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Child dependency guardlaridan keyin, fixture'lardan oldin progressni boshlaydi."""
    reporting.start_progress(item)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Suite natija hooklaridan keyin umumiy diagnostikani bir marta yozadi."""
    outcome = yield
    report = outcome.get_result()
    reporting.record_test_report(item, report, call, data_file())
