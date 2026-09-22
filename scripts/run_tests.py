from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import dotenv_values

from report_lifecycle import generate_report, generate_test_summary, show_trace
from smoke_environment import CREATED_COMPANY_PASSWORD, check_requiremants


ROOT = Path(__file__).resolve().parents[1]

GROUP_0_RUNNER_PATH = "tests/smoke/test_groups/test_a_grup/test_0_group_runner.py"
GROUP_REPORT_RUNNER_PATH = (
    "tests/smoke/test_groups/test_report_grup/test_0_group_runner.py"
)
GROUP_VISIT_RUNNER_PATH = "tests/smoke/test_groups/test_visit_grup/test_0_visit_runner.py"
GROUP_RUNNER_PATHS = (
    GROUP_0_RUNNER_PATH,
    GROUP_VISIT_RUNNER_PATH,
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
    "setup-smoke": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            GROUP_0_RUNNER_PATH,
            GROUP_VISIT_RUNNER_PATH,
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
    "setup-visit": (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            GROUP_VISIT_RUNNER_PATH,
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
    "group-visit": (GROUP_VISIT_RUNNER_PATH, ""),
    "group-report": (GROUP_REPORT_RUNNER_PATH, ""),
    "forms": (FORMS_RUNNER_PATH, ""),
}

GROUP_ONLY_CODE_TARGETS = {
    "groups",
    "group-0",
    "group-visit",
}


def env_flag(env, name):
    """1/0 environment flagida faqat `1` bo'lsa `True` qaytaradi."""
    return env.get(name, "0") == "1"


def new_code_enabled(env, *, local_dotenv_exists, pytest_extra):
    """Joriy precedence bo'yicha pytest yangi session code yaratishini aniqlaydi."""
    if local_dotenv_exists:
        return env_flag(env, "NEW_CODE")
    return env_flag(env, "NEW_CODE") or "--new-code" in pytest_extra


def load_local_dotenv(env):
    env_path = ROOT / ".env"
    if not env_path.exists():
        return False
    values = dotenv_values(env_path, interpolate=False)
    env.update({key: value for key, value in values.items() if value is not None})
    return True


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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smartup smoke testlarini Mac, Linux va Windows terminalida ishga tushiradi."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        help=(
            "Default: all. CI uchun: setup-smoke yoki forms. Debug uchun: setup, "
            "setup-smoke, setup-group-0, setup-visit, setup-report, setup-a2-admin, "
            "company, groups, group-0, group-visit, group-report, "
            "forms yoki pytest target path."
        ),
    )
    parser.add_argument("--url", help="Server URL; lokal .env bo'lsa COMPANY_URL ishlatiladi.")
    parser.add_argument("--company-code", help="Majburiy: 1 — yangi company yaratish; boshqa kod — mavjud company.")
    parser.add_argument("--company-password", help="Mavjud company admin paroli; company code 1 bo'lmasa majburiy.")
    parser.add_argument("--head-email", help="--company-code 1 bilan head profil emaili.")
    parser.add_argument("--head-password", help="--company-code 1 bilan head profil paroli.")
    parser.add_argument("--headless", action="store_true", help="Chromium headless rejimda ishlaydi.")
    parser.add_argument(
        "--disable-license-policy",
        action="store_true",
        help="--company-code 1 bilan company Security tabidagi 'Политика лицензирования'ni o'chiradi.",
    )
    parser.add_argument("--open-report", action="store_true", help="Allure reportni generate qilib ochadi.")
    parser.add_argument(
        "--clean-results",
        "--new-report",
        dest="clean_results",
        action="store_true",
        help="Yangi toza Allure report boshlaydi; --clean-results eski alias sifatida ishlaydi.",
    )
    parser.add_argument("--show-trace", action="store_true", help="Oxirgi Playwright trace viewerini ochadi.")
    parser.add_argument("--dry-run", action="store_true", help="Commandni ko'rsatadi, lekin ishga tushirmaydi.")
    return parser.parse_known_args()


