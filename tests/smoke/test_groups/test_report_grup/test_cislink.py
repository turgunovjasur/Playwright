import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, select_b_input_option

pytestmark = [allure.epic("Report Group"), allure.feature("Integration Report"), allure.story("CisLink")]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_cislink_check(page, code, login=True):
    """Report-01: CisLink integration report — sozlash va .zip yuklab olishni tekshirish.

    Login (login=True bo'lsa): admin login va test filialiga (filial-pw{code}) o'tish.

    Qadamlar (Allure step):
      1. trade/rep/integration/cislink sahifasini ochish (menyuda yo'q — URL orqali)
      2. Настройки modalini ochish
      3. Filtrlarni to'ldirish: identification code='test', Характеристики=Группа,
         Продуктовое направление=Группа, Тип цены=Price Type UZB-pw{code}
      4. Сохранить -> modal yopilib asosiy sahifa qaytadi
      5. Сформировать -> cislink*.zip yuklanishi, fayl bo'sh emasligi tekshiriladi
    """
    base = BasePage(page)
    price_type_name = f"Price Type UZB-pw{code}"

    if login:
        authorization(page)
        base.switch_filial(name=f"filial-pw{code}")

    with allure.step("1 - CisLink integration report sahifasini ochish"):
        base, _, rest = page.url.partition("#/")
        session_token = rest.split("/", 1)[0]
        page.goto(f"{base}#/{session_token}/trade/rep/integration/cislink")
        expect(page.get_by_role("heading").filter(has_text="CisLink")).to_be_visible()

    with allure.step("2 - Настройки modalini ochish"):
        page.get_by_role("button", name="Настройки", exact=True).click()
        expect(page.locator('button[b-hotkey="save"]')).to_be_visible()

    with allure.step("3 - Filtrlarni to'ldirish"):
        base.input(ng_model="d.identification_code", value="test")
        select_b_input_option(page, "person_groups", "Группа")
        select_b_input_option(page, "product_groups", "Группа")
        select_b_input_option(page, "price_types", price_type_name)

    with allure.step("4 - Sozlamani saqlash va asosiy sahifaga qaytish"):
        page.locator('button[b-hotkey="save"]').click()
        expect(page.locator('button[b-hotkey="save"]')).to_be_hidden()
        expect(page.get_by_role("button", name="Сформировать", exact=True)).to_be_visible()

    with allure.step("5 - Сформировать va cislink*.zip yuklanishini tekshirish"):
        generate_and_verify_download(
            page,
            page.locator('button[ng-click="generate()"]'),
            expected_prefix="cislink",
            save_name=f"cislink_pw{code}.zip",
        )
