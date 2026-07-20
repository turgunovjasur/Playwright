import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import attach_license_policy_skip_note, license_policy_disabled
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

# ----------------------------------------------------------------------------------------------------------------------

def run_attach_license(page, code, logger):
    """Testcase: sotib olingan litsenziyani foydalanuvchiga (natural_person-pw{code}) ulash.

    1. Лицензии и документы bo'limini ochish.
    2. "ERP users" litsenziyasini ochib, "Прикрепить пользователей" oynasiga o'tish.
    3. Oldin biriktirilgan foydalanuvchilar bo'lsa — ularni Открепить bilan tozalash.
    4. "Доступные" ro'yxatidan natural_person-pw{code} ni topib Прикрепить bilan ulash.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa — skip. Лицензии sahifasida bo'lish shart:
    setup zanjirida run_buy_license shu holatni qoldiradi; standalone uchun
    test_attach_license wrapper switch_filial(Администрирование) + navigate_to(Лицензии) qiladi.
    """
    if license_policy_disabled():
        attach_license_policy_skip_note(logger, "Litsenziyani foydalanuvchiga ulash")
        return

    base = BasePage(page)

    with allure.step("1 - Litsenziyalar va hujjatlar sahifasiga o'tish"):
        base.switch_filial(name="Администрирование")
        base.navigate_to(tab="Главное", name="Лицензии")
        base.expect_page(heading="Лицензии")
        page.get_by_role("link", name="Лицензии и документы").click()
        expect(page.locator("b-page")).to_contain_text("Лицензии и документы")

    with allure.step("2 - ERP users litsenziyasini ochish"):
        base.grid("ERP users", click=True)
        page.get_by_role("button", name="Прикрепить пользователей").click()
        base.expect_page(heading="Прикрепленные пользователи")

    with allure.step("3 - Mavjud foydalanuvchilarni tozalab, yangi foydalanuvchini ulash"):
        if not base.grid(root='b-grid[name="table"]', is_empty=True):
            base.grid(checkbox="all")
            page.get_by_role("button", name="Открепить").click()
            base.confirm_biruni("Открепить пользователей в количестве")

        page.get_by_role("button", name="Доступные").click()
        base.expect_page(heading="Доступные пользователи")
        base.wait_for_loader(timeout=120_000)
        # Bu sahifada 2 ta b-grid-controller bor: yashirin (table_license grid) va ko'rinadigan(table grid = mavjud userlar)
        base.grid_controller(search=f"natural_person-pw{code}", root="b-grid-controller:visible")
        base.grid(f"natural_person-pw{code}", root='b-grid[name="table"]', click=True)
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni("Прикрепить пользователя")
        base.wait_for_loader(timeout=120_000)

        base.expect_page(heading="Доступные пользователи")
        page.get_by_role("button", name="Закрыть").click()

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga litsenziya ulash")
def test_attach_license(page, code, logger):
    authorization(page, who='admin')
    run_attach_license(page, code, logger)
