import os
import json
import random
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


def _resolve_code(code=None, generated_code="new"):
    """`who='user'` emailini yig'ish uchun code'ni hal qiladi.

    - code berilsa: o'sha ishlatiladi (runner zanjiri session code'ni shu yo'l bilan beradi)
    - generated_code='old': data_store.json dagi mavjud code (yakka/debug run uchun)
    - aks holda ('new'): yangi random 6 xonali code
    """
    if code:
        return str(code)
    if generated_code == "old":
        saved = None
        if DATA_STORE_PATH.exists():
            try:
                data = json.loads(DATA_STORE_PATH.read_text(encoding="utf-8"))
                saved = data.get("code") if isinstance(data, dict) else None
            except json.JSONDecodeError:
                saved = None
        if not saved:
            raise AssertionError(
                "generated_code='old': data_store.json da 'code' topilmadi. "
                "Avval to'liq runner ishga tushiring."
            )
        return str(saved)
    return str(random.randint(100000, 999999))

# ----------------------------------------------------------------------------------------------------------------------

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

def authorization(page, who="admin", *, email=None, password=None, code=None, generated_code="new"):
    """Rolga qarab tizimga kiradi.

    who:
        "admin" → ADMIN_EMAIL / admin@{company} + ADMIN_PASSWORD / company parol
        "head"  → HEAD_ADMIN_EMAIL + HEAD_ADMIN_PASSWORD (company yaratish uchun)
        "user"  → user-pw{code}@{company} + USER_PASSWORD / USER_PASS

    email/password to'g'ridan-to'g'ri berilsa — who e'tiborsiz, o'shalar ishlatiladi (eski chaqiruvlar uchun).
    generated_code: "new" → yangi random code; "old" → data_store.json dagi code (user emailini yig'ish uchun).
    code berilsa — generated_code e'tiborsiz, o'sha code ishlatiladi.
    """
    if email is None and password is None:
        if who == "admin":
            email, password = admin_email(), admin_password()
        elif who == "head":
            email, password = head_email(), head_password()
        elif who == "user":
            resolved_code = _resolve_code(code, generated_code)
            email, password = user_email_for(resolved_code), user_password()
        else:
            raise ValueError(
                f"authorization: noma'lum who={who!r}. 'admin', 'user' yoki 'head' bo'lishi kerak."
            )
    login(page, email=email, password=password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
