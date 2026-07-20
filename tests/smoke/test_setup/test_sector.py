import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Sector")]

# ----------------------------------------------------------------------------------------------------------------------

def run_sector(page, code):
    """Testcase: TMC to'plamini roomga biriktirib yaratish.

    1. Справочники -> ТМЦ -> Наборы ТМЦ ro'yxatini ochish.
    2. Kod va nomni kiritib, room-pw{code} ish zonasini tanlash.
    3. Saqlab, ro'yxatda to'plamning kodi va nomini tekshirish.
    """
    sector_code = f"c_s_pw{code}"
    sector_name = f"sector-pw{code}"
    base = BasePage(page)
    with allure.step("1 - TMC to'plamlari ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")
        page.get_by_role("link", name="Наборы ТМЦ").click()
        base.expect_page(heading="Наборы ТМЦ")

    with allure.step("2 - Yangi to'plam formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Набор ТМЦ (создание)")
        base.input(label="Код", value=sector_code)
        base.input(label="Название", value=sector_name)
        base.multiselect(label="Рабочие зоны", value=f"room-pw{code}")

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.save_and_expect_heading("Наборы ТМЦ")
        base.grid(sector_code, sector_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("TMC to'plami (sector) yaratish")
def test_sector(page, code):
    authorization(page, who="user", code=code)
    run_sector(page, code)
