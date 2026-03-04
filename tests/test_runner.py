import time
from playwright.sync_api import Page
from flows.flow_authorization import authorization
from tests.robot_test import test_robot
from tests.test_filial import test_filial
from tests.test_legal_person import test_legal_person
from tests.test_natural_person import test_natural_person
from tests.test_room import test_room
from tests.test_user import test_user, test_user_attach_form


# ----------------------------------------------------------------------------------------------------------------------

def test_for_test(page: Page, random_code, save_data) -> None:
    save_data("random_code", random_code)

    authorization(page)

    test_legal_person(page, random_code)

    test_filial(page, random_code)

    test_room(page, random_code)

    test_robot(page, random_code)

    test_natural_person(page, random_code)

    test_user(page, random_code)
    test_user_attach_form(page, random_code)

    time.sleep(2)

# ----------------------------------------------------------------------------------------------------------------------
