import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


@pytest.mark.asyncio
async def test_login(page):
    # 1. Page Object-ni yaratamiz
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)

    # 2. Harakatlarni bajaramiz
    await login_page.navigate("https://smartup.online/login.html")
    await login_page.element_visible()
    await login_page.fill_form(email="admin@autotest", password="greenwhite")
    await login_page.click_button()

    # 3. Assert (Tekshiruv) - Test o'tgan yoki o'tmaganini aniqlash
    title = await dashboard_page.element_visible()
    assert "Trade" in title
    print(f"\nTest muvaffaqiyatli! Topilgan sarlavha: {title}")