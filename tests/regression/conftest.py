"""Regression setup dependency va suite metadata qoidalari."""

import os
import json
import sys
import traceback
from pathlib import Path
from uuid import uuid4

import pytest

from utils.data_store import load_data_file
from tests.regression.runtime import (
    begin_case, case_directory, finalize_run, order_page_context, record_phase, run_directory,
)
from tests.shared.reporting import reporting_warning
from utils.report_safety import safe_text

REGRESSION_DIR = Path(__file__).resolve().parent
_SETUP_FAILED = None


@pytest.fixture
def order_case(page, code, tmp_path):
    """Order testcase uchun fresh login va alohida mijoz/mahsulot/qoldiq.

    Parent conftestda turadi: leaf, Order runner va umumiy regression runner
    bir xil fixture'ni ko'radi. `page` har test uchun yangi browser context.
    """
    import allure

    from tests.shared.authorization import authorization
    from tests.regression.test_orders.order_data import OrderCase
    from tests.regression.test_orders.order_environment import (
        cleanup_order_environment,
        prepare_order_environment,
    )

    key = f"{code}-{uuid4().hex[:8]}"
    case = OrderCase(key=key, room=f"room-pw{code}", staff=f"robot-pw{code}", client=f"Order client {key}", product=f"Order product {key}", product_code=f"op-{key}", bonus_product=f"Order bonus {key}", bonus_code=f"ob-{key}", price_type=f"Price Type USA-pw{code}", reference=f"OR{code}{key[-8:]}", directory=tmp_path)
    try:
        with allure.step("Order setup: alohida user sessiyasiga kirish"):
            authorization(page, who="user", code=code)
        prepare_order_environment(page, case, code)
        yield case
    finally:
        setup_error = sys.exc_info()[0] is not None
        try:
            cleanup_order_environment(page, case)
        except Exception as error:
            if not setup_error:
                raise
            allure.attach(str(error), "Setup xatosidan keyingi cleanup xatosi", allure.attachment_type.TEXT)


def pytest_configure(config):
    global _SETUP_FAILED
    _SETUP_FAILED = None
    config.addinivalue_line("markers", "order_positive: positive A2 Order cases and explicit preparations")
    config.addinivalue_line("markers", "order_group(name): full ordered Order regression group")
    config.addinivalue_line("markers", "order_requires(*test_names): explicit earlier prerequisites in the same runner")


@pytest.fixture(scope="session")
def regression_run_dir(request):
    return run_directory(request.config)


@pytest.fixture
def regression_case_dir(request, regression_run_dir):
    return case_directory(request.node)


