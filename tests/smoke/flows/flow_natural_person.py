import allure
from playwright.sync_api import Page

from utils.base_page import BasePage


def create_natural_person(page: Page, name: str, person_code: str, *, client: bool = False) -> None:
    """To'g'ri filialda yangi jismoniy shaxs yaratib, ro'yxatga qaytadi."""
    base = BasePage(page)

    with allure.step("Jismoniy shaxs yaratish formasini ochish"):
        base.navigate_to(tab="Справочники", name="Физические лица")
        base.expect_page(heading="Физические лица")
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Физическое лицо (создание)")

    with allure.step("Jismoniy shaxs ma'lumotlarini to'ldirish"):
        base.input(ng_model="d.first_name", value=name)
        base.input(label="Код", value=person_code)
        if client:
            base.checkbox(label="Клиент", checked=True)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("Jismoniy shaxsni saqlash"):
        base.save_and_expect_heading("Физические лица", confirm_text="")


# ----------------------------------------------------------------------------------------------------------------------

def check_natural_person_view(page: Page, name: str) -> None:
    """Tanlangan jismoniy shaxsning view formasida nom va statusni tekshiradi."""
    base = BasePage(page)

    with allure.step("Jismoniy shaxs view formasini ochish"):
        base.grid(name, click=True)
        page.get_by_role("button", name="Просмотр", exact=True).click()
        base.expect_page(heading="Физическое лицо (просмотр)")

    with allure.step("View formasidagi ma'lumotlarni tekshirish"):
        base.text(name, "Активный")
        page.get_by_role("button", name="Закрыть").first.click()
        base.expect_page(heading="Физические лица")
