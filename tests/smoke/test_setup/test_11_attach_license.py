import re
from urllib.parse import urlsplit

import allure

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_setup.flow_setup.flow_license import open_admin_licenses, skip_license_flow_if_needed
from tests.smoke.test_setup.flow_setup.flow_license import xtrade_license_rows
from utils.data_store import load_data
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

    open_admin_licenses(page, base)

    with allure.step("1 - Litsenziyalar va hujjatlar bo'limini ochish"):
        base.tab("Лицензии и документы", section=True)
        base.text("Лицензии и документы")

    with allure.step("2 - ERP users litsenziyasining foydalanuvchilar sahifasini ochish"):
        xtrade = urlsplit(page.url).path.startswith("/xtrade/a2/")
        if xtrade:
            purchase = load_data("ui_purchased_license")
            assert purchase["code"] == str(code), "Litsenziya joriy setup runiga tegishli emas"
            base.grid("ERP users")
            row = xtrade_license_rows(page).filter(has=page.get_by_text(purchase["created_on"], exact=True))
            assert row.count() == 1, "Joriy xaridning yagona qatori topilmadi"
            row.get_by_text("ERP users", exact=True).click()
        else:
            base.grid("ERP users", click=True)
        base.click(name="Прикрепить пользователей")
        base.expect_page(heading=re.compile(r"^\s*(?:Прикрепленные пользователи|Пользователи прикрепленные к лицензии)\s*$"), url="biruni/kl/license_user_list")
        base.wait_for_loader()

    with allure.step("3 - Mavjud foydalanuvchilarni tozalash"):
        # A fresh license starts empty; never detach people from an unexpected assignment.
        if not xtrade and not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Открепить")
            base.confirm_biruni(re.compile(r"Открепить пользователей в количестве|Detach \d+ user\(s\)\?"))
            base.wait_for_loader()
        base.grid(state="empty")

    with allure.step("4 - Mavjud foydalanuvchilar sahifasini ochish"):
        base.tab("Доступные")
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
        if xtrade:
            base.tab("Прикрепленные")
            base.grid_controller(search=f"natural_person-pw{code}")
            base.grid(f"natural_person-pw{code}", f"user-pw{code}")
            # This full-page A2 list has no Close button.
            base.navigate_to(tab="Главное", name="Лицензии")
        else:
            base.click(name="Закрыть")
        base.expect_page(heading="Лицензии", url="biruni/kl/license_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Foydalanuvchiga litsenziya ulash")
def test_attach_license(page, code, logger):
    authorization(page, who="admin")
    run_attach_license(page, code, logger)
