import time
from playwright.sync_api import Page
from tests.flow_navigate import navigate_to, switch_filial
from tests.flow_authorization import authorization


def test_for_test(page: Page) -> None:
    authorization(page)
    switch_filial(page, name="Test_filial-14")
    navigate_to(page, tab="Главное", name="Организации")

    time.sleep(5)