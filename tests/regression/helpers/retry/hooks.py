"""Pytest integration, limited to positive Order regression runners."""
import allure
import pytest

from tests.regression.helpers.runtime import case_directory
from tests.regression.helpers.retry.state import ACTIVE, Journal, snapshot, write


def start(item):
    directory = case_directory(item)
    plan = getattr(item.config, "_retry_plan", {})
    source = getattr(item, "_order_inline_source", None) or plan.get("journals", {}).get(item.nodeid)
    journal = Journal(item, directory, source)
    item._retry_journal = journal
    item._retry_before = snapshot(item)
    return ACTIVE.set(journal)


def finish(item, token):
    try:
        journal = item._retry_journal
        write(journal.directory / "retry-state.json", {
            "nodeid": item.nodeid, "before": item._retry_before, "after": snapshot(item),
        })
        journal.save()
    finally:
        ACTIVE.reset(token)


def check_retry(item):
    plan = getattr(item.config, "_retry_plan", {})
    if item.nodeid in plan.get("blocked", {}):
        item._smartup_blocked_by = plan["blocked"][item.nodeid]
        pytest.skip("BLOCKED: " + item._smartup_blocked_by)


def attach_attempt(request):
    plan = getattr(request.config, "_retry_plan", {})
    inline = getattr(request.node, "_order_inline_source", None)
    label = ("2 — shu testning darhol qayta urinishi" if inline else
             "2 — suite tugagach bir martalik retry" if plan else "1 — dastlabki urinish")
    allure.dynamic.parameter("Urinish", label, excluded=True)
    if inline:
        allure.attach("Faqat yiqilgan test boshidan bajariladi. Avvalgi identity va yozish jurnali "
                      "saqlanadi; tasdiqlanmagan to‘lov yoki yozish takrorlanmaydi.",
                      "Qayta urinish manbasi", allure.attachment_type.TEXT)
    if plan:
        allure.attach(
            "Manba run: " + plan["source_run"] + "\nOldingi PASS testlar qayta bajarilmadi. "
            "Yozuvlar serverdan tekshiriladi; noaniq amal takrorlanmaydi.",
            "Qayta urinish manbasi", allure.attachment_type.TEXT,
        )
