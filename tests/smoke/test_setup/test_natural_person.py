import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_natural_person import (
    check_natural_person_view,
    create_natural_person,
)
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def run_natural_person(page, code):
    """Testcase: xodim uchun jismoniy shaxs (natural person) yaratish.

    1. Физические лица ro'yxatidan yangi shaxs yaratish
       (Код = c_n_p_pw{code}, Имя = natural_person-pw{code}) va saqlash.
    2. Ro'yxatda yaratilgan shaxs nomi va "Активный" statusini tekshirish.
    3. View oynasida nom va statusni tekshirib, oynani yopish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da (run_room shu filialga
    o'tgan), shuning uchun bu yerda switch_filial qilinmaydi — standalone debug uchun
    filialga o'tish test_natural_person wrapper'ida bajariladi.
    """
    base = BasePage(page)
    person_code = f"c_n_p_pw{code}"
    person_name = f"natural_person-pw{code}"

    with allure.step("1 - Yangi jismoniy shaxs yaratish"):
        create_natural_person(page, person_name, person_code)

    with allure.step("2 - Ro'yxatda yaratilgan shaxsni tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(person_name, "Активный")

    with allure.step("3 - View oynasida tekshirish"):
        check_natural_person_view(page, person_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim uchun jismoniy shaxs yaratish")
def test_natural_person(page, code):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_natural_person(page, code)
