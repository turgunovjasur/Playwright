import allure
from playwright.sync_api import Page, expect
from tests.smoke.flows.flow_navigate import navigate_to

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Robot")]

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Xodim (robot) yaratish")
def test_robot(page: Page, code) -> None:
    with allure.step("1 - Xodimlar ro'yxatiga o'tish"):
        navigate_to(page, tab="Справочники", name="Штат")
        expect(page.get_by_role("heading")).to_contain_text("Штат")

    with allure.step("2 - Yangi xodim formasini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Штат (создание)")
        page.get_by_role("textbox").first.fill(f"code_robot-pw{code}")
        page.get_by_role("textbox").nth(1).fill(f"robot-pw{code}")
        page.get_by_role("textbox", name="Поиск").first.click()
        page.get_by_text("Админ", exact=True).click()
        page.locator("b-input").filter(has_text="Админ 1 Выбранных ATS-").get_by_placeholder("Поиск").press("Escape")
        page.locator("b-input").filter(has_text="0 Выбранных").get_by_placeholder("Поиск").click()
        page.get_by_text(f"room-pw{code}").click()
        expect(page.get_by_text("Активный")).to_be_visible()

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить").click()
        expect(page.get_by_role("heading")).to_contain_text("Штат")
        expect(page.get_by_text(f"code_robot-pw{code}")).to_be_visible()
        expect(page.get_by_text(f"robot-pw{code}", exact=True)).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------