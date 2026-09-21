"""Pytest smoke hooklari va umumiy fixture'lar uchun yagona kirish nuqtasi."""

import os
import random
import time
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

from scripts.report_lifecycle import generate_report, generate_test_summary, show_trace
from tests.smoke import smoke_config, smoke_reporting
from tests.smoke.smoke_browser import browser_context, browser_page
from tests.smoke.flows.flow_authorization import authorization
from utils.data_store import data_file, load_data_file
from utils.logger import get_logger, write_failure_log
from utils.report_context import begin_test, end_test


ROOT_DIR = smoke_config.ROOT_DIR
TRACE_DIR = smoke_reporting.TRACE_DIR

_USER_SETUP_FAILED = False
_FAILED_SMOKE_GROUPS = {}


# Lokal run profili pytest hooklari ishlashidan oldin yuklanishi kerak.
smoke_config.load_local_dotenv()


# 1. Run konfiguratsiyasi va boshlang'ich holat
# ----------------------------------------------------------------------------------------------------------------------

def pytest_addoption(parser):
    """Smartup smoke uchun CLI optionlarini pytestga ro'yxatdan o'tkazadi."""
    smoke = parser.getgroup("smartup smoke")
    smoke.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Chromium ni headless rejimda ishga tushiradi",
    )
    smoke.addoption(
        "--new-code",
        action="store_true",
        default=False,
        help=(
            "Yangi 6 xonali code yaratadi; berilmasa data_store.json dagi "
            "mavjud code ishlatiladi"
        ),
    )
    smoke.addoption("--url", default="", help="Majburiy server URL")
    smoke.addoption(
        "--company-code",
        default="",
        help="Majburiy: 1 — yangi company yaratish; boshqa kod — mavjud company.",
    )
    smoke.addoption(
        "--company-password",
        default="",
        help="Mavjud company admin paroli; company code 1 bo'lmasa majburiy.",
    )
    smoke.addoption(
        "--head-email",
        default="",
        help="--company-code 1 bilan head profil emaili.",
    )
    smoke.addoption(
        "--head-password",
        default="",
        help="--company-code 1 bilan head profil paroli.",
    )
    smoke.addoption(
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
    global _USER_SETUP_FAILED
    config._smartup_started_at = time.time()
    _USER_SETUP_FAILED = False
    _FAILED_SMOKE_GROUPS.clear()
    expect.set_options(timeout=10_000)
    run_info = smoke_config.configure_environment(config)
    smoke_reporting.prepare_allure_results(run_info, ROOT_DIR)


# 2. Testlarni tanlash va collection progressi
# ----------------------------------------------------------------------------------------------------------------------

def pytest_collection_modifyitems(config, items):
    """Company yaratish testini joriy company rejimiga qarab ro'yxatdan chiqaradi."""
    if os.environ["COMPANY_CODE"] != "1":
        company_items = [
            item
            for item in items
            if (
                Path(str(item.path)).name == "test_0_setup_runner.py"
                and item.name == "test_00_company"
            ) or (
                Path(str(item.path)).name == "test_00_company.py"
                and item.name == "test_company"
            )
        ]
        if company_items:
            items[:] = [item for item in items if item not in company_items]
            config.hook.pytest_deselected(items=company_items)


def pytest_deselected(items):
    """Collectiondan chiqarilgan test nomlarini progress consumeriga uzatadi."""
    for item in items:
        smoke_reporting.emit_item_progress(item, "deselected")


def pytest_collection_finish(session):
    """Filtrlardan keyin progress uchun yakuniy test sonlarini bir marta hisoblaydi."""
    test_total = 0
    form_total = 0
    for item in session.items:
        if smoke_reporting.is_user_setup(item) or smoke_reporting.smoke_group_name(item):
            test_total += 1
        if smoke_reporting.form_case_from_item(item) is not None:
            form_total += 1
    setattr(
        session,
        smoke_reporting.PROGRESS_TOTALS_ATTR,
        {"test_total": test_total, "form_total": form_total},
    )


# 3. Browser, context va page fixture'lari
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


# 4. Test data va logger fixture'lari
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


# 5. Har bir testning lifecycle'i va dependency tekshiruvi
# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Skip/setup failure ham kiradigan testcase chegarasida kontekstni ajratadi."""
    token = begin_test(item.nodeid)
    try:
        yield
    finally:
        end_test(token)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Setup/group dependency qoidalarini tekshiradi va progressni boshlaydi."""
    if smoke_reporting.is_user_setup(item):
        if _USER_SETUP_FAILED:
            item._smartup_blocked_by = _USER_SETUP_FAILED
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
        item._smartup_blocked_by = _USER_SETUP_FAILED
        pytest.skip(
            "User setup failed bo'lgani uchun setupga bog'liq group test skip qilindi"
        )

    if (
        group_name in _FAILED_SMOKE_GROUPS
        and not smoke_reporting.smoke_group_independent(item)
    ):
        item._smartup_blocked_by = _FAILED_SMOKE_GROUPS[group_name]
        pytest.skip(
            f"{group_name} group ichidagi oldingi test failed bo'lgani "
            "uchun skip qilindi"
        )

    smoke_reporting.start_progress(item)


# 6. Test natijalari va xato diagnostikasi
# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Avval dependency holatini yangilaydi, keyin natija va diagnostikani yozadi."""
    global _USER_SETUP_FAILED
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        if smoke_reporting.is_user_setup(item):
            _USER_SETUP_FAILED = _USER_SETUP_FAILED or item.nodeid

        group_name = smoke_reporting.smoke_group_name(item)
        if (
            group_name
            and not smoke_reporting.smoke_group_independent(item)
        ):
            _FAILED_SMOKE_GROUPS.setdefault(group_name, item.nodeid)

    smoke_reporting.record_test_report(item, report, call, data_file())


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
        smoke_reporting.reporting_warning(report.nodeid, "Xato logini saqlash", error)


# 7. Yakuniy hisobot va session yakunlash
# ----------------------------------------------------------------------------------------------------------------------

def pytest_terminal_summary(terminalreporter):
    """Forms runnerning strukturali natijalarini capture yopilgach chiqaradi."""
    reports = getattr(terminalreporter, "_smartup_forms_reports", [])
    for summary in reports:
        terminalreporter.write_sep("=", "FORMS — MARKAZIY MONITORING HISOBOTI")
        for line in summary.splitlines():
            terminalreporter.write_line(line)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Direct pytest summarysini yaratadi va so'ralgan trace/Allure reportni ochadi."""
    if smoke_config.env_flag("SMARTUP_RUNNER"):
        return

    generate_test_summary(
        ROOT_DIR,
        os.environ,
        test_exit=exitstatus,
        command_text="direct pytest run",
        started_at=session.config._smartup_started_at,
    )
    if smoke_config.env_flag("SHOW_TRACE"):
        show_trace(ROOT_DIR, os.environ, background=True)
    if smoke_config.env_flag("OPEN_REPORT"):
        generate_report(ROOT_DIR, os.environ, open_report=True, background=True)
