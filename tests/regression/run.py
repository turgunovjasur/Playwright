"""Barcha yangi Order guruhlarini qat'iy tartibda ishga tushirish.

python tests/regression/run.py
Bitta guruh uchun uning runners/test_*_runner.py faylini pytest bilan Run qiling.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
from scripts.report_lifecycle import generate_test_summary, _open_report
from scripts.allure_report_cli import AllureCliNotInstalled, generate_report as generate_allure_report
from tests.regression.runtime import finalize_run, new_run_id, prepare_run

from tests.regression.test_orders.ordering import GROUP_RUNNERS, GROUP_NAMES
from tests.regression.test_orders.reporting import prepare_presentation

def run_pytest(command, environment):
    """SIGINT/SIGTERMni childga uzatib, yakuniy natijani yozish uchun kutish."""
    process = subprocess.Popen(command, cwd=ROOT, env=environment)
    stopped = None
    deadline = None

    def stop(signum, _frame):
        nonlocal stopped, deadline
        if process.poll() is not None:
            return
        if stopped is None:
            stopped = signal.Signals(signum).name
            deadline = time.monotonic() + 10
            process.send_signal(signum)
        else:
            process.kill()

    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        while True:
            try:
                return process.wait(timeout=0.5), stopped
            except subprocess.TimeoutExpired:
                if deadline is not None and time.monotonic() >= deadline:
                    process.kill()
                    return process.wait(), stopped
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def prepare_run_report(directory):
    """Joriy run katalogini tayyorlaydi; global natijalar nusxalanmaydi."""
    results = directory / "allure-results"
    results.mkdir(exist_ok=True)
    return results


def generate_run_report(directory, results, environment):
    """Faqat shu run natijalaridan HTML; oldingi report o'zgarmaydi."""
    report = directory / "allure-report"
    report_environment = {**environment, "ALLURE_HISTORY_PATH": str(directory / "allure-history.jsonl")}
    try:
        generated = generate_allure_report(
            results, report, ROOT / "allurerc.mjs", project_root=ROOT,
            env=report_environment, clean_output=False,
        )
    except (AllureCliNotInstalled, OSError, ValueError) as error:
        print(f"[ALLURE] Joriy run reporti yaratilmadi: {error}")
        return
    if generated.returncode != 0:
        print(f"[ALLURE] Joriy run reporti yaratilmadi: exit_code={generated.returncode}")
    elif environment.get("OPEN_REPORT") == "1":
        _open_report(ROOT, report, environment, dry_run=False, background=True)


def main():
    parser = argparse.ArgumentParser(description="Order guruhlari: statuslar → aksiya → to‘lov → majburiy shartlar → ombor → bonus limiti → qaytarish → ko‘p order to‘lovi → qo‘lda skidka → TMZ limiti → ikki ombor → majburiy+ixtiyoriy aksiya → avtomatik hisob-kitob → orderdan oldingi avans; parametr talab qilinmaydi")
    parser.add_argument("--resume-run", help="Tugagan original run ID: oldingi PASS tayyorlovlardan davom etish")
    parser.add_argument("--group", choices=["product_limit", "bonus_limit"], help="Davom ettiriladigan guruh")
    parser.add_argument("--order-id", help="OL-09 davom ettiradigan saqlangan order IDsi")
    args = parser.parse_args()
    if bool(args.order_id) != (args.group == "bonus_limit"):
        parser.error("bonus_limit resume uchun --order-id kerak")
    if bool(args.resume_run) != bool(args.group):
        parser.error("--resume-run va --group birga beriladi")
    load_dotenv(ROOT / ".env", override=True)
    runners = (GROUP_RUNNERS[GROUP_NAMES.index(args.group)],) if args.resume_run else GROUP_RUNNERS
    command = [sys.executable, "-m", "pytest", *runners]
    if not args.resume_run:
        command.append("--maxfail=1")
    started=time.time()
    environment=os.environ.copy()
    for key in ("ORDER_RESUME_RUN", "ORDER_RESUME_GROUP", "ORDER_RESUME_ORDER_ID", "ORDER_RETRY_PLAN"):
        environment.pop(key, None)
    if args.resume_run:
        environment.update(ORDER_RESUME_RUN=args.resume_run, ORDER_RESUME_GROUP=args.group)
    if args.order_id:
        environment["ORDER_RESUME_ORDER_ID"] = args.order_id
    environment["SMARTUP_RUNNER"]="1"
    environment["REGRESSION_RUN_ID"]=new_run_id()
    directory=prepare_run(environment["REGRESSION_RUN_ID"],environment=environment)
    command.append(f"--alluredir={directory / 'allure-results'}")
    result=2
    stopped=None
    try:
        result,stopped=run_pytest(command,environment)
    finally:
        run = finalize_run(directory, result, stop_signal=stopped)
    if run["status"] == "blocked" and result == 0:
        result = 2
        run["runner_exit_code"] = result
        (directory / "run.json").write_text(
            json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    from tests.regression.retry.suite import combined_results, summarize
    prepare_run_report(directory)
    results = directory / "allure-results" if args.order_id else combined_results(directory, None)
    if not args.resume_run:
        result = summarize(directory, None)
    try:
        results = prepare_presentation(results, directory / "allure-presentation-results")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"[ALLURE] Order taqdimoti tayyorlanmadi: {type(error).__name__}; asl natijalar ishlatiladi")
    description = f"Order regression resume: {args.group}; manba {args.resume_run}" if args.resume_run else "Order regression: statuslar → aksiya → to‘lov → majburiy shartlar → ombor → bonus limiti → qaytarish → ko‘p order to‘lovi → qo‘lda skidka → TMZ limiti → ikki ombor → majburiy+ixtiyoriy aksiya → avtomatik hisob-kitob → orderdan oldingi avans"
    generate_test_summary(ROOT, environment, test_exit=result, command_text=description,
                          started_at=started, results_dir=results, output_dir=directory)
    generate_run_report(directory,results,environment)
    return result

if __name__=="__main__":
    raise SystemExit(main())
