import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import license_policy_disabled
from utils.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Company")]

# Faqat company create/save flowiga tegishli lokal timeout: 10 minut.
COMPANY_SAVE_TIMEOUT = 600_000

# ----------------------------------------------------------------------------------------------------------------------

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
    9. Companyni ro'yxatda code bo'yicha tekshirish.
    10. Company viewni ochish.
    11. Security sozlamalarini qo'llash.
    12. Company code ni data storega saqlash.
    """
    base = AutoBasePage(page)
    company_code = f"autotest{code}".lower()

    with allure.step("1 - admin head profilga kirish"):
        authorization(page, who="head")

    with allure.step("2 - Company ro'yxatiga o'tish"):
        base.switch_filial(name="Администрирование")
        base.navigate_to(tab="Главное", name="Компании")
        base.expect_page(heading="Компании", url="biruni/md/company_list")

    with allure.step("3 - Company mavjudligini code bo'yicha tekshirish"):
        base.grid_controller(search=company_code)
        company_exists = base.grid(company_code, return_bool=True)

    if not company_exists:
        with allure.step("4 - Yangi company formasini ochish"):
            base.click(name="Создать")
            base.expect_page(heading="Компания (создание)", url="company_add")

        with allure.step("5 - Majburiy maydonlarni to'ldirish"):
            base.input(label="Код сервера", value=company_code)
            base.input(label="Название", value=f"Autotest company {code}")
            base.b_input(label="Язык", expect_value="Русский")

        with allure.step("6 - Majburiy shablonlarni tanlash"):
            base.b_input(label="Маркировка", value="UZ Marking")
            base.b_input(label="План счетов", value="UZ COA")
            base.b_input(label="Банки", value="UZ BANK")

        with allure.step("7 - Trade va modullarni yoqish"):
            root = "app-project-module"
            trade_modules = (
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
            base.checkbox(label="trade", checked=True, root=root)
            for module in trade_modules:
                base.checkbox(label=module, checked=True, root=root)
            for module in trade_modules:
                base.checkbox(label=module, expect_checked=True, root=root)

        with allure.step("8 - Companyni saqlab, ro'yxatga qaytish"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni()
            base.expect_page(heading="Компании", url="biruni/md/company_list", timeout=COMPANY_SAVE_TIMEOUT)

    with allure.step("9 - Company code ni ro'yxatda tekshirish"):
        base.grid_controller(search=company_code)
        base.grid(company_code)

    with allure.step("10 - Company viewni ochish"):
        base.grid(company_code, click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Компания (просмотр)", url="company_view")

    with allure.step("11 - Company viewda security sozlamalarini qo'llash"):
        base.click(name="Безопасность", role="tab", exact=True, root="app-company-view")
        base.choice(label="Ограничение количества одновременных сеансов", option="Отключено", root="app-company-security-form")
        if license_policy_disabled():
            base.checkbox(label="Политика лицензирования", checked=False, root="app-company-security-form")

    with allure.step("12 - Company code ni data storega saqlash"):
        save_data("company_code", company_code)

    return company_code


@allure.title("Company yaratish")
def test_company(page, code, save_data):
    run_company(page, code, save_data)
