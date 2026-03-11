from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------------------------------------------------------

    def click_js(self):
        self.page.wait_for_load_state("networkidle")
        checkbox = self.page.locator(".checkbox").first
        checkbox.evaluate("el => el.click()")

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(self, timeout: int = 120_000):
        """
        Loader (overlay) paydo bo'lishini va keyin yo'qolishini kutadi.
        """
        overlay = self.page.locator(".block-ui-overlay")
        try:
            overlay.wait_for(state="visible", timeout=2_000)
        except Exception:
            # Agar loader 2 soniyada chiqmasa, demak jarayon tugagan yoki juda tez o'tgan
            return

        try:
            overlay.wait_for(state="hidden", timeout=timeout)
        except Exception as e:
            print(f"Xato: Loader {timeout} ms ichida yo'qolmadi: {e}")
            raise
    # ------------------------------------------------------------------------------------------------------------------
