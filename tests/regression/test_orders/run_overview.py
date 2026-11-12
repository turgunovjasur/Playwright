"""Reconcile a presentation copy with final run ledgers, never raw test results."""
from collections import Counter
from datetime import datetime
from hashlib import md5
from pathlib import Path
import json
from uuid import NAMESPACE_URL, uuid5


def _read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fullname(nodeid):
    module, _, test = nodeid.partition("::")
    return module.removesuffix(".py").replace("/", ".") + "#" + test


def _milliseconds(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000) if value else 0


def reconcile_results(directory, run_directory):
    """Add final phase evidence and honest NOT_RUN/INTERRUPTED rows before enrichment."""
    from tests.regression.test_orders.reporting import (
        GROUP_FEATURES, SPECS, _identity, _attempt_number, order_report_title,
        order_report_section,
    )
    directory, run_directory = Path(directory), Path(run_directory)
    run = _read(run_directory / "run.json")
    if not run:
        return
    outcome = _read(run_directory / "suite-outcome.json")
    sources = {1: run_directory}
    retry_id = outcome.get("retry_run")
    if retry_id and Path(retry_id).name == retry_id:
        sources[2] = run_directory.parent / retry_id
    ledgers, nodes, latest, attempts_by_node = {}, {}, {}, {}
    from tests.regression.retry.planning import final_result
    for round_number, source in sources.items():
        for path in sorted(source.glob("*/attempt-*/result.json")):
            phase = _read(path)
            node = phase.get("nodeid")
            if not node:
                continue
            attempt = round_number if round_number == 2 else phase.get("attempt", 1)
            name = _fullname(node)
            ledgers[name, attempt] = (phase, path.parent)
            nodes[name] = node
            attempts_by_node.setdefault(node, []).append((attempt, path, phase))
    for node, attempts in attempts_by_node.items():
        attempts.sort(key=lambda entry: entry[0])
        latest[node] = final_result([(path, phase) for _, path, phase in attempts])[1].get("status", "unknown")
    manifest = _read(run_directory / "retry-manifest.json")
    for case in manifest.get("cases", []):
        nodes[_fullname(case["nodeid"])] = case["nodeid"]
        latest.setdefault(case["nodeid"], "not_run")
    existing = {}
    for path in directory.glob("*-result.json"):
        value = _read(path)
        name = value.get("fullName", "")
        existing.setdefault(name, []).append((path, value))
    finish = _read(sources[2] / "run.json") if 2 in sources else run
    finish = finish or run
    end = _milliseconds(finish.get("completed_at_utc") or finish.get("started_at_utc"))
    for name, records in existing.items():
        if name in nodes and latest.get(nodes[name]) == "not_run":
            latest[nodes[name]] = max(records, key=lambda record: _attempt_number(record[1]))[1].get("status", "unknown")
    for name, node in nodes.items():
        records = existing.setdefault(name, [])
        recorded_attempts = {_attempt_number(value) for _, value in records}
        ledger_attempts = {attempt for ledger_name, attempt in ledgers if ledger_name == name}
        missing_attempts = ledger_attempts - recorded_attempts
        if not records and not ledger_attempts:
            missing_attempts = {1}  # A manifest case with no evidence never started.
        template = min(records, key=lambda record: _attempt_number(record[1]))[1] if records else {}
        synthetic_ids = set()
        for attempt in sorted(missing_attempts):
            group, test = _identity(name)
            spec = SPECS.get((group, test))
            ledger = ledgers.get((name, attempt))
            state = ledger[0].get("status", "unknown") if ledger else "not_run"
            uid = str(uuid5(NAMESPACE_URL, f"{run['run_id']}:{node}:attempt-{attempt}"))
            value = {
                "uuid": uid, "historyId": template.get("historyId") or md5(name.encode()).hexdigest(),
                "fullName": name, "name": order_report_title(group, test) if spec else test,
                "status": state if state in {"passed", "failed", "skipped", "broken"} else "skipped",
                "statusDetails": {"message": "Allure ijro yozuvi mavjud emas; yakuniy ledger asosida ko‘rsatilgan."},
                "stage": "finished", "start": end, "stop": end,
                "parameters": [{"name": "Urinish", "value": f"{attempt} — " + ("dastlabki" if attempt == 1 else "qayta urinish"), "excluded": True}],
                "labels": [{"name": "epic", "value": "Order regression"},
                           {"name": "feature", "value": GROUP_FEATURES.get(group, "Order")},
                           {"name": "story", "value": order_report_section(group, test) if spec else "Test"}],
            }
            if template.get("testCaseId"):
                value["testCaseId"] = template["testCaseId"]
            records.append((directory / f"{uid}-result.json", value))
            synthetic_ids.add(uid)
        for path, value in records:
            synthetic = value["uuid"] in synthetic_ids
            attempt = _attempt_number(value)
            evidence = ledgers.get((name, attempt))
            if evidence is None and not synthetic:
                continue  # An existing execution record is never invented as NOT_RUN.
            phase, case_dir = evidence if evidence else ({"nodeid": node, "status": "not_run", "phases": {}}, None)
            state = phase.get("status")
            if synthetic and evidence:
                value["start"] = _milliseconds(phase.get("started_at_utc")) or end
                value["stop"] = _milliseconds(phase.get("updated_at_utc")) or end
            # Replace only our generated labels/parameters when rebuilding a copy.
            value["labels"] = [label for label in value.get("labels", [])
                               if not (label.get("name") == "tag" and label.get("value") in {"INTERRUPTED", "NOT_RUN"})]
            value["parameters"] = [parameter for parameter in value.get("parameters", [])
                                   if parameter.get("name") != "Ijro holati"]
            # A final ledger wins over a call-only PASS when teardown was interrupted.
            if state in {"process", "interrupted", "not_run"}:
                state = "interrupted" if state == "process" else state
                phase = {**phase, "status": state}
                value["status"] = "skipped"
                message = ("INTERRUPTED — test yakunlanmadi; PASS tasdiqlanmagan." if state == "interrupted"
                           else "NOT_RUN — ushbu test boshlanmagan.")
                value.setdefault("statusDetails", {})["message"] = message
                value.setdefault("labels", []).append({"name": "tag", "value": state.upper()})
                value.setdefault("parameters", []).append({"name": "Ijro holati", "value": state.upper(), "excluded": True})
            elif state == "failed" and value.get("status") not in {"failed", "broken"}:
                value["status"] = "broken"
                value.setdefault("statusDetails", {})["message"] = "Yakuniy faza natijasida xato qayd etilgan."
            elif state == "skipped" and value.get("status") == "passed":
                value["status"] = "skipped"
                value.setdefault("statusDetails", {})["message"] = "Yakuniy faza natijasi SKIPPED; to‘liq PASS tasdiqlanmagan."
            if state == "skipped" and attempt > 1 and latest.get(node) == "failed":
                # Allure chooses the latest retry as the headline. Preserve the
                # failed testcase headline when retry never executed its body.
                value["status"] = "broken"
                value.setdefault("statusDetails", {})["message"] = (
                    "Retry bajarilmadi; dastlabki FAIL saqlanadi. "
                    + str(phase.get("blocked_by") or "Retry SKIPPED bilan tugadi.")
                )
                value.setdefault("parameters", []).append({
                    "name": "Ijro holati", "value": "RETRY SKIPPED — FINAL FAILED", "excluded": True,
                })
            attachments = value.setdefault("attachments", [])
            attachments[:] = [a for a in attachments if a.get("name") != "Order fazalari natijasi"]
            filename = f"{value['uuid']}-final-phases.json"
            _write(directory / filename, phase)
            attachments.append({"name": "Order fazalari natijasi", "source": filename, "type": "application/json"})
            if state in {"failed", "interrupted"} and case_dir and (case_dir / "trace.zip").is_file():
                # Reference is resolved and copied by the existing presentation builder.
                reference = f"{value['uuid']}-final-trace-reference.json"
                _write(directory / reference, {"path": str(case_dir / "trace.zip"), "scope": "test"})
                attachments[:] = [a for a in attachments if a.get("name") != "trace-reference"]
                attachments.append({"name": "trace-reference", "source": reference, "type": "application/json"})
            _write(path, value)
    counts = Counter(latest.values())
    kinds = Counter(SPECS.get(_identity(_fullname(node)), (None, "Test"))[1] for node in latest)
    start = _milliseconds(run.get("started_at_utc"))
    duration = max(0, end - start) / 1000
    stop = finish.get("stop_signal") or ("Normal yakun" if finish.get("exit_code") == 0 else f"Exit code: {finish.get('exit_code', 'noma’lum')}")
    final_exit = outcome.get("exit_code", finish.get("exit_code"))
    if counts["interrupted"] or finish.get("status") == "interrupted":
        final_status = "interrupted"
    elif counts["failed"] or counts["broken"] or final_exit not in (0, None):
        final_status = "failed"
    elif latest and counts["passed"] == len(latest) and final_exit == 0:
        final_status = "passed"
    else:
        final_status = "incomplete"
    summary = {"run_id": run["run_id"], "status": final_status, "total": len(latest),
               "counts": dict(counts), "types": dict(kinds), "started_at_utc": run.get("started_at_utc"),
               "duration_seconds": duration, "stop_reason": stop}
    _write(directory / "run-overview.json", summary)
    properties = directory / "environment.properties"
    lines = properties.read_text(encoding="utf-8").splitlines() if properties.exists() else []
    lines = [line for line in lines if not line.startswith("Order.")]
    entries = {"Run": run["run_id"], "Status": final_status, "Total": len(latest),
               **{state.upper(): counts[state] for state in ("passed", "failed", "broken", "interrupted", "not_run", "skipped")},
               "Setup": kinds["Tayyorlov"], "Business": kinds["Biznes testi"],
               "Started.UTC": run.get("started_at_utc", ""), "Duration.seconds": duration, "Stop": stop,
               "Status.note": "INTERRUPTED va NOT_RUN Allure’da skipped; Ijro holati orqali ajratiladi"}
    properties.write_text("\n".join(lines + [f"Order.{key}={value}" for key, value in entries.items()]) + "\n", encoding="utf-8")
