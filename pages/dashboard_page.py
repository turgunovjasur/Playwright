from pages.base_page import BasePage

class DashboardPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    dashboard_header = "//div/h3[contains(text(), 'Trade')]"

    async def element_visible(self):
        await self.wait_for_selector(self.dashboard_header)
        return await self.get_text(self.dashboard_header)
    # ------------------------------------------------------------------------------------------------------------------
