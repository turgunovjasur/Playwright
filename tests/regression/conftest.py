"""Regression setup dependency va suite metadata qoidalari."""

import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from utils.data_store import load_data_file

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
    requires_setup = any(item.get_closest_marker("regression_requires_setup") for item in regression_items)
    setup_selected = any(item.get_closest_marker("regression_setup") for item in regression_items)
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
