import allure
import re
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

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
        base.grid(f"natural_person-pw{code}", click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="Пользователь (просмотр)")
        base.text(f"natural_person-pw{code}")
        page.get_by_role("link", name=re.compile(r"Формы")).click()

    with allure.step("2 - Формы ulash"):
        page.get_by_role("tab", name="Формы").click()
        page.get_by_role("button", name="Доступные").click()
        base.grid_controller(expand="1000")
        base.grid(checkbox="all")
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni(expected_text="Прикрепить формы в количестве", button_name="да")

    with allure.step("3 - Отчеты ulash"):
        page.get_by_role("tab", name="Отчеты").click()
        base.grid_controller(expand="1000")
        base.grid(checkbox="all")
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni(expected_text="Прикрепить формы в количестве", button_name="да")

    with allure.step("4 - Накладные ulash"):
        page.get_by_role("tab", name="Накладные").click()
        base.wait_for_loader()
        base.grid_controller(expand="500")
        base.grid(checkbox="all")
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni(expected_text="Прикрепить формы в количестве", button_name="да")

    with allure.step("5 - Внешние системы ulash"):
        page.get_by_role("tab", name="Внешние системы").click()
        base.wait_for_loader()
        base.grid_controller(expand="1000")
        base.grid(checkbox="all")
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni(expected_text="Прикрепить формы в количестве", button_name="да")

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
