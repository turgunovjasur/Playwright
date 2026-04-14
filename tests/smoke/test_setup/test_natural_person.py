import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to, switch_filial

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Natural Person")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim uchun jismoniy shaxs yaratish")
def test_natural_person(page: Page, code) -> None:
    with allure.step("1 - Filialga o'tish va jismoniy shaxslar ro'yxatini ochish"):
        switch_filial(page, name=f"filial-pw{code}")
        navigate_to(page, tab="Справочники", name="Физические лица")
        expect(page.get_by_role("heading")).to_contain_text("Физические лица")

    with allure.step("2 - Yangi jismoniy shaxs formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Физическое лицо (создание)")
        page.get_by_role("textbox", name="Поиск").first.click()
        page.locator("b-input").filter(has_text="Поиск").get_by_placeholder("Поиск").fill(f"natural_person-pw{code}")
        expect(page.get_by_text("Активный")).to_be_visible()

    with allure.step("3 - Saqlash va tasdiqlash"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")

    with allure.step("4 - Ro'yxatda yaratilganini tekshirish"):
        expect(page.get_by_text(f"natural_person-pw{code}", exact=True)).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Mijoz uchun jismoniy shaxs yaratish")
def test_natural_person_for_client_1(page: Page, code) -> None:
    with allure.step("1 - Jismoniy shaxslar ro'yxatini ochish"):
        navigate_to(page, tab="Справочники", name="Физические лица")
        expect(page.get_by_role("heading")).to_contain_text("Физические лица")

    with allure.step("2 - Yangi mijoz jismoniy shaxs formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Физическое лицо (создание)")
        page.get_by_role("textbox", name="Поиск").first.click()
        page.locator("b-input").filter(has_text="Поиск").get_by_placeholder("Поиск").fill(f"natural_client-pw{code}")
        expect(page.get_by_text("Активный")).to_be_visible()
        page.get_by_text("Клиент", exact=True).click()

    with allure.step("3 - Saqlash va tasdiqlash"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.locator("#biruniConfirm")).to_be_visible()
        page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
        page.locator("#biruniConfirm").get_by_role("button", name="да").click()
        page.locator("#biruniConfirm").wait_for(state="hidden")

    with allure.step("4 - Jismoniy shaxslar va Mijozlar ro'yxatida ko'rinishini tekshirish"):
        expect(page.get_by_text(f"natural_client-pw{code}", exact=True)).to_be_visible()
        navigate_to(page, tab="Справочники", name="Клиенты")
        expect(page.get_by_role("heading")).to_contain_text("Клиенты")
        expect(page.locator("b-grid")).to_contain_text(f"natural_client-pw{code}")

# ----------------------------------------------------------------------------------------------------------------------