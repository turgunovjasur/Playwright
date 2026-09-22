"""Regression setup dependency va suite metadata qoidalari."""

import os
from pathlib import Path

import pytest

from tests.shared import config as run_config
from utils.data_store import load_data_file

REGRESSION_DIR = Path(__file__).resolve().parent
_SETUP_FAILED = None


def pytest_configure(config):
    global _SETUP_FAILED
    _SETUP_FAILED = None


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Faqat regression itemlarini belgilaydi; umumiy reporting parent hookda."""
    regression_items = [item for item in items if Path(str(item.path)).is_relative_to(REGRESSION_DIR)]
    product_paths = {Path(str(item.path)) for item in regression_items if Path(str(item.path)).parent.name == "test_products"}
    if any(path.name == "test_0_products_runner.py" for path in product_paths) and len(product_paths) > 1:
        raise pytest.UsageError("ТМЦ runner va standalone leaflarni birga tanlamang: caselar ikki marta bajariladi. regression-products targeti yoki bitta leaf faylini ishlating.")
    requires_setup = any(item.get_closest_marker("regression_requires_setup") for item in regression_items)
    setup_selected = any(item.get_closest_marker("regression_setup") for item in regression_items)
    if requires_setup and not setup_selected:
        if os.environ.get("COMPANY_CODE") == "1":
            raise pytest.UsageError("Regression domain-only run uchun mavjud COMPANY_CODE kerak; yangi company uchun setup-regression-products targetini ishlating.")
        if run_config.env_flag("NEW_CODE"):
            raise pytest.UsageError("Regression domainlari yangi code uchun setupni talab qiladi. NEW_CODE=0 yoki setup-regression-products targetini ishlating.")
        baseline = load_data_file()
        saved_code = baseline.get("code")
        if not saved_code or baseline.get("filial_name") != f"filial-pw{saved_code}":
            raise pytest.UsageError("Regression uchun mos code/filial baseline topilmadi. Avval regression-setup yoki setup-regression-products ishlating.")
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
    if report.failed and item.get_closest_marker("regression_setup") is not None:
        _SETUP_FAILED = _SETUP_FAILED or item.nodeid
