import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]
ROLE_FORMS_LOADER_TIMEOUT = 600_000

# ----------------------------------------------------------------------------------------------------------------------

def run_role_attach_form(page):
    """Testcase: Admin roliga barcha formalarga ruxsat berish.

    1. Пользователи ro'yxatini ochish.
    2. Роли ro'yxatini ochish.
    3. "Админ" rolining view formasini ochish.
    4. Формы ruxsatlari sahifasini ochish.
    5. "Доступ ко всем формам" -> "Разрешить" bilan barcha formalarga ruxsat berish.
    6. "Доступные" ro'yxati bo'shligini tekshirish.
    7. Sahifani yopib, Роли ro'yxatiga qaytish.
    """
    base = BasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")

    with allure.step("2 - Rollar ro'yxatini ochish"):
        base.click(name="Роли", role="link")
        base.expect_page(heading="Роли")

    with allure.step("3 - Admin rolining view formasini ochish"):
        base.grid("Админ", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Роль (Просмотр)")

    with allure.step("4 - Admin rolining formalar ruxsatini ochish"):
        base.click(name="Формы", role="link")
        base.text("Доступ ко всем формам")

    with allure.step("5 - Barcha formalarga ruxsat berish"):
        base.click(name="Доступ ко всем формам")
        base.click(name="Разрешить", role="link")
        base.confirm_biruni(expected_text="Разрешить доступ ко всем формам?")
        base.wait_for_loader(timeout=ROLE_FORMS_LOADER_TIMEOUT)
        base.expect_page(heading="Роль (Просмотр)")

    with allure.step("6 - Ruxsatlar berilganini tekshirish"):
        base.click(name="Доступные")
        base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("7 - Sahifani yopib, rollar ro'yxatiga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Роли")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin roliga barcha formalarga ruxsat berish")
def test_role_attach_form(page):
    authorization(page, who="admin")
    run_role_attach_form(page)
