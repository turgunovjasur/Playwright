import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Sector")]

# ----------------------------------------------------------------------------------------------------------------------

def run_sector(page, code):
    """Testcase: TMC to'plamini roomga biriktirib yaratish.

    1. Справочники -> ТМЦ ro'yxatini ochish.
    2. Наборы ТМЦ ro'yxatini ochish.
    3. Yangi to'plam formasida kod, nom va room-pw{code} ish zonasini kiritish.
    4. Saqlab, ro'yxatda to'plamning kodi va nomini tekshirish.
    """
    sector_code = f"c_s_pw{code}"
    sector_name = f"sector-pw{code}"
    base = BasePage(page)
    with allure.step("1 - TMC ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")

    with allure.step("2 - TMC to'plamlari ro'yxatini ochish"):
        base.click(name="Наборы ТМЦ", role="link")
        base.expect_page(heading="Наборы ТМЦ")

    with allure.step("3 - Yangi to'plam formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="Набор ТМЦ (создание)")
        base.input(label="Код", value=sector_code)
        base.input(label="Название", value=sector_name)
        base.multiselect(label="Рабочие зоны", value=f"room-pw{code}")

    with allure.step("4 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Наборы ТМЦ")
        base.grid(sector_code, sector_name)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("TMC to'plami (sector) yaratish")
def test_sector(page, code):
    authorization(page, who="user", code=code)
    run_sector(page, code)
