import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_license import attach_license_policy_skip_note, license_policy_disabled
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

# ----------------------------------------------------------------------------------------------------------------------

def run_attach_license(page, code, logger):
    """Testcase: sotib olingan litsenziyani foydalanuvchiga (natural_person-pw{code}) ulash.

    1. Лицензии и документы bo'limini ochish.
    2. "ERP users" litsenziyasining biriktirilgan foydalanuvchilar sahifasini ochish.
    3. Oldin biriktirilgan foydalanuvchilar bo'lsa, ularni tozalash.
    4. Доступные пользователи sahifasini ochish.
    5. natural_person-pw{code} foydalanuvchisini topib ulash.
    6. Oynani yopib, biriktirilgan foydalanuvchilar sahifasiga qaytish.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa flow o'tkazib yuboriladi. `run_` Лицензии
    sahifasidagi login qilingan page qabul qiladi: setup zanjirida run_buy_license shu
    holatni qoldiradi, standalone wrapper esa preconditionni o'zi tayyorlaydi.
    """
    if license_policy_disabled():
        attach_license_policy_skip_note(logger, "Litsenziyani foydalanuvchiga ulash")
        return

    base = BasePage(page)

    base.switch_filial(name="Администрирование")
    base.navigate_to(tab="Главное", name="Лицензии")
    base.expect_page(heading="Лицензии")

    with allure.step("1 - Litsenziyalar va hujjatlar bo'limini ochish"):
        base.click(name="Лицензии и документы", role="link")
        base.text("Лицензии и документы")

    with allure.step("2 - ERP users litsenziyasining foydalanuvchilar sahifasini ochish"):
        base.grid("ERP users", click=True)
        base.click(name="Прикрепить пользователей")
        base.expect_page(heading="Прикрепленные пользователи")

    with allure.step("3 - Mavjud foydalanuvchilarni tozalash"):
        if not base.grid(state="empty", return_bool=True, root='b-grid[name="table"]'):
            base.grid(checkbox="all")
            base.click(name="Открепить")
            base.confirm_biruni("Открепить пользователей в количестве")
            base.wait_for_loader()
        base.grid(state="empty", root='b-grid[name="table"]')

    with allure.step("4 - Mavjud foydalanuvchilar sahifasini ochish"):
        base.click(name="Доступные")
        base.expect_page(heading="Доступные пользователи")
        base.wait_for_loader()

    with allure.step("5 - Foydalanuvchini litsenziyaga ulash"):
        # Bu sahifada 2 ta b-grid-controller bor: yashirin (table_license grid) va ko'rinadigan(table grid = mavjud userlar)
        base.grid_controller(search=f"natural_person-pw{code}", root="b-grid-controller:visible")
        base.grid(f"natural_person-pw{code}", root='b-grid[name="table"]', click=True)
        base.click(name="Прикрепить")
        base.confirm_biruni("Прикрепить пользователя")
        base.wait_for_loader()
        base.expect_page(heading="Доступные пользователи")

    with allure.step("6 - Oynani yopib, biriktirilgan foydalanuvchilarga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Лицензии")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga litsenziya ulash")
def test_attach_license(page, code, logger):
    authorization(page, who="admin")
    run_attach_license(page, code, logger)
