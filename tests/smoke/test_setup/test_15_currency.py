import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Currency")]

# ----------------------------------------------------------------------------------------------------------------------

def run_currency(page, logger, save_data):
    """USD kursini yangilash va USD/UZS currency IDlarini saqlash.

    1. Финансы -> Валюты ro'yxatini ochish.
    2. USD valyutasining view formasida Курсы tabini ochish.
    3. View URLdan USD currency IDni olib, data_store ga saqlash.
    4. Markaziy bank kursini yangilab, bugungi sana uchun kurs mavjudligini tekshirish.
    5. Manual kurs qo'shish modalini ochish.
    6. Bugungi sana uchun manual kursni kiritib saqlash.
    7. Kurslar gridida sana va kursni tekshirish.
    8. Valyutalar ro'yxatidan UZS viewini ochib, currency IDni saqlash.
    """
    base = BasePage(page)

    with allure.step("1 - Valyutalar ro'yxatini ochish"):
        base.navigate_to(tab="Финансы", name="Валюты")
        base.expect_page(heading="Валюты", url="currency_list")

    with allure.step("2 - USD valyutasining kurslar tabini ochish"):
        base.grid("840", "USD", "Доллар США", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Валюта (просмотр)", url="currency_view?currency_id=")
        base.click(name="Курсы", role="link")
        base.text("Курсы")

    with allure.step("3 - USD currency IDni olish va saqlash"):
        save_data("currency_id", query_int_from_url(page.url, "currency_id"))

    with allure.step("4 - Markaziy bank kursini yangilash"):
        base.click(name="Установить курс валюты по ЦБ Узбекистана")
        base.confirm_biruni(expected_text="Вы уверены что хотите установите курс валюты по ЦБ Узбекистана?")
        base.wait_for_loader()

        if not base.grid(base.date("today"), return_bool=True):
            logger.warning("Kurs Markaziy bankdan olinmadi!")

    with allure.step("5 - Manual kurs qo'shish modalini ochish"):
        base.click(name="Установить курс", exact=True)
        modal = page.get_by_role("dialog")
        base.expect_page(heading="Добавить курс", root=modal)

    with allure.step("6 - Manual kursni kiritib saqlash"):
        base.date_picker(label="Дата курса", date="today", auto_fill=True, root=modal)
        base.input(label="Курс валют", value="10000", root=modal)
        base.form_view(label="Базовая валюта", expect_value="Узбекский сум", root=modal)
        base.click(name="Сохранить", exact=True, root=modal)
        base.expect_page(heading="Валюта (просмотр)", url="currency_view")

    with allure.step("7 - Manual kursni gridda tekshirish"):
        base.text("Курсы")
        base.grid(base.date("today"), "10000")

    with allure.step("8 - UZS currency IDni olish va saqlash"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Валюты", url="currency_list")
        base.grid("860", "сум", "Узбекский сум", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Валюта (просмотр)", url="currency_view?currency_id=")
        save_data("currency_id_uzb", query_int_from_url(page.url, "currency_id"))

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("USD kursini yangilash va USD/UZS currency IDlarini saqlash")
def test_currency(page, code, logger, save_data):
    authorization(page, who="user", code=code)
    run_currency(page, logger, save_data)
