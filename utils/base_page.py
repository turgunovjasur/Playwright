import re
from datetime import datetime, timedelta

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

    def wait_for_loader(self, timeout=120_000):
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

    def select_option(self, ng_model, option_text, clear=False):
        b_input = self.page.locator(f'b-input:has(input[ng-model="{ng_model}"])')
        b_input.locator("input").click()
        if clear:
            b_input.locator(".edit").click()
        b_input.locator("div.hint").get_by_text(option_text).click()

    # ------------------------------------------------------------------------------------------------------------------

    def select_date(self, ng_model, option="custom", day=None, add_days=0):
        today = datetime.today()

        if option == "first":
            target = today.replace(day=1)
        elif option == "last":
            next_month = today.replace(day=28) + timedelta(days=4)
            target = next_month - timedelta(days=next_month.day)
        elif option == "today":
            target = today + timedelta(days=add_days)
        else:  # custom
            target = today.replace(day=day)

        self.page.locator(f'input[ng-model="{ng_model}"]').click()
        self.page.get_by_role("cell", name=str(target.day)).first.click()

    # ------------------------------------------------------------------------------------------------------------------
