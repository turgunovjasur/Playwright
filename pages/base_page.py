from playwright.async_api import Page, Locator


class BasePage:
    def __init__(self, page: Page):
        self.page = page
    # ------------------------------------------------------------------------------------------------------------------

    def locator(self, selector: str) -> Locator:
        """Locator object qaytaradi"""
        return self.page.locator(selector)
    # ------------------------------------------------------------------------------------------------------------------

    async def navigate(self, url: str):
        await self.page.goto(url)
    # ------------------------------------------------------------------------------------------------------------------

    async def click(self, locator: Locator):
        await locator.click()
    # ------------------------------------------------------------------------------------------------------------------

    async def fill(self, locator: Locator, text: str):
        await locator.fill(text)
    # ------------------------------------------------------------------------------------------------------------------

    async def get_text(self, locator: Locator) -> str:
        return await locator.inner_text()
    # ------------------------------------------------------------------------------------------------------------------

    async def wait_for(self, locator: Locator):
        await locator.wait_for(timeout=30_000, state="visible")
    # ------------------------------------------------------------------------------------------------------------------

    async def is_visible(self, locator: Locator) -> bool:
        try:
            await locator.wait_for(timeout=30_000, state="visible")
            return True
        except Exception:
            return False
    # ------------------------------------------------------------------------------------------------------------------

    async def is_page_loaded(self) -> bool:
        """Sahifa toliq ochilganligini tekshiradi"""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=30_000)
            return True
        except Exception:
            return False
    # ------------------------------------------------------------------------------------------------------------------
