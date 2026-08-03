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

def run_natural_person(page, code):
    """Testcase: xodim uchun jismoniy shaxs (natural person) yaratish.

    1. Физические лица ro'yxatini ochish.
    2. Yangi jismoniy shaxs yaratish formasini ochish.
    3. Код = c_n_p_pw{code}, Имя = natural_person-pw{code} ni kiritib saqlash.
    4. Ro'yxatda yaratilgan shaxs nomi va "Активный" statusini tekshirish.
    5. View formasini ochish.
    6. View formasida nom va statusni tekshirish.
    7. View formasini yopib, ro'yxatga qaytish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da (run_room shu filialga
    o'tgan), shuning uchun bu yerda switch_filial qilinmaydi — standalone debug uchun
    filialga o'tish test_natural_person wrapper'ida bajariladi.
    """
    base = BasePage(page)
    person_code = f"c_n_p_pw{code}"
    person_name = f"natural_person-pw{code}"

    open_natural_person_list(page, step_name="1 - Jismoniy shaxslar ro'yxatini ochish")
    open_natural_person_create(page, step_name="2 - Yangi jismoniy shaxs formasini ochish")
    create_natural_person(page, person_name, person_code, step_name="3 - Jismoniy shaxs ma'lumotlarini kiritib saqlash")

    with allure.step("4 - Ro'yxatda yaratilgan shaxsni tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(person_name, "Активный")

    open_natural_person_view(page, person_name, step_name="5 - Jismoniy shaxs view formasini ochish")

    with allure.step("6 - View formasida nom va statusni tekshirish"):
        base.text(person_name, "Активный")

    close_natural_person_view(page, step_name="7 - View formasini yopib, ro'yxatga qaytish")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim uchun jismoniy shaxs yaratish")
def test_natural_person(page, code):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_natural_person(page, code)
