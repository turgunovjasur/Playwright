import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Currency")]

# ----------------------------------------------------------------------------------------------------------------------

def run_currency(page, logger):
    """USD uchun bugungi valyuta kursini yangilash va tekshirish.

    1. Финансы -> Валюты ro'yxatidan USD valyutasining view formasini ochadi.
    2. Курсы tabida Markaziy bank kursini yangilaydi.
    3. Bugungi sana uchun manual kursni saqlab, gridda sana va kursni tekshiradi.
    """
    base = BasePage(page)

    with allure.step("1 - USD valyutasining kurslar tabini ochish"):
        base.navigate_to(tab="Финансы", name="Валюты")
        base.expect_page(heading="Валюты", url="currency_list")

    with allure.step("2 - Markaziy bank va manual valyuta kurslarini yangilash"):
        base.grid("840", "USD", "Доллар США", click=True)
        page.get_by_role("button", name="Просмотреть").click()
        base.expect_page(heading="Валюта (просмотр)", url="currency_view")
        page.get_by_role("link", name="Курсы").click()
        base.text("Курсы")
        if base.grid(is_empty=True):
            logger.warning("currency list bosh emas!")
        page.get_by_role("button", name="Установить курс валюты по ЦБ Узбекистана").click()
        base.confirm_biruni(expected_text="Вы уверены что хотите установите курс валюты по ЦБ Узбекистана?")
        base.wait_for_loader(timeout=120_000)

        if not base.grid(text=base.date("today"), is_visible=True):
            logger.warning("Kurs Markaziy bank dan olinmadi!")

        page.get_by_role("button", name="Установить курс", exact=True).click()

        modal = page.get_by_role("dialog")
        base.expect_page(heading="Добавить курс", root=modal)
        base.date_picker(label="Дата курса", date="today", auto_fill=True, root=modal)
        base.input(label="Курс валют", value="10000", root=modal)
        base.form_view(label="Базовая валюта", expect_value="Узбекский сум", root=modal)
        page.get_by_role("button", name="Сохранить").click()

        base.text("Курсы")
        base.grid(base.date("today"), "10000")


@allure.title("USD uchun bugungi valyuta kursini o'rnatish")
def test_price_type_uzb(page, code, logger):
    """USD valyutasining bugungi kursini saqlab, gridda tekshiradi."""
    authorization(page, who='user', code=code)
    run_currency(page, logger)
