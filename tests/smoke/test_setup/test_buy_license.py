import os
import re
from datetime import datetime, timedelta

import allure
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("License")]

MANDATORY_LICENSE_COUNT = "5"
REGULAR_LICENSE_COUNT = "1"
MANDATORY_LICENSE_ROW_RE = re.compile(r"Smartup ERP:\s*Базовый пользователь\s*\(Обязательный\)")
REGULAR_LICENSE_ROW_RE = re.compile(r"Smartup ERP:\s*Базовый пользователь\s+За пользователя")

# ----------------------------------------------------------------------------------------------------------------------

def _env_flag(name):
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _license_policy_disabled():
    return _env_flag("DISABLE_LICENSE_POLICY")


def _attach_license_skip_note(logger, step_name):
    message = (
        f"{step_name} o'tkazib yuborildi: --disable-license-policy berilgani uchun "
        "companyda Политика лицензирования o'chirilgan."
    )
    allure.attach(message, name="license-policy-disabled", attachment_type=allure.attachment_type.TEXT)
    logger.info(message)


def _select_date(page, ng_model, option="custom", day=None, add_days=0):
    today = datetime.today()

    if option == "first":
        target = today.replace(day=1)
    elif option == "last":
        next_month = today.replace(day=28) + timedelta(days=4)
        target = next_month - timedelta(days=next_month.day)
    elif option == "today":
        target = today + timedelta(days=add_days)
    else:
        target = today.replace(day=day)

    page.locator(f'input[ng-model="{ng_model}"]').click()
    page.get_by_role("cell", name=str(target.day), exact=True).first.click()


def _prepare_license_purchase(page, base):
    if not page.get_by_role("button", name="Купить").is_visible():
        page.get_by_role("link", name="Покупка").click()

    base.b_input(ng_model="purchase.payer.name", value="AUTOTEST GWS", clear=True)
    base.b_input(ng_model="purchase.contract_name", value="Договор № bn от 01.01.2025", clear=True)
    _select_date(page, ng_model="purchase.begin_date", option="today")
    base.wait_for_loader()


def _optional_license_row(page, row_name, timeout=3_000):
    row = page.get_by_role("row", name=row_name).first
    try:
        row.wait_for(state="visible", timeout=timeout)
        return row
    except PlaywrightTimeoutError:
        return None


def _license_row(page, row_name):
    row = page.get_by_role("row", name=row_name).first
    expect(row).to_be_visible()
    return row


def _close_extended_alert(page):
    alert = page.locator("#biruniAlertExtended")
    expect(alert).to_be_visible()
    alert.locator("button.close").click()
    alert.wait_for(state="hidden")


def _buy_license_row(
    page,
    base,
    row,
    count,
    logger,
    success_message,
    editable_quantity=True,
):
    if editable_quantity:
        quantity = row.get_by_role("textbox").first
        quantity.fill(count)
        expect(quantity).to_have_value(count)
    else:
        expect(page.locator("body")).to_contain_text(f"Итого лицензий: {count}")

    page.get_by_role("button", name="Купить").click()
    terms = page.locator("span").filter(has_text="Я ознакомился с тем").first
    expect(terms).to_be_visible()
    terms.click()
    page.get_by_role("button", name="Да", exact=True).click()
    base.wait_for_loader()
    # Sotib olingach Smartup natijani #biruniAlertExtended (kvitansiya) modalida ko'rsatadi;
    # keyingi sotib olish yoki run_attach_license uni bloklamasligi uchun (chiqsa) yopiladi.
    try:
        page.locator("#biruniAlertExtended").wait_for(state="visible", timeout=5_000)
        _close_extended_alert(page)
    except PlaywrightTimeoutError:
        pass
    logger.info(success_message)


# ----------------------------------------------------------------------------------------------------------------------

def run_buy_license(page, logger):
    """Testcase: Администрирование filialida litsenziya sotib olish.

    1. Администрирование filialiga o'tib, Лицензии sahifasini ochish.
    2. Kompaniya balansi musbatligini tekshirish.
    3. Покупка formasida to'lovchi/kontrakt/sanani tanlab, majburiy (agar chiqqan bo'lsa)
       va oddiy bazaviy litsenziyalarni sotib olish.

    DISABLE_LICENSE_POLICY yoqilgan bo'lsa — butun step skip qilinadi.
    switch_filial shu run_ ichida: setup zanjirida bu — Администрирование filialiga
    o'tuvchi birinchi qadam (chain shunga suyanadi). authorization esa test_buy_license
    wrapper'ida (standalone/debug uchun).
    """
    base = BasePage(page)

    if _license_policy_disabled():
        _attach_license_skip_note(logger, "Litsenziya sotib olish")
        return

    with allure.step("1 - Litsenziyalar sahifasiga o'tish"):
        base.switch_filial(name="Администрирование")
        base.navigate_to(tab="Главное", name="Лицензии")
        base.expect_page(heading="Лицензии")

    with allure.step("2 - Balansni tekshirish"):
        balance_locator = page.locator('p.text-success[ng-if="q.balance > 0"]')
        try:
            balance_locator.wait_for(state="visible", timeout=5_000)
            logger.info("Balans musbat — Success")
        except Exception:
            logger.fail("Balans musbat emas yoki element topilmadi!", raise_error=True)

    with allure.step("3 - Litsenziya sotib olish"):
        _prepare_license_purchase(page, base)

        # Majburiy litsenziya soni avtomatik hisoblanadi va cartga qo'shiladi: talab bo'lsa
        # "Итого лицензий: {MANDATORY_LICENSE_COUNT}", bu davr uchun allaqachon olingan bo'lsa
        # "Итого лицензий: 0" ko'rinadi. Idempotentlik uchun 0 bo'lsa sotib olish o'tkazib yuboriladi.
        mandatory_row = _optional_license_row(page, MANDATORY_LICENSE_ROW_RE)
        mandatory_already_bought = page.get_by_text("Итого лицензий: 0").is_visible()
        if mandatory_row and not mandatory_already_bought:
            with allure.step("3.1 - Majburiy bazaviy litsenziyalarni sotib olish"):
                _buy_license_row(
                    page,
                    base,
                    mandatory_row,
                    MANDATORY_LICENSE_COUNT,
                    logger,
                    "Majburiy bazaviy litsenziyalar olindi",
                    editable_quantity=False,
                )
                _prepare_license_purchase(page, base)
        else:
            logger.info("Majburiy bazaviy litsenziya talab qilinmaydi (bu davr uchun 0 yoki chiqmagan)")

        with allure.step("3.2 - Oddiy bazaviy litsenziya sotib olish"):
            row = _license_row(page, REGULAR_LICENSE_ROW_RE)
            _buy_license_row(page, base, row, REGULAR_LICENSE_COUNT, logger, "Litsenziya olindi")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Litsenziya sotib olish")
def test_buy_license(page, logger):
    authorization(page, who='admin')
    run_buy_license(page, logger)
