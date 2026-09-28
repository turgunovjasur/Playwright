import os
import re

from playwright.sync_api import expect

from utils.base_pages.auto_base_page import AutoBasePage
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

def kernel_api_base_url(company_url=None):
    """Kernel ng-serve API prefix; app3/smartup URLs stay unchanged."""
    url = str(company_url or os.environ["COMPANY_URL"]).strip().rstrip("/")
    if "localhost" in url or "127.0.0.1" in url:
        if not url.endswith("/api"):
            return f"{url}/api"
    return url

# ----------------------------------------------------------------------------------------------------------------------

def kernel_dev_proxy_headers():
    """Dev-proxy header so /api does not fall back to local:8080."""
    pair = _kernel_dev_proxy_pair()
    if not pair:
        return {}
    return {"X-Kernel-Dev-Proxy": pair[0]}

# ----------------------------------------------------------------------------------------------------------------------

def _kernel_dev_proxy_pair():
    key = os.environ.get("KERNEL_DEV_PROXY", "").strip()
    if not key:
        return None
    if key.startswith("app3"):
        host = "app3"
    elif key.startswith("smartup"):
        host = "smartup"
    elif key.startswith("local"):
        host = "local"
    else:
        host = "app3"
    return key, host


def configure_kernel_dev_proxy(page):
    """Kernel login page proxies /api; default local 8080 is often down."""
    pair = _kernel_dev_proxy_pair()
    if not pair:
        return
    key, _host = pair
    page.context.add_cookies(
        [
            {
                "name": "smartup_dev_proxy",
                "value": key,
                "url": os.environ["COMPANY_URL"],
            }
        ]
    )


def apply_kernel_dev_proxy_storage(page):
    pair = _kernel_dev_proxy_pair()
    if not pair:
        return
    key, host = pair
    page.evaluate(
        """([proxyKey, hostKey]) => {
            localStorage.setItem('smartup.dev.proxy', proxyKey);
            localStorage.setItem('smartup.dev.proxy.host', hostKey);
            document.cookie = 'smartup_dev_proxy=' + proxyKey + ';path=/;max-age=2592000';
          }""",
        [key, host],
    )
    page.reload(wait_until="domcontentloaded")
    page.get_by_placeholder("Логин@компания").wait_for(state="visible", timeout=30_000)


def login(page, email=None, password=None, *, profile=None):
    email = email or f"admin@{current_company_code()}"
    password = password or os.environ["COMPANY_PASSWORD"]
    company_url = os.environ["COMPANY_URL"]
    account, _, company = email.rpartition("@")
    profile = profile or ("admin" if account == "admin" else "user" if account.startswith("user-pw") else "custom")
    match = re.fullmatch(r"user-pw(\d+)", account)
    start_login(page, server=company_url, company=company if profile != "head" else "", profile=profile, login=email, password=password, code=match.group(1) if match else None)

    configure_kernel_dev_proxy(page)
    if "localhost" in company_url or "127.0.0.1" in company_url:
        page.goto(f"{company_url}/auth/login", wait_until="domcontentloaded")
    else:
        page.goto(f"{company_url}/login.html")
        if "/auth/login" not in page.url and page.locator("smt-input, app-login-form").count() == 0:
            page.goto(f"{company_url}/auth/login", wait_until="domcontentloaded")
    apply_kernel_dev_proxy_storage(page)

    base = AutoBasePage(page)
    base.input(placeholder="Логин@компания", value=email)
    base.input(placeholder="Пароль", value=password)
    submit = page.locator("app-login-form button[type='submit']")
    expect(submit).to_be_enabled(timeout=15_000)
    submit.click()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page):
    AutoBasePage(page).expect_page(heading="Trade", url="dashboard", timeout=120_000)
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
