import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.test_natural_person import create_natural_person, assert_natural_person_view
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def run_natural_person_for_client_1(page, code):
    """Testcase: mijoz uchun jismoniy shaxs (natural client) yaratish.

    1. Физические лица ro'yxatidan "Клиент" belgili yangi shaxs yaratish
       (Имя = natural_client-pw{code}, Код = natural_client_pw{code}) va saqlash.
    2. Ro'yxat va view oynasida nom/status tekshirish.
    3. Клиенты ro'yxatida ham ko'rinishini tekshirish.
    """
    base = BasePage(page)
    full_name = f"natural_client-pw{code}"
    person_code = f"natural_client_pw{code}"

    with allure.step("1 - 'Клиент' belgili yangi jismoniy shaxs yaratish"):
        create_natural_person(page, full_name, person_code, client=True)

    with allure.step("2 - Ro'yxat va view oynasida tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(full_name, "Активный")
        assert_natural_person_view(page, full_name)

    with allure.step("3 - Mijozlar ro'yxatida ko'rinishini tekshirish"):
        base.navigate_to(tab="Справочники", name="Клиенты")
        base.expect_page(heading="Клиенты")
        base.grid_controller(search=full_name)
        base.grid(full_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Mijoz uchun jismoniy shaxs yaratish")
def test_natural_person_for_client_1(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_natural_person_for_client_1(page, code)
