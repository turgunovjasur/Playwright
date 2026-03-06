from playwright.sync_api import Page, Locator


class BasePage:
    def __init__(self, page: Page):
        self.page = page
    # ------------------------------------------------------------------------------------------------------------------

    def locator(self, selector: str) -> Locator:
        """Locator object qaytaradi"""
        return self.page.locator(selector)
    # ------------------------------------------------------------------------------------------------------------------

    def navigate(self, url: str):
        self.page.goto(url)
    # ------------------------------------------------------------------------------------------------------------------

    def click(self, locator=None, click_js=False):
        if click_js:
            self.page.wait_for_load_state("networkidle")
            checkbox = self.page.locator(".checkbox").first
            checkbox.evaluate("el => el.click()")
        else:
            locator.click()
    # ------------------------------------------------------------------------------------------------------------------

    def fill(self, locator: Locator, text: str):
        locator.fill(text)
    # ------------------------------------------------------------------------------------------------------------------

    def get_text(self, locator: Locator) -> str:
        return locator.inner_text()
    # ------------------------------------------------------------------------------------------------------------------

    def wait_for(self, locator: Locator):
        locator.wait_for(timeout=30_000, state="visible")
    # ------------------------------------------------------------------------------------------------------------------