def main():
    args, pytest_extra = parse_args()
    env = os.environ.copy()
    local_dotenv_exists = load_local_dotenv(env)

    unsupported_ai_flags = [
        item
        for item in pytest_extra
        if item in {"--ai-summary", "--no-ai-summary"}
        or item.startswith("--ai-model")
    ]
    if unsupported_ai_flags:
        print(
            "AI tahlili AI_ANALYSIS=1/0 bilan boshqariladi; yoqish uchun GEMINI_API_KEY kerak. "
            "AI_MAX_CASES (default 5) va GEMINI_MODEL orqali limit/model tanlanadi.",
            file=sys.stderr,
        )
        return 2

    environment_url = env.get("COMPANY_URL") or env.get("URL") or ""
    if local_dotenv_exists:
        company_url_arg = environment_url
        company_code = env.get("COMPANY_CODE", "")
        disable_license_policy = env_flag(env, "DISABLE_LICENSE_POLICY")
    else:
        company_url_arg = args.url or environment_url
        company_code = args.company_code or env.get("COMPANY_CODE") or ""
        disable_license_policy = args.disable_license_policy or env_flag(env, "DISABLE_LICENSE_POLICY")

    create_company = company_code == "1"
    env["COMPANY_CODE"] = company_code

    env["SMARTUP_RUNNER"] = "1"
    env["COMPANY_URL"] = company_url_arg
    if args.clean_results:
        env["CLEAN_ALLURE_RESULTS"] = "1"
    group_only_targets = {*GROUP_ONLY_CODE_TARGETS, "group-report", "forms"}
    if create_company and args.target in group_only_targets:
        print(
            "COMPANY_CODE=1 group-only targetlar bilan ishlamaydi; all, setup yoki company ishlating",
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
            "ishlaydigan targetni tanlang (Group-0 uchun: setup-group-0; "
            "Visit uchun: setup-visit).",
            file=sys.stderr,
        )
        return 2
    if create_company and args.target in {"setup-report", "setup-a2-admin"}:
        print(f"{args.target} targeti faqat mavjud kompaniya kodi bilan ishlaydi", file=sys.stderr)
        return 2
    if args.target == "company" and not create_company:
        print("company target faqat COMPANY_CODE=1 bilan ishlaydi", file=sys.stderr)
        return 2

    if create_company:
        head_email = (
            env.get("HEAD_ADMIN_EMAIL", "")
            if local_dotenv_exists
            else (args.head_email or env.get("HEAD_ADMIN_EMAIL") or "")
        )
        head_password = (
            env.get("HEAD_ADMIN_PASSWORD", "")
            if local_dotenv_exists
            else (args.head_password or env.get("HEAD_ADMIN_PASSWORD") or "")
        )
        env["HEAD_ADMIN_EMAIL"] = head_email
        env["HEAD_ADMIN_PASSWORD"] = head_password
    else:
        if local_dotenv_exists:
            company_password = env.get("COMPANY_PASSWORD", "")
        else:
            company_password = args.company_password or env.get("COMPANY_PASSWORD") or ""
        env["COMPANY_PASSWORD"] = company_password

    if not local_dotenv_exists:
        for enabled, name in (
            (args.headless, "HEADLESS"),
            ("--new-code" in pytest_extra, "NEW_CODE"),
            (args.disable_license_policy, "DISABLE_LICENSE_POLICY"),
        ):
            if enabled:
                env[name] = "1"
    if args.open_report:
        env["OPEN_REPORT"] = "1"
    if args.show_trace:
        env["SHOW_TRACE"] = "1"
    try:
        check_requiremants(env, cli_options={} if local_dotenv_exists else vars(args))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if create_company:
        env["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD

    targets, code_mode = TARGETS.get(args.target, (args.target, ""))
    if isinstance(targets, str):
        targets = (targets,)
    pytest_command = [sys.executable, "-m", "pytest", *targets]

    if code_mode:
        pytest_command.append(code_mode)
    headless = env_flag(env, "HEADLESS")
    if not local_dotenv_exists:
        headless = headless or args.headless
    if headless:
        pytest_command.append("--headless")
    pytest_command.extend(["--url", company_url_arg])
    pytest_command.extend(["--company-code", company_code])
    if create_company:
        pytest_command.extend(["--head-email", env["HEAD_ADMIN_EMAIL"]])
        pytest_command.extend(["--head-password", env["HEAD_ADMIN_PASSWORD"]])
    else:
        pytest_command.extend(["--company-password", env["COMPANY_PASSWORD"]])
    if disable_license_policy:
        pytest_command.append("--disable-license-policy")
    pytest_command.extend(pytest_extra)

    if create_company:
        print(f"Company setup: enabled by COMPANY_CODE=1 ({company_url_arg})")
        if disable_license_policy:
            print("Company license policy: will be disabled")
    else:
        print(f"Company setup: skipped; using company_code={env['COMPANY_CODE']}")

    run_started_at = time.time()
    test_exit = run(pytest_command, env, dry_run=args.dry_run)

    generate_test_summary(
        ROOT,
        env,
        test_exit=test_exit,
        command_text=command_text(pytest_command),
        started_at=run_started_at,
        dry_run=args.dry_run,
    )

    if not env_flag(env, "DEFER_ALLURE_REPORT"):
        generate_report(
            ROOT,
            env,
            open_report=args.open_report or env_flag(env, "OPEN_REPORT"),
            dry_run=args.dry_run,
        )
    if args.show_trace or env_flag(env, "SHOW_TRACE"):
        show_trace(ROOT, env, dry_run=args.dry_run)

    return test_exit


if __name__ == "__main__":
    raise SystemExit(main())
