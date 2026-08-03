import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Currency")]

# ----------------------------------------------------------------------------------------------------------------------

def run_currency(page, logger):
    """USD uchun bugungi valyuta kursini yangilash va tekshirish.

    1. Финансы -> Валюты ro'yxatini ochish.
    2. USD valyutasining view formasida Курсы tabini ochish.
    3. Markaziy bank kursini yangilab, bugungi sana uchun kurs mavjudligini tekshirish.
    4. Manual kurs qo'shish modalini ochish.
    5. Bugungi sana uchun manual kursni kiritib saqlash.
    6. Kurslar gridida sana va kursni tekshirish.
    """
    base = BasePage(page)

    with allure.step("1 - Valyutalar ro'yxatini ochish"):
        base.navigate_to(tab="Финансы", name="Валюты")
        base.expect_page(heading="Валюты", url="currency_list")

    with allure.step("2 - USD valyutasining kurslar tabini ochish"):
        base.grid("840", "USD", "Доллар США", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Валюта (просмотр)", url="currency_view")
        base.click(name="Курсы", role="link")
        base.text("Курсы")

    with allure.step("3 - Markaziy bank kursini yangilash"):
        base.click(name="Установить курс валюты по ЦБ Узбекистана")
        base.confirm_biruni(expected_text="Вы уверены что хотите установите курс валюты по ЦБ Узбекистана?")
        base.wait_for_loader()

        if not base.grid(base.date("today"), return_bool=True):
            logger.warning("Kurs Markaziy bankdan olinmadi!")

    with allure.step("4 - Manual kurs qo'shish modalini ochish"):
        base.click(name="Установить курс", exact=True)
        modal = page.get_by_role("dialog")
        base.expect_page(heading="Добавить курс", root=modal)

    with allure.step("5 - Manual kursni kiritib saqlash"):
        base.date_picker(label="Дата курса", date="today", auto_fill=True, root=modal)
        base.input(label="Курс валют", value="10000", root=modal)
        base.form_view(label="Базовая валюта", expect_value="Узбекский сум", root=modal)
        base.click(name="Сохранить", exact=True, root=modal)
        base.expect_page(heading="Валюта (просмотр)", url="currency_view")

    with allure.step("6 - Manual kursni gridda tekshirish"):
        base.text("Курсы")
        base.grid(base.date("today"), "10000")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("USD kursini Markaziy bank va manual usulda yangilash")
def test_currency(page, code, logger):
    authorization(page, who="user", code=code)
    run_currency(page, logger)
