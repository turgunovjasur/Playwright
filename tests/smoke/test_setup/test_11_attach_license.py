import re

import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.flow_setup.flow_license import skip_license_flow_if_needed
from utils.base_pages.auto_base_page import AutoBasePage

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

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa flow o'tkazib yuboriladi. `run_` login
    qilingan page qabul qiladi va Лицензии sahifasiga o'zi navigatsiya qiladi;
    standalone wrapper admin login preconditionini tayyorlaydi.
    """
    if skip_license_flow_if_needed(logger, "Litsenziyani foydalanuvchiga ulash"):
        return

    base = AutoBasePage(page)

    base.switch_filial(name="Администрирование")
    base.navigate_to(tab="Главное", name="Лицензии")
    base.expect_page(heading="Лицензии", url="biruni/kl/license_list")

    with allure.step("1 - Litsenziyalar va hujjatlar bo'limini ochish"):
        base.tab("Лицензии и документы", section=True)
        base.text("Лицензии и документы")

    with allure.step("2 - ERP users litsenziyasining foydalanuvchilar sahifasini ochish"):
        base.grid("ERP users", click=True)
        base.click(name="Прикрепить пользователей")
        base.expect_page(heading=re.compile(r"^\s*(?:Прикрепленные пользователи|Пользователи прикрепленные к лицензии)\s*$"), url="biruni/kl/license_user_list")
        base.wait_for_loader()

    with allure.step("3 - Mavjud foydalanuvchilarni tozalash"):
        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Открепить")
            base.confirm_biruni(re.compile(r"Открепить пользователей в количестве|Detach \d+ user\(s\)\?"))
            base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("4 - Mavjud foydalanuvchilar sahifasini ochish"):
        base.click(name="Доступные")
        base.expect_page(heading=re.compile(r"^\s*(?:Доступные пользователи|Пользователи прикрепленные к лицензии)\s*$"))  # navigation: same-url - Available tab updates users inside the open license-user page.
        base.wait_for_loader()

    with allure.step("5 - Foydalanuvchini litsenziyaga ulash"):
        base.grid_controller(search=f"natural_person-pw{code}")
        base.grid(f"natural_person-pw{code}", click=True)
        base.click(name="Прикрепить")
        base.confirm_biruni(re.compile(r"Прикрепить (?:пользователя|форму)"))
        base.wait_for_loader()
        base.grid(state="empty")
        base.expect_page(heading=re.compile(r"^\s*(?:Доступные пользователи|Пользователи прикрепленные к лицензии)\s*$"))  # navigation: same-url - Attaching a user refreshes the current available-users tab.

    with allure.step("6 - Oynani yopib, biriktirilgan foydalanuvchilarga qaytish"):
        base.click(name="Закрыть")
        base.expect_page(heading="Лицензии", url="biruni/kl/license_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga litsenziya ulash")
def test_attach_license(page, code, logger):
    authorization(page, who="admin")
    run_attach_license(page, code, logger)
