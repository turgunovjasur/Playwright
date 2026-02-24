from playwright.async_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    async def navigate(self, url: str):
        await self.page.goto(url)

    async def click(self, selector: str):
        # Playwright avtomatik ravishda elementni kutadi (Auto-wait)
        await self.page.click(selector)

    async def input_text(self, selector: str, text: str):
        await self.page.fill(selector, text)

    async def get_text(self, selector: str) -> str:
        return await self.page.inner_text(selector)

    async def wait_for_selector(self, selector: str):
        await self.page.wait_for_selector(selector)

    async def is_visible(self, selector: str) -> bool:
        try:
            await self.page.wait_for_selector(selector, state="visible", timeout=5000)
            return True
        except:
            return False