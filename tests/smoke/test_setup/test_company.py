import os
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Company")]

# Faqat company create/save flowiga tegishli lokal timeout: 10 minut.
COMPANY_SAVE_TIMEOUT = 600_000

# Faqat company form/control render bo'lishiga tegishli lokal timeout: 1 minut.
COMPANY_FORM_TIMEOUT = 60_000


def company_code_for(code):
    return f"autotest{code}".lower()


def _company_code_text_pattern(company_code):
    split_code_match = re.match(r"^([a-z]+)(\d+)$", company_code, re.IGNORECASE)
    if split_code_match:
        return re.compile(
            rf"{re.escape(split_code_match.group(1))}\s*{re.escape(split_code_match.group(2))}",
            re.IGNORECASE,
        )
    return re.compile(re.escape(company_code), re.IGNORECASE)


def _open_company_add(page):
    base = BasePage(page)
    page.get_by_role("button", name="Создать").click()
    base.expect_page(heading=re.compile(r"создание|Creation", re.IGNORECASE))

    form = page.locator("#companyForm").first
    base.text(root=form, timeout=COMPANY_FORM_TIMEOUT)
    expect(form.locator("smt-control").first).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)
    return form


def _template_control(page, label):
    label_pattern = re.compile(
        rf"^\s*{re.escape(label)}\s*(?:\*)?\s*$",
        re.IGNORECASE,
    )
    control = page.locator("#companyForm smt-control").filter(
        has=page.locator("label").filter(has_text=label_pattern)
    ).first
    expect(control).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)
    return control


def _products_card(page):
    products_title = page.get_by_role(
        "heading",
        name=re.compile(r"^products$", re.IGNORECASE),
    ).first
    expect(products_title).to_be_visible()
    products_card = products_title.locator(
        "xpath=ancestor::section[contains(@class, 'custom-card')][1]"
    )
    expect(products_card).to_be_visible()
    return products_card


def _product_switch(products_card, name):
    label = products_card.get_by_text(
        re.compile(rf"^\s*{re.escape(name)}\s*$", re.IGNORECASE)
    ).first
    expect(label).to_be_visible()
    switch = label.locator(
        "xpath=ancestor::*[.//*[@role='switch']][1]"
    ).get_by_role("switch").first
    expect(switch).to_be_visible()
    return switch


def _open_company_view(page, company_code_pattern):
    base = BasePage(page)
    base.grid(company_code_pattern, click=True)

    view_button = page.get_by_role(
        "button",
        name=re.compile(r"просмотреть|View", re.IGNORECASE),
    ).first
    expect(view_button).to_be_visible()
    view_button.click()
    base.expect_page(heading=re.compile(r"просмотр|View", re.IGNORECASE))


def _open_security_tab(page):
    base = BasePage(page)
    security_tab = page.get_by_text(
        re.compile(r"^\s*(Безопасность|Security)\s*$", re.IGNORECASE)
    ).first
    expect(security_tab).to_be_visible()
    security_tab.click()
    base.wait_for_loader()
    base.text("Политика лицензирования", root="body")


def _disable_concurrent_sessions(page):
    concurrent_label = page.get_by_text(
        "Ограничение количества одновременных сеансов",
        exact=True,
    ).first
    expect(concurrent_label).to_be_visible()
    concurrent_container = concurrent_label.locator(
        "xpath=ancestor::*[.//*[normalize-space()='Отключено'] and .//*[normalize-space()='1']][1]"
    ).first
    if concurrent_container.count() == 0:
        raise AssertionError("'Ограничение количества одновременных сеансов' control topilmadi")

    disabled_option = concurrent_container.get_by_role(
        "button",
        name="Отключено",
        exact=True,
    ).first
    if disabled_option.count() == 0:
        disabled_option = concurrent_container.get_by_text("Отключено", exact=True).first
    expect(disabled_option).to_be_visible()
    disabled_option.click()


def _disable_license_policy(page):
    base = BasePage(page)
    policy_label = page.get_by_text("Политика лицензирования", exact=True).first
    expect(policy_label).to_be_visible()
    policy_container = policy_label.locator(
        "xpath=ancestor::*[.//*[@role='switch'] or .//input[@type='checkbox'] "
        "or .//*[contains(@class,'switch')]][1]"
    ).first

    switch = policy_container.locator("[role='switch'], input[type='checkbox']").first
    if switch.count() > 0 and switch.is_visible():
        base.checkbox(locator=switch, checked=False)
        return

    off_option = policy_container.get_by_text(
        re.compile(r"^\s*(нет|no|off|отключено|выкл)\s*$", re.IGNORECASE)
    ).first
    expect(off_option).to_be_visible()
    off_option.click()


