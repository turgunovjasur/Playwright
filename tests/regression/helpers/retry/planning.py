"""Immutable first attempt → dependency-aware, single retry execution plan."""
from copy import deepcopy
from pathlib import Path
import hashlib
import os

import pytest

from tests.regression.helpers.runtime import ROOT, run_directory
from tests.regression.helpers.retry.state import day, read, write


def source_hash():
    files = sorted((ROOT / "tests/regression").rglob("*.py"))
    return hashlib.sha256(b"".join(str(p.relative_to(ROOT)).encode() + p.read_bytes() for p in files)).hexdigest()


def record_collection(config, items):
    if config.option.collectonly:
        return
    write(run_directory(config) / "retry-manifest.json", {
        "version": 1, "day": day(), "source_hash": source_hash(),
        "cases": [{"nodeid": item.nodeid, "group": item.get_closest_marker("order_group").args[0],
                   "requires": list(item._order_required_steps)} for item in items],
    })


def attempt_results(directory):
    """Return every immutable attempt, ordered within each testcase."""
    found = {}
    for path in sorted(Path(directory).glob("*/attempt-*/result.json")):
        value = read(path)
        number = value.get("attempt", 1)
        if type(number) is not int or number < 1 or path.parent.name != f"attempt-{number:02d}":
            raise ValueError("Test urinish raqami dalil papkasiga mos emas")
        attempts = found.setdefault(value["nodeid"], [])
        if any(previous[1].get("attempt", 1) == number for previous in attempts):
            raise ValueError("Bitta testcase urinishining takroriy result fayli bor")
        attempts.append((path, value))
    for attempts in found.values():
        attempts.sort(key=lambda entry: entry[1].get("attempt", 1))
    return found


def final_result(attempts):
    """A completed retry can recover a failure; an unexecuted retry cannot."""
    path, latest = attempts[-1]
    if latest.get("status") == "process":
        return path, {**latest, "status": "interrupted"}
    if latest.get("status") == "skipped":
        failed = next((entry for entry in reversed(attempts[:-1])
                       if entry[1].get("status") == "failed"), None)
        if failed:
            return failed[0], {**failed[1], "retry_status": "skipped",
                               "retry_blocked_by": latest.get("blocked_by", "")}
    return path, latest


def results(directory):
    """One authoritative outcome per test, while raw attempts remain intact."""
    return {node: final_result(attempts) for node, attempts in attempt_results(directory).items()}


def passed(result):
    return result.get("status") == "passed" and all(
        result.get("phases", {}).get(p, {}).get("outcome") == "passed"
        for p in ("setup", "call", "teardown"))


def apply_delta(target, before, after):
    """Apply PASS fixture deltas. Retained IDs alone are never proof of a PASS."""
    for key in before.keys() - after.keys():
        target.pop(key, None)
    for key, value in after.items():
        if key not in before:
            target[key] = deepcopy(value)
        elif isinstance(value, dict) and isinstance(before[key], dict):
            apply_delta(target.setdefault(key, {}), before[key], value)
        elif before[key] != value:
            target[key] = deepcopy(value)


def dependency_closure(cases, node):
    by_node = {row["nodeid"]: row for row in cases}
    found, pending = set(), list(by_node[node]["requires"])
    while pending:
        current = pending.pop()
        if current not in found:
            found.add(current)
            pending.extend(by_node[current]["requires"])
    return found


