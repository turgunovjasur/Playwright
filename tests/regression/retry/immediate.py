"""One immediate retry for audited cases; dependency failures stay local.

Every attempt enters the complete pytest protocol, including Allure's wrapper.
Only terminal copies of a provisional failure use the ``rerun`` outcome: the
phase ledger and raw Allure result retain the original failure unchanged.
"""
from copy import copy, deepcopy
from types import SimpleNamespace

import pytest
from _pytest.runner import runtestprotocol

from tests.regression.retry.state import day, read, write

# Admission is explicit, not inferred from a group/setup marker or a saved ID.
# These flows reconcile exact identities and stop on uncertain monetary writes.
PILOT_CASES = frozenset({
    "test_000_catalog", "test_001_prices", "test_002_stock",
    "test_00_prepare_promotions", "test_00a_prepare_discount",
    "test_01_prepare_ordinary_client", "test_02_prepare_promoted_client",
    "test_03_partial_full_payment", "test_04_promoted_order_payment",
})


def enabled(config):
    return bool(getattr(config, "_order_immediate_policy", False))


class _ParentBoundary:
    """Keep shared fixtures, while closing the current function's context."""

    def __init__(self, item):
        self.item = item

    def listchain(self):
        return self.item.listchain()[:-1]

    def __getattr__(self, name):
        return getattr(self.item, name)


def finish_teardown(item):
    """Make the retry decision inside the one ordinary teardown report.

    All function finalizers run first. If retry is denied, shared finalizers
    then run in this same CallInfo, so their failures are never lost.
    """
    outcome = yield
    if not getattr(item, "_order_boundary_active", False):
        return
    reports = [getattr(item, "rep_" + phase) for phase in ("setup", "call")
               if hasattr(item, "rep_" + phase)]
    reports.append(SimpleNamespace(when="teardown", passed=outcome.excinfo is None,
                                   failed=outcome.excinfo is not None, skipped=False))
    retry, reason = eligibility(item, reports)
    item._order_retry_decision = (retry, reason)
    if not retry:
        nextitem = item._order_actual_nextitem
        if item.session.shouldstop or item.session.shouldfail:
            nextitem = None
        try:
            item.session._setupstate.teardown_exact(nextitem)
        except BaseException as error:
            original = outcome.exception
            # Preserve interrupts unchanged; ordinary dual cleanup failures
            # belong to the same teardown report.
            interruptions = (KeyboardInterrupt, SystemExit, pytest.exit.Exception)
            if isinstance(error, interruptions):
                outcome.force_exception(error)
                return
            if isinstance(original, interruptions):
                return
            outcome.force_exception(BaseExceptionGroup("Test teardown xatolari", [original, error])
                                    if original is not None else error)


def eligibility(item, reports):
    """Return an explicit reason as well as the decision; default is no retry."""
    config = item.config
    group = item.get_closest_marker("order_group").args[0]
    if config.getoption("order_retries", 1) != 1:
        return False, "Retry foydalanuvchi sozlamasida o‘chirilgan"
    if getattr(item, "_regression_attempt", 1) != 1:
        return False, "Bitta qayta urinish limiti tugadi"
    if group != "payments" or item.name not in PILOT_CASES:
        return False, "Bu testcase avtomatik retry pilotiga hali kiritilmagan"
    if getattr(config, "_retry_plan", None) or getattr(config, "_order_resume", None):
        return False, "Resume yoki tashqi retry ichida yana retry qilinmaydi"
    if config._order_environment_block or item.session.shouldstop or item.session.shouldfail:
        return False, "Muhit yoki sessiya to‘xtash holatida"
    phases = {report.when: report for report in reports}
    if not phases.get("teardown") or not phases["teardown"].passed:
        return False, "Teardown muvaffaqiyatli tugamagan"
    if not any(report.failed for report in reports):
        return False, "Qayta urinish uchun FAILED natija yo‘q"
    if any(report.skipped for report in reports):
        return False, "SKIP/BLOCKED testi takrorlanmaydi"
    for definitions in item._fixtureinfo.name2fixturedefs.values():
        for fixture in definitions:
            cached = fixture.cached_result
            if fixture.scope != "function" and cached is not None and cached[2] is not None:
                return False, "Umumiy fixture setup xatosi cache’da qolgan; retry uni tiklamaydi"
    evidence = getattr(item, "regression_reports", {})
    if any(row.get("retry_safety_reason") or row.get("error_type") in {
        "RetryBlocked", "PreparationRepairRequired", "KeyboardInterrupt", "SystemExit",
    } for row in evidence.values()):
        return False, "Takrorlash xavfsizligi yoki uzilish himoyasi ishlagan"
    journal = getattr(item, "_retry_journal", None)
    if not journal or not hasattr(item, "_retry_before"):
        return False, "Dastlabki urinish jurnali yoki fixture snapshoti yo‘q"
    try:
        journal.save()
        saved = read(journal.directory / "retry-journal.json")
        if saved != journal.data or saved.get("nodeid") != item.nodeid or saved.get("day") != day():
            return False, "Jurnal testcase yoki joriy kunga mos emas"
    except (OSError, ValueError, TypeError):
        return False, "Urinish jurnalini tasdiqlab bo‘lmadi"
    return True, "Shu test yangi contextda, asl identity va yozish jurnali bilan boshidan bajariladi"


