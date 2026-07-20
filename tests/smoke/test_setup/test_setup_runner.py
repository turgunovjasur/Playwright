import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.test_balance import run_balance
from tests.smoke.test_setup.test_init_balance import run_init_balance
from tests.smoke.test_setup.test_payment_type import run_payment_type
from tests.smoke.test_setup.test_product import run_product
from tests.smoke.test_setup.test_robot import run_robot
from tests.smoke.test_setup.test_company import run_company
from tests.smoke.test_setup.test_filial import run_filial
from tests.smoke.test_setup.test_legal_person import run_legal_person
from tests.smoke.test_setup.test_buy_license import run_buy_license
from tests.smoke.test_setup.test_attach_license import run_attach_license
from tests.smoke.test_setup.test_natural_person import run_natural_person
from tests.smoke.test_setup.test_natural_person_for_client_1 import run_natural_person_for_client_1
from tests.smoke.test_setup.test_price_type import run_price_type_uzb
from tests.smoke.test_setup.test_room import run_room
from tests.smoke.test_setup.test_room_attachment import run_room_attachment
from tests.smoke.test_setup.test_sector import run_sector
from tests.smoke.test_setup.test_user import run_user
from tests.smoke.test_setup.test_user_attach_form import run_user_attach_form
from tests.smoke.test_setup.test_role import run_role
from tests.smoke.test_setup.test_role_attach_form import run_role_attach_form
from tests.smoke.test_setup.test_change_password import run_change_password

pytestmark = [
    pytest.mark.user_setup,
    allure.epic("Smoke"),
    allure.feature("Setup"),
    allure.story("Setup Chain"),
]

# ----------------------------------------------------------------------------------------------------------------------


def run_setup_authorization(session_page, code, save_data, use_created_company=False):
    save_data("code", code)
    if not use_created_company:
        save_data("company_code", None)
    authorization(session_page, who="admin")


@allure.title("00 - Company")
def test_00_company(session_page, code, save_data, company_setup_enabled):
    if not company_setup_enabled:
        pytest.skip("Company setup faqat --create-company flagi bilan ishlaydi")
    run_company(session_page, code, save_data)


@allure.title("01 - Authorization")
def test_01_authorization(session_page, code, save_data, company_setup_enabled):
    run_setup_authorization(
        session_page,
        code,
        save_data,
        use_created_company=company_setup_enabled,
    )


@allure.title("02 - Legal Person")
def test_02_legal_person(session_page, code, save_data):
    run_legal_person(session_page, code, save_data)


@allure.title("03 - Filial")
def test_03_filial(session_page, code, load_data, save_data):
    run_filial(
        session_page,
        code,
        legal_person_code=load_data("legal_person_code"),
        legal_person_name=load_data("legal_person_name"),
        save_data=save_data,
    )


@allure.title("04 - Room")
def test_04_room(session_page, code):
    run_room(session_page, code)


@allure.title("05 - Robot")
def test_05_robot(session_page, code):
    run_robot(session_page, code)


@allure.title("06 - Natural Person")
def test_06_natural_person(session_page, code):
    run_natural_person(session_page, code)


@allure.title("07 - User")
def test_07_user(session_page, code):
    run_user(session_page, code)


@allure.title("08 - User Attach Form")
def test_08_user_attach_form(session_page, code):
    run_user_attach_form(session_page, code)


@allure.title("09 - Role")
def test_09_role(session_page):
    run_role(session_page)


@allure.title("10 - Role Attach Form")
def test_10_role_attach_form(session_page):
    run_role_attach_form(session_page)


@allure.title("11 - Buy License")
def test_11_buy_license(session_page, logger):
    run_buy_license(session_page, logger)


@allure.title("12 - Attach License")
def test_12_attach_license(session_page, code, logger):
    run_attach_license(session_page, code, logger)


@allure.title("13 - Change Password")
def test_13_change_password(session_page, code):
    run_change_password(session_page, code)


@allure.title("14 - Price Type")
def test_14_price_type(session_page, code, logger, save_data):
    run_price_type_uzb(session_page, code, logger, save_data=save_data)


@allure.title("15 - Payment Type")
def test_15_payment_type(session_page):
    run_payment_type(session_page)


@allure.title("16 - Sector")
def test_16_sector(session_page, code):
    run_sector(session_page, code)


@allure.title("17 - Product")
def test_17_product(session_page, code):
    run_product(session_page, code)


@allure.title("18 - Natural Person For Client 1")
def test_18_natural_person_for_client_1(session_page, code):
    run_natural_person_for_client_1(session_page, code)


@allure.title("19 - Room Attachment")
def test_19_room_attachment(session_page, code):
    run_room_attachment(session_page, code)


@allure.title("20 - Init Balance")
def test_20_init_balance(session_page, code):
    run_init_balance(session_page, code)


@allure.title("21 - Balance")
def test_21_balance(session_page, code):
    run_balance(session_page, code)

# ----------------------------------------------------------------------------------------------------------------------
