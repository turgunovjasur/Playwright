"""A2 Order konteksti; qo'shimcha data alohida tayyorlov testlarida yaratiladi."""
import json
import os
from contextlib import contextmanager
from functools import partialmethod
from pathlib import Path
from tests.regression.retry.state import stable_uuid as uuid4

import allure
import pytest

from scripts.api_setup_bridge import select_api_baseline, validate_api_baseline
from tests.regression.environment import RegressionEnvironmentError
from tests.regression.test_orders.reporting import GROUP_FEATURES, order_report_title
from tests.regression.test_orders.models import OrderContext, _json_value
from tests.regression.test_orders.auth_recovery import order_session_recovery
from tests.regression.session_recovery import bind_lookup_context, bind_grid_settings_context
from utils.data_store import load_data_file
from tests.regression.test_orders.ordering import (
    check_previous_steps, record_step, validate_and_order,
)


@pytest.fixture(autouse=True)
def order_loader_appearance_window(monkeypatch, request):
    """Order uses a 250ms DOM-only appearance probe, not an assertion.

    Full skeleton/busy completion assertions and response/value oracles remain.
    The shared default stays 8000ms; pytest restores it after each case.
    """
    if request.node.get_closest_marker("order_group") is not None:
        from utils.base_pages.angular_base_page import AngularBasePage
        monkeypatch.setattr(
            AngularBasePage, "_wait_for_loader",
            partialmethod(AngularBasePage._wait_for_loader, appear_timeout=250),
        )


@pytest.fixture(autouse=True)
def regression_lookup_recovery(monkeypatch, request):
    """Register the current b_input once; no testcase-specific login code."""
    if request.node.get_closest_marker("order_group") is not None:
        bind_lookup_context(monkeypatch)
        bind_grid_settings_context(monkeypatch)


@pytest.fixture(scope="session")
def api_business_baseline():
    root = Path(__file__).resolve().parents[3]
    try:
        select_api_baseline(root, os.environ)
        baseline = load_data_file()
        verified = validate_api_baseline(root, os.environ)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise RegressionEnvironmentError("API setup manifesti yoki baseline yaroqsiz; qayta tayyorlash kerak") from error
    if baseline != verified:
        raise RegressionEnvironmentError(
            "Tasdiqlangan API baseline kerak; avval API setupni muvaffaqiyatli yakunlang"
        )
    from tests.regression.retry.state import ACTIVE, digest, read, write
    journal = ACTIVE.get()
    if journal:
        config = journal.item.config
        plan = getattr(config, "_retry_plan", {})
        signature = digest(baseline)
        if plan and plan.get("baseline_signature") != signature:
            raise RegressionEnvironmentError("Retry API baseline dastlabki urinishga mos emas")
        from tests.regression.runtime import run_directory
        manifest = run_directory(config) / "retry-manifest.json"
        if manifest.exists():
            data = read(manifest)
            data["baseline_signature"] = signature
            write(manifest, data)
    return baseline


@pytest.fixture(scope="module")
def order_group_login(api_business_baseline):
    from tests.regression.test_orders.group_auth import GroupLogin
    login = GroupLogin(api_business_baseline)
    try:
        yield login
    finally:
        login.clear()


@pytest.fixture
def order_user_page(session_browser, regression_case_dir, request, order_group_login):
    from tests.regression.runtime import order_page_context
    with order_page_context(session_browser, request.node, storage_state=order_group_login.snapshot()) as page:
        page._order_group_login = order_group_login
        yield page


@pytest.fixture(scope="module")
def catalog_data(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "catalog_data")


@pytest.fixture
def business_baseline(api_business_baseline, catalog_data):
    """Group-local copy; never write own SKU IDs into the API setup baseline."""
    from copy import deepcopy
    from tests.regression.retry.state import digest
    baseline = deepcopy(api_business_baseline)
    baseline["_baseline_signature"] = digest(api_business_baseline)
    for kind, field, name in (("goods", "product_id", "product_name"),
                              ("bonus", "product_id_usa", "bonus_product_name")):
        if kind in catalog_data:
            baseline[field] = catalog_data[kind]["id"]
            baseline[name] = catalog_data[kind]["name"]
    return baseline


