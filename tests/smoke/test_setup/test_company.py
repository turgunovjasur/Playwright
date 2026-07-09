import os
import re

import allure
import pytest
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Company")]

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
COMPANY_FORM_TIMEOUT = 60_000


def head_admin_email():
    value = os.getenv("HEAD_ADMIN_EMAIL", "").strip()
    if not value:
        raise AssertionError("--head-email majburiy: company yaratish uchun head profil emailini bering")
    return value


def head_admin_password():
    value = os.getenv("HEAD_ADMIN_PASSWORD", "").strip()
    if not value:
        raise AssertionError("--head-password majburiy: company yaratish uchun head profil parolini bering")
    return value


def company_code_for(code):
    return f"autotest{code}".lower()


def run_company(page, code, save_data=None, company_code=None):
    base = BasePage(page)
    company_code = company_code or company_code_for(code)
    company_code_pattern = re.compile(re.escape(company_code), re.IGNORECASE)
    split_code_match = re.match(r"^([a-z]+)(\d+)$", company_code, re.IGNORECASE)
    if split_code_match:
        company_code_pattern = re.compile(
            rf"{re.escape(split_code_match.group(1))}\s*{re.escape(split_code_match.group(2))}",
            re.IGNORECASE,
        )

    with allure.step("1 - Head profilga kirish"):
        authorization(page, email=head_admin_email(), password=head_admin_password())

    with allure.step("2 - Company ro'yxatiga o'tish"):
        base.navigate_to(tab="Главное", name="Компании")
        base.expect_page(heading=re.compile(r"Комп|Comp"))

    with allure.step("3 - Company mavjudligini tekshirish"):
        search = page.get_by_role("searchbox", name="Поиск")
        expect(search).to_be_visible()
        search.fill(company_code)
        search.press("Enter")
        base.wait_for_loader()

        company_exists = True
        try:
            expect(page.locator("body")).to_contain_text(company_code_pattern, timeout=3_000)
        except (AssertionError, PlaywrightTimeoutError):
            company_exists = False

    if not company_exists:
        with allure.step("4 - Yangi company formasini ochish"):
            page.get_by_role("button", name="Создать").click()
            base.wait_for_loader()
            expect(page.locator("h1").first).to_contain_text(re.compile(r"создание|Creation", re.IGNORECASE))
            form = page.locator("#companyForm").first
            expect(form).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)
            expect(form.locator("smt-control").first).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)

        with allure.step("5 - Majburiy maydonlarni to'ldirish"):
            for labels, value in (
                (("Код сервера", "Server code"), company_code),
                (("Название", "Наименование", "Company name", "Name"), f"Autotest company {code}"),
            ):
                label_pattern = re.compile(
                    rf"^\s*(?:{'|'.join(re.escape(label) for label in labels)})\s*(?:\*)?\s*$",
                    re.IGNORECASE,
                )
                control = page.locator("smt-control").filter(
                    has=page.locator("label").filter(has_text=label_pattern)
                ).first
                expect(control).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)
                textbox = control.get_by_role("textbox").first
                expect(textbox).to_be_visible()
                textbox.fill(value)
                expect(textbox).to_have_value(value)

            language_control = page.locator("smt-control").filter(
                has=page.locator("label").filter(
                    has_text=re.compile(r"^\s*Язык\s*(?:\*)?\s*$", re.IGNORECASE)
                )
            ).first
            expect(language_control.get_by_role("textbox").first).to_have_value(
                re.compile(r"Русский|Russian", re.IGNORECASE)
            )

        with allure.step("6 - Majburiy shablonlarni tanlash"):
            for label, option_text in (
                ("Маркировка", "UZ Marking"),
                ("План счетов", "UZ COA"),
                ("Банки", "UZ BANK"),
            ):
                control = page.locator("smt-control").filter(
                    has=page.locator("label").filter(
                        has_text=re.compile(rf"^\s*{re.escape(label)}\s*(?:\*)?\s*$", re.IGNORECASE)
                    )
                ).first
                expect(control).to_be_visible(timeout=COMPANY_FORM_TIMEOUT)

                trigger = control.locator("smt-select-trigger").first
                if trigger.count() > 0:
                    expect(trigger).to_be_visible()
                    trigger.click()
                else:
                    textbox = control.get_by_role("textbox").first
                    expect(textbox).to_be_visible()
                    textbox.click()

                overlay = page.locator(".cdk-overlay-container")
                expect(overlay).to_contain_text(option_text)
                option = overlay.locator("li, [role='option']").filter(has_text=option_text).first
                if option.count() == 0:
                    option = overlay.get_by_text(option_text, exact=True).first
                expect(option).to_be_visible()
                option.click()
                expect(control.get_by_role("textbox").first).to_have_value(re.compile(re.escape(option_text)))
                base.wait_for_loader()

        with allure.step("7 - Trade va modullarni yoqish"):
            products_title = page.get_by_role("heading", name=re.compile(r"^products$", re.IGNORECASE)).first
            expect(products_title).to_be_visible()
            products_card = products_title.locator("xpath=ancestor::section[contains(@class, 'custom-card')][1]")
            expect(products_card).to_be_visible()

            trade_label = products_card.get_by_text(re.compile(r"^\s*trade\s*$", re.IGNORECASE)).first
            expect(trade_label).to_be_visible()
            trade_switch = trade_label.locator(
                "xpath=ancestor::*[.//*[@role='switch']][1]"
            ).get_by_role("switch").first
            expect(trade_switch).to_be_visible()
            if trade_switch.get_attribute("aria-checked") != "true":
                trade_switch.click()
            expect(trade_switch).to_have_attribute("aria-checked", "true")
            base.wait_for_loader()
            expect(products_card).to_contain_text("Warehouse - Advanced", timeout=30_000)

            clicked_modules = []
            skipped_modules = []
            for module_name in TRADE_MODULES:
                module_label = products_card.get_by_text(
                    re.compile(rf"^\s*{re.escape(module_name)}\s*$", re.IGNORECASE)
                ).first
                expect(module_label).to_be_visible()
                module_switch = module_label.locator(
                    "xpath=ancestor::*[.//*[@role='switch']][1]"
                ).get_by_role("switch").first
                expect(module_switch).to_be_visible()
                if module_switch.get_attribute("aria-checked") != "true":
                    module_switch.click()
                    expect(module_switch).to_have_attribute("aria-checked", "true")
                    clicked_modules.append(module_name)
                else:
                    skipped_modules.append(module_name)

            module_result = {
                "clicked": clicked_modules,
                "skipped": skipped_modules,
                "moduleCount": len(clicked_modules) + len(skipped_modules),
            }
            allure.attach(
                str(module_result),
                name="company-trade-modules",
                attachment_type=allure.attachment_type.TEXT,
            )
            if module_result["moduleCount"] != len(TRADE_MODULES):
                raise AssertionError("Trade modullari to'liq yoqilmadi")
            base.wait_for_loader()

        with allure.step("8 - Company saqlash va list ochilishini kutish"):
            page.get_by_role("button", name="Сохранить").click()
            confirm_candidates = (
                page.locator("#biruniConfirm"),
                page.get_by_role("dialog").filter(has=page.get_by_role("button", name="да", exact=True)),
            )
            for confirm in confirm_candidates:
                try:
                    expect(confirm).to_be_visible(timeout=3_000)
                except (AssertionError, PlaywrightTimeoutError):
                    continue
                try:
                    expect(confirm).to_have_css("opacity", "1", timeout=3_000)
                except (AssertionError, PlaywrightTimeoutError):
                    pass
                confirm.get_by_role("button", name="да", exact=True).first.click()
                confirm.wait_for(state="hidden", timeout=30_000)
                break
            base.wait_for_loader(timeout=600_000)
            expect(page.locator("h1").first).to_contain_text(
                re.compile(r"^\s*(Компании|Companies)\s*$", re.IGNORECASE),
                timeout=600_000,
            )

        with allure.step("9 - Ro'yxatda yaratilgan company code ni tekshirish"):
            search = page.get_by_role("searchbox", name="Поиск")
            expect(search).to_be_visible()
            search.fill(company_code)
            search.press("Enter")
            base.wait_for_loader()
            try:
                expect(page.locator("body")).to_contain_text(company_code_pattern, timeout=10_000)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                allure.attach(
                    page.locator("body").inner_text(),
                    name="company-list-body-text",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise AssertionError(f"Company listda '{company_code}' topilmadi") from exc

    with allure.step("10 - Company viewni ochish"):
        page.get_by_text(company_code_pattern).first.click()
        view_opened = False
        buttons = page.get_by_role("button")
        for index in range(buttons.count()):
            button = buttons.nth(index)
            if not button.is_visible():
                continue
            button_text = re.sub(r"\s+", " ", button.inner_text()).strip()
            if "просмотреть" in button_text.lower():
                button.click()
                view_opened = True
                break
        if not view_opened:
            raise AssertionError("Company listda 'Просмотреть' button topilmadi")
        base.wait_for_loader()
        expect(page.locator("h1").first).to_contain_text(re.compile(r"просмотр|View", re.IGNORECASE))

    with allure.step("11 - Company viewda security sozlamalarini qo'llash"):
        for tab_name in ("Безопасность", "Security"):
            tab = page.get_by_text(tab_name, exact=True).first
            if tab.count() == 0:
                continue
            expect(tab).to_be_visible()
            tab.click()
            base.wait_for_loader()
            expect(page.locator("body")).to_contain_text("Политика лицензирования")
            break
        else:
            raise AssertionError("Company viewda Security/Безопасность tab topilmadi")

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
        disabled_option = concurrent_container.get_by_role("button", name="Отключено", exact=True).first
        if disabled_option.count() == 0:
            disabled_option = concurrent_container.get_by_text("Отключено", exact=True).first
        expect(disabled_option).to_be_visible()
        disabled_option.click()

        if os.getenv("DISABLE_LICENSE_POLICY", "").strip().lower() in {"1", "true", "yes", "on"}:
            policy_label = page.get_by_text("Политика лицензирования", exact=True).first
            expect(policy_label).to_be_visible()
            policy_container = policy_label.locator(
                "xpath=ancestor::*[.//*[@role='switch'] or .//input[@type='checkbox'] or .//*[contains(@class,'switch')]][1]"
            ).first
            switch = policy_container.get_by_role("switch").first
            if switch.count() > 0 and switch.is_visible():
                if switch.get_attribute("aria-checked") == "true":
                    switch.click(timeout=5_000)
                expect(switch).to_have_attribute("aria-checked", "false")
            else:
                off_option = policy_container.get_by_text(
                    re.compile(r"^\s*(нет|no|off|отключено|выкл)\s*$", re.IGNORECASE)
                ).first
                expect(off_option).to_be_visible()
                off_option.click()

        base.wait_for_loader(timeout=600_000)
        save_button = page.get_by_role("button", name="Сохранить", exact=True).first
        if save_button.count() > 0 and save_button.is_visible():
            save_button.click()
            confirm = page.locator("#biruniConfirm")
            try:
                expect(confirm).to_be_visible(timeout=3_000)
                expect(confirm).to_have_css("opacity", "1", timeout=3_000)
                confirm.get_by_role("button", name="да", exact=True).click()
                confirm.wait_for(state="hidden", timeout=30_000)
            except (AssertionError, PlaywrightTimeoutError):
                pass
            base.wait_for_loader(timeout=600_000)

    with allure.step("12 - Company code ni data storega saqlash"):
        if save_data is not None:
            save_data("company_code", company_code)

    return company_code


@allure.title("Company yaratish")
def test_company(page, code, save_data, company_setup_enabled):
    """
    1. --head-email/--head-password bilan head profilga kirish.
    2. Главное -> Компании ro'yxatida yangi company yaratish yoki mavjudini ochish.
    3. Company maydonlari, shablonlar, trade modullari va security sozlamalarini tekshirish.
    4. Company code ni data storega saqlash.
    """
    if not company_setup_enabled:
        pytest.skip("Company setup faqat --create-company flagi bilan ishlaydi")
    run_company(page, code, save_data)
