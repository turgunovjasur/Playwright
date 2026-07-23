import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_role_attach_form(page):
    """Testcase: Admin roliga barcha formalarga ruxsat berish.

    1. Роли ro'yxatidan "Админ" rolini ochib, Формы sahifasiga o'tish.
    2. "Доступ ко всем формам" -> "Разрешить" bilan barcha formalarga ruxsat berish.
    3. "Доступные" ro'yxati bo'shligini ("нет данных") tekshirib, sahifani yopish.
    """
    base = BasePage(page)
    with allure.step("1 - Rollar ro'yxatidan Admin roli Formalar sahifasini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")
        page.get_by_role("link", name="Роли").click()
        base.expect_page(heading="Роли")
        base.grid("Админ", click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="Роль (Просмотр)")
        page.get_by_role("link", name="Формы").click()

    with allure.step("2 - Barcha formalarga ruxsat berish"):
        page.get_by_role("button", name="Доступ ко всем формам").click()
        page.get_by_role("link", name="Разрешить").click()
        base.confirm_biruni(expected_text="Разрешить доступ ко всем формам?")
        base.expect_page(heading="Роль (Просмотр)", timeout=300_000)

    with allure.step("3 - Ruxsatlar berilganini tekshirish"):
        page.get_by_role("button", name="Доступные").click()
        expect(page.locator("b-page")).to_contain_text("нет данных")
        page.get_by_role("button", name="Закрыть").click()
        base.expect_page(heading="Роли")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin roliga barcha formalarga ruxsat berish")
def test_role_attach_form(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_role_attach_form(page)
