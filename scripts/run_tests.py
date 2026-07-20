from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "test-results" / "allure-results"
REPORT_DIR = ROOT / "test-results" / "allure-report"
TRACE_DIR = ROOT / "test-results" / "traces"
SUMMARY_FILES = (
    ROOT / "test-results" / "system-summary.md",
    ROOT / "test-results" / "system-summary.json",
    ROOT / "test-results" / "ai-summary.md",
    ROOT / "test-results" / "ai-summary.json",
)
CREATED_COMPANY_PASSWORD = "greenwhite"

TARGETS = {
    "all": (
        (
            "tests/smoke/test_setup/test_setup_runner.py",
            "tests/smoke/test_all_runner.py",
        ),
        "--new-code",
    ),
    "setup": ("tests/smoke/test_setup/test_setup_runner.py", "--new-code"),
    "company": ("tests/smoke/test_setup/test_setup_runner.py::test_00_company", "--new-code"),
    "group-a": ("tests/smoke/test_groups/test_A_grup/test_a_group_runner.py", ""),
    "group-b": ("tests/smoke/test_groups/test_B_grup/test_b_group_runner.py", ""),
    "group-c": ("tests/smoke/test_groups/test_C_grup/test_c_group_runner.py", ""),
    "group-report": ("tests/smoke/test_groups/test_report_grup/test_report_group_runner.py", ""),
}


def normalized_url(value):
    return (value or "").strip().rstrip("/")


def env_flag(env, name):
    return str(env.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def load_local_dotenv(env):
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in env:
                env[key] = value


def clean_allure_results():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for item in RESULTS_DIR.iterdir():
        if item.name == "history":
            continue
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)
    for item in SUMMARY_FILES:
        item.unlink(missing_ok=True)


def command_text(command):
    masked = []
    hide_next = False
    for item in command:
        if hide_next:
            masked.append("***")
            hide_next = False
            continue
        masked.append(item)
        if item in {"--company-password", "--head-password"}:
            hide_next = True
    return " ".join(masked)


def run(command, env, dry_run=False):
    print(command_text(command))
    if dry_run:
        return 0
    return subprocess.call(command, cwd=ROOT, env=env)


def generate_report(env, open_report, dry_run):
    allure = shutil.which("allure")
    if not allure:
        return

    generate_command = [allure, "generate", str(RESULTS_DIR), "-o", str(REPORT_DIR), "--clean"]
    run(generate_command, env, dry_run=dry_run)

    if open_report:
        run([sys.executable, str(ROOT / "scripts" / "open_allure_report.py"), str(REPORT_DIR)], env, dry_run=dry_run)


def show_trace(env, dry_run):
    playwright = shutil.which("playwright")
    if not playwright or not TRACE_DIR.exists():
        return

    traces = sorted(TRACE_DIR.glob("*.zip"), key=lambda item: item.stat().st_mtime, reverse=True)
    if traces:
        run([playwright, "show-trace", str(traces[0])], env, dry_run=dry_run)


def generate_test_summary(
    env,
    test_exit,
    pytest_command,
    started_at,
    ai_summary,
    dry_run,
):
    command = [
        sys.executable,
        str(ROOT / "scripts" / "analyze_test_result.py"),
        "--exit-code",
        str(test_exit),
        "--command",
        command_text(pytest_command),
        "--started-at",
        str(started_at),
    ]
    if ai_summary:
        command.append("--ai-summary")
    run(command, env, dry_run=dry_run)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smartup smoke testlarini Mac, Linux va Windows terminalida ishga tushiradi."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        help="Default: all. Debug uchun: setup, company, group-a, group-b, group-c, group-report yoki pytest target path.",
    )
    parser.add_argument("--url", required=True, help="Majburiy server URL. Masalan: https://app3.greenwhite.uz/xtrade")
    parser.add_argument("--company-code", help="Mavjud company code. --create-company bo'lmasa majburiy.")
    parser.add_argument("--company-password", help="Mavjud company admin paroli. --create-company bo'lmasa majburiy.")
    parser.add_argument("--head-email", help="--create-company bilan head profil emaili.")
    parser.add_argument("--head-password", help="--create-company bilan head profil paroli.")
    parser.add_argument(
        "--create-company",
        action="store_true",
        help="Suite boshida yangi company yaratadi va keyingi testlarda shu company_code ishlatiladi.",
    )
    parser.add_argument("--headless", action="store_true", help="Chromium headless rejimda ishlaydi.")
    parser.add_argument(
        "--disable-license-policy",
        action="store_true",
        help="--create-company bilan company Security tabidagi 'Политика лицензирования'ni o'chiradi.",
    )
    parser.add_argument("--open-report", action="store_true", help="Allure reportni generate qilib ochadi.")
    parser.add_argument("--show-trace", action="store_true", help="Oxirgi Playwright trace viewerini ochadi.")
    parser.add_argument(
        "--ai-summary",
        action="store_true",
        help="Test tugagach Gemini orqali faqat qo'shimcha AI xulosa yozadi. Default: off.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Commandni ko'rsatadi, lekin ishga tushirmaydi.")
    return parser.parse_known_args()