def execute_protocol(item, nextitem):
    """Called inside the normal protocol hook wrappers, exactly once per attempt."""
    if not enabled(item.config):
        return None
    ihook = item.ihook
    ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
    try:
        from tests.regression.retry.hooks import attach_attempt
        attach_attempt(SimpleNamespace(config=item.config, node=item))
        group = item.get_closest_marker("order_group").args[0]
        boundary = (group == "payments" and item.name in PILOT_CASES
                    and getattr(item, "_regression_attempt", 1) == 1
                    and item.config.getoption("order_retries", 1) == 1)
        item._order_boundary_active = boundary
        item._order_actual_nextitem = nextitem
        item._order_retry_decision = (False, "Retry qarori tasdiqlanmagan")
        reports = runtestprotocol(item, log=False,
                                  nextitem=_ParentBoundary(item) if boundary else nextitem)
        retry, reason = item._order_retry_decision if boundary else eligibility(item, reports)
        item._order_boundary_active = False
        item._order_retry_pending = retry
        if any(report.failed for report in reports):
            write(item.regression_case_dir / "retry-decision.json", {
                "nodeid": item.nodeid, "attempt": item._regression_attempt,
                "retry": retry, "reason": reason,
            })
        emitted = [copy(report) for report in reports]
        if retry:
            item._order_initial_failure = next(copy(r) for r in reports if r.failed)
            for report in emitted:
                if report.failed:
                    report.outcome = "rerun"
        elif getattr(item, "_order_initial_failure", None) and not any(r.failed for r in reports):
            # A second attempt blocked in setup is not a recovered first failure.
            if not all(any(r.when == phase and r.passed for r in reports)
                       for phase in ("setup", "call", "teardown")):
                report = next((r for r in emitted if r.skipped), emitted[-1])
                report.outcome = "failed"
                report.longrepr = ("Retry muvaffaqiyatli tugamadi; dastlabki xato saqlanadi.\n"
                                   + str(item._order_initial_failure.longrepr))
        for report in emitted:
            ihook.pytest_runtest_logreport(report=report)
        from tests.shared.reporting import emit_item_progress, finish_progress
        if retry:
            emit_item_progress(item, "retrying", attempt=2, message=reason)
        else:
            result = getattr(item, "_smartup_final_result", {"event": "passed"})
            if any(report.failed for report in emitted) and result["event"] != "failed":
                result = {"event": "failed", "message": "Retry tugamadi; dastlabki xato saqlanadi"}
            finish_progress(item, **result)
    finally:
        ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
    return True


def prepare_second_attempt(item):
    """Rollback only local fixture state; never delete/undo server writes."""
    config = item.config
    journal = item._retry_journal
    source = read(journal.directory / "retry-journal.json")
    snapshot = read(journal.directory / "retry-state.json")
    if source.get("nodeid") != item.nodeid or snapshot.get("nodeid") != item.nodeid:
        raise pytest.UsageError("Retry dalili boshqa testcasega tegishli")
    group = item.get_closest_marker("order_group").args[0]
    values = getattr(config, "_retry_states", {}).get(group, {})
    before = snapshot["before"]
    # Module fixtures cache these dictionaries. Replacing their objects breaks
    # isolation; clear/update keeps every cached reference on the restored state.
    for name in values.keys() | before.keys():
        target = values.setdefault(name, {})
        target.clear()
        target.update(deepcopy(before.get(name, {})))
    item._order_inline_source = source
    item._order_retry_pending = False
    config._order_phases.pop(item.nodeid, None)
    config._order_blocked_by.pop(item.nodeid, None)
    config._order_passed.discard(item.nodeid)
    for key in ("rep_setup", "rep_call", "rep_teardown", "_smartup_blocked_by",
                "_smartup_final_result", "_smartup_progress_started", "_smartup_progress_finished"):
        if hasattr(item, key):
            delattr(item, key)
    from tests.regression.runtime import begin_case
    begin_case(item)


def run_loop(session):
    if not enabled(session.config):
        return None
    if session.testsfailed and not session.config.option.continue_on_collection_errors:
        raise session.Interrupted(f"{session.testsfailed} collection error")
    if session.config.option.collectonly:
        return True
    for index, item in enumerate(session.items):
        nextitem = session.items[index + 1] if index + 1 < len(session.items) else None
        item.ihook.pytest_runtest_protocol(item=item, nextitem=nextitem)
        if getattr(item, "_order_retry_pending", False):
            if session.shouldstop:
                raise session.Interrupted(session.shouldstop)
            prepare_second_attempt(item)
            item.ihook.pytest_runtest_protocol(item=item, nextitem=nextitem)
        if session.shouldfail:
            raise session.Failed(session.shouldfail)
        if session.shouldstop:
            raise session.Interrupted(session.shouldstop)
    return True
