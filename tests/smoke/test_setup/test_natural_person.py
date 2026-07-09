import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

def create_natural_person(page, full_name, person_code, *, client=False):
    """Физические лица ro'yxatidan yangi jismoniy shaxs yaratib saqlaydi.

    Qayta ishlatiladi (masalan legal person regressioni director uchun chaqirishi mumkin).
    `page` to'g'ri filialda login qilingan deb keladi. `client=True` bo'lsa "Клиент" yoqiladi.
    """
    base = BasePage(page)
    base.navigate_to(tab="Справочники", name="Физические лица")
    base.expect_page(heading="Физические лица")
    page.get_by_role("button", name="Создать").click()

    base.expect_page(heading="Физическое лицо (создание)")
    base.input(ng_model="d.first_name", value=full_name)
    base.input(label="Код", value=person_code)
    if client:
        base.checkbox(label="Клиент", checked=True)
        base.checkbox(label="Клиент", expect_checked=True)
    base.checkbox(label="Статус", expect_checked=True)
    base.save_and_expect_heading("Физические лица", confirm_text="")

# ----------------------------------------------------------------------------------------------------------------------

def assert_natural_person_view(page, full_name):
    """Ro'yxatdan shaxsni ochib (Просмотр), view oynasida nom/status tekshirib, yopadi."""
    base = BasePage(page)
    base.grid(full_name, click=True)
    page.get_by_role("button", name="Просмотр", exact=True).click()
    base.expect_page(heading="Физическое лицо (просмотр)")
    base.text(full_name, "Активный")
    page.get_by_role("button", name="Закрыть").first.click()
    base.expect_page(heading="Физические лица")

# ----------------------------------------------------------------------------------------------------------------------

def run_natural_person(page, code):
    """Testcase: xodim uchun jismoniy shaxs (natural person) yaratish.

    1. Физические лица ro'yxatidan yangi shaxs yaratish
       (Имя = natural_person-pw{code}, Код = natural_person_pw{code}) va saqlash.
    2. Ro'yxatda yaratilgan shaxs nomi va "Активный" statusini tekshirish.
    3. View oynasida nom va statusni tekshirib, oynani yopish.

    Setup zanjirida sahifa allaqachon filial-pw{code} da (run_room shu filialga
    o'tgan), shuning uchun bu yerda switch_filial qilinmaydi — standalone debug uchun
    filialga o'tish test_natural_person wrapper'ida bajariladi.
    """
    base = BasePage(page)
    full_name = f"natural_person-pw{code}"
    person_code = f"natural_person_pw{code}"

    with allure.step("1 - Yangi jismoniy shaxs yaratish"):
        create_natural_person(page, full_name, person_code)

    with allure.step("2 - Ro'yxatda yaratilgan shaxsni tekshirish"):
        base.grid_controller(search=person_code)
        base.grid(full_name, "Активный")

    with allure.step("3 - View oynasida tekshirish"):
        assert_natural_person_view(page, full_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim uchun jismoniy shaxs yaratish")
def test_natural_person(page, code):
    base = BasePage(page)
    authorization(page, who='admin')
    base.switch_filial(name=f"filial-pw{code}")
    run_natural_person(page, code)
