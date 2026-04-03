import os
from playwright.sync_api import Page, expect

BASE_URL       = os.getenv("BASE_URL",       "https://smartup.online")
DEFAULT_EMAIL  = os.getenv("TEST_EMAIL",     "admin@autotest")
DEFAULT_PASS   = os.getenv("TEST_PASSWORD",  "greenwhite")

# Dashboard to'liq yuklanishini kutish uchun alohida timeout (sekin server hisobi)
DASHBOARD_TIMEOUT = 120_000

# ----------------------------------------------------------------------------------------------------------------------

def logout(page: Page) -> None:
    page.locator(".btn.btn-icon.w-auto").click()
    expect(page.locator("#kt_header").get_by_text("Admin")).to_be_visible()
    page.locator('a[ng-click="a.logout()"]').click()
    expect(page.locator("#biruniConfirm")).to_contain_text("Хотите выйти?")
    page.locator("#biruniConfirm").get_by_role("button", name="да").click()

# ----------------------------------------------------------------------------------------------------------------------

def login(page: Page, email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASS) -> None:
    page.goto(f"{BASE_URL}/login.html")
    page.get_by_placeholder("Логин@компания").fill(email)
    page.get_by_role("textbox", name="Пароль").fill(password)
    page.get_by_role("button", name="Войти").click()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page: Page) -> None:
    expect(page.get_by_role("heading", name="Trade")).to_be_visible(timeout=DASHBOARD_TIMEOUT)

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page: Page, email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASS) -> None:
    login(page, email, password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
