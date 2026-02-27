import pytest
from pages.login_page import LoginPage


@pytest.mark.asyncio
async def test_login(page):
    email = "admin@autotest"
    password= "greenwhite"

    login_page = LoginPage(page)

    await login_page.open()
    await login_page.element_visible()
    await login_page.fill_form(email, password)
    await login_page.click_button()
