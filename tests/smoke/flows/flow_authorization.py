import os
import re

from utils.base_pages.base_page import BasePage
from utils.base_pages.page_reporting import capture_filial
from utils.data_store import load_data
from utils.report_context import confirm_login, start_login

# ----------------------------------------------------------------------------------------------------------------------

def current_company_code():
    value = os.environ["COMPANY_CODE"]
    if value == "1":
        return load_data("company_code")
    return value

# ----------------------------------------------------------------------------------------------------------------------

def login(page, email=None, password=None, *, profile=None):
    email = email or f"admin@{current_company_code()}"
    password = password or os.environ["COMPANY_PASSWORD"]
    company_url = os.environ["COMPANY_URL"]
    account, _, company = email.rpartition("@")
    profile = profile or ("admin" if account == "admin" else "user" if account.startswith("user-pw") else "custom")
    match = re.fullmatch(r"user-pw(\d+)", account)
    start_login(page, server=company_url, company=company if profile != "head" else "", profile=profile, login=email, password=password, code=match.group(1) if match else None)

    page.goto(f"{company_url}/login.html")

    base = BasePage(page)
    base.input(placeholder="Логин@компания", value=email)
    base.input(placeholder="Пароль", value=password)
    base.click(name="Войти")

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page):
    BasePage(page).expect_page(heading="Trade", url="dashboard", timeout=120_000)
    confirm_login(page)
    capture_filial(page)

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page, *, who, code=None):
    """Rolga qarab tizimga kiradi.

    who:
        "admin" → admin@{current_company_code} + COMPANY_PASSWORD
        "head"  → HEAD_ADMIN_EMAIL + HEAD_ADMIN_PASSWORD (company yaratish uchun)
        "user"  → user-pw{code}@{company} + USER_PASSWORD

    Credentiallar faqat who qiymatiga qarab tanlanadi.
    who="user" uchun code fixture qiymati majburiy; yangi/eski code tanlovini faqat NEW_CODE boshqaradi.
    """
    if who == "admin":
        email = f"admin@{current_company_code()}"
        password = os.environ["COMPANY_PASSWORD"]
    elif who == "head":
        email = os.environ["HEAD_ADMIN_EMAIL"]
        password = os.environ["HEAD_ADMIN_PASSWORD"]
    elif who == "user":
        email = f"user-pw{code}@{current_company_code()}"
        password = os.environ["USER_PASSWORD"]
    else:
        raise ValueError(f"authorization: noma'lum who={who!r}. 'admin', 'user' yoki 'head' bo'lishi kerak.")

    login(page, email=email, password=password, profile=who)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
