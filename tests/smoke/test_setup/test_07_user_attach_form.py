import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

# ----------------------------------------------------------------------------------------------------------------------

def _attach_available_permissions(base, *, expand):
    """Joriy tabdagi barcha available permissionlarni biriktiradi va natijani tekshiradi."""
    base.click(name="Доступные")
    base.wait_for_loader()
    base.grid_controller(expand=expand)
    base.grid(checkbox="all")
    base.click(name="Прикрепить")
    base.confirm_biruni(expected_text="Прикрепить формы в количестве", button_name="да")
    base.wait_for_loader()
    base.grid(state="empty")

# ----------------------------------------------------------------------------------------------------------------------

def run_user_attach_form(page, code):
    """Testcase: foydalanuvchiga forma, hisobot, nakladnaya va tashqi tizim ruxsatlarini ulash.

    1. Пользователи ro'yxatini ochish.
    2. natural_person-pw{code} foydalanuvchisining view sahifasini ochish.
    3. Foydalanuvchining Формы ruxsatlari sahifasini ochish.
    4. Формы tab: barcha mavjud formalarni ulash.
    5. Отчеты tab: barcha mavjud hisobotlarni ulash.
    6. Накладные tab: barcha mavjud nakladnaylarni ulash.
    7. Внешние системы tab: barcha mavjud tashqi tizimlarni ulash.
    8. Sahifani yopib, Пользователи ro'yxatiga qaytishni tekshirish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da; standalone debug uchun filialga
    o'tish test_user_attach_form wrapper'ida bajariladi.
    """
    base = BasePage(page)

    with allure.step("1 - Foydalanuvchilar ro'yxatini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи")

    with allure.step("2 - Foydalanuvchi view sahifasini ochish"):
        base.grid(f"natural_person-pw{code}", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Пользователь (просмотр)")
        base.text(f"natural_person-pw{code}")

    with allure.step("3 - Foydalanuvchining Формы ruxsatlari sahifasini ochish"):
        base.click(name="Формы", role="link")
        base.expect_page(heading="Пользователь (просмотр)")
        base.wait_for_loader()

    with allure.step("4 - Формы ulash"):
        base.click(name="Формы", role="tab")
        _attach_available_permissions(base, expand="1000")

    with allure.step("5 - Отчеты ulash"):
        base.click(name="Отчеты", role="tab")
        base.wait_for_loader()
        _attach_available_permissions(base, expand="1000")

    with allure.step("6 - Накладные ulash"):
        base.click(name="Накладные", role="tab")
        base.wait_for_loader()
        _attach_available_permissions(base, expand="500")

    with allure.step("7 - Внешние системы ulash"):
        base.click(name="Внешние системы", role="tab")
        base.wait_for_loader()
        _attach_available_permissions(base, expand="1000")

    with allure.step("8 - Foydalanuvchilar ro'yxatiga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Пользователи")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga formalar ulash")
def test_user_attach_form(page, code):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_user_attach_form(page, code)
