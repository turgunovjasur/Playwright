import allure
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def run_room(page, code, save_data):
    """Testcase: yangi ish zonasi (room) yaratish.

    1. filial-pw{code} ga o'tib, Справочники -> Рабочие зоны ro'yxatini ochish.
    2. "Создать" -> code (c_rm_pw{code}) va nom (room-pw{code}) ni kiritish.
    3. Saqlab, ro'yxatda room nomi va kodi ko'rinishini tekshirish.
    4. View formasini ochib, room IDni data_store ga saqlash.
    5. View formasini yopib, ro'yxatga qaytish.
    """
    base = BasePage(page)
    room_name = f"room-pw{code}"
    room_code = f"c_rm_pw{code}"

    with allure.step("1 - Ish zonalari ro'yxatiga o'tish"):
        base.switch_filial(name=f"filial-pw{code}")
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны")

    with allure.step("2 - Yangi ish zonasi formasini to'ldirish"):
        base.click(name="Создать")
        base.wait_for_loader()
        base.expect_page(heading="Рабочая зона (создание)")
        base.input(label="Код", value=room_code)
        base.input(label="Название", value=room_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Рабочие зоны")
        base.grid(room_name, room_code)

    with allure.step("4 - View formasidan room IDni olish va saqlash"):
        base.grid(room_name, room_code, click=True)
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="Рабочая зона (просмотр)", url="room_view?room_id=")
        base.text(room_name, room_code, "Активный")
        save_data("room_id", query_int_from_url(page.url, "room_id"))

    with allure.step("5 - View formasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Рабочие зоны", url="room_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasi yaratish")
def test_room(page, code, save_data):
    authorization(page, who="admin")
    run_room(page, code, save_data)
