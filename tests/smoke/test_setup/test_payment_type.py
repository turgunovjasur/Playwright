import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Payment Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_payment_type(page):
    """Testcase: global katalogdagi to'lov turlarini company'ga ulash.

    1. Справочники -> Цены -> Типы оплат ro'yxatini ochish.
    2. Прикрепление sahifasida barcha mavjud to'lov turlarini tanlab, tasdiqlash.
    3. Mavjud ro'yxat bo'shligini va company ro'yxatida 4 ta to'lov turi ko'rinishini tekshirish.
    """
    base = BasePage(page)
    with allure.step("1 - To'lov turlari ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")
        page.get_by_role("link", name="Типы оплат").click()
        base.expect_page(heading="Типы оплат")

    with allure.step("2 - Barcha to'lov turlarini tanlash va ulash"):
        page.get_by_role("button", name="Прикрепление").click()
        base.expect_page(heading="Тип оплат (прикрепление)")
        base.grid(checkbox="all")
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni("Прикрепить типы оплат в количестве 4?")
        base.wait_for_loader()
        if not base.grid(is_empty=True):
            raise AssertionError("To'lov turlari ulangandan keyin mavjud grid bo'shamadi")
        page.get_by_role("button", name="Закрыть").click()

    with allure.step("3 - To'lov turlari ro'yxatida ko'rinishini tekshirish"):
        base.expect_page(heading="Типы оплат")
        base.grid("Наличные деньги")
        base.grid("Перечисление")
        base.grid("Терминал")
        base.grid("Чековая книжка")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("To'lov turlarini tizimga ulash")
def test_payment_type(page, code):
    authorization(page, who="user", code=code)
    run_payment_type(page)
