import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Filial")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Filial (tashkilot) yaratish")
def test_filial(page: Page, code) -> None:
    with allure.step("1 - Tashkilotlar ro'yxatiga o'tish"):
        navigate_to(page, tab="Главное", name="Организации")
        expect(page.get_by_role("heading")).to_contain_text("Организации")

    with allure.step("2 - Yangi tashkilot formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Организация (создание)")
        page.get_by_role("textbox").first.fill(f"filial-pw{code}")

        page.locator("b-input").filter(has_text="Код Валюта Добавить Показать все").get_by_placeholder("Поиск").click()
        page.get_by_text("Узбекский сум").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Продолжить?")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")

        page.locator("b-input").filter(has_text="Код Название Добавить Показать все").get_by_placeholder("Поиск").click()
        page.locator("b-input").filter(has_text="Код Название Добавить Показать все Поиск").get_by_placeholder("Поиск").fill(f"cod_lg_pw{code}")
        page.get_by_text(f"cod_lg_pw{code}").click()
        expect(page.locator("b-input").filter(has_text=f"Код Название cod_lg_pw{code}").get_by_placeholder("Поиск")).to_have_value(f"legal_person-pw{code}")

    with allure.step("3 - Saqlash va tasdiqlash"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Сохранить")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")

    with allure.step("4 - Ro'yxatda yaratilganini tekshirish"):
        expect(page.get_by_role("heading")).to_contain_text("Организации")
        page.get_by_role("searchbox", name="Поиск").fill(f"filial-pw{code}")
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        expect(page.get_by_text(f"cod_lg_pw{code}")).to_be_visible()
        expect(page.get_by_text(f"filial-pw{code}")).to_be_visible()

        page.reload()
        BasePage(page).wait_for_loader(timeout=600_000)

# ----------------------------------------------------------------------------------------------------------------------