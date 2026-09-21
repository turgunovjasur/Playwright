"""Smoke run environmenti va browser sozlamalari."""

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
