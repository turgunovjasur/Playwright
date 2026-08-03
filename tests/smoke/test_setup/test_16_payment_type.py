import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Payment Type")]

# ----------------------------------------------------------------------------------------------------------------------

def run_payment_type(page):
    """Testcase: global katalogdagi to'lov turlarini company'ga ulash.

    1. Справочники -> Цены ro'yxatini ochish.
    2. Типы оплат ro'yxatini ochish.
    3. Тип оплат (прикрепление) sahifasini ochish.
    4. Barcha mavjud to'lov turlarini tanlab ulash va available grid bo'shligini tekshirish.
    5. Прикрепление sahifasini yopib, Типы оплат ro'yxatiga qaytish.
    6. Company ro'yxatida 4 ta to'lov turi ko'rinishini tekshirish.
    """
    base = BasePage(page)
    with allure.step("1 - Narxlar ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Цены")
        base.expect_page(heading="Цены")

    with allure.step("2 - To'lov turlari ro'yxatini ochish"):
        base.click(name="Типы оплат", role="link")
        base.expect_page(heading="Типы оплат")

    with allure.step("3 - To'lov turlarini biriktirish sahifasini ochish"):
        base.click(name="Прикрепление")
        base.expect_page(heading="Тип оплат (прикрепление)")

    with allure.step("4 - Barcha to'lov turlarini tanlash va ulash"):
        base.grid(checkbox="all")
        base.click(name="Прикрепить")
        base.confirm_biruni("Прикрепить типы оплат в количестве 4?")
        base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("5 - Biriktirish sahifasini yopib, ro'yxatga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Типы оплат")

    with allure.step("6 - To'lov turlarini ro'yxatda tekshirish"):
        base.grid("Наличные деньги")
        base.grid("Перечисление")
        base.grid("Терминал")
        base.grid("Чековая книжка")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("To'lov turlarini tizimga ulash")
def test_payment_type(page, code):
    authorization(page, who="user", code=code)
    run_payment_type(page)
