import os
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

load_dotenv()

COMPANY_URL = os.environ["COMPANY_URL"]
COMPANY_CODE = os.environ["COMPANY_CODE"]
COMPANY_PASS = os.environ["COMPANY_PASSWORD"]
USER_PASS = os.environ["USER_PASSWORD"]

ADMIN_EMAIL = f"admin{COMPANY_CODE}"

# ----------------------------------------------------------------------------------------------------------------------

def logout(page: Page) -> None:
    page.locator(".btn.btn-icon.w-auto").click()
    expect(page.locator("#kt_header").get_by_text("Admin")).to_be_visible()
    page.locator('a[ng-click="a.logout()"]').click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Хотите выйти?")
    page.locator("#biruniConfirm").get_by_role("button", name="да").click()

# ----------------------------------------------------------------------------------------------------------------------

def login(page: Page, email: str = ADMIN_EMAIL, password: str = COMPANY_PASS) -> None:
    page.goto(f"{COMPANY_URL}/login.html")
    page.get_by_placeholder("Логин@компания").fill(email)
    page.get_by_role("textbox", name="Пароль").fill(password)
    page.get_by_role("button", name="Войти").click()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page: Page) -> None:
    expect(page.get_by_role("heading", name="Trade")).to_be_visible(timeout=120_000)

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page: Page, email: str = ADMIN_EMAIL, password: str = COMPANY_PASS) -> None:
    login(page, email=email, password=password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------

def authorization_user(page: Page, code: str) -> None:
    user_email = f"user-pw{code}{COMPANY_CODE}"
    login(page, email=user_email, password=USER_PASS)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
