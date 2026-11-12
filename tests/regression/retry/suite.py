"""Run exactly one retry round after the first pytest process has finished."""
import shutil
import sys

from tests.regression.runtime import new_run_id, prepare_run, finalize_run
from tests.regression.retry.planning import build_plan, attempt_results, final_result, passed
from tests.regression.retry.state import read, write


def retry_after_suite(directory, environment, run_pytest):
    plan = build_plan(directory)
    if plan["selected"]:
        from tests.regression.preparation.scan import scan_after_suite
        scan_after_suite(directory, environment)
        plan = build_plan(directory)
    plan_path = directory / "retry-plan.json"
    write(plan_path, plan)
    if not plan["selected"]:
        if plan.get("reason"):
            print("[RETRY] " + plan["reason"])
        return None
    print(f"[RETRY] Suite tugadi. {len(plan['selected'])} ta FAIL/bog‘liq SKIP uchun yagona qayta urinish.")
    child_env = {**environment, "REGRESSION_RUN_ID": new_run_id(), "ORDER_RETRY_PLAN": str(plan_path)}
    child = prepare_run(child_env["REGRESSION_RUN_ID"], environment=child_env)
    # Full group files are still collected and validated before internal selection.
    runners = list(dict.fromkeys(node.split("::", 1)[0] for node in plan["selected"]))
    command = [sys.executable, "-m", "pytest", *runners, f"--alluredir={child / 'allure-results'}"]
    result, stopped = 2, None
    write(directory / "retry-execution.json", {"retry_run": child.name, "status": "process"})
    try:
        result, stopped = run_pytest(command, child_env)
    except OSError as error:
        print(f"[RETRY] Pytest processini boshlash xatosi: {type(error).__name__}")
    finally:
        outcome = finalize_run(child, result, stop_signal=stopped)
        write(directory / "retry-execution.json", {"retry_run": child.name, "status": outcome["status"], "exit_code": result})
    return child


def combined_results(directory, retry_directory):
    """Copy, never rewrite either raw attempt. Allure uses stable historyId retries."""
    target = directory / "allure-combined-results"
    target.mkdir(exist_ok=False)
    for attempt, source in enumerate((directory, retry_directory), 1):
        if source is None:
            continue
        for path in (source / "allure-results").glob("*"):
            if not path.is_file():
                continue
            dest = target / path.name
            if dest.exists():
                if path.name in ("environment.properties", "executor.json", "categories.json"):
                    continue
                if dest.read_bytes() != path.read_bytes():
                    raise ValueError("Allure dalil nomlari to‘qnashdi; original dalil almashtirilmadi")
                continue
            shutil.copy2(path, dest)
            if path.name.endswith("-result.json"):
                value = read(dest)
                params = value.setdefault("parameters", [])
                recorded = next((p for p in params if p.get("name") == "Urinish"), None)
                # Inline attempts already carry their own number. A legacy child
                # process is round two even though its local case directory is 01.
                if attempt == 2 or recorded is None:
                    params[:] = [p for p in params if p.get("name") != "Urinish"]
                    params.append({"name": "Urinish", "value": f"{attempt} — " + ("dastlabki" if attempt == 1 else "qayta urinish"), "excluded": True})
                # Status, UUID, historyId, timings and original failure remain unchanged.
                write(dest, value)
    return target


def summarize(directory, retry_directory):
    first = attempt_results(directory)
    second = attempt_results(retry_directory) if retry_directory else {}
    original_run = read(directory / "run.json")
    retry_run = read(retry_directory / "run.json") if retry_directory else None
    cases, counts = [], {}
    for node, original_attempts in first.items():
        attempts = original_attempts + second.get(node, [])
        original = attempts[0][1]
        retried = attempts[-1][1] if len(attempts) > 1 else None
        _, final = final_result(attempts)
        state = final["status"]
        counts[state] = counts.get(state, 0) + 1
        cases.append({"nodeid": node, "initial": original["status"],
                      "retry": retried["status"] if retried else None, "final": state,
                      "recovered": not passed(original) and passed(final),
                      "attempts": [{"number": number, "status": value.get("status"),
                                    "result": str(path), "blocked_by": value.get("blocked_by", "")}
                                   for number, (path, value) in enumerate(attempts, 1)]})
    manifest_path = directory / "retry-manifest.json"
    manifest = read(manifest_path) if manifest_path.is_file() else {}
    expected = {row["nodeid"] for row in manifest.get("cases", [])}
    not_run = sorted(expected - first.keys())
    recovered_all = not not_run and bool(first) and all(row["final"] == "passed" for row in cases)
    infrastructure_exit = next((run.get("exit_code") for run in (original_run, retry_run)
                                if run and run.get("exit_code") not in (0, 1, None)), None)
    exit_code = infrastructure_exit if infrastructure_exit is not None else (0 if recovered_all else 1)
    write(directory / "suite-outcome.json", {
        "initial_run": directory.name, "retry_run": retry_directory.name if retry_directory else None,
        "retry_rounds": 1 if retry_directory or any(len(rows) > 1 for rows in first.values()) else 0,
        "retry_mode": "suite" if retry_directory else "immediate" if any(len(rows) > 1 for rows in first.values()) else "none",
        "final_counts": counts,
        "recovered_count": sum(row["recovered"] for row in cases),
        "exit_code": exit_code, "cases": cases, "not_run": not_run,
        "note": "Original run.json o‘zgarmaydi; Allure’da dastlabki xato va retry natijasi saqlanadi.",
    })
    print("[SUITE] " + ", ".join(f"{n} {key.upper()}" for key, n in counts.items()))
    return exit_code
