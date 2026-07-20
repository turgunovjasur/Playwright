import allure
from datetime import datetime

from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Report Group"), allure.feature("Integration Report"), allure.story("Integration Three")]
REPORT_RENDER_TIMEOUT = 60_000


# ----------------------------------------------------------------------------------------------------------------------

def _one_month_ago():
    """Bir oy oldingi sana, dd.mm.yyyy (datetime.now() - 1 oy)."""
    now = datetime.now()
    month = now.month - 1 or 12
    year = now.year - 1 if now.month == 1 else now.year
    day = min(now.day, 28)  # oy oxiri kunlari uchun xavfsiz
    return f"{day:02d}.{month:02d}.{year}"


# ----------------------------------------------------------------------------------------------------------------------

def run_report_integration_three_check(page, code, login=True):
    """Report-02: Integration №3 (NEON) report — 3 ta sheet render bo'lishini tekshirish.

    Login (login=True bo'lsa): admin login va test filialiga (filial-pw{code}) o'tish.

    Qadamlar (Allure step):
      1. trade/rep/integration/integration_three sahifasini ochish (menyuda yo'q — URL orqali)
      2. Настройки rejimini ochib, sozlamani saqlash (saveSettings)
      3. begin_date ga bir oy oldingi sana kiritib, datepicker yopilishini tekshirish
      4. Сформировать (HTML) -> loader tugagach hisobot iframe'i render bo'ladi
      5. Hisobot iframe'ida 3 ta sheet (tab 1->#sheet1, 2->#sheet2, 3->#sheet3) ko'rinishini tekshirish
    """
    base = BasePage(page)
    if login:
        authorization(page, who="admin")  # ADMIN login (checklist preconditioniga ko'ra)
        base.switch_filial(name=f"filial-pw{code}")

    with allure.step("1 - Integration №3 report sahifasini ochish"):
        base, _, rest = page.url.partition("#/")
        session_token = rest.split("/", 1)[0]
        page.goto(f"{base}#/{session_token}/trade/rep/integration/integration_three")
        expect(page.get_by_role("button", name="Настройки")).to_be_visible()

    with allure.step("2 - Настройки rejimi va sozlamani saqlash"):
        page.locator("button[ng-click=\"setRunMode('S')\"]").click()
        save_settings = page.locator('button[ng-click="saveSettings()"]')
        expect(save_settings).to_be_visible()
        save_settings.click()
        expect(save_settings).to_be_hidden()

    with allure.step("3 - begin_date (bir oy oldingi sana) kiritish va dropdown yopilishi"):
        begin_date = page.locator('input[ng-model="d.begin_date"]')
        begin_date.click()
        begin_date.fill(_one_month_ago())
        page.keyboard.press("Escape")
        expect(page.locator(".bootstrap-datetimepicker-widget")).to_be_hidden()

    with allure.step("4 - Сформировать (HTML hisobot) va loaderlar tugashini kutish"):
        page.locator("button.btn-primary[ng-click=\"run('html', true)\"]").click()
        base.wait_for_loader()

    with allure.step("5 - Hisobot iframe'ida 3 ta sheet tekshiriladi"):
        report = page.frame_locator('iframe[src*="integration_three"]')
        tabs = report.locator("a.nav-link")
        expect(report.locator("#sheet1")).to_be_visible(timeout=REPORT_RENDER_TIMEOUT)
        tabs.nth(1).click()
        expect(report.locator("#sheet2")).to_be_visible()
        tabs.nth(2).click()
        expect(report.locator("#sheet3")).to_be_visible()
