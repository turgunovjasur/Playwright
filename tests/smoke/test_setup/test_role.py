import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_role(page):
    """Testcase: Admin roliga barcha ruxsatlarni (switchlarni) yoqish.

    1. Пользователи -> Роли ro'yxatini ochish.
    2. "Админ" rolini "Изменить" qilib, barcha "нет" switchlarini ketma-ket yoqish.
    3. Saqlab, Роли ro'yxatiga qaytishni tekshirish.
    """
    base = BasePage(page)
    with allure.step("1 - Rollar ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")
        page.get_by_role("link", name="Роли").click()
        base.expect_page(heading="Роли")

    with allure.step("2 - Admin rolini o'zgartirish — barcha switchlarni yoqish"):
        base.grid("Админ", click=True)
        page.get_by_role("button", name="Изменить").click()
        base.expect_page(heading="Роль (изменение)")
        base.hide_ui("#onboarding-launcher, .b24-widget-button-popup, .b24-widget-button-popup-image")

        off_switches = page.locator('label.switch:has(t:text-is("нет"))')
        remaining = off_switches.count()
        while remaining > 0:
            off_switches.first.click()
            expect(off_switches).to_have_count(remaining - 1)
            remaining -= 1

    with allure.step("3 - Saqlash va natijani tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.expect_page(heading="Роли", url="role_list", timeout=300_000)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_role(page)