def _apply_security_settings(page):
    base = BasePage(page)
    _open_security_tab(page)
    _disable_concurrent_sessions(page)

    if os.getenv("DISABLE_LICENSE_POLICY", "").strip().lower() in {"1", "true", "yes", "on"}:
        _disable_license_policy(page)

    base.wait_for_loader(timeout=COMPANY_SAVE_TIMEOUT)
    save_button = page.get_by_role("button", name="Сохранить", exact=True).first
    if save_button.count() > 0 and save_button.is_visible():
        save_button.click()
        base.confirm_biruni()
        base.wait_for_loader(timeout=COMPANY_SAVE_TIMEOUT)


def run_company(page, code, save_data=None, company_code=None):
    """Testcase: company yaratish yoki mavjud company sozlamalarini yangilash.

    1. Head profilga kirish.
    2. Company ro'yxatini ochish.
    3. Company mavjudligini code bo'yicha tekshirish.
    4. Mavjud bo'lmasa yaratish formasini ochish.
    5. Majburiy maydonlarni to'ldirish.
    6. Majburiy shablonlarni tanlash.
    7. Trade va uning modullarini yoqish.
    8. Companyni saqlash.
    9. Yaratilgan companyni ro'yxatda tekshirish.
    10. Company viewni ochish.
    11. Security sozlamalarini qo'llash.
    12. Company code ni data storega saqlash.
    """
    base = BasePage(page)
    company_code = company_code or company_code_for(code)
    company_code_pattern = _company_code_text_pattern(company_code)

    with allure.step("2 - Company ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Компании")
        base.expect_page(url="/a2/biruni/md/company_list")

    with allure.step("4 - Yangi company formasini ochish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(url="company_add")

    with allure.step("5 - Majburiy maydonlarni to'ldirish"):
        base.input(label="Код сервера", value=company_code, root="app-main-info")
        base.input(label="Ф.И.О.", value=f"Autotest company {code}", root="app-main-info")
        base.b_input(label="Язык", value="Русский", clear=True, root="app-main-info")

    with allure.step("6 - Majburiy shablonlarni tanlash"):
        base.b_input(label="Маркировка", value="UZ Marking", root="app-template")
        base.b_input(label="План счетов", value="UZ COA", root="app-template")
        base.b_input(label="Банки", value="UZ BANK", root="app-template")

    with allure.step("7 - Trade va modullarni yoqish"):
        base.checkbox(label="trade", checked=True, root="app-project-module")
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
        for module in TRADE_MODULES:
            base.checkbox(label=module, checked=True, root="app-project-module")

    with allure.step("8 - Company saqlash va list ochilishini kutish"):
        base.expect_page(heading="Компании")

        base.save_and_expect_heading(
            expected_heading="Компании",
            confirm_text="",
            timeout=COMPANY_SAVE_TIMEOUT,
            expected_state="Company list ochilishi",
        )

    with allure.step("9 - Ro'yxatda yaratilgan company code ni tekshirish"):
        base.grid_controller(search=company_code)
        base.grid(company_code_pattern)

    with allure.step("10 - Company viewni ochish"):
        _open_company_view(page, company_code_pattern)

    with allure.step("11 - Company viewda security sozlamalarini qo'llash"):
        _apply_security_settings(page)

    with allure.step("12 - Company code ni data storega saqlash"):
        if save_data is not None:
            save_data("company_code", company_code)

    return company_code


@allure.title("Company yaratish")
def test_company(page, code, save_data, company_setup_enabled):
    """Testcase: company yaratish va majburiy sozlamalarni qo'llash.

    1. Head profil bilan Company ro'yxatini ochish.
    2. Company mavjud bo'lmasa maydonlar, shablonlar va Trade modullari bilan yaratish.
    3. Company viewda concurrent session va license policy sozlamalarini qo'llash.
    4. Company code ni keyingi setup/group testlari uchun saqlash.
    """
    if not company_setup_enabled:
        pytest.skip("Company setup faqat --create-company flagi bilan ishlaydi")

    authorization(page, who="head")
    run_company(page, code, save_data)
