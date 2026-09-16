import os

from utils.base_page import BasePage
from utils.data_store import load_data

# ----------------------------------------------------------------------------------------------------------------------

def current_company_code():
    value = os.environ["COMPANY_CODE"]
    if value == "1":
        return load_data("company_code")
    return value

# ----------------------------------------------------------------------------------------------------------------------

def login(page, email=None, password=None):
    email = email or f"admin@{current_company_code()}"
    password = password or os.environ["COMPANY_PASSWORD"]
    company_url = os.environ["COMPANY_URL"]

    page.goto(f"{company_url}/login.html")

    base = BasePage(page)
    base.input(placeholder="Логин@компания", value=email)
    base.input(placeholder="Пароль", value=password)
    base.click(name="Войти")

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page):
    BasePage(page).expect_page(heading="Trade", url="dashboard", timeout=120_000)

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

    login(page, email=email, password=password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
