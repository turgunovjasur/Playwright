import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import license_policy_disabled
from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Company")]

# Faqat company create/save flowiga tegishli lokal timeout: 10 minut.
COMPANY_SAVE_TIMEOUT = 600_000


def run_company(page, code, save_data):
    """Testcase: company yaratish yoki mavjud company sozlamalarini yangilash.

    1. Head profilga kirish.
    2. Company ro'yxatini ochish.
    3. Company mavjudligini code bo'yicha tekshirish.
    4. Mavjud bo'lmasa yaratish formasini ochish.
    5. Majburiy maydonlarni to'ldirish.
    6. Majburiy shablonlarni tanlash.
    7. Trade va uning modullarini yoqish.
    8. Companyni saqlash.
    9. Yaratilgan companyni ro'yxatda tekshirish.
    10. Company viewni ochish.
    11. Security sozlamalarini qo'llash.
    12. Company code ni data storega saqlash.
    """
    legacy = BasePage(page)
    angular = AngularBasePage(page)
    company_code = f"autotest{code}"

    with allure.step("1 - admin head profilga kirish"):
        authorization(page, who="head")

    with allure.step("2 - Company ro'yxatiga o'tish"):
        legacy.switch_filial(name="Администрирование")
        legacy.navigate_to(tab="Главное", name="Компании")
        angular.expect_page(heading="Компании", url="/a2/biruni/md/company_list")

    with allure.step("4 - Yangi company formasini ochish"):
        angular.button(name="Создать", click=True)
        angular.expect_page(heading="Компания (создание)", url="company_add")

    with allure.step("5 - Majburiy maydonlarni to'ldirish"):
        angular.input(label="Код сервера", value=company_code)
        angular.input(label="Ф.И.О.", value=f"Autotest company {code}")
        angular.select(label="Язык", expect_value="Русский")

    with allure.step("6 - Majburiy shablonlarni tanlash"):
        angular.select(label="Маркировка", value="UZ Marking")
        angular.select(label="План счетов", value="UZ COA")
        angular.select(label="Банки", value="UZ BANK")

    with allure.step("7 - Trade va modullarni yoqish"):
        root = "app-project-module"
        angular.switch(label="trade", checked=True, root=root)
        TRADE_MODULES = (
            "Call center",
            "Equipment",
            "Finance - Main",
            "Finance - Advanced",
            "HR and Payroll",
            "Image Recognition",
            "Main",
            "Manufacturing",
            "Marking",
            "Sales - Main",
            "Sales - Advanced",
            "Store",
            "Telegram",
            "Trade Marketing",
            "Uzbekistan Module",
            "Warehouse - Main",
            "Warehouse - Advanced",
        )
        for module in TRADE_MODULES:
            angular.switch(label=module, checked=True, root=root)
        for module in TRADE_MODULES:
            angular.switch(label=module, expect_checked=True, root=root)

    with allure.step("8 - Company saqlash va list ochilishini kutish"):
        angular.save_and_expect_page(expected_heading="Компании", expected_url="/a2/biruni/md/company_list", timeout=COMPANY_SAVE_TIMEOUT)

    with allure.step("9 - Ro'yxatda yaratilgan company code ni tekshirish"):
        angular.grid_controller(search=company_code)
        angular.grid(company_code, is_visible=True)

    with allure.step("10 - Company viewni ochish"):
        angular.grid(company_code, click=True)
        angular.button(name="Просмотреть", click=True)
        angular.expect_page(heading="Компания (просмотр)", url="company_view")

    with allure.step("11 - Company viewda security sozlamalarini qo'llash"):
        angular.tab(name="Безопасность", root="app-company-view")
        angular.choice(label="Ограничение количества одновременных сеансов", option="Отключено", root="app-company-security-form")
        if license_policy_disabled():
            angular.switch(label="Политика лицензирования", checked=False, root="app-company-security-form")

    with allure.step("12 - Company code ni data storega saqlash"):
        save_data("company_code", company_code)

    return company_code


@allure.title("Company yaratish")
def test_company(page, code, save_data):
    """Testcase: company yaratish va majburiy sozlamalarni qo'llash.

    1. Head profil bilan Company ro'yxatini ochish.
    2. Company mavjud bo'lmasa maydonlar, shablonlar va Trade modullari bilan yaratish.
    3. Company viewda concurrent session va license policy sozlamalarini qo'llash.
    4. Company code ni keyingi setup/group testlari uchun saqlash.
    """
    run_company(page, code, save_data)
