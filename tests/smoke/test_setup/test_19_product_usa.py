import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_product import create_product_with_price
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------


def run_product_usa(page, code):
    """Testcase: USD TMC yaratish va 1 USD narx belgilash.

    1. TMC ro'yxatini ochish.
    2. USD TMC yaratish formasini to'ldirish.
    3. TMCni saqlab, ro'yxatda tekshirish.
    4. View formasida yaratilgan TMCni tekshirish.
    5. View formasini yopish.
    6. Narx belgilash formasini ochish.
    7. 1 USD narxni saqlash va ro'yxatda tekshirish.
    """
    create_product_with_price(
        page,
        product_name=f"product-usa-pw{code}",
        product_code=f"c_p_usa_pw{code}",
        sector_name=f"sector-pw{code}",
        price_type_name=f"Price Type USA-pw{code}",
        price="1",
        price_label="USD",
    )


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("USD mahsulotini yaratish va narx belgilash")
def test_product_usa(page, code):
    authorization(page, who="user", code=code)
    BasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product_usa(page, code)
