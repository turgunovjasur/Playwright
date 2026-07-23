import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from tests.smoke.test_groups.test_report_grup.report_helpers import generate_and_verify_download, select_b_input_option

pytestmark = [allure.epic("Report Group"), allure.feature("Integration Report"), allure.story("Spot 2d")]


# ----------------------------------------------------------------------------------------------------------------------

def run_report_spot_check(page, code):
    """Report-05: Spot 2d report — yangi shablon yaratib, Spot2D.zip yuklab olishni tekshirish.

    Test admin login va test filialiga (filial-pw{code}) o'tishdan boshlanadi.

    Qadamlar (Allure step):
      1. Spot sahifasini ochish
      2. Шаблоны -> Создать -> nom + Продуктовое направление (Группа) -> Сохранить
      3. Yaratilgan shablon Spot'da tanlanib, Сформировать tugmasi ko'rinishini tekshirish
      4. Сформировать -> Spot2D.zip yuklanishi va bo'sh emasligini tekshirish
    """
    base = BasePage(page)
    template_name = f"Spot2D-pw{code}"

    authorization(page, who="admin")
    base.switch_filial(name=f"filial-pw{code}")

    with allure.step("1 - Spot sahifasini ochish"):
        base_url, _, rest = page.url.partition("#/")
        session_token = rest.split("/", 1)[0]
        page.goto(f"{base_url}#/{session_token}/trade/rep/integration/spot")
        expect(page.get_by_role("button", name="Шаблоны")).to_be_visible()

    with allure.step("2 - Yangi shablon yaratish"):
        page.locator('button[ng-click="selectSpotTemplate()"]').click()
        page.locator('button[ng-click="add()"]').click()
        base.input(ng_model="d.name", value=template_name)
        select_b_input_option(page, "product_groups", "Группа")
        page.locator('button[b-hotkey="save"]').click()

    with allure.step("3 - Yaratilgan shablon Spot'da tanlanganini tekshirish"):
        expect(page.get_by_role("button", name="Сформировать", exact=True)).to_be_visible()

    with allure.step("4 - Сформировать -> Spot2D.zip yuklanishi"):
        generate_and_verify_download(
            page,
            page.get_by_role("button", name="Сформировать", exact=True),
            expected_prefix="Spot2D",
            save_name=f"Spot2D_pw{code}.zip",
        )
