"""HTTP-only setup chain in the same order as the existing UI setup runner."""

import allure
import pytest

from tests.api.setup.test_00_company import run_company
from tests.api.setup.test_01_legal_person import run_legal_person
from tests.api.setup.test_02_filial import run_filial
from tests.api.setup.test_03_room import run_room
from tests.api.setup.test_04_robot import run_robot
from tests.api.setup.test_05_natural_person import run_natural_person
from tests.api.setup.test_06_user import run_user
from tests.api.setup.test_07_user_attach_form import run_user_attach_form
from tests.api.setup.test_08_role import run_role
from tests.api.setup.test_09_role_attach_form import run_role_attach_form
from tests.api.setup.test_10_buy_license import run_buy_license
from tests.api.setup.test_11_attach_license import run_attach_license
from tests.api.setup.test_12_change_password import run_change_password
from tests.api.setup.test_13_price_type_uzb import run_price_type_uzb
from tests.api.setup.test_14_price_type_usa import run_price_type_usa
from tests.api.setup.test_15_currency import run_currency
from tests.api.setup.test_16_payment_type import run_payment_type
from tests.api.setup.test_17_sector import run_sector
from tests.api.setup.test_18_product import run_product
from tests.api.setup.test_19_product_usa import run_product_usa
from tests.api.setup.test_20_natural_person_for_client_1 import run_natural_person_for_client_1
from tests.api.setup.test_21_room_attachment import run_room_attachment
from tests.api.setup.test_22_warehouse import run_warehouse
from tests.api.setup.test_23_init_balance import run_init_balance
from tests.api.setup.test_24_balance import run_balance
from tests.api.setup.test_25_quantity_discount import run_quantity_discount
from tests.api.setup.test_26_quantity_bonus import run_quantity_bonus
from tests.api.setup.test_27_amount_discount import run_amount_discount
from tests.api.setup.test_28_amount_bonus import run_amount_bonus
from tests.api.setup.test_29_cyclic_bonus import run_cyclic_bonus

pytestmark = [pytest.mark.api_setup, allure.epic("API"), allure.feature("Setup"), allure.story("Setup Chain")]


@allure.title("API 00 - Company")
def test_00_company(api_setup):
    run_company(api_setup)


@allure.title("API 01 - Legal Person")
def test_01_legal_person(api_setup):
    run_legal_person(api_setup)


@allure.title("API 02 - Filial")
def test_02_filial(api_setup):
    run_filial(api_setup)


@allure.title("API 03 - Room")
def test_03_room(api_setup):
    run_room(api_setup)


@allure.title("API 04 - Robot")
def test_04_robot(api_setup):
    run_robot(api_setup)


@allure.title("API 05 - Natural Person")
def test_05_natural_person(api_setup):
    run_natural_person(api_setup)


@allure.title("API 06 - User")
def test_06_user(api_setup):
    run_user(api_setup)


@allure.title("API 07 - User Attach Form")
def test_07_user_attach_form(api_setup):
    run_user_attach_form(api_setup)


@allure.title("API 08 - Role")
def test_08_role(api_setup):
    run_role(api_setup)


@allure.title("API 09 - Role Attach Form")
def test_09_role_attach_form(api_setup):
    run_role_attach_form(api_setup)


@allure.title("API 10 - Buy License")
def test_10_buy_license(api_setup):
    run_buy_license(api_setup)


@allure.title("API 11 - Attach License")
def test_11_attach_license(api_setup):
    run_attach_license(api_setup)


@allure.title("API 12 - Change Password")
def test_12_change_password(api_setup):
    run_change_password(api_setup)


@allure.title("API 13 - Price Type UZB")
def test_13_price_type_uzb(api_setup):
    run_price_type_uzb(api_setup)


@allure.title("API 14 - Price Type USA")
def test_14_price_type_usa(api_setup):
    run_price_type_usa(api_setup)


@allure.title("API 15 - Currency")
def test_15_currency(api_setup):
    run_currency(api_setup)


@allure.title("API 16 - Payment Type")
def test_16_payment_type(api_setup):
    run_payment_type(api_setup)


@allure.title("API 17 - Sector")
def test_17_sector(api_setup):
    run_sector(api_setup)


@allure.title("API 18 - Product UZS")
def test_18_product(api_setup):
    run_product(api_setup)


@allure.title("API 19 - Product USD")
def test_19_product_usa(api_setup):
    run_product_usa(api_setup)


@allure.title("API 20 - Natural Person For Client")
def test_20_natural_person_for_client_1(api_setup):
    run_natural_person_for_client_1(api_setup)


@allure.title("API 21 - Room Attachment")
def test_21_room_attachment(api_setup):
    run_room_attachment(api_setup)


@allure.title("API 22 - Warehouse")
def test_22_warehouse(api_setup):
    run_warehouse(api_setup)


@allure.title("API 23 - Init Balance")
def test_23_init_balance(api_setup):
    run_init_balance(api_setup)


@allure.title("API 24 - Balance")
def test_24_balance(api_setup):
    run_balance(api_setup)


@allure.title("API 25 - Quantity Discount")
def test_25_quantity_discount(api_setup):
    run_quantity_discount(api_setup)


@allure.title("API 26 - Quantity Bonus")
def test_26_quantity_bonus(api_setup):
    run_quantity_bonus(api_setup)


@allure.title("API 27 - Amount Discount")
def test_27_amount_discount(api_setup):
    run_amount_discount(api_setup)


@allure.title("API 28 - Amount Bonus")
def test_28_amount_bonus(api_setup):
    run_amount_bonus(api_setup)


@allure.title("API 29 - Cyclic Bonus")
def test_29_cyclic_bonus(api_setup):
    run_cyclic_bonus(api_setup)
