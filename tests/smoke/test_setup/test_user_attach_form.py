import allure
import re
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def _attach_available_permissions(page, base):
    page_size = page.locator("button").filter(has_text=re.compile(r"\b50\s*/")).first
    if page_size.count() > 0 and page_size.is_visible():
        page_size.click()
        option = page.get_by_role("link", name="1000").first
        expect(option).to_be_visible()
        option.click()
        base.wait_for_loader()

    try:
        expect(page.locator("b-page")).to_contain_text("нет данных", timeout=1_000)
        return
    except (AssertionError, PlaywrightTimeoutError):
        pass

    base.checkbox(first_visible=True, checked=True)
    base.wait_for_loader()
    page.get_by_role("button", name="Прикрепить").click()
    expect(
        page.get_by_role("heading", name="Прикрепить формы в количестве", exact=False)
    ).to_be_visible()
    base.confirm_biruni()
    base.wait_for_loader()
    expect(page.locator("b-page")).to_contain_text("нет данных")

# ----------------------------------------------------------------------------------------------------------------------

def run_user_attach_form(page, code):
    """Testcase: foydalanuvchiga forma, hisobot, nakladnaya va tashqi tizim ruxsatlarini ulash.

    1. Пользователи ro'yxatidan natural_person-pw{code} userini topib, Формы sahifasini ochish.
    2. Формы tab: barcha mavjud formalarni ulash.
    3. Отчеты tab: barcha mavjud hisobotlarni ulash.
    4. Накладные tab: barcha mavjud nakladnaylarni ulash.
    5. Внешние системы tab: barcha mavjud tashqi tizimlarni ulash.
    6. Sahifani yopib, Пользователи ro'yxatiga qaytishni tekshirish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da; standalone debug uchun filialga
    o'tish test_user_attach_form wrapper'ida bajariladi.
    """
    base = BasePage(page)

    with allure.step("1 - Foydalanuvchi sahifasini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")
        base.grid_controller(search=f"natural_person-pw{code}")
        base.grid(f"natural_person-pw{code}", click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="Пользователь (просмотр)")
        base.text(f"natural_person-pw{code}")
        page.get_by_role("link", name=" Формы").click()

    with allure.step("2 - Формы ulash"):
        page.get_by_role("tab", name="Формы").click()
        page.get_by_role("button", name="Доступные").click()
        _attach_available_permissions(page, base)

    with allure.step("3 - Отчеты ulash"):
        page.get_by_role("tab", name="Отчеты").click()
        _attach_available_permissions(page, base)

    with allure.step("4 - Накладные ulash"):
        page.get_by_role("tab", name="Накладные").click()
        base.wait_for_loader()
        _attach_available_permissions(page, base)

    with allure.step("5 - Внешние системы ulash"):
        page.get_by_role("tab", name="Внешние системы").click()
        base.wait_for_loader()
        _attach_available_permissions(page, base)

    with allure.step("6 - Foydalanuvchilar ro'yxatiga qaytish"):
        page.get_by_role("button", name="Закрыть").click()
        base.expect_page(heading="Пользователи")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga formalar ulash")
def test_user_attach_form(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_user_attach_form(page, code)
