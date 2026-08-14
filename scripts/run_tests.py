from __future__ import annotations

import argparse
import json
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
DATA_STORE_PATH = ROOT / "test-results" / "data" / "data_store.json"
SUMMARY_FILES = (
    ROOT / "test-results" / "system-summary.md",
    ROOT / "test-results" / "system-summary.json",
    ROOT / "test-results" / "ai-summary.md",
    ROOT / "test-results" / "ai-summary.json",
)
CREATED_COMPANY_PASSWORD = "greenwhite"

GROUP_0_RUNNER_PATH = "tests/smoke/test_groups/test_a_grup/test_0_group_runner.py"
GROUP_REPORT_RUNNER_PATH = (
    "tests/smoke/test_groups/test_report_grup/test_0_group_runner.py"
)
GROUP_RUNNER_PATHS = (
    GROUP_0_RUNNER_PATH,
    GROUP_REPORT_RUNNER_PATH,
)
FORMS_RUNNER_PATH = "tests/smoke/test_forms/test_0_forms_runner.py"
A2_ANGULAR_FORMS_PATH = "tests/smoke/test_forms/test_a2_angular_forms.py"

TARGETS = {
    "all": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            *GROUP_RUNNER_PATHS,
            FORMS_RUNNER_PATH,
        ),
        "--new-code",
    ),
    "setup": ("tests/smoke/test_setup/test_0_setup_runner.py", "--new-code"),
    "setup-group-0": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            GROUP_0_RUNNER_PATH,
        ),
        "--new-code",
    ),
    "setup-report": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            GROUP_REPORT_RUNNER_PATH,
        ),
        "--new-code",
    ),
    "setup-a2-admin": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            A2_ANGULAR_FORMS_PATH,
        ),
        "--new-code",
    ),
    "setup-forms": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            FORMS_RUNNER_PATH,
        ),
        "--new-code",
    ),
    "company": ("tests/smoke/test_setup/test_0_setup_runner.py::test_00_company", "--new-code"),
    "groups": (GROUP_RUNNER_PATHS, ""),
    "group-0": (GROUP_0_RUNNER_PATH, ""),
    "group-report": (GROUP_REPORT_RUNNER_PATH, ""),
    "forms": (FORMS_RUNNER_PATH, ""),
}

GROUP_ONLY_CODE_TARGETS = {
    "groups",
    "group-0",
    "group-report",
}


def normalized_url(value):
    return (value or "").strip().rstrip("/")


