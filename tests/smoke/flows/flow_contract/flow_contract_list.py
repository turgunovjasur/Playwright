import re

import allure
from playwright.sync_api import expect

from utils.base_page import BasePage


def flow_open_contract_list(page):
    base = BasePage(page)
    base.navigate_to(tab="Финансы", name="Договоры")
    base.wait_for_loader()
    base.expect_page(url="anor/mkf/contract_list")
    base.expect_page(heading="Договоры")
    expect(page.get_by_role("button", name="Создать", exact=True)).to_be_visible()


def flow_contract_list(page, add=False, find_code=None, view=False):
    base = BasePage(page)
    base.expect_page(url="anor/mkf/contract_list")
    base.expect_page(heading="Договоры")

    if add:
        with allure.step("Contract List: 'Создать' button click"):
            page.get_by_role("button", name="Создать", exact=True).click()
            expect(page).to_have_url(re.compile(r".*/anor/mkf/contract\+add"))
            return

    if find_code:
        with allure.step(f"Contract List: contract code -> '{find_code}' qidirish"):
            page.get_by_role("searchbox", name="Поиск").fill(find_code)
            page.get_by_role("searchbox", name="Поиск").press("Enter")
            base.wait_for_loader()
            expect(page.locator("b-grid")).to_contain_text(find_code)
            page.locator("b-grid").get_by_text(find_code).first.click()

    if view:
        with allure.step("Contract List: 'Просмотр' button click"):
            expect(page.get_by_role("button", name="Просмотр", exact=True)).to_be_visible()
            page.get_by_role("button", name="Просмотр", exact=True).click()
            expect(page).to_have_url(re.compile(r".*/anor/mkf/contract_view"))
