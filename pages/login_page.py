from pages.base_page import BasePage

class LoginPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    login_header = '//div[@class="loginbox__logo"]'

    async def element_visible(self):
        await self.wait_for_selector(self.login_header)
    # ------------------------------------------------------------------------------------------------------------------
    email_input = '//input[@id="login"]'
    password_input = '//input[@id="password"]'

    async def fill_form(self, email, password):
        await self.input_text(self.email_input, email)
        await self.input_text(self.password_input, password)
    # ------------------------------------------------------------------------------------------------------------------
    signup_button = '//button[@id="sign_in"]'

    async def click_button(self):
        await self.click(self.signup_button)
    # ------------------------------------------------------------------------------------------------------------------