def build_plan(directory, *, saved_order_resume=False):
    run = read(directory / "run.json")
    plan = {"version": 1, "source_run": directory.name, "round": 1, "selected": [],
            "passed": [], "states": {}, "journals": {}, "blocked": {}, "evidence": {}}
    if run.get("retry_of") or run.get("resumed_from") or run.get("status") == "interrupted":
        plan["reason"] = "To‘xtatilgan run yoki qayta urinishdan yana retry boshlanmaydi"
        return plan
    manifest = read(directory / "retry-manifest.json")
    if not saved_order_resume and (run.get("immediate_retry") or manifest.get("retry_policy") == "immediate"
            or any(len(attempts) > 1 for attempts in attempt_results(directory).values())):
        plan["reason"] = "Test ichidagi retry siyosatidan keyin suite retry qayta boshlanmaydi"
        return plan
    plan["source_hash"] = manifest["source_hash"]
    plan["day"] = manifest["day"]
    plan["baseline_signature"] = manifest.get("baseline_signature")
    if manifest["day"] != day() or (not saved_order_resume and manifest["source_hash"] != source_hash()):
        plan["reason"] = "Sana yoki regression kodi o‘zgargan; eski muhit avtomatik davom ettirilmaydi"
        return plan
    if not plan["baseline_signature"]:
        plan["reason"] = "API baseline tasdiqlanmagan"
        return plan
    found = results(directory)
    registry = directory / "preparations.json"
    if registry.is_file():
        plan["preparations"] = read(registry)
        plan["evidence"][registry.name] = hashlib.sha256(registry.read_bytes()).hexdigest()
    for evidence in [directory / "retry-manifest.json", directory / "run.json", *directory.glob("*/attempt-*/result.json"), *directory.glob("*/attempt-*/retry-state.json"), *directory.glob("*/attempt-*/retry-journal.json")]:
        plan["evidence"][str(evidence.relative_to(directory))] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    if set(found) != {row["nodeid"] for row in manifest["cases"]}:
        plan["reason"] = "Barcha testcase natijalari saqlanmagan"
        return plan
    if any(result.get("environment_failure") for _, result in found.values()):
        plan["reason"] = "Umumiy muhit/login/API setup xatosi; biznes retry boshlanmaydi"
        return plan
    selected = set()
    for spec in manifest["cases"]:
        node = spec["nodeid"]
        path, result = found[node]
        if passed(result):
            plan["passed"].append(node)
            snapshot_path = path.parent / "retry-state.json"
            if snapshot_path.is_file():
                state = read(snapshot_path)
                apply_delta(plan["states"].setdefault(spec["group"], {}), state["before"], state["after"])
            journal_path = path.parent / "retry-journal.json"
            if journal_path.is_file():
                evidence = read(journal_path)
                for key, contract in evidence.get("contracts", {}).items():
                    operation = evidence.get("operations", {}).get(key, {})
                    plan.setdefault("preparation_contracts", {}).setdefault(node, {})[key] = {
                        **contract, "entity_id": operation.get("entity_id")}
            continue
        eligible = result.get("status") == "failed" or (
            result.get("status") == "skipped" and result.get("blocked_by")
            and any(dep in selected for dep in spec["requires"]))
        if not eligible:
            continue
        selected.add(node)
        plan["selected"].append(node)
        journal = path.parent / "retry-journal.json"
        if result.get("status") == "failed":
            if not journal.is_file():
                plan["blocked"][node] = "Oldingi yozish amallari jurnali yo‘q; dublikat xavfini tekshirib bo‘lmaydi"
            else:
                plan["journals"][node] = read(journal)
        for evidence in (path, journal, path.parent / "retry-state.json"):
            if evidence.is_file():
                plan["evidence"][str(evidence.relative_to(directory))] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    # Only actual prerequisites can block a selected business case, never an unrelated sibling.
    contracts = plan.get("preparation_contracts", {})
    plan["readiness"] = {}
    plan["preparation_consumers"] = {}
    for node in plan["selected"]:
        for prerequisite in dependency_closure(manifest["cases"], node):
            if prerequisite in contracts:
                plan["readiness"].setdefault(node, {}).update(contracts[prerequisite])
                plan["preparation_consumers"].setdefault(prerequisite, []).append(node)
    scan_path = directory / "retry-readiness.json"
    if not saved_order_resume and scan_path.is_file():
        scan = read(scan_path)
        plan["evidence"][scan_path.name] = hashlib.sha256(scan_path.read_bytes()).hexdigest()
        plan["blocked"].update(scan.get("blocked", {}))
        repairs = set(scan.get("repair_nodes", []))
        if not repairs.issubset(plan["preparation_consumers"]):
            raise ValueError("Repair faqat selected testcase prerequisite bo‘lishi mumkin")
        plan["repairs"] = sorted(repairs)
        invalid_owners = {row["preparation"] for row in scan.get("checks", [])
                          if row.get("status") == "blocked" and row.get("preparation")}
        for node in repairs:
            prerequisites = dependency_closure(manifest["cases"], node)
            invalid = prerequisites & invalid_owners
            if invalid:
                plan["blocked"][node] = "Tayyorlovni tiklash bloklandi: uning zarur ma’lumoti yaroqsiz — " + ", ".join(sorted(invalid))
            for prerequisite in prerequisites:
                plan["readiness"].setdefault(node, {}).update(contracts.get(prerequisite, {}))
            plan["passed"].remove(node)
            journal = found[node][0].parent / "retry-journal.json"
            plan["journals"][node] = read(journal)
        plan["selected"] = [row["nodeid"] for row in manifest["cases"] if row["nodeid"] in selected | repairs]
    # Saved prerequisites must have durable fixture evidence, including API preparations.
    for node in plan["passed"]:
        path = found[node][0].parent / "retry-state.json"
        if not path.is_file():
            plan["reason"] = "PASS tayyorlovning fixture nusxasi yetishmaydi"
            plan["selected"] = []
            break
    return plan


def apply_retry(config, items):
    plan_path = os.environ.get("ORDER_RETRY_PLAN")
    if not plan_path:
        return
    path = Path(plan_path).resolve()
    if not path.is_relative_to(ROOT / "test-results/runs"):
        raise pytest.UsageError("Retry reja faqat regression run papkasidan olinadi")
    plan = read(path)
    if plan.get("round") != 1 or plan["day"] != day() or plan["source_hash"] != source_hash():
        raise pytest.UsageError("Retry reja sanasi, kodi yoki urinish raqami yaroqsiz")
    source = ROOT / "test-results/runs" / plan["source_run"]
    if source.resolve() != path.parent:
        raise pytest.UsageError("Retry manbasi reja papkasiga mos emas")
    for relative, expected in plan["evidence"].items():
        evidence = (source / relative).resolve()
        if not evidence.is_relative_to(source) or hashlib.sha256(evidence.read_bytes()).hexdigest() != expected:
            raise pytest.UsageError("Retry manbasi o‘zgargan")
    if build_plan(source) != plan:
        raise pytest.UsageError("Retry reja asl natijalar va bog‘liqliklarga mos emas")
    selected = set(plan["selected"])
    if not selected or not selected.issubset({item.nodeid for item in items}):
        raise pytest.UsageError("Retry testcase ro‘yxati runnerlarga mos emas")
    config._retry_plan = plan
    config._order_passed.update(plan["passed"])
    excluded = [item for item in items if item.nodeid not in selected]
    items[:] = [item for item in items if item.nodeid in selected]
    config.hook.pytest_deselected(items=excluded)
    directory = run_directory(config)
    if plan.get("preparations"):
        write(directory / "preparations.json", deepcopy(plan["preparations"]))
    run = read(directory / "run.json")
    run["retry_of"] = {"run_id": plan["source_run"], "round": 1}
    write(directory / "run.json", run)
