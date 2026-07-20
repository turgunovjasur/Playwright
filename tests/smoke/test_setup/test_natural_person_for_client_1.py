import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_natural_person import (
    check_natural_person_view,
    create_natural_person,
)
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def run_natural_person_for_client_1(page, code):
    """Testcase: mijoz uchun jismoniy shaxs (natural client) yaratish.

    1. Физические лица ro'yxatidan "Клиент" belgili yangi shaxs yaratish
       (Код = c_n_c_pw{code}, Имя = natural_client-pw{code}) va saqlash.
    2. Ro'yxat va view oynasida nom/status tekshirish.
    3. Клиенты ro'yxatida ham ko'rinishini tekshirish.
    """
    base = BasePage(page)
    person_code = f"c_n_c_pw{code}"
    person_name = f"natural_client-pw{code}"

    with allure.step("1 - 'Клиент' belgili yangi jismoniy shaxs yaratish"):
        create_natural_person(page, person_name, person_code, client=True)

    with allure.step("2 - Ro'yxat va view oynasida tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(person_name, "Активный")
        check_natural_person_view(page, person_name)

    with allure.step("3 - Mijozlar ro'yxatida ko'rinishini tekshirish"):
        base.navigate_to(tab="Справочники", name="Клиенты")
        base.expect_page(heading="Клиенты")
        base.grid_controller(search=person_name)
        base.grid(person_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Mijoz uchun jismoniy shaxs yaratish")
def test_natural_person_for_client_1(page, code):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_natural_person_for_client_1(page, code)