def env_flag(env, name):
    return str(env.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def new_code_enabled(env, *, local_dotenv_exists, pytest_extra):
    """Joriy precedence bo'yicha pytest yangi session code yaratishini aniqlaydi."""
    if local_dotenv_exists:
        return env_flag(env, "NEW_CODE")
    return env_flag(env, "NEW_CODE") or "--new-code" in pytest_extra


def saved_company_code():
    if not DATA_STORE_PATH.exists():
        return ""
    try:
        data = json.loads(DATA_STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    if not isinstance(data, dict):
        return ""
    value = data.get("company_code")
    return str(value or "").strip().lstrip("@")


def load_local_dotenv(env):
    env_path = ROOT / ".env"
    if not env_path.exists():
        return False
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
            if key:
                env[key] = value
    return True


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
    if not playwright:
        venv_playwright = Path(sys.executable).with_name("playwright")
        if venv_playwright.is_file():
            playwright = str(venv_playwright)
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
        help=(
            "Default: all. CI uchun: setup-forms. Debug uchun: setup, setup-group-0, "
            "setup-report, setup-a2-admin, "
            "company, groups, group-0, group-report, "
            "forms yoki pytest target path."
        ),
    )
    parser.add_argument("--url", help="Server URL; lokal .env bo'lsa COMPANY_URL ishlatiladi.")
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
    local_dotenv_exists = load_local_dotenv(env)

    unsupported_ai_flags = [item for item in pytest_extra if item == "--no-ai-summary" or item.startswith("--ai-model")]
    if unsupported_ai_flags:
        print("--no-ai-summary va --ai-model kerak emas; AI default off, kerak bo'lsa faqat --ai-summary ishlating", file=sys.stderr)
        return 2

    if local_dotenv_exists:
        company_url_arg = normalized_url(env.get("COMPANY_URL"))
        create_company = env_flag(env, "CREATE_COMPANY")
        disable_license_policy = env_flag(env, "DISABLE_LICENSE_POLICY")
    else:
        company_url_arg = normalized_url(args.url or env.get("COMPANY_URL"))
        create_company = args.create_company or env_flag(env, "CREATE_COMPANY")
        disable_license_policy = args.disable_license_policy or env_flag(env, "DISABLE_LICENSE_POLICY")

    if not company_url_arg:
        print("COMPANY_URL yoki --url majburiy", file=sys.stderr)
        return 2
    env["SMARTUP_RUNNER"] = "1"
    env["COMPANY_URL"] = company_url_arg

    if disable_license_policy and not create_company:
        print("DISABLE_LICENSE_POLICY faqat CREATE_COMPANY=1 bilan ishlaydi", file=sys.stderr)
        return 2
    group_only_targets = {*GROUP_ONLY_CODE_TARGETS, "forms"}
    if create_company and args.target in group_only_targets:
        print(
            "CREATE_COMPANY=1 group-only targetlar bilan ishlamaydi; all, setup yoki company ishlating",
            file=sys.stderr,
        )
        return 2
    if (
        args.target in GROUP_ONLY_CODE_TARGETS
        and new_code_enabled(
            env,
            local_dotenv_exists=local_dotenv_exists,
            pytest_extra=pytest_extra,
        )
    ):
        print(
            "NEW_CODE=1 group-only target bilan ishlamaydi: yangi code uchun "
            "setup user hali yaratilmagan. .env da NEW_CODE=0 qilib joriy "
            "setup baseline'ni ishlating yoki setup bilan bir sessiyada "
            "ishlaydigan targetni tanlang (Group-0 uchun: setup-group-0).",
            file=sys.stderr,
        )
        return 2
    if create_company and args.target in {"setup-report", "setup-a2-admin"}:
        print(f"{args.target} targeti faqat CREATE_COMPANY=0 bilan ishlaydi", file=sys.stderr)
        return 2
    if args.target == "company" and not create_company:
        print("company target faqat CREATE_COMPANY=1 bilan ishlaydi", file=sys.stderr)
        return 2

    if create_company:
        company_password = "" if local_dotenv_exists else (args.company_password or "").strip()
        head_email = (
            str(env.get("HEAD_ADMIN_EMAIL", "") or "").strip()
            if local_dotenv_exists
            else (args.head_email or env.get("HEAD_ADMIN_EMAIL") or "").strip()
        )
        head_password = (
            str(env.get("HEAD_ADMIN_PASSWORD", "") or "").strip()
            if local_dotenv_exists
            else (args.head_password or env.get("HEAD_ADMIN_PASSWORD") or "").strip()
        )
        if not local_dotenv_exists and args.company_code:
            print("--create-company bilan --company-code berilmaydi", file=sys.stderr)
            return 2
        if company_password:
            print("--company-password --create-company bilan berilmaydi; yangi company admin paroli test ichidagi default qiymat", file=sys.stderr)
            return 2
        if not head_email:
            print("CREATE_COMPANY=1 uchun HEAD_ADMIN_EMAIL majburiy", file=sys.stderr)
            return 2
        if not head_password:
            print("CREATE_COMPANY=1 uchun HEAD_ADMIN_PASSWORD majburiy", file=sys.stderr)
            return 2
        env["CREATE_COMPANY"] = "1"
        env["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD
        env["HEAD_ADMIN_EMAIL"] = head_email
        env["HEAD_ADMIN_PASSWORD"] = head_password
        env.pop("COMPANY_CODE", None)
    else:
        if local_dotenv_exists:
            company_code = str(env.get("COMPANY_CODE", "") or "").strip().lstrip("@")
            company_password = str(env.get("COMPANY_PASSWORD", "") or "").strip()
        else:
            company_code = (args.company_code or env.get("COMPANY_CODE") or "").strip().lstrip("@")
            company_password = (args.company_password or env.get("COMPANY_PASSWORD") or "").strip()
        if company_code == "0":
            company_code = saved_company_code()
            if not company_code:
                print("COMPANY_CODE=0, lekin data_store.json ichida saqlangan company_code topilmadi", file=sys.stderr)
                return 2
        if not company_code:
            print("CREATE_COMPANY=0 uchun COMPANY_CODE majburiy", file=sys.stderr)
            return 2
        if not company_password:
            print("CREATE_COMPANY=0 uchun COMPANY_PASSWORD majburiy", file=sys.stderr)
            return 2
        env["COMPANY_CODE"] = company_code
        env["COMPANY_PASSWORD"] = company_password
        env.pop("HEAD_ADMIN_EMAIL", None)
        env.pop("HEAD_ADMIN_PASSWORD", None)
        env.pop("CREATE_COMPANY", None)

    if disable_license_policy:
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
    if create_company:
        pytest_command.append("--create-company")
        pytest_command.extend(["--head-email", env["HEAD_ADMIN_EMAIL"]])
        pytest_command.extend(["--head-password", env["HEAD_ADMIN_PASSWORD"]])
    else:
        pytest_command.extend(["--company-code", env["COMPANY_CODE"]])
        pytest_command.extend(["--company-password", env["COMPANY_PASSWORD"]])
    if disable_license_policy:
        pytest_command.append("--disable-license-policy")
    pytest_command.extend(pytest_extra)

    if create_company:
        print(f"Company setup: enabled by CREATE_COMPANY=1 ({company_url_arg})")
        if disable_license_policy:
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
    if args.show_trace or env_flag(env, "SHOW_TRACE"):
        show_trace(env, dry_run=args.dry_run)

    return test_exit


if __name__ == "__main__":
    raise SystemExit(main())
