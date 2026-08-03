import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_natural_person import (
    close_natural_person_view,
    create_natural_person,
    open_natural_person_create,
    open_natural_person_list,
    open_natural_person_view,
)
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def run_natural_person_for_client_1(page, code):
    """Testcase: mijoz uchun jismoniy shaxs (natural client) yaratish.

    1. Физические лица ro'yxatini ochish.
    2. Yangi jismoniy shaxs yaratish formasini ochish.
    3. "Клиент" belgisi, Код = c_n_c_pw{code} va Имя = natural_client-pw{code} ni kiritib saqlash.
    4. Ro'yxatda nom va statusni tekshirish.
    5. View formasini ochish.
    6. View formasida nom va statusni tekshirish.
    7. View formasini yopib, Физические лица ro'yxatiga qaytish.
    8. Клиенты ro'yxatida mijoz ko'rinishini tekshirish.
    """
    base = BasePage(page)
    person_code = f"c_n_c_pw{code}"
    person_name = f"natural_client-pw{code}"

    open_natural_person_list(page, step_name="1 - Jismoniy shaxslar ro'yxatini ochish")
    open_natural_person_create(page, step_name="2 - Yangi jismoniy shaxs formasini ochish")
    create_natural_person(page, person_name, person_code, step_name="3 - 'Клиент' belgili jismoniy shaxsni saqlash", client=True)

    with allure.step("4 - Ro'yxatda yaratilgan mijozni tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(person_name, "Активный")

    open_natural_person_view(page, person_name, step_name="5 - Jismoniy shaxs view formasini ochish")

    with allure.step("6 - View formasida nom va statusni tekshirish"):
        base.text(person_name, "Активный")

    close_natural_person_view(page, step_name="7 - View formasini yopib, ro'yxatga qaytish")

    with allure.step("8 - Mijozlar ro'yxatida ko'rinishini tekshirish"):
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
