import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Legal Person")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Yuridik shaxs yaratish")
def test_legal_person(page: Page, code) -> None:
    with allure.step("1 - Yuridik shaxslar ro'yxatiga o'tish"):
        navigate_to(page, tab="Справочники", name="Юридические лица")
        expect(page.get_by_role("heading")).to_contain_text("Юридические лица")

    with allure.step("2 - Yangi yuridik shaxs formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Юридическое лицо (создание)")
        page.get_by_role("textbox").nth(4).fill(f"legal_person-pw{code}")
        page.get_by_role("textbox").first.fill(f"cod_lg_pw{code}")
        expect(page.get_by_text("Активный")).to_be_visible()

    with allure.step("3 - Saqlash va tasdiqlash"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_contain_text("Сохранить")
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")

    with allure.step("4 - Ro'yxatda yaratilganini tekshirish"):
        page.get_by_role("searchbox", name="Поиск").fill(f"cod_lg_pw{code}")
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        expect(page.get_by_text(f"cod_lg_pw{code}")).to_be_visible()
        expect(page.get_by_text(f"legal_person-pw{code}").first).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------