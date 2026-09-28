import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def _enable_legacy_off_switches(page):
    """Legacy `label.switch` + `<t>нет</t>` (anor `/anor/mr/role+edit`)."""
    for text in ("нет", "no"):
        off_switches = page.locator(f'label.switch:has(t:text-is("{text}"))')
        remaining = off_switches.count()
        while remaining > 0:
            off_switches.first.click()
            expect(off_switches).to_have_count(remaining - 1)
            remaining -= 1


def _enable_angular_off_function_switches(page):
    """Kernel `smt-switch` function rows (`нет`/`no`), not A/P state (active/passive)."""
    for no_text in ("нет", "no"):
        while True:
            labels = page.get_by_text(no_text, exact=True)
            if labels.count() == 0:
                break
            row = labels.first.locator("xpath=ancestor::*[.//*[@role='switch']][1]")
            switch = row.get_by_role("switch")
            if switch.count() == 0:
                break
            if (switch.first.get_attribute("aria-checked") or "").lower() == "true":
                break
            before = labels.count()
            switch.first.click()
            expect(labels).to_have_count(before - 1)


def run_role(page):
    """Testcase: Admin roliga barcha ruxsatlarni (switchlarni) yoqish.

    1. Пользователи ro'yxatini ochish.
    2. Роли ro'yxatini ochish.
    3. "Админ" rolining edit formasini ochish.
    4. Barcha "нет" switchlarini ketma-ket yoqish.
    5. Saqlab, Роли ro'yxatiga qaytishni tekshirish.

    `mr_role_functions` (Order = function_id 1) Query_Role_Function_Robots uchun
    session filial + project_code bo'yicha yoziladi — operational filialda ochish.
    """
    base = AutoBasePage(page)
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
        _enable_legacy_off_switches(page)
        _enable_angular_off_function_switches(page)

    with allure.step("5 - Rolni saqlab, ro'yxatga qaytish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Роли", url="role_list", timeout=300_000)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page, code):
    authorization(page, who="admin")
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_role(page)
