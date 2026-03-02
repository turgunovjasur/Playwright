from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

# ----------------------------------------------------------------------------------------------------------------------

def login(page, email, password):
    login_page = LoginPage(page)
    login_page.open()
    login_page.element_visible()
    login_page.fill_form(email, password)
    login_page.click_button()

# ----------------------------------------------------------------------------------------------------------------------

def dashboard(page):
    dashboard_page = DashboardPage(page)
    dashboard_page.element_visible()

# ----------------------------------------------------------------------------------------------------------------------

def authorization(page):
    email = "admin@autotest"
    password= "greenwhite"

    login(page, email, password)
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------
