from pages.base_page import BasePage

class LoginPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    async def open(self):
        await self.navigate("https://smartup.online/login.html")
    # ------------------------------------------------------------------------------------------------------------------

    async def element_visible(self):
        await self.wait_for(self.locator('//div[@class="loginbox__logo"]'))
    # ------------------------------------------------------------------------------------------------------------------

    async def fill_form(self, email, password):
        await self.fill(self.page.get_by_placeholder("Логин@компания"), email)
        await self.fill(self.page.get_by_role("textbox", name="Пароль"), password)
    # ------------------------------------------------------------------------------------------------------------------

    async def click_button(self):
        await self.click(self.page.get_by_role("button", name="Войти"))
    # ------------------------------------------------------------------------------------------------------------------
