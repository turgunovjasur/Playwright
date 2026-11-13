"""Finished run evidence → explicitly supported group continuation.

Prior PASS is a prerequisite, never a new test result. Live validation is
owned by the group's fixture before the first resumed mutation.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re

import allure
import pytest

from tests.regression.helpers.runtime import ROOT, run_directory


@dataclass
class ResumePlan:
    source_run: str
    workflow: dict
    source_case: dict
    prior_passed: tuple
    selected: tuple
    evidence: dict
    preflight_done: bool = False

    def verify_baseline(self, baseline):
        source = self.source_case
        expected = {
            "code": source["baseline_code"], "url": source["server"],
            "company_code": source["company"], "filial_id": source["filial_id"],
            "room_id": source["fixtures"]["room"]["id"],
            "warehouse_id": source["fixtures"]["warehouse_id"],
        }
        if any(str(baseline.get(key)) != str(value) for key, value in expected.items()):
            raise AssertionError("Resume muhiti/API baseline oldingi run bilan mos emas; mutatsiya bajarilmaydi")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _passed(result):
    return result.get("status") == "passed" and all(
        result.get("phases", {}).get(phase, {}).get("outcome") == "passed"
        for phase in ("setup", "call", "teardown")
    )


def _resume_bonus_order(config, items, source):
    from tests.regression.helpers.retry.planning import build_plan, results
    order_id = os.environ.get("ORDER_RESUME_ORDER_ID", "")
    if not re.fullmatch(r"[1-9][0-9]*", order_id):
        raise pytest.UsageError("Bonus limitini davom ettirish uchun saqlangan order IDsi kerak")
    target = items[-1]
    plan = build_plan(source, saved_order_resume=True)
    prefix = [item.nodeid for item in items[:-1]]
    if (target.name != "test_09_second_client_reuses_limit" or plan["selected"] != [target.nodeid]
            or set(prefix) != set(plan["passed"]) or plan["blocked"].get(target.nodeid)):
        raise pytest.UsageError("OL-09 uchun oldingi PASS qadamlar va yagona saqlangan urinish kerak")
    old_manifest = _read(source / "retry-manifest.json")
    if any(list(item._order_required_steps) != row["requires"] or item.nodeid != row["nodeid"]
           for item, row in zip(items, old_manifest["cases"], strict=True)):
        raise pytest.UsageError("OL-09 bog‘liqliklari manba run bilan mos emas")
    prior = results(source)[target.nodeid][0].parent
    case = _read(prior / "case-data.json")
    ref = case["reference"]
    op = plan["journals"][target.nodeid]["operations"].get("entity:order:" + ref, {})
    if (case["order_ids"] != [order_id] or op.get("entity_id") != order_id
            or op.get("state") not in {"confirmed", "verified"}):
        raise pytest.UsageError("OL-09 order IDsi oldingi saqlangan order bilan mos emas")
    plan["saved_order"] = {"id": order_id, "reference": ref}
    config._retry_plan = plan  # Restore the original fixtures, journal and live prerequisites.
    config._order_passed.update(prefix)
    excluded = items[:-1]
    items[:] = [target]
    config.hook.pytest_deselected(items=excluded)
    directory = run_directory(config)
    evidence = dict(run_id=source.name, group="bonus_limit", first_test=target.nodeid, order_id=order_id)
    current = _read(directory / "run.json")
    current["resumed_from"] = evidence
    (directory / "run.json").write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    (directory / "resume.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def apply_resume(config, items):
    """Keep the runner's ordered suffix; import verified prefix prerequisites."""
    source_id = os.environ.get("ORDER_RESUME_RUN")
    group = os.environ.get("ORDER_RESUME_GROUP")
    if not source_id and not group:
        return
    if group not in {"product_limit", "bonus_limit"} or not source_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", source_id):
        raise pytest.UsageError("Davom ettirish uchun mos guruh va manba run IDsi kerak")
    if {item.get_closest_marker("order_group").args[0] for item in items} != {group}:
        raise pytest.UsageError("Resume bitta guruh runneridan davom etishi kerak")
    source = ROOT / "test-results/runs" / source_id
    if group == "bonus_limit":
        return _resume_bonus_order(config, items, source)
    try:
        run = _read(source / "run.json")
        if run.get("status") not in ("passed", "failed", "blocked", "interrupted") or not run.get("completed_at_utc"):
            raise ValueError("Manba run hali tugamagan")
        if run.get("resumed_from"):
            raise ValueError("Hozircha original to‘liq guruh qatnashgan runni tanlang")
        results = {}
        for path in source.glob("*/attempt-*/result.json"):
            result = _read(path)
            node = result.get("nodeid")
            if node not in {item.nodeid for item in items}:
                continue
            if node in results:
                raise ValueError("Manbada bir testcase uchun bir nechta attempt bor; noaniq resume taqiqlanadi")
            results[node] = (path, result)
        if set(results) != {item.nodeid for item in items}:
            raise ValueError("Manbada guruhning barcha bosqich natijalari bo‘lishi kerak")
        first = next((index for index, item in enumerate(items) if not _passed(results[item.nodeid][1])), len(items))
        if first == len(items):
            raise ValueError("Guruh allaqachon PASS; davom ettiriladigan test yo‘q")
        if items[first].name not in ("test_06_cancel_first_order", "test_07_reuse_released_limit"):
            raise ValueError("09 resume faqat ikkala order yaratilgandan keyingi bekor qilish yoki limitni qayta ishlatishdan boshlanadi")
        checkpoint_path = results[items[first - 1].nodeid][0].parent / "case-data.json"
        checkpoint = _read(checkpoint_path)
        if checkpoint.get("case") != items[first - 1].nodeid:
            raise ValueError("Checkpoint identity oldingi PASS testcase bilan mos emas")
        workflow = deepcopy(checkpoint["workflow"])
        if workflow.get("status") != "passed" or set(workflow.get("orders", {})) != {"first", "second"}:
            raise ValueError("Saqlangan workflow to‘liq emas")
        expected_stage = "verified" if items[first].name == "test_06_cancel_first_order" else "cancel_verified"
        if workflow["orders"]["first"].get("stage") != expected_stage or workflow["orders"]["second"].get("stage") != "verified":
            raise ValueError("Checkpoint bosqichi davom ettiriladigan testga mos emas")
        if any(_passed(results[item.nodeid][1]) for item in items[first:]):
            raise ValueError("Resume suffixida avval PASS bo‘lgan test bor; uni avtomatik qaytarmaymiz")
        prefix, suffix = tuple(item.nodeid for item in items[:first]), tuple(item.nodeid for item in items[first:])
        paths = [source / "run.json", checkpoint_path, *(path for path, _ in results.values())]
        evidence = {
            "source_run": source_id, "group": group,
            "reused_passed_prerequisites": prefix, "selected_tests": suffix,
            "source_files_sha256": {str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
            "note": "Oldingi PASS testlar qayta bajarilmadi; yangi natijalar faqat selected_tests uchun.",
        }
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise pytest.UsageError(f"Resume manbasi yaroqsiz: {error}") from error
    plan = ResumePlan(source_id, workflow, checkpoint, prefix, suffix, evidence)
    config._order_resume = plan
    config._order_passed.update(prefix)
    excluded = items[:first]
    items[:] = items[first:]
    config.hook.pytest_deselected(items=excluded)
    directory = run_directory(config)
    (directory / "resume.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    current = _read(directory / "run.json")
    current["resumed_from"] = {"run_id": source_id, "group": group, "first_test": suffix[0]}
    (directory / "run.json").write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def attach_resume(plan):
    allure.attach(json.dumps(plan.evidence, ensure_ascii=False, indent=2),
                  "Davom ettirish manbasi — oldingi PASS va yangi testlar", allure.attachment_type.JSON)
