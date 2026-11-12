"""Order guruhlarini to'liq va runnerda yozilgan tartibda bajarish."""
from pathlib import Path

import pytest

from tests.regression.environment import environment_failure
from tests.regression.test_orders.reporting import SPECS

ROOT = Path(__file__).resolve().parents[3]
GROUP_RUNNERS = (
    "tests/regression/test_orders/runners/test_statuses_runner.py",
    "tests/regression/test_orders/runners/test_promotions_runner.py",
    "tests/regression/test_orders/runners/test_payments_runner.py",
    "tests/regression/test_orders/runners/test_mandatory_runner.py",
    "tests/regression/test_orders/runners/test_stock_runner.py",
    "tests/regression/test_orders/runners/test_bonus_limit_runner.py",
    "tests/regression/test_orders/runners/test_returns_runner.py",
    "tests/regression/test_orders/runners/test_multi_payments_runner.py",
    "tests/regression/test_orders/runners/test_manual_discounts_runner.py",
    "tests/regression/test_orders/runners/test_product_limit_runner.py",
    "tests/regression/test_orders/runners/test_two_warehouses_runner.py",
    "tests/regression/test_orders/runners/test_mixed_promotions_runner.py",
    "tests/regression/test_orders/runners/test_auto_offset_runner.py",
    "tests/regression/test_orders/runners/test_prepayment_first_runner.py",
)
GROUP_NAMES = ("statuses", "promotions", "payments", "mandatory", "stock", "bonus_limit", "returns", "multi_payments", "manual_discounts", "product_limit", "two_warehouses", "mixed_promotions", "auto_offset", "prepayment_first")
VERIFICATION_RUNNERS = {"recovery": "tests/regression/test_orders/verification/test_recovery_runner.py"}


