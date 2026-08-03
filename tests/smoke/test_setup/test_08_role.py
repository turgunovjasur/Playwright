import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def run_role(page):
    """Testcase: Admin roliga barcha ruxsatlarni (switchlarni) yoqish.

    1. Пользователи ro'yxatini ochish.
    2. Роли ro'yxatini ochish.
    3. "Админ" rolining edit formasini ochish.
    4. Barcha "нет" switchlarini ketma-ket yoqish.
    5. Saqlab, Роли ro'yxatiga qaytishni tekshirish.
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")

    with allure.step("2 - Rollar ro'yxatini ochish"):
        base.click(name="Роли", role="link")
        base.expect_page(heading="Роли")

    with allure.step("3 - Admin rolining edit formasini ochish"):
        base.grid("Админ", click=True)
        base.click(name="Изменить")
        base.expect_page(heading="Роль (изменение)")

    with allure.step("4 - Barcha ruxsat switchlarini yoqish"):
        base.hide_ui("#onboarding-launcher, .b24-widget-button-popup, .b24-widget-button-popup-image")

        off_switches = page.locator('label.switch:has(t:text-is("нет"))')
        remaining = off_switches.count()
        while remaining > 0:
            off_switches.first.click()
            expect(off_switches).to_have_count(remaining - 1)
            remaining -= 1

    with allure.step("5 - Rolni saqlab, ro'yxatga qaytish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Роли", url="role_list", timeout=300_000)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page):
    authorization(page, who="admin")
    run_role(page)
