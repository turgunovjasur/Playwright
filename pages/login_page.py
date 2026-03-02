from pages.base_page import BasePage

class LoginPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------

    def open(self):
        self.navigate("https://smartup.online/login.html")
    # ------------------------------------------------------------------------------------------------------------------

    def element_visible(self):
        self.wait_for(self.locator(".loginbox__logo"))
    # ------------------------------------------------------------------------------------------------------------------

    def fill_form(self, email, password):
        self.fill(self.page.get_by_placeholder("Логин@компания"), email)
        self.fill(self.page.get_by_role("textbox", name="Пароль"), password)
    # ------------------------------------------------------------------------------------------------------------------

    def click_button(self):
        self.click(self.page.get_by_role("button", name="Войти"))
    # ------------------------------------------------------------------------------------------------------------------