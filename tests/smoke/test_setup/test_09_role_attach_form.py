from urllib.parse import unquote, urlsplit

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages import UI_TIMEOUT_MS
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]
ROLE_FORMS_LOADER_TIMEOUT = UI_TIMEOUT_MS

# ----------------------------------------------------------------------------------------------------------------------

def run_role_attach_form(page):
    """Testcase: Admin roliga barcha formalarga ruxsat berish.

    1. Пользователи ro'yxatini ochish.
    2. Роли ro'yxatini ochish.
    3. "Админ" rolining view formasini ochish.
    4. Формы ruxsatlari sahifasini ochish.
    5. "Доступ ко всем формам" -> "Разрешить" bilan ruxsat berib, server javobini kutish.
    6. "Доступные" ro'yxati bo'shligini tekshirish.
    7. Sahifani yopib, Роли ro'yxatiga qaytish.
    """
    base = AutoBasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи", url="anor/mr/user_list")

    with allure.step("2 - Rollar ro'yxatini ochish"):
        base.click(name="Роли", role="link")
        base.expect_page(heading="Роли", url="trade/tr/role_list")

    with allure.step("3 - Admin rolining view formasini ochish"):
        role_name = page.locator("main").get_by_text("Админ", exact=True).filter(visible=True)
        view_button = page.get_by_role("button", name="Просмотреть", exact=True)
        list_url = page.url
        for attempt in range(2):
            role_name.click()
            try:
                view_button.click(timeout=5_000)
            except PlaywrightTimeoutError:
                if attempt or page.url != list_url or view_button.is_visible():
                    raise
                # A grid redraw can dismiss the row actions before the click.
                continue
            break
        base.expect_page(heading="Роль (Просмотр)", url="role_view")
        base.text("Админ", include_input_values=True)

    with allure.step("4 - Admin rolining formalar ruxsatini ochish"):
        base.tab("Формы", section=True)
        base.text("Доступ ко всем формам")

    with allure.step("5 - Barcha formalarga ruxsat berish"):
        base.click(name="Доступ ко всем формам")
        base.click(locator=page.get_by_text("Разрешить", exact=True))
        # A2 closes the confirmation before the grant finishes. Switching the
        # table now lets the pending attached-forms reload overwrite Available.
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(unquote(response.url)).path.endswith(
                "/biruni/md/role_form_list$access_generate_all"
            ),
            timeout=ROLE_FORMS_LOADER_TIMEOUT,
        ) as grant_response:
            base.confirm_biruni(expected_text="Разрешить доступ ко всем формам?")
        response = grant_response.value
        response.finished()
        if not response.ok:
            raise AssertionError(f"Barcha formalarga ruxsat berish: HTTP {response.status}")
        base.wait_for_loader(timeout=ROLE_FORMS_LOADER_TIMEOUT)
        base.expect_page(heading="Роль (Просмотр)")  # navigation: same-url - Granting permissions updates the already-open role view.

    with allure.step("6 - Ruxsatlar berilganini tekshirish"):
        base.tab("Доступные")
        base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("7 - Sahifani yopib, rollar ro'yxatiga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Роли", url="trade/tr/role_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin roliga barcha formalarga ruxsat berish")
def test_role_attach_form(page):
    authorization(page, who="admin")
    run_role_attach_form(page)
