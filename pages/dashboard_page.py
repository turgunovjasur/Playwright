from pages.base_page import BasePage

class DashboardPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------

    async def element_visible(self):
        await self.wait_for(self.page.get_by_role("heading", name="Trade"))
    # ------------------------------------------------------------------------------------------------------------------

    async def is_page_fully_loaded(self) -> bool:
        """Sahifa toliq ochilganligini tekshiradi"""
        return await self.is_page_loaded()
    # ------------------------------------------------------------------------------------------------------------------
