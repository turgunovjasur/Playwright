import allure
from playwright.sync_api import Page

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.test_payment_type import test_payment_type as run_payment_type
from tests.smoke.test_setup.test_product import test_product as run_product
from tests.smoke.test_setup.test_robot import test_robot as run_robot
from tests.smoke.test_setup.test_filial import test_filial as run_filial
from tests.smoke.test_setup.test_legal_person import test_legal_person as run_legal_person
from tests.smoke.test_setup.test_license import test_attach_license as run_attach_license, test_buy_license as run_buy_license
from tests.smoke.test_setup.test_natural_person import test_natural_person as run_natural_person
from tests.smoke.test_setup.test_price_type import test_price_type_uzb as run_price_type_uzb
from tests.smoke.test_setup.test_room import test_room as run_room
from tests.smoke.test_setup.test_sector import test_sector as run_sector
from tests.smoke.test_setup.test_user import (
    test_user as run_user,
    test_user_attach_form as run_user_attach_form,
    test_role as run_role,
    test_role_attach_form as run_role_attach_form,
    test_change_password as run_change_password,
)

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Full Smoke Run")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("01 - Authorization")
def test_01_authorization(session_page: Page, code, save_data):
    save_data("code", code)
    authorization(session_page)

@allure.title("02 - Legal Person")
def test_02_legal_person(session_page: Page, code):
    run_legal_person(session_page, code)

@allure.title("03 - Filial")
def test_03_filial(session_page: Page, code):
    run_filial(session_page, code)

@allure.title("04 - Room")
def test_04_room(session_page: Page, code):
    run_room(session_page, code)

@allure.title("05 - Robot")
def test_05_robot(session_page: Page, code):
    run_robot(session_page, code)

@allure.title("06 - Natural Person")
def test_06_natural_person(session_page: Page, code):
    run_natural_person(session_page, code)

@allure.title("07 - User")
def test_07_user(session_page: Page, code):
    run_user(session_page, code)

@allure.title("08 - User Attach Form")
def test_08_user_attach_form(session_page: Page, code):
    run_user_attach_form(session_page, code)

@allure.title("09 - Role")
def test_09_role(session_page: Page):
    run_role(session_page)

@allure.title("10 - Role Attach Form")
def test_10_role_attach_form(session_page: Page):
    run_role_attach_form(session_page)

@allure.title("11 - Buy License")
def test_11_buy_license(session_page: Page, logger):
    run_buy_license(session_page, logger)

@allure.title("12 - Attach License")
def test_12_attach_license(session_page: Page, code, logger):
    run_attach_license(session_page, code, logger)

@allure.title("13 - Change Password")
def test_13_change_password(session_page: Page, code):
    run_change_password(session_page, code)

@allure.title("14 - Price Type")
def test_14_price_type(session_page: Page, code, logger):
    run_price_type_uzb(session_page, code, logger)

@allure.title("15 - Payment Type")
def test_15_payment_type(session_page: Page):
    run_payment_type(session_page)

@allure.title("16 - Sector")
def test_16_sector(session_page: Page, code):
    run_sector(session_page, code)

@allure.title("17 - Product")
def test_17_product(session_page: Page, code):
    run_product(session_page, code)

# ----------------------------------------------------------------------------------------------------------------------
