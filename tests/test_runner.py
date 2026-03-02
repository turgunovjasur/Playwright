import time
from playwright.sync_api import Page
from flows.flow_authorization import authorization
from tests.test_filial import test_filial
from tests.test_legal_person import test_legal_person

# ----------------------------------------------------------------------------------------------------------------------

def test_for_test(page: Page, random_code) -> None:
    authorization(page)
    test_legal_person(page, random_code)
    test_filial(page, random_code)

    time.sleep(2)

# ----------------------------------------------------------------------------------------------------------------------
