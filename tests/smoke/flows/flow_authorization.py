import os
import json
from pathlib import Path

from playwright.sync_api import expect
from utils.base_page import BasePage

USER_PASS = "123456789"

DATA_STORE_PATH = Path("test-results/data/data_store.json")


def _normalize_company_code(value):
    return value.strip().lstrip("@")


def _create_company_enabled():
    return os.getenv("CREATE_COMPANY", "").strip().lower() in {"1", "true", "yes", "on"}


def company_url():
    value = os.getenv("COMPANY_URL", "").strip().rstrip("/")
    if not value:
        raise AssertionError("--url majburiy. Testni scripts/run_tests.py --url <server_url> orqali ishga tushiring.")
    return value


def company_password():
    value = os.getenv("COMPANY_PASSWORD", "").strip()
    if not value:
        raise AssertionError(
            "--company-password majburiy yoki --create-company orqali yangi company admin paroli set qilingan bo'lishi kerak."
        )
    return value


def current_company_code():
    if _create_company_enabled() and DATA_STORE_PATH.exists():
        try:
            data = json.loads(DATA_STORE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        company_code = data.get("company_code") if isinstance(data, dict) else None
        if company_code:
            return _normalize_company_code(str(company_code))
    value = os.getenv("COMPANY_CODE", "").strip()
    if not value:
        raise AssertionError(
            "--company-code majburiy yoki --create-company orqali yangi company yaratilgan bo'lishi kerak."
        )
    return _normalize_company_code(value)

def company_suffix():
    return f"@{current_company_code()}"

def admin_email():
    value = os.getenv("ADMIN_EMAIL", "").strip()
    if value:
        return value
    return f"admin{company_suffix()}"

def admin_password():
    value = os.getenv("ADMIN_PASSWORD", "").strip()
    if value:
        return value
    return company_password()

def user_email_for(code):
    return f"user-pw{code}{company_suffix()}"

def user_password():
    value = os.getenv("USER_PASSWORD", "").strip()
    if value:
        return value
    return USER_PASS

def head_email():
    value = os.getenv("HEAD_ADMIN_EMAIL", "").strip()
    if not value:
        raise AssertionError(
            "head profil uchun HEAD_ADMIN_EMAIL kerak: .env yoki --head-email orqali bering."
        )
    return value

def head_password():
    value = os.getenv("HEAD_ADMIN_PASSWORD", "").strip()
    if not value:
        raise AssertionError(
            "head profil uchun HEAD_ADMIN_PASSWORD kerak: .env yoki --head-password orqali bering."
        )
    return value


def logout(page):
    base = BasePage(page)
    page.locator(".btn.btn-icon.w-auto").click()
    expect(page.locator("#kt_header").get_by_text("Admin")).to_be_visible()
    page.locator('a[ng-click="a.logout()"]').click()
    base.confirm_biruni("Хотите выйти?")

# ----------------------------------------------------------------------------------------------------------------------

def login(page, email=None, password=None):
    email = email or admin_email()
    password = password or company_password()
    page.goto(f"{company_url()}/login.html")
    page.get_by_placeholder("Логин@компания").fill(email)
    page.get_by_role("textbox", name="Пароль").fill(password)
    page.get_by_role("button", name="Войти").click()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page, timeout=120_000):
    expect(page.get_by_role("heading", name="Trade")).to_be_visible(timeout=timeout)

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page, *, who, code=None):
    """Rolga qarab tizimga kiradi.

    who:
        "admin" → ADMIN_EMAIL / admin@{company} + ADMIN_PASSWORD / company parol
        "head"  → HEAD_ADMIN_EMAIL + HEAD_ADMIN_PASSWORD (company yaratish uchun)
        "user"  → user-pw{code}@{company} + USER_PASSWORD / USER_PASS

    Credentiallar faqat who qiymatiga qarab tanlanadi.
    who="user" uchun code fixture qiymati majburiy; yangi/eski code tanlovini faqat NEW_CODE boshqaradi.
    """
    if who == "admin":
        email, password = admin_email(), admin_password()
    elif who == "head":
        email, password = head_email(), head_password()
    elif who == "user":
        if not code:
            raise AssertionError(
                "authorization(who='user') uchun code fixture qiymatini code=code orqali bering."
            )
        email, password = user_email_for(str(code)), user_password()
    else:
        raise ValueError(
            f"authorization: noma'lum who={who!r}. 'admin', 'user' yoki 'head' bo'lishi kerak."
        )
    login(page, email=email, password=password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
