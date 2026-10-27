from urllib.parse import urlsplit

import allure

from tests.shared.reporting import safe_page_screenshot
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.setup_errors import SetupDependencyReadyError
from utils.data_store import save_data
from utils.base_pages.auto_base_page import AutoBasePage
from utils.helper_utils import query_int_from_url

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Currency")]

# ----------------------------------------------------------------------------------------------------------------------

def run_currency(page, logger):
    """USD kursini yangilash va USD/UZS currency IDlarini saqlash.

    1. Финансы -> Валюты ro'yxatini ochish.
    2. USD valyutasining view formasida Курсы tabini ochish.
    3. View URLdan USD currency IDni olib, data_store ga saqlash.
    4. Markaziy bank kursini yangilab, natijani qayd etish.
    5. Manual kurs qo'shish modalini ochish.
    6. Bugungi sana uchun manual kursni kiritib saqlash.
    7. Kurslar gridida sana va kursni tekshirish.
    8. Valyutalar ro'yxatidan UZS viewini ochib, currency IDni saqlash.
    9. CBU tekshiruvini yakunlash: xato bo'lsa test failed, tayyor baseline saqlanadi.
    """
    base = AutoBasePage(page)
    central_bank_error = None

    with allure.step("1 - Valyutalar ro'yxatini ochish"):
        base.navigate_to(tab="Финансы", name="Валюты")
        base.expect_page(heading="Валюты", url="currency_list")

    with allure.step("2 - USD valyutasining kurslar tabini ochish"):
        base.grid("840", "USD", "Доллар США", click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Валюта (просмотр)", url="currency_view?currency_id=")
        base.click(name="Курсы", role="tab")
        base.text("Курсы")

    with allure.step("3 - USD currency IDni olish va saqlash"):
        save_data("currency_id", query_int_from_url(page.url, "currency_id"))

    with allure.step("4 - Markaziy bank kursini yangilash"):
        base.click(name="Установить курс валюты по ЦБ Узбекистана")
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path.endswith("/b/anor/mk/currency_view:update_currency_rate")
        ) as rate_response:
            base.confirm_biruni(expected_text="Вы уверены что хотите установите курс валюты по ЦБ Узбекистана?")
        response = rate_response.value
        base.wait_for_loader()

        if response.status == 500 and "java.net.SocketTimeoutException: Connect timed out" in response.text():
            central_bank_error = "CBU kursini olish: HTTP 500, java.net.SocketTimeoutException: Connect timed out"
            allure.attach(central_bank_error, name="CBU integration failure", attachment_type=allure.attachment_type.TEXT)
            allure.attach(safe_page_screenshot(page), name="CBU error dialog", attachment_type=allure.attachment_type.PNG)
            base.close_biruni_alert("currency_view:update_currency_rate", "java.net.SocketTimeoutException: Connect timed out")
            logger.warning(central_bank_error + "; manual baseline tayyorlanadi, CBU tekshiruvi failed bo'lib qoladi")
        else:
            base.expect_page(heading="Валюта (просмотр)", url="currency_view")
            if response.status != 200:
                raise AssertionError(f"CBU kursini olish: HTTP {response.status}")
            if not base.grid(base.date("today"), return_bool=True):
                central_bank_error = "CBU so'rovi HTTP 200 qaytardi, ammo bugungi kurs jadvalda yo'q"
                logger.warning(central_bank_error)

    with allure.step("5 - Manual kurs qo'shish modalini ochish"):
        base.click(name="Установить курс", exact=True)
        modal = page.get_by_role("dialog")
        base.expect_page(heading="Добавить курс", root=modal)  # navigation: same-url - Exchange-rate dialog opens inside the currency view.

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

    with allure.step("9 - Markaziy bank kursi natijasini tekshirish"):
        if central_bank_error:
            raise SetupDependencyReadyError(
                central_bank_error + "; manual kurs va USD/UZS IDlari tekshirildi, qolgan testlar davom etishi mumkin"
            )

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("USD kursini yangilash va USD/UZS currency IDlarini saqlash")
def test_currency(page, code, logger):
    authorization(page, who="user", code=code)
    run_currency(page, logger)
