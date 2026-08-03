import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.test_00_company import run_company
from tests.smoke.test_setup.test_01_legal_person import run_legal_person
from tests.smoke.test_setup.test_02_filial import run_filial
from tests.smoke.test_setup.test_03_room import run_room
from tests.smoke.test_setup.test_04_robot import run_robot
from tests.smoke.test_setup.test_05_natural_person import run_natural_person
from tests.smoke.test_setup.test_06_user import run_user
from tests.smoke.test_setup.test_07_user_attach_form import run_user_attach_form
from tests.smoke.test_setup.test_08_role import run_role
from tests.smoke.test_setup.test_09_role_attach_form import run_role_attach_form
from tests.smoke.test_setup.test_10_buy_license import run_buy_license
from tests.smoke.test_setup.test_11_attach_license import run_attach_license
from tests.smoke.test_setup.test_12_change_password import run_change_password
from tests.smoke.test_setup.test_13_price_type_uzb import run_price_type_uzb
from tests.smoke.test_setup.test_14_price_type_usa import run_price_type_usa
from tests.smoke.test_setup.test_15_currency import run_currency
from tests.smoke.test_setup.test_16_payment_type import run_payment_type
from tests.smoke.test_setup.test_17_sector import run_sector
from tests.smoke.test_setup.test_18_product import run_product
from tests.smoke.test_setup.test_19_natural_person_for_client_1 import run_natural_person_for_client_1
from tests.smoke.test_setup.test_20_room_attachment import run_room_attachment
from tests.smoke.test_setup.test_21_init_balance import run_init_balance
from tests.smoke.test_setup.test_22_balance import run_balance

pytestmark = [
    pytest.mark.user_setup,
    allure.epic("Smoke"),
    allure.feature("Setup"),
    allure.story("Setup Chain"),
]

# ----------------------------------------------------------------------------------------------------------------------


@allure.title("00 - Company")
def test_00_company(session_page, code, save_data):
    run_company(session_page, code, save_data)


@allure.title("01 - Legal Person")
def test_01_legal_person(session_page, code, save_data):
    run_legal_person(session_page, code, save_data)


@allure.title("02 - Filial")
def test_02_filial(session_page, code, load_data, save_data):
    run_filial(session_page, code, load_data, save_data)


@allure.title("03 - Room")
def test_03_room(session_page, code):
    run_room(session_page, code)


@allure.title("04 - Robot")
def test_04_robot(session_page, code):
    run_robot(session_page, code)


@allure.title("05 - Natural Person")
def test_05_natural_person(session_page, code):
    run_natural_person(session_page, code)


@allure.title("06 - User")
def test_06_user(session_page, code):
    run_user(session_page, code)


@allure.title("07 - User Attach Form")
def test_07_user_attach_form(session_page, code):
    run_user_attach_form(session_page, code)


@allure.title("08 - Role")
def test_08_role(session_page):
    run_role(session_page)


@allure.title("09 - Role Attach Form")
def test_09_role_attach_form(session_page):
    run_role_attach_form(session_page)


@pytest.mark.skip(reason="Buy License setup is disabled")
@allure.title("10 - Buy License")
def test_10_buy_license(session_page, logger):
    run_buy_license(session_page, logger)


@allure.title("11 - Attach License")
def test_11_attach_license(session_page, code, logger):
    run_attach_license(session_page, code, logger)


@allure.title("12 - Change Password")
def test_12_change_password(session_page, code):
    run_change_password(session_page, code)


@allure.title("13 - Price Type UZB")
def test_13_price_type_uzb(session_page, code, logger, save_data):
    run_price_type_uzb(session_page, code, logger, save_data)


@allure.title("14 - Price Type USA")
def test_14_price_type_usa(session_page, code, save_data):
    run_price_type_usa(session_page, code, save_data)


@allure.title("15 - Currency")
def test_15_currency(session_page, logger):
    run_currency(session_page, logger)


@allure.title("16 - Payment Type")
def test_16_payment_type(session_page):
    run_payment_type(session_page)


@allure.title("17 - Sector")
def test_17_sector(session_page, code):
    run_sector(session_page, code)


@allure.title("18 - Product")
def test_18_product(session_page, code):
    run_product(session_page, code)


@allure.title("19 - Natural Person For Client 1")
def test_19_natural_person_for_client_1(session_page, code):
    run_natural_person_for_client_1(session_page, code)


@allure.title("20 - Room Attachment")
def test_20_room_attachment(session_page, code):
    run_room_attachment(session_page, code)


@allure.title("21 - Init Balance")
def test_21_init_balance(session_page, code):
    run_init_balance(session_page, code)


@allure.title("22 - Balance")
def test_22_balance(session_page, code):
    run_balance(session_page, code)

# ----------------------------------------------------------------------------------------------------------------------
