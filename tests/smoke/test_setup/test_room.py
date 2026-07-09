import allure
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def run_room(page, code):
    """Testcase: yangi ish zonasi (room) yaratish.

    1. filial-pw{code} ga o'tib, Справочники -> Рабочие зоны ro'yxatini ochish.
    2. "Создать" -> code (code_room_pw{code}) va nom (room-pw{code}) ni kiritish.
    3. Saqlab, ro'yxatda room nomi va kodi ko'rinishini tekshirish.
    """
    base = BasePage(page)
    room_name = f"room-pw{code}"
    room_code = f"code_room_pw{code}"

    with allure.step("1 - Ish zonalari ro'yxatiga o'tish"):
        base.switch_filial(name=f"filial-pw{code}")
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны")

    with allure.step("2 - Yangi ish zonasi formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Рабочая зона (создание)")
        base.input(label="Код", value=room_code)
        base.input(label="Название", value=room_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.expect_page(heading="Рабочие зоны")
        base.grid(room_name, room_code)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasi yaratish")
def test_room(page, code):
    authorization(page, who='admin')
    run_room(page, code)