@pytest.fixture(scope="module")
def business_promotions(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "business_promotions")


@pytest.fixture(scope="module")
def payment_clients(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "payment_clients")


@contextmanager
def _context(page, baseline, promotions, directory, node, *, client=None):
    code = str(baseline["code"])
    client = client or {
        "name": f"natural_client-pw{code}",
        "person_id": str(baseline["client_person_id"]),
    }
    case = OrderContext(
        page=page, baseline=baseline, code=code, room=f"room-pw{code}",
        staff=f"robot-pw{code}", client=client["name"],
        product=baseline.get("product_name", f"product-pw{code}"),
        bonus_product=baseline.get("bonus_product_name", f"product-usa-pw{code}"),
        price_type=f"Price Type UZB-pw{code}", reference="B" + uuid4("order_reference").hex[:11],
        promotions=promotions,
    )
    from tests.regression.retry.state import ACTIVE
    journal = ACTIVE.get()
    if journal:
        journal.case = case
    ledger_path = directory / "case-data.json"

    def persist():
        data = {
            "case": node.nodeid, "baseline_code": code, "reference": case.reference,
            "client": client, "order_ids": case.orders, "payments": case.payments,
            "allocations": case.allocations, "returns": case.returns,
            "workflow": _json_value(case.workflow),
            "observations": case.observations, "server": baseline["url"],
            "company": baseline["company_code"], "filial_id": baseline["filial_id"],
            "setup_run_id": promotions.get("run_id"),
            "mandatory_setup": {key: promotions[key] for key in ("prices", "payments", "actions") if key in promotions} if "actions" in promotions else {},
            "bonus_limit_setup": promotions if "limit" in promotions else {},
            "promotion_ids": {
                key: promotions[key]["action_id"]
                for key in ("bonus", "discount") if promotions.get(key, {}).get("action_id")
            },
            "fixtures": {
                "product": {"id": str(baseline["product_id"]), "name": case.product},
                "bonus_product": {"id": str(baseline["product_id_usa"]), "name": case.bonus_product},
                "room": {"id": str(baseline["room_id"]), "name": case.room},
                "staff_name": case.staff,
                "warehouse_id": str(baseline["warehouse_id"]),
                "price_type": next((value for value in promotions.get("prices", {}).values() if value["name"] == case.price_type), {"id": str(baseline["price_type_id_uzb"]), "name": case.price_type}),
            },
            "retention": "retained",
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        temporary = ledger_path.with_suffix(".json.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(ledger_path)

    case.checkpoint = persist
    case.checkpoint()
    try:
        login = page._order_group_login
        with order_session_recovery(page, baseline, directory, on_authenticated=lambda: login.refresh_cookies(page)):
            login.authorize(page, baseline, directory)
            if "prepare" not in node.name and node.name not in {"test_000_catalog", "test_001_prices", "test_002_stock"}:
                from tests.regression.preparation.readiness import verify_retry_preparations
                verify_retry_preparations(case, node, directory)
            yield case
    finally:
        case.checkpoint()
        allure.attach(ledger_path.read_text(encoding="utf-8"),
                      "Order, klient va to'lov IDlari", allure.attachment_type.JSON)


def _base_promotions(baseline):
    return {"unit_price": "7000"}


def _require_bonus(promotions):
    if promotions.get("status") != "passed":
        pytest.skip("BLOCKED: bonus tayyorlovi bajarilmagan yoki muvaffaqiyatsiz; test_bonus kerak")


def _require_client(clients, key):
    client = clients.get(key, {})
    if client.get("status") != "passed":
        pytest.skip(f"BLOCKED: {key} to'lov klienti tayyorlanmagan; test_payment_clients kerak")
    return client


@pytest.fixture
def ordinary_order(order_user_page, business_baseline, regression_case_dir, request):
    with _context(order_user_page, business_baseline, _base_promotions(business_baseline),
                  regression_case_dir, request.node) as case:
        yield case


@pytest.fixture
def catalog_order(order_user_page, business_baseline, regression_case_dir, request):
    with _context(order_user_page, business_baseline, _base_promotions(business_baseline),
                  regression_case_dir, request.node) as case:
        yield case


@pytest.fixture
def promoted_order(order_user_page, business_baseline, business_promotions,
                   regression_case_dir, request):
    _require_bonus(business_promotions)
    with _context(order_user_page, business_baseline, business_promotions,
                  regression_case_dir, request.node) as case:
        yield case


@pytest.fixture
def ordinary_payment_order(order_user_page, business_baseline, payment_clients,
                           regression_case_dir, request):
    client = _require_client(payment_clients, "ordinary")
    with _context(order_user_page, business_baseline, _base_promotions(business_baseline),
                  regression_case_dir, request.node, client=client) as case:
        yield case


@pytest.fixture
def promoted_payment_order(order_user_page, business_baseline, business_promotions,
                           payment_clients, regression_case_dir, request):
    _require_bonus(business_promotions)
    client = _require_client(payment_clients, "promoted")
    with _context(order_user_page, business_baseline, business_promotions,
                  regression_case_dir, request.node, client=client) as case:
        yield case



@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection_modifyitems(config, items):
    # Boshqa hooklar, jumladan -k/-m filtrlari tugagach to'liq guruhni tekshirish.
    initial = [item for item in items if item.get_closest_marker("order_positive")]
    yield
    validate_and_order(config, items, initial)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    # Pytest fixture/login/browser setupidan oldin zanjirni tekshirish.
    check_previous_steps(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    record_step(item, outcome.get_result(), call)
    group = item.get_closest_marker("order_group")
    if (call.when == "call" and getattr(item.config, "_retry_plan", None)
            and group and group.args[0] in GROUP_FEATURES):
        allure.dynamic.title(order_report_title(group.args[0], item.name, rerun=True))


@pytest.fixture(scope="module")
def mandatory_data(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "mandatory_data")


@pytest.fixture
def mandatory_order(order_user_page, business_baseline, mandatory_data, regression_case_dir, request):
    if mandatory_data.get("status") != "passed":
        pytest.skip("BLOCKED: majburiy aksiya tayyorlovi yakunlanmagan")
    with _context(order_user_page, business_baseline, mandatory_data, regression_case_dir, request.node) as case:
        yield case


@pytest.fixture(scope="module")
def bonus_limit_data(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "bonus_limit_data")


@contextmanager
def _limit_context(page, baseline, data, directory, node, client_kind):
    if data.get("status") != "passed":
        pytest.skip("BLOCKED: umumiy bonus limiti tayyorlovi yakunlanmagan")
    client = data["clients"][client_kind]
    if client.get("status") != "passed":
        pytest.skip("BLOCKED: bonus limiti klienti tekshirilmagan")
    with _context(page, baseline, data, directory, node, client=client) as case:
        case.price_type = data["prices"]["quota"]["name"]
        case.checkpoint()
        yield case


@pytest.fixture
def first_limit_order(order_user_page, business_baseline, bonus_limit_data, regression_case_dir, request):
    with _limit_context(order_user_page, business_baseline, bonus_limit_data, regression_case_dir, request.node, "first") as case:
        yield case


@pytest.fixture
def second_limit_order(order_user_page, business_baseline, bonus_limit_data, regression_case_dir, request):
    with _limit_context(order_user_page, business_baseline, bonus_limit_data, regression_case_dir, request.node, "second") as case:
        yield case


@pytest.fixture(scope="module")
def workflow_data(request):
    """Faqat shu qat'iy runnerning tayyorlov va biznes qadamlariga tegishli."""
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "workflow_data")


@pytest.fixture
def workflow_order(order_user_page, business_baseline, workflow_data, regression_case_dir, request):
    client = workflow_data.get("client", {})
    if client.get("status") != "passed":
        pytest.skip("BLOCKED: guruh uchun alohida klient tayyorlanmagan")
    promotions = workflow_data.get("promotions", _base_promotions(business_baseline))
    with _context(order_user_page, business_baseline, promotions, regression_case_dir,
                  request.node, client=client) as case:
        case.workflow = workflow_data
        case.orders = workflow_data.setdefault("order_ids", [])
        case.payments = workflow_data.setdefault("payments", [])
        case.allocations = workflow_data.setdefault("allocations", [])
        case.returns = workflow_data.setdefault("returns", [])
        case.checkpoint()
        yield case


@pytest.fixture(scope="module")
def mixed_promotions_data(request):
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "mixed_promotions_data")


@pytest.fixture
def mixed_order(order_user_page, business_baseline, mixed_promotions_data, regression_case_dir, request):
    if mixed_promotions_data.get("status") != "passed":
        pytest.skip("BLOCKED: majburiy va ixtiyoriy aksiya tayyorlanmagan")
    with _context(order_user_page, business_baseline, mixed_promotions_data, regression_case_dir, request.node) as case:
        case.price_type = mixed_promotions_data["prices"]["mixed"]["name"]
        case.checkpoint()
        yield case


@pytest.fixture(scope="module")
def product_limit_data(request):
    from copy import deepcopy
    plan = getattr(request.config, "_order_resume", None)
    if plan:
        return deepcopy(plan.workflow)
    from tests.regression.retry.state import fixture_state
    return fixture_state(request, "product_limit_data")


@pytest.fixture
def product_limit_order(order_user_page, business_baseline, api_business_baseline, product_limit_data, regression_case_dir, request):
    plan = getattr(request.config, "_order_resume", None)
    if plan:
        plan.verify_baseline(api_business_baseline)
    client = product_limit_data.get("client", {})
    if client.get("status") != "passed" or not product_limit_data.get("product"):
        pytest.skip("BLOCKED: TMZ limiti mahsulot va klient tayyorlovi bajarilmagan")
    baseline = {**business_baseline, "product_id": product_limit_data["product"]["id"]}
    with _context(order_user_page, baseline, {"unit_price": "7000"}, regression_case_dir, request.node, client=client) as case:
        case.product = product_limit_data["product"]["name"]
        case.price_type = product_limit_data["price"]["name"]
        case.workflow = product_limit_data
        case.orders = product_limit_data.setdefault("order_ids", [])
        case.checkpoint()
        if plan:
            from tests.regression.resume import attach_resume
            from tests.regression.test_orders.stock.test_product_limit import verify_resume_state
            attach_resume(plan)
            if not plan.preflight_done:
                verify_resume_state(case)
                plan.preflight_done = True
                case.checkpoint()
        yield case


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    if item.get_closest_marker("order_positive") is None:
        yield
        return
    from tests.regression.retry.hooks import start, finish
    token = start(item)
    try:
        yield
    finally:
        finish(item, token)


@pytest.fixture(autouse=True)
def regression_retry_capture(monkeypatch, request):
    if request.node.get_closest_marker("order_positive") is None:
        yield
        return
    from tests.api.client import SmartupAPI
    from tests.regression.retry.reconcile import api_send
    from tests.regression.retry.hooks import attach_attempt
    original = SmartupAPI._send
    def observed(api, endpoint, *, payload=None, form=None, timeout=None):
        return api_send(original, api, endpoint, payload=payload, form=form, timeout=timeout)
    monkeypatch.setattr(SmartupAPI, "_send", observed)
    attach_attempt(request)
    yield
    journal = request.node._retry_journal
    allure.attach.file(str(journal.directory / "retry-journal.json"),
                       "Urinish jurnali — yaratilgan/qayta ishlatilgan yozuvlar", allure.attachment_type.JSON)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if pyfuncitem.get_closest_marker("order_positive") is not None:
        from tests.regression.preparation.repair import execute_selected_repair
        return execute_selected_repair(pyfuncitem)
    return None