def main():
    args, pytest_extra = parse_args()
    env = os.environ.copy()
    load_local_dotenv(env)

    unsupported_ai_flags = [item for item in pytest_extra if item == "--no-ai-summary" or item.startswith("--ai-model")]
    if unsupported_ai_flags:
        print("--no-ai-summary va --ai-model kerak emas; AI default off, kerak bo'lsa faqat --ai-summary ishlating", file=sys.stderr)
        return 2

    company_url_arg = normalized_url(args.url)
    if not company_url_arg:
        print("--url bo'sh bo'lishi mumkin emas", file=sys.stderr)
        return 2
    env["SMARTUP_RUNNER"] = "1"
    env["COMPANY_URL"] = company_url_arg

    if args.disable_license_policy and not args.create_company:
        print("--disable-license-policy faqat --create-company bilan ishlaydi", file=sys.stderr)
        return 2
    if args.create_company and args.target in {"group-a", "group-b", "group-c", "group-report"}:
        print("--create-company group-a/group-b targetlari bilan ishlamaydi; all, setup yoki company ishlating", file=sys.stderr)
        return 2
    if args.target == "company" and not args.create_company:
        print("company target faqat --create-company bilan ishlaydi", file=sys.stderr)
        return 2

    company_password = (args.company_password or "").strip()
    head_email = (args.head_email or "").strip()
    head_password = (args.head_password or "").strip()

    if args.create_company:
        if args.company_code:
            print("--create-company bilan --company-code berilmaydi", file=sys.stderr)
            return 2
        if company_password:
            print("--company-password --create-company bilan berilmaydi; yangi company admin paroli test ichidagi default qiymat", file=sys.stderr)
            return 2
        if not head_email:
            print("--head-email majburiy: --create-company uchun head profil emailini bering", file=sys.stderr)
            return 2
        if not head_password:
            print("--head-password majburiy: --create-company uchun head profil parolini bering", file=sys.stderr)
            return 2
        env["CREATE_COMPANY"] = "1"
        env["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD
        env["HEAD_ADMIN_EMAIL"] = head_email
        env["HEAD_ADMIN_PASSWORD"] = head_password
        env.pop("COMPANY_CODE", None)
    else:
        company_code = (args.company_code or "").strip().lstrip("@")
        if head_email or head_password:
            print("--head-email/--head-password faqat --create-company bilan ishlaydi", file=sys.stderr)
            return 2
        if not company_code:
            print("--company-code majburiy yoki --create-company flagini bering", file=sys.stderr)
            return 2
        if not company_password:
            print("--company-password majburiy yoki --create-company flagini bering", file=sys.stderr)
            return 2
        env["COMPANY_CODE"] = company_code
        env["COMPANY_PASSWORD"] = company_password
        env.pop("HEAD_ADMIN_EMAIL", None)
        env.pop("HEAD_ADMIN_PASSWORD", None)
        env.pop("CREATE_COMPANY", None)

    if args.disable_license_policy:
        env["DISABLE_LICENSE_POLICY"] = "1"
    else:
        env.pop("DISABLE_LICENSE_POLICY", None)

    targets, code_mode = TARGETS.get(args.target, (args.target, ""))
    if isinstance(targets, str):
        targets = (targets,)
    pytest_command = [sys.executable, "-m", "pytest", *targets]

    if code_mode:
        pytest_command.append(code_mode)
    if args.headless or env.get("HEADLESS", "").lower() in {"1", "true", "yes", "on"}:
        pytest_command.append("--headless")
    pytest_command.extend(["--url", company_url_arg])
    if args.create_company:
        pytest_command.append("--create-company")
        pytest_command.extend(["--head-email", env["HEAD_ADMIN_EMAIL"]])
        pytest_command.extend(["--head-password", env["HEAD_ADMIN_PASSWORD"]])
    else:
        pytest_command.extend(["--company-code", env["COMPANY_CODE"]])
        pytest_command.extend(["--company-password", env["COMPANY_PASSWORD"]])
    if args.disable_license_policy:
        pytest_command.append("--disable-license-policy")
    pytest_command.extend(pytest_extra)

    if args.create_company:
        print(f"Company setup: enabled by --create-company ({company_url_arg})")
        if args.disable_license_policy:
            print("Company license policy: will be disabled")
    else:
        print(f"Company setup: skipped; using company_code={env['COMPANY_CODE']}")

    if not args.dry_run:
        clean_allure_results()
    run_started_at = time.time()
    test_exit = run(pytest_command, env, dry_run=args.dry_run)

    generate_test_summary(
        env,
        test_exit=test_exit,
        pytest_command=pytest_command,
        started_at=run_started_at,
        ai_summary=args.ai_summary,
        dry_run=args.dry_run,
    )

    generate_report(env, open_report=args.open_report or env_flag(env, "OPEN_REPORT"), dry_run=args.dry_run)
    if args.show_trace:
        show_trace(env, dry_run=args.dry_run)

    return test_exit


if __name__ == "__main__":
    raise SystemExit(main())