def validate_and_order(config, items, initial):
    if not initial:
        return
    if len(initial) != len(items):
        raise pytest.UsageError(
            "Order guruh runnerlarini smoke, legacy yoki alohida leaflar bilan aralashtirmang."
        )
    for key in ("keyword", "markexpr", "lf", "failedfirst", "stepwise", "stepwise_skip",
                "numprocesses", "reruns", "count"):
        value = getattr(config.option, key, None)
        if value and not (key == "count" and value == 1):
            raise pytest.UsageError(
                f"Order guruhi to'liq va ketma-ket bajariladi: {key} qo'llanmaydi. "
                "Runner faylining o'zini Run qiling."
            )
    groups = {}
    for item in initial:
        marker = item.get_closest_marker("order_group")
        path = Path(str(item.path)).resolve()
        if marker is None or not marker.args or marker.args[0] not in (*GROUP_NAMES, *VERIFICATION_RUNNERS):
            raise pytest.UsageError(
                "Order leaf/tayyorlov faylini alohida Run qilmang; "
                "runners/ ichidagi tegishli to‘liq runner faylini tanlang."
            )
        group = marker.args[0]
        runner = VERIFICATION_RUNNERS[group] if group in VERIFICATION_RUNNERS else GROUP_RUNNERS[GROUP_NAMES.index(group)]
        if path != ROOT / runner:
            raise pytest.UsageError("Order guruhi uchun noma'lum runner fayli")
        groups[group] = item.module
    if set(groups) == set(GROUP_NAMES):
        config.option.maxfail = 1
    ordered = []
    if any(group in VERIFICATION_RUNNERS for group in groups) and len(groups) != 1:
        raise pytest.UsageError("Boshqariladigan uzilish verification runneri oddiy suite bilan aralashtirilmaydi")
    for group in (*GROUP_NAMES, *VERIFICATION_RUNNERS):
        if group not in groups:
            continue
        module = groups[group]
        # Testlar ro'yxatini boshqa joyda takrorlamaymiz: runnerning o'zi manba.
        functions = sorted(
            ((name, obj) for name, obj in vars(module).items()
             if name.startswith("test_") and callable(obj)
             and getattr(obj, "__module__", None) == module.__name__),
            key=lambda pair: pair[1].__code__.co_firstlineno,
        )
        expected = [name for name, _ in functions]
        selected = [item for item in items if item.module is module]
        if len(selected) != len(expected) or set(item.name for item in selected) != set(expected):
            raise pytest.UsageError(
                f"{group} guruhi to'liq tanlanmagan yoki takrorlangan. "
                "Alohida testni emas, runner faylining o'zini Run qiling."
            )
        by_name = {item.name: item for item in selected}
        ordered.extend(by_name[name] for name in expected)
    items[:] = ordered
    config._order_passed = set()
    config._order_blocked_by = {}
    config._order_environment_block = None
    config._order_phases = {}
    earlier_by_group = {}
    preparations_by_group = {}
    business_started = set()
    for item in ordered:
        group = item.get_closest_marker("order_group").args[0]
        earlier = earlier_by_group.setdefault(group, {})
        declarations = list(item.iter_markers("order_requires"))
        if len(declarations) != 1 or declarations[0].kwargs:
            raise pytest.UsageError(f"{item.nodeid}: yagona order_requires(*test_names) kerak")
        names = declarations[0].args
        if any(not isinstance(name, str) for name in names) or len(set(names)) != len(names):
            raise pytest.UsageError(f"{item.nodeid}: dependency nomlari yagona matn bo‘lishi kerak")
        if any(name not in earlier for name in names):
            raise pytest.UsageError(
                f"{item.nodeid}: dependency faqat shu runnerdagi oldingi testga tegishli bo‘lsin"
            )
        required = [earlier[name] for name in names]
        if group in GROUP_NAMES:
            spec = SPECS.get((group, item.name))
            if not spec or spec[1] not in {"Tayyorlov", "Biznes testi"}:
                raise pytest.UsageError(f"{item.nodeid}: tayyorlov yoki biznes turi belgilanmagan")
            preparations = preparations_by_group.setdefault(group, [])
            if spec[1] == "Tayyorlov":
                if group in business_started:
                    raise pytest.UsageError(f"{item.nodeid}: tayyorlov biznes testlaridan oldin turishi kerak")
                preparations.append(item.nodeid)
            else:
                business_started.add(group)
                required = [*preparations, *required]
        # The first attempt and the retry manifest share the same prerequisites.
        item._order_required_steps = tuple(dict.fromkeys(required))
        earlier[item.name] = item.nodeid

    from tests.regression.retry.planning import record_collection, apply_retry
    record_collection(config, items)
    apply_retry(config, items)
    from tests.regression.resume import apply_resume
    apply_resume(config, items)


def check_previous_steps(item):
    if item.get_closest_marker("order_group") is None:
        return
    config = item.config
    from tests.regression.retry.hooks import check_retry
    check_retry(item)
    if config._order_environment_block:
        source, reason = config._order_environment_block
        item._smartup_blocked_by = source
        pytest.skip("BLOCKED: umumiy test muhiti yaroqsiz: " + reason)
    missing = [node for node in item._order_required_steps if node not in config._order_passed]
    if missing:
        roots = tuple(dict.fromkeys(
            root for node in missing for root in config._order_blocked_by.get(node, (node,))
        ))
        config._order_blocked_by[item.nodeid] = roots
        item._smartup_blocked_by = "; ".join(roots)
        pytest.skip("BLOCKED: zarur tayyorlov yoki biznes qadami o‘tmagan: " + item._smartup_blocked_by)


def record_step(item, report, call):
    if item.get_closest_marker("order_group") is None:
        return
    config = item.config
    phases = config._order_phases.setdefault(item.nodeid, {})
    phases[report.when] = report.outcome
    if report.failed or report.skipped:
        config._order_blocked_by.setdefault(item.nodeid, (item.nodeid,))
    if report.failed and call.excinfo is not None:
        failure = environment_failure(call.excinfo.value)
        if failure is not None and config._order_environment_block is None:
            config._order_environment_block = (item.nodeid, str(failure))
    if report.when == "teardown" and all(phases.get(key) == "passed" for key in ("setup", "call", "teardown")):
        config._order_passed.add(item.nodeid)
