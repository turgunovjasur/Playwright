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

        # Har bir ruxsat — <label class="switch"> ichidagi yashirin Angular checkbox. O'rovchi
        # label'ni bosish uni ishonchli toggle qiladi (ichki <span> ni bosish barqaror emas edi).
        # `t:text-is("нет")` faqat o'chiq (state='N') switchlarni belgilaydi — status switch va
        # chat-widget tegmaydi, shuning uchun pozitsiya/widget-zona hisob-kitobi kerak emas.
        off_switches = page.locator('label.switch:has(t:text-is("нет"))')
        remaining = off_switches.count()
        while remaining > 0:
            off_switches.first.click()
            expect(off_switches).to_have_count(remaining - 1)
            remaining -= 1

    with allure.step("3 - Saqlash va natijani tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.wait_for_loader(timeout=600_000)
        base.expect_page(heading="Роли", timeout=600_000)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page):
    authorization(page, who='admin')
    run_role(page)
