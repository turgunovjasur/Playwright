from pages.base_page import BasePage

class DashboardPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------

    def element_visible(self):
        self.wait_for(self.page.get_by_role("heading", name="Trade"))
    # ------------------------------------------------------------------------------------------------------------------
