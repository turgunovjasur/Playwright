import pytest
from pages.dashboard_page import DashboardPage


@pytest.mark.asyncio
async def test_dashboard(page):
    dashboard_page = DashboardPage(page)

    await dashboard_page.element_visible()

