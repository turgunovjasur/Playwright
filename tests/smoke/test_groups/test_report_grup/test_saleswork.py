import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, select_b_input_option

pytestmark = [allure.epic("Report Group"), allure.feature("Integration Report"), allure.story("Sales Work")]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_saleswork_check(page, code, login=True):
    """Report-03: SalesWork report — yangi shablon yaratib, sales_work.zip yuklab olishni tekshirish.

    Login (login=True bo'lsa): admin login va test filialiga (filial-pw{code}) o'tish.

    Qadamlar (Allure step):
      1. SalesWork sahifasini ochish (URL orqali)
      2. Шаблоны -> Создать -> nom + Продуктовое направление (Группа) -> Сохранить
      3. SalesWork'da tanlangan shablon nomi kiritilgan nom bilan mosligini tekshirish
      4. Экспорт -> sales_work.zip yuklanishi va bo'sh emasligini tekshirish
    """
    base = BasePage(page)
    template_name = f"SalesWork-pw{code}"

    if login:
        authorization(page, who="admin")
        base.switch_filial(name=f"filial-pw{code}")

    with allure.step("1 - SalesWork sahifasini ochish"):
        base, _, rest = page.url.partition("#/")
        session_token = rest.split("/", 1)[0]
        page.goto(f"{base}#/{session_token}/trade/rep/integration/saleswork")
        expect(page.get_by_role("button", name="Шаблоны")).to_be_visible()

    with allure.step("2 - Yangi shablon yaratish"):
        page.locator('button[ng-click="selectTemplate()"]').click()
        page.locator('button[ng-click="add()"]').click()
        expect(page.get_by_role("heading")).to_contain_text("Шаблон Saleswork")
        base.input(ng_model="d.name", value=template_name)
        select_b_input_option(page, "product_groups", "Группа")
        page.locator('button[ng-click="save()"]').click()

    with allure.step("3 - Tanlangan shablon nomi tekshiriladi"):
        expect(page.locator('input[ng-model="d.template_name"]')).to_have_value(template_name)

    with allure.step("4 - Экспорт -> sales_work.zip yuklanishi"):
        generate_and_verify_download(
            page,
            page.get_by_role("button", name="Экспорт", exact=True),
            expected_prefix="sales_work",
            save_name=f"sales_work_pw{code}.zip",
        )
