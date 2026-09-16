"""Smoke run sozlamalari va company yaratish testini tanlash qoidasi."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from scripts.smoke_environment import CREATED_COMPANY_PASSWORD, check_requiremants


ROOT_DIR = Path(__file__).resolve().parents[2]

_LOCAL_DOTENV_EXISTS = False


def load_local_dotenv():
    """Repo rootidagi `.env` qiymatlarini lokal pytest run uchun yuklaydi."""
    global _LOCAL_DOTENV_EXISTS
    env_path = ROOT_DIR / ".env"
    _LOCAL_DOTENV_EXISTS = env_path.exists()
    if _LOCAL_DOTENV_EXISTS:
        load_dotenv(env_path, override=True, interpolate=False)


def env_flag(name):
    """1/0 environment flagida faqat `1` bo'lsa `True` qaytaradi."""
    return os.getenv(name, "0") == "1"


def option_or_env(config, option_name, *env_names):
    """Qiymatni lokal `.env`dan yoki CLI/environment manbalaridan oladi."""
    if not _LOCAL_DOTENV_EXISTS:
        value = config.getoption(option_name) or ""
        if value:
            return value
    for env_name in env_names:
        value = os.getenv(env_name, "")
        if value:
            return value
    return ""


def add_pytest_options(parser):
    """Smartup smoke run uchun qo'shimcha pytest CLI optionlarini ro'yxatdan o'tkazadi."""
    smoke = parser.getgroup("smartup smoke")
    smoke.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Chromium ni headless rejimda ishga tushiradi",
    )
    smoke.addoption(
        "--new-code",
        action="store_true",
        default=False,
        help=(
            "Yangi 6 xonali code yaratadi; berilmasa data_store.json dagi "
            "mavjud code ishlatiladi"
        ),
    )
    smoke.addoption("--url", default="", help="Majburiy server URL")
    smoke.addoption(
        "--company-code",
        default="",
        help="Majburiy: 1 — yangi company yaratish; boshqa kod — mavjud company.",
    )
    smoke.addoption(
        "--company-password",
        default="",
        help="Mavjud company admin paroli; company code 1 bo'lmasa majburiy.",
    )
    smoke.addoption(
        "--head-email",
        default="",
        help="--company-code 1 bilan head profil emaili.",
    )
    smoke.addoption(
        "--head-password",
        default="",
        help="--company-code 1 bilan head profil paroli.",
    )
    smoke.addoption(
        "--disable-license-policy",
        action="store_true",
        default=False,
        help=(
            "--company-code 1 bilan yangi companyda Политика лицензирования "
            "ni o'chiradi."
        ),
    )


def modify_collected_items(config, items):
    """Mavjud company bilan run qilinganda company yaratish testini chiqaradi."""
    if os.environ["COMPANY_CODE"] != "1":
        company_items = [
            item
            for item in items
            if (
                Path(str(item.path)).name == "test_0_setup_runner.py"
                and item.name == "test_00_company"
            ) or (
                Path(str(item.path)).name == "test_00_company.py"
                and item.name == "test_company"
            )
        ]
        if company_items:
            items[:] = [item for item in items if item not in company_items]
            config.hook.pytest_deselected(items=company_items)


def configure_environment(config):
    """Run qiymatlarini yig'adi, umumiy tekshiruvdan o'tkazadi va environmentga yuklaydi."""
    company_url = option_or_env(
        config,
        "--url",
        "COMPANY_URL",
        "URL",
    )
    company_code = option_or_env(config, "--company-code", "COMPANY_CODE")
    create_company = company_code == "1"

    env = os.environ.copy()
    env["COMPANY_URL"] = company_url
    env["COMPANY_CODE"] = company_code
    if create_company:
        env["HEAD_ADMIN_EMAIL"] = option_or_env(config, "--head-email", "HEAD_ADMIN_EMAIL")
        env["HEAD_ADMIN_PASSWORD"] = option_or_env(config, "--head-password", "HEAD_ADMIN_PASSWORD")
    else:
        env["COMPANY_PASSWORD"] = option_or_env(config, "--company-password", "COMPANY_PASSWORD")
    cli_options = {}
    if not _LOCAL_DOTENV_EXISTS:
        cli_options = {
            name.replace("-", "_"): config.getoption(f"--{name}")
            for name in ("company-password", "head-email", "head-password")
        }
        for option_name, env_name in (
            ("--headless", "HEADLESS"),
            ("--new-code", "NEW_CODE"),
            ("--disable-license-policy", "DISABLE_LICENSE_POLICY"),
        ):
            if config.getoption(option_name):
                env[env_name] = "1"
    try:
        check_requiremants(env, cli_options=cli_options)
    except ValueError as error:
        raise pytest.UsageError(str(error)) from None

    if create_company:
        env["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD
    os.environ.update(env)

    return {
        "company_url": company_url,
        "create_company": create_company,
    }


def browser_launch_options():
    """Chromium launch uchun Playwright optionlarini tayyorlaydi."""
    headless = env_flag("HEADLESS")
    return {
        "headless": headless,
        "args": [] if headless else ["--start-maximized"],
    }


def browser_context_options():
    """Yangi browser context uchun umumiy Playwright optionlarini qaytaradi."""
    options = {
        "accept_downloads": True,
        "timezone_id": "Asia/Tashkent",
    }
    if env_flag("HEADLESS"):
        options["viewport"] = {"width": 1920, "height": 1080}
    else:
        options["no_viewport"] = True
    return options
