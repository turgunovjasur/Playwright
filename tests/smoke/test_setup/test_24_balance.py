import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def run_balance(page, code):
    """UZS va USD setup mahsulotlari uchun ombor qoldig'ini tekshirish.

    1. Склад -> Остатки ТМЦ sahifasini ochish.
    2. `product-pw{code}` qoldig'ini tekshirish.
    3. `product-usa-pw{code}` qoldig'ini tekshirish.
    """
    base = BasePage(page)
    with allure.step("1 - TMC qoldiqlar sahifasiga o'tish"):
        base.navigate_to(tab="Склад", name="Остатки ТМЦ")
        base.expect_page(heading="Остатки ТМЦ", url="balance_list")

    with allure.step("2 - UZS mahsuloti qoldig'ini ro'yxatda tekshirish"):
        base.grid(f"c_p_pw{code}", f"product-pw{code}")

    with allure.step("3 - USD mahsuloti qoldig'ini ro'yxatda tekshirish"):
        base.grid(f"c_p_usa_pw{code}", f"product-usa-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("TMC qoldiqlarini tekshirish")
def test_balance(page, code):
    authorization(page, who="user", code=code)
    run_balance(page, code)
