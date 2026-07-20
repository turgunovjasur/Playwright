import allure
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def run_balance(page, code):
    base = BasePage(page)
    with allure.step("1 - TMC qoldiqlar sahifasiga o'tish"):
        base.navigate_to(tab="Склад", name="Остатки ТМЦ")
        base.expect_page(heading="Остатки ТМЦ", url="balance_list")

    with allure.step("2 - Mahsulot qoldig'i ro'yxatda ko'rinishini tekshirish"):
        base.grid(f"c_p_pw{code}", f"product-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("TMC qoldiqlarini tekshirish")
def test_balance(page, code):
    run_balance(page, code)
