import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Robot")]

# ----------------------------------------------------------------------------------------------------------------------

def run_robot(page, code):
    """Testcase: yangi xodim (robot) yaratish.

    1. Справочники -> Штат ro'yxatini ochish.
    2. "Создать" -> kod (c_rb_pw{code}) va nom (robot-pw{code}) ni kiritish.
    3. ATS rolini "Админ" qilib belgilab, Рабочая зона sifatida room-pw{code} ni
       biriktirish va "Активный" statusini tekshirish.
    4. Saqlab, ro'yxatda xodim nomi va kodi ko'rinishini tekshirish.
    """
    base = BasePage(page)
    robot_name = f"robot-pw{code}"
    robot_code = f"c_rb_pw{code}"
    room_name = f"room-pw{code}"

    with allure.step("1 - Xodimlar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Штат")
        base.expect_page(heading="Штат")

    with allure.step("2 - Yangi xodim formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Штат (создание)")
        base.input(label="Код", value=robot_code)
        base.input(label="Название", value=robot_name)

    with allure.step("3 - ATS roli (Админ) va ish zonasini biriktirish"):
        base.multiselect(label="Роли", value="Админ")
        base.multiselect(label="Рабочие зоны", value=room_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("4 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Штат")
        base.grid(robot_name, robot_code)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim (robot) yaratish")
def test_robot(page, code):
    base = BasePage(page)
    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")
    run_robot(page, code)
