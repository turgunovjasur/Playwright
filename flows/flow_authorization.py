from playwright.sync_api import Page, expect

# ----------------------------------------------------------------------------------------------------------------------

def login(page: Page, email, password) -> None:
    page.goto("https://smartup.online/login.html")
    page.get_by_placeholder("Логин@компания").fill(email)
    page.get_by_role("textbox", name="Пароль").fill(password)
    page.get_by_role("button", name="Войти").click()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page: Page) -> None:
    expect(page.get_by_role("heading", name="Trade")).to_be_visible(timeout=120_000)

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page, logger):
    email = "admin@autotest"
    password= "greenwhite"

    login(page, email, password)
    logger.step("login")

    dashboard(page)
    logger.step("dashboard")

# ----------------------------------------------------------------------------------------------------------------------
