import random
import time
from playwright.sync_api import Page

from flows.flow_authorization import authorization
from tests.test_filial import test_filial
from tests.test_legal_person import test_legal_person


def test_for_test(page: Page) -> None:
    i = random.randint(1000, 9999)

    authorization(page)
    test_legal_person(page, i)
    test_filial(page, i)

    time.sleep(5)