@pytest.fixture
def order_page(session_browser, regression_case_dir, request):
    """Positive Order uchun alohida context va aynan shu run/attempt trace'i."""
    with order_page_context(session_browser, request.node) as page:
        yield page


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Faqat regression itemlarini belgilaydi; umumiy reporting parent hookda."""
    regression_items = [item for item in items if Path(str(item.path)).is_relative_to(REGRESSION_DIR)]
    regression_paths = {Path(str(item.path)) for item in regression_items}
    if REGRESSION_DIR / "test_0_regression_runner.py" in regression_paths and len(regression_paths) > 1:
        raise pytest.UsageError("Asosiy regression runnerni uning setup/products/orders runnerlari yoki leaflari bilan birga tanlamang. Faqat test_0_regression_runner.py yoki alohida runnerni ishlating.")
    product_paths = {Path(str(item.path)) for item in regression_items if Path(str(item.path)).parent.name == "test_products"}
    if any(path.name == "test_0_products_runner.py" for path in product_paths) and len(product_paths) > 1:
        raise pytest.UsageError("ТМЦ runner va standalone leaflarni birga tanlamang: caselar ikki marta bajariladi. regression-products targeti yoki bitta leaf faylini ishlating.")
    order_paths = {Path(str(item.path)) for item in regression_items if Path(str(item.path)).parent.name == "test_orders"}
    if any(path.name == "test_0_orders_runner.py" for path in order_paths) and len(order_paths) > 1:
        raise pytest.UsageError("Order runner va standalone leaflarni birga tanlamang: caselar ikki marta bajariladi. regression-orders targeti yoki bitta leaf faylini ishlating.")
    legacy_items = [item for item in regression_items if item.get_closest_marker("order_positive") is None]
    requires_setup = any(item.get_closest_marker("regression_requires_setup") for item in legacy_items)
    setup_selected = any(item.get_closest_marker("regression_setup") for item in legacy_items)
    if requires_setup and not setup_selected:
        if os.environ.get("COMPANY_CODE") == "1":
            raise pytest.UsageError("Regression domain-only run uchun mavjud COMPANY_CODE kerak; yangi company uchun setup-regression-products yoki setup-regression-orders targetini ishlating.")
        baseline = load_data_file()
        saved_code = baseline.get("code")
        if not saved_code or baseline.get("filial_name") != f"filial-pw{saved_code}":
            raise pytest.UsageError("Regression uchun mos code/filial baseline topilmadi. Avval regression-setup yoki mos setup-regression-products/setup-regression-orders targetini ishlating.")
    for item in items:
        if not Path(str(item.path)).is_relative_to(REGRESSION_DIR):
            continue
        setup = item.get_closest_marker("regression_setup") is not None
        title = getattr(getattr(item, "obj", None), "__allure_display_name__", None)
        item._smartup_progress_context = {
            "group": "Regression Setup" if setup else "Regression",
            "runner": Path(str(item.path)).name,
            "test_id": item.name,
            "title": title or item.name,
        }


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Setup failure faqat shu regression suite'ning bog'liq testlarini bloklaydi."""
    if item.get_closest_marker("order_positive") is not None:
        case_directory(item)
        return
    depends_on_setup = (
        item.get_closest_marker("regression_setup") is not None
        or item.get_closest_marker("regression_requires_setup") is not None
    )
    if _SETUP_FAILED and depends_on_setup:
        item._smartup_blocked_by = _SETUP_FAILED
        pytest.skip(f"Regression setup failed: {_SETUP_FAILED}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Intentional litsenziya skipi failure emas; haqiqiy xato chainni bloklaydi."""
    global _SETUP_FAILED
    outcome = yield
    report = outcome.get_result()
    if item.get_closest_marker("order_positive") is not None:
        try:
            record_phase(item, report, call)
        except Exception as error:
            reporting_warning(item.nodeid, "Order regression dalillarini yozish", safe_text(str(error)))
        return
    if report.failed and item.get_closest_marker("regression_setup") is not None:
        _SETUP_FAILED = _SETUP_FAILED or item.nodeid


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """Final fixturelar tugagach direct Order runi uchun alohida Allure nusxasi."""
    original_runner = os.environ.get("SMARTUP_RUNNER")
    standalone = (
        not os.environ.get("REGRESSION_RUN_ID")
        and original_runner != "1"
        and getattr(session.config, "_regression_run_dir", None) is not None
        and bool(session.items)
        and all(item.get_closest_marker("order_positive") for item in session.items)
        and not session.config.option.collectonly
    )
    if standalone:
        # Parent avtomatik reportni erta yaratmasin; aynan shu Order runi pastda yaratiladi.
        os.environ["SMARTUP_RUNNER"] = "1"
    try:
        outcome = yield
        outcome.get_result()
    finally:
        if standalone:
            if original_runner is None: os.environ.pop("SMARTUP_RUNNER", None)
            else: os.environ["SMARTUP_RUNNER"] = original_runner
    directory = getattr(session.config, "_regression_run_dir", None)
    if directory is None or os.environ.get("REGRESSION_RUN_ID"):
        return
    run = finalize_run(directory, int(session.exitstatus))
    if run["status"] == "blocked" and int(session.exitstatus) == 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        run["runner_exit_code"] = int(session.exitstatus)
        (directory / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if standalone:
        results = getattr(session.config.option, "allure_report_dir", None)
        if results:
            try:
                from tests.regression.test_orders.reporting import prepare_presentation
                from tests.regression.run import generate_run_report, run_pytest
                from tests.regression.retry.suite import retry_after_suite, combined_results, summarize
                # Snapshot only this session before merging the retry attempt.
                prepare_presentation(results, directory / "allure-results",
                                     started_at_ms=session.config._smartup_started_at * 1000)
                retry_directory = None
                if run["status"] != "interrupted" and session.config.option.maxfail != 1:
                    environment = {**os.environ, "SMARTUP_RUNNER": "1"}
                    try:
                        retry_directory = retry_after_suite(directory, environment, run_pytest)
                    except Exception as error:
                        # A readiness/reporting error must not hide the completed
                        # first attempt or prevent its Allure report being built.
                        (directory / "retry-error.json").write_text(json.dumps({
                            "error_type": type(error).__name__,
                            "detail": safe_text(traceback.format_exc()),
                        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                        reporting_warning("Order regression", "Yagona qayta urinish", error)
                session.exitstatus = summarize(directory, retry_directory)
                presentation = prepare_presentation(
                    combined_results(directory, retry_directory), directory / "allure-presentation-results",
                )
                from scripts.report_lifecycle import generate_test_summary
                generate_test_summary(
                    REGRESSION_DIR.parents[1], dict(os.environ),
                    test_exit=int(session.exitstatus), command_text="Order regression — direct pytest",
                    started_at=session.config._smartup_started_at,
                    results_dir=presentation, output_dir=directory,
                )
                generate_run_report(directory, presentation, dict(os.environ))
            except Exception as error:
                (directory / "reporting-error.json").write_text(json.dumps({
                    "error_type": type(error).__name__,
                    "detail": safe_text(traceback.format_exc()),
                }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                reporting_warning("Order regression", "Allure taqdimotini tayyorlash", error)
