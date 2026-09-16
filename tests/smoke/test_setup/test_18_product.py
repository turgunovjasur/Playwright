import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_product import create_product_with_price
from utils.data_store import save_data
from utils.auto_base_page import AutoBasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Product")]

# ----------------------------------------------------------------------------------------------------------------------


def run_product(page, code, *, save_product_id=False):
    """Testcase: UZS TMC yaratish, IDni saqlash va 7000 UZS narx belgilash.

    1. TMC ro'yxatini ochish.
    2. UZS TMC yaratish formasini to'ldirish.
    3. TMCni saqlab, ro'yxatda tekshirish.
    4. View formasidan product IDni olish.
    5. View formasini yopish.
    6. Narx belgilash formasini ochish.
    7. 7000 UZS narxni saqlash va ro'yxatda tekshirish.

    save_product_id=True bo'lsa product ID umumiy data-store'ga saqlanadi.
    """
    product_view_url = create_product_with_price(
        page,
        product_name=f"product-pw{code}",
        product_code=f"c_p_pw{code}",
        sector_name=f"sector-pw{code}",
        price_type_name=f"Price Type UZB-pw{code}",
        price="7000",
        price_label="UZS",
    )
    if save_product_id:
        save_data("product_id", query_int_from_url(product_view_url, "product_id"))
# ----------------------------------------------------------------------------------------------------------------------


@allure.title("UZS mahsulotini yaratish va narx belgilash")
def test_product(page, code):
    authorization(page, who="user", code=code)
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_product(page, code, save_product_id=True)
