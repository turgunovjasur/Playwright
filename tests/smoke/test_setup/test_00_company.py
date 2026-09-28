import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.flow_setup.flow_license import license_policy_disabled
from utils.data_store import save_data
from utils.base_pages.auto_base_page import AutoBasePage
from utils.helper_utils import label_pattern

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Company")]

# Faqat company create/save flowiga tegishli lokal timeout: 10 minut.
COMPANY_SAVE_TIMEOUT = 600_000

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


def _trade_card(page):
    """Products card: TRADE header switch lives outside smt-control."""
    return page.locator("app-project-module article").filter(
        has=page.locator("header span").filter(has_text=label_pattern("trade"))
    )


def _enable_project_switch(base, card, *, timeout=15_000):
    toggle = card.locator("header").get_by_role("switch").first
    toggle.scroll_into_view_if_needed()
    base.checkbox(locator=toggle, checked=True)
    expect(toggle).to_have_attribute("aria-checked", "true", timeout=timeout)


def _enable_module_switch(base, card, name, *, timeout=15_000):
    row = card.locator("div.flex").filter(
        has=card.page.locator("span").filter(has_text=label_pattern(name))
    )
    toggle = row.get_by_role("switch").first
    expect(toggle).to_be_visible(timeout=timeout)
    toggle.scroll_into_view_if_needed()
    base.checkbox(locator=toggle, checked=True)
    expect(toggle).to_have_attribute("aria-checked", "true", timeout=timeout)

# ----------------------------------------------------------------------------------------------------------------------

def run_company(page, code):
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
            trade_card = _trade_card(page)
            expect(trade_card).to_be_visible(timeout=10_000)
            _enable_project_switch(base, trade_card)
            expect(
                trade_card.get_by_text(label_pattern("Call center")).first
            ).to_be_visible(timeout=15_000)
            for module in TRADE_MODULES:
                _enable_module_switch(base, trade_card, module)
            for module in TRADE_MODULES:
                row = trade_card.locator("div.flex").filter(
                    has=page.locator("span").filter(has_text=label_pattern(module))
                )
                expect(row.get_by_role("switch").first).to_have_attribute(
                    "aria-checked", "true", timeout=10_000
                )

        with allure.step("8 - Companyni saqlab, ro'yxatga qaytish"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni()
            base.expect_page(heading="Компании", url="biruni/md/company_list", timeout=COMPANY_SAVE_TIMEOUT)

    with allure.step("9 - Company code ni ro'yxatda tekshirish"):
        base.grid_controller(search=company_code)
        if not base.grid(company_code, return_bool=True):
            base.grid_controller(reload=True)
            base.grid_controller(search=company_code)
        base.grid(company_code)

    with allure.step("10 - Company viewni ochish"):
        base.grid(company_code, click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="Компания (просмотр)", url="company_view")

    with allure.step("11 - Company viewda security sozlamalarini qo'llash"):
        base.click(name="Безопасность", role="tab", exact=True, root="app-company-view")
        base.choice(label="Ограничение количества одновременных сеансов", option="Отключено", root="app-company-security-form")
        base.checkbox(label="Политика паролей", checked=False, root="app-company-security-form")
        if license_policy_disabled():
            licensing_switch = page.locator("smt-switch#licensing_policy_enabled [role='switch']")
            expect(licensing_switch).to_be_visible(timeout=15_000)
            base.checkbox(locator=licensing_switch, checked=False)
            expect(licensing_switch).to_have_attribute("aria-checked", "false", timeout=15_000)
            page.wait_for_timeout(1_500)

    with allure.step("12 - Company code ni data storega saqlash"):
        save_data("company_code", company_code)

    return company_code


@allure.title("Company yaratish")
def test_company(page, code):
    run_company(page, code)
