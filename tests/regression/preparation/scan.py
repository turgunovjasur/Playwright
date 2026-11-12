"""Freeze a read-only readiness decision before building the final retry plan."""
import os
from pathlib import Path
import subprocess
import sys
import traceback
from scripts.api_setup_bridge import validate_api_baseline
from tests.regression.runtime import ROOT
from tests.regression.retry.state import digest, write
from tests.regression.preparation.readiness import verify_contract, PreparationRepairRequired
from tests.regression.test_orders.auth_recovery import RegressionSetupState


def scan_after_suite(directory, environment):
    """Read current prerequisites outside pytest's closed Allure test lifecycle.

    SmartupAPI attaches diagnostics on every response. After pytest finishes,
    its Allure listener still exists but no test can own those attachments.
    A plain Python child has no pytest listener; it writes the readiness JSON
    instead. This starts neither a test nor a setup mutation.
    """
    directory = Path(directory)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "tests.regression.preparation.scan", str(directory)],
            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=180,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        write(directory / "retry-readiness-error.json", {"error_type": type(error).__name__,
                                                       "phase": "readiness_process"})
        raise ValueError("Retry oldidan o‘qish jarayoni yakunlanmadi; qayta yozish boshlanmadi") from error
    if result.returncode != 0:
        if not (directory / "retry-readiness-error.json").exists():
            write(directory / "retry-readiness-error.json", {"phase": "readiness_process",
                                                           "exit_code": result.returncode})
        raise ValueError("Retry oldidan tayyorlov tekshiruvi yakunlanmadi; retry-readiness-error.json dalilini ko‘ring")


def scan_preparations(plan, directory):
    result = {"version": 1, "repair_nodes": [], "blocked": {}, "checks": []}
    if not plan.get("preparation_consumers"):
        write(directory / "retry-readiness.json", result)
        return
    baseline = validate_api_baseline(ROOT, os.environ)
    if digest(baseline) != plan["baseline_signature"]:
        raise ValueError("Retry readiness baseline o‘zgargan")
    state = RegressionSetupState(directory / "readiness-scan-state.json", dict(baseline))
    try:
        try:
            api = state.user()
        except Exception as error:
            result["checks"].append({"status": "blocked", "phase": "login", "error_type": type(error).__name__})
            result["blocked"] = {node: "Retry oldidan API sessiyasi tasdiqlanmadi; yozish bajarilmadi (" + type(error).__name__ + ")" for node in plan["selected"]}
            write(directory / "retry-readiness.json", result)
            return
        for owner, consumers in plan["preparation_consumers"].items():
            repair = False
            try:
                for contract in plan["preparation_contracts"][owner].values():
                    try:
                        verify_contract(api, baseline, contract)
                    except PreparationRepairRequired:
                        repair = True
                result["checks"].append({"preparation": owner, "status": "repair_required" if repair else "ready"})
                if repair:
                    result["repair_nodes"].append(owner)
            except Exception as error:
                # Unknown response or altered entity must never trigger automatic creation.
                result["checks"].append({"preparation": owner, "status": "blocked", "error_type": type(error).__name__})
                for node in consumers:
                    result["blocked"][node] = "Zarur tayyorlovning joriy holati tasdiqlanmadi: " + owner.rsplit("::", 1)[-1] + " (" + type(error).__name__ + ")"
    finally:
        state.close()
    write(directory / "retry-readiness.json", result)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Completed regression run directory is required")
    directory = Path(sys.argv[1]).resolve()
    if not directory.is_relative_to(ROOT / "test-results/runs") or not (directory / "run.json").is_file():
        raise SystemExit("Only an existing regression run directory is allowed")
    try:
        from tests.regression.retry.planning import build_plan
        scan_preparations(build_plan(directory), directory)
    except Exception as error:
        from utils.report_safety import safe_text
        write(directory / "retry-readiness-error.json", {
            "error_type": type(error).__name__, "detail": safe_text(traceback.format_exc()),
        })
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
