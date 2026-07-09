import json
import re
from datetime import datetime, timedelta

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    flow_order_final_page,
    flow_order_main_page,
    flow_order_product_page,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_open_order_list, flow_order_list
from utils.base_page import BasePage

B_GROUP_ORDER_INVOICE_REPORT_OPTIONS = [
    "Загрузочный лист",
    "Лист заказов № 3",
    "Лист заказов № 6",
    "Лист заказов №1",
    "Накладная №3(2007)",
    "Накладная №4(2012)",
    "Накладная №5 (2018)",
    "Накладная №7",
    "Общая сумма",
    "Общая сумма возврата",
    "Перечень форма 1",
    "Счет на оплату",
    "Счет-фактура с НДС",
    "Счет-фактура №1(2004)",
    "ТТН",
    "Требование на отпуск форма 1",
    "Чек-лист (80 мм)",
]
B_GROUP_ORDER_INVOICE_DOWNLOAD_OPTIONS = ["Экспортировать заказ"]
B_GROUP_ORDER_INVOICE_OPEN_ONLY_OPTIONS = {"Чек-лист (80 мм)"}
B_GROUP_ORDER_INVOICE_REPORT_DATA_CHECKS = {
    "Загрузочный лист": ("product", "total"),
    "Лист заказов № 3": ("product", "total"),
    "Лист заказов № 6": ("product", "total"),
    "Лист заказов №1": ("product", "total"),
    "Накладная №3(2007)": ("product", "total"),
    "Накладная №4(2012)": ("product", "total"),
    "Накладная №5 (2018)": ("product", "total"),
    "Накладная №7": ("product", "total"),
    "Общая сумма": ("product", "total"),
    "Общая сумма возврата": (),
    "Перечень форма 1": ("product", "total"),
    "Счет на оплату": ("client", "product", "total"),
    "Счет-фактура с НДС": ("client", "product", "total"),
    "Счет-фактура №1(2004)": ("client", "product", "total"),
    "ТТН": ("product", "total"),
    "Требование на отпуск форма 1": (),
}
B_GROUP_ORDER_INVOICE_REPORT_CONTROL_RE = re.compile(r"(печать|распечатать|excel)", re.IGNORECASE)


def _normalize_report_text(value):
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def _contains_amount(value, amount):
    expected_digits = re.sub(r"\D", "", amount)
    actual_digits = re.sub(r"\D", "", value)
    return bool(expected_digits and expected_digits in actual_digits)


def _invoice_dropdown_option_names(page):
    return page.locator(".dropdown-menu:visible a.dropdown-item").evaluate_all(
        """elements => elements
            .map(element => (element.innerText || element.textContent || "").replace(/\\s+/g, " ").trim())
            .filter(Boolean)
        """
    )


def _open_order_invoice_dropdown(page, client):
    flow_open_order_list(page)
    expect(page.locator("#kt_content")).to_contain_text(client, timeout=120_000)
    flow_order_list(page, find_row=client)
    invoice_button = page.locator("#trade81-button-report_one").first
    expect(invoice_button).to_be_visible()
    invoice_button.click()
    expect(page.locator(".dropdown-menu:visible a.dropdown-item").first).to_be_visible()


def _assert_invoice_dropdown_options(page):
    expected_options = B_GROUP_ORDER_INVOICE_REPORT_OPTIONS + B_GROUP_ORDER_INVOICE_DOWNLOAD_OPTIONS
    actual_options = _invoice_dropdown_option_names(page)
    missing = [option for option in expected_options if option not in actual_options]
    if missing:
        allure.attach(
            json.dumps(actual_options, ensure_ascii=False, indent=2),
            name="actual-invoice-dropdown-options",
            attachment_type=allure.attachment_type.JSON,
        )
        raise AssertionError(f"Накладные dropdown optionlari topilmadi: {', '.join(missing)}")


def _assert_report_loaded(report_page, option_name):
    expect(report_page.locator("body")).to_contain_text(B_GROUP_ORDER_INVOICE_REPORT_CONTROL_RE, timeout=60_000)
    report_text = report_page.locator("body").inner_text(timeout=60_000)
    normalized_text = _normalize_report_text(report_text)
    normalized_lower = normalized_text.lower()
    if not any(marker in normalized_lower for marker in ("печать", "распечатать", "excel")):
        allure.attach(
            report_text[:4_000],
            name=f"{option_name}-report-text",
            attachment_type=allure.attachment_type.TEXT,
        )
        raise AssertionError(f"{option_name} report sahifasi ochildi, lekin print/export control ko'rinmadi")
    return normalized_text


def _assert_report_contains_expected_data(option_name, report_text, expected_data):
    missing = []
    for check_name in B_GROUP_ORDER_INVOICE_REPORT_DATA_CHECKS.get(option_name, ()):
        expected_value = expected_data.get(check_name, "")
        if not expected_value:
            continue
        if check_name == "total":
            if not _contains_amount(report_text, expected_value):
                missing.append(f"{check_name}={expected_value}")
        elif expected_value not in report_text:
            missing.append(f"{check_name}={expected_value}")

    if missing:
        allure.attach(
            report_text[:6_000],
            name=f"{option_name}-report-text",
            attachment_type=allure.attachment_type.TEXT,
        )
        raise AssertionError(f"{option_name} reportida kutilgan order data topilmadi: {', '.join(missing)}")


def _invoice_report_option_locator(page, option_name):
    exact_option_re = re.compile(rf"^\s*{re.escape(option_name)}\s*$")
    span_option = page.locator(".dropdown-menu:visible span").filter(has_text=exact_option_re).first
    if span_option.count() > 0:
        return span_option
    return page.locator(".dropdown-menu:visible a.dropdown-item").filter(has_text=exact_option_re).first


def _install_report_print_guard(page):
    page.context.add_init_script(
        """
        (() => {
            window.__smartupPrintCalls = 0;
            Object.defineProperty(window, 'print', {
                configurable: true,
                writable: true,
                value: () => {
                    window.__smartupPrintCalls += 1;
                },
            });
        })();
        """
    )


def _open_invoice_report_and_assert(page, client, option_name, expected_data):
    _open_order_invoice_dropdown(page, client)
    option = _invoice_report_option_locator(page, option_name)
    expect(option).to_be_visible()
    _install_report_print_guard(page)

    report_page = None
    try:
        with page.context.expect_page(timeout=30_000) as report_info:
            option.click()
        report_page = report_info.value
        report_page.wait_for_load_state("domcontentloaded", timeout=60_000)
        report_page.bring_to_front()
        if option_name in B_GROUP_ORDER_INVOICE_OPEN_ONLY_OPTIONS:
            return report_page.url
        try:
            report_page.wait_for_load_state("networkidle", timeout=10_000)
        except PlaywrightTimeoutError:
            pass
        report_text = _assert_report_loaded(report_page, option_name)
        _assert_report_contains_expected_data(option_name, report_text, expected_data)
        return report_page.url
    except PlaywrightTimeoutError as exc:
        raise AssertionError(f"{option_name} report popup oynasi ochilmadi") from exc
    except Exception:
        if report_page and not report_page.is_closed():
            try:
                allure.attach(report_page.url, name=f"{option_name}-report-url", attachment_type=allure.attachment_type.TEXT)
                allure.attach(
                    report_page.screenshot(full_page=True),
                    name=f"{option_name}-report-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as attach_exc:
                allure.attach(str(attach_exc), name="report-attach-error", attachment_type=allure.attachment_type.TEXT)
        raise
    finally:
        if report_page and not report_page.is_closed():
            report_page.close()


def _download_invoice_export_and_assert(page, client, option_name):
    _open_order_invoice_dropdown(page, client)
    option = _invoice_report_option_locator(page, option_name)
    expect(option).to_be_visible()

    with page.expect_download(timeout=60_000) as download_info:
        option.click()
    download = download_info.value
    failure = download.failure()
    if failure:
        raise AssertionError(f"{option_name} download xato bilan tugadi: {failure}")
    suggested_filename = download.suggested_filename
    if not suggested_filename:
        raise AssertionError(f"{option_name} download filename qaytarmadi")
    allure.attach(suggested_filename, name=f"{option_name}-download-filename", attachment_type=allure.attachment_type.TEXT)
    return suggested_filename


def _save_visible_confirm_if_open(page):
    confirm = page.get_by_role("dialog").filter(has=page.get_by_role("button", name="да"))
    try:
        expect(confirm).to_be_visible(timeout=3_000)
    except Exception:
        return

    confirm.get_by_role("button", name="да").click()
    confirm.wait_for(state="hidden")


def _input_validation_state_by_label(page, label, index=0):
    base = BasePage(page)
    input_el = base.input(label=label, index=index)
    return {
        "value": input_el.input_value(),
        "className": input_el.get_attribute("class") or "",
        "ariaInvalid": input_el.get_attribute("aria-invalid") or "",
    }


def _input_has_non_neutral_border_by_label(page, label, neutral_colors):
    base = BasePage(page)
    input_el = base.input(label=label)
    for color in neutral_colors:
        try:
            expect(input_el).to_have_css("border-color", color, timeout=200)
            return False
        except AssertionError:
            continue
    return True


def _page_text_is_present(page, text, timeout=3_000):
    try:
        expect(page.locator("body")).to_contain_text(text, timeout=timeout)
        return True
    except Exception:
        return False


def _page_text_occurrences(page, text):
    return page.locator("body").inner_text().count(text)


def _order_id_from_current_url(page):
    order_id = re.search(r"[?&]deal_id=(\d+)", page.url)
    if not order_id:
        raise AssertionError(f"Order id URL ichidan topilmadi: {page.url}")
    return order_id.group(1)


def _expect_text_visible(page, text):
    expect(page.locator("body")).to_contain_text(text)


def _click_visible_text(page, text):
    _expect_text_visible(page, text)
    page.get_by_text(text, exact=True).first.click()


def _close_error_dialog(page, expected_text=None):
    dialog = page.get_by_role("dialog").filter(has_text="Ошибка")
    expect(dialog).to_be_visible()
    if expected_text:
        expect(dialog).to_contain_text(expected_text)
    dialog.get_by_role("button").first.click()
    dialog.wait_for(state="hidden")


def _save_order_from_final_page(page):
    # Order wizard save tugmasi ikonkali: exact accessible name mos kelmaydi -> exact=False
    base = BasePage(page)
    page.get_by_role("button", name="Сохранить", exact=False).first.click()
    base.confirm_biruni()
    base.wait_for_loader()
    base.expect_page(heading="Заказы")


def _assert_save_blocked_without_confirm(page, expected_date=None):
    page.get_by_role("button", name="Сохранить").click()
    confirm = page.get_by_role("dialog").filter(has=page.get_by_role("button", name="да"))
    try:
        expect(confirm).to_be_visible(timeout=1_500)
    except Exception:
        try:
            _close_error_dialog(page)
            return
        except Exception:
            invalid_inputs = page.locator("input:invalid")
            if invalid_inputs.count() > 0:
                details = []
                for index in range(invalid_inputs.count()):
                    input_item = invalid_inputs.nth(index)
                    details.append(
                        {
                            "id": input_item.get_attribute("id"),
                            "name": input_item.get_attribute("name"),
                            "value": input_item.input_value(),
                            "min": input_item.get_attribute("min"),
                            "max": input_item.get_attribute("max"),
                        }
                    )
                allure.attach(
                    json.dumps(details, ensure_ascii=False, indent=2),
                    name="invalid-consignment-inputs",
                    attachment_type=allure.attachment_type.JSON,
                )
                return
            if expected_date:
                expect(page).to_have_url(re.compile(r".*/order\+edit"))
                state = _input_validation_state_by_label(page, "Дата оплаты по консигнации")
                allure.attach(
                    json.dumps(state, ensure_ascii=False, indent=2),
                    name="consignment-date-validation-state",
                    attachment_type=allure.attachment_type.JSON,
                )
                neutral_border_colors = {
                    "rgb(206, 212, 218)",
                    "rgb(226, 230, 239)",
                    "rgb(228, 233, 242)",
                }
                if state["value"] == expected_date and _input_has_non_neutral_border_by_label(
                    page,
                    "Дата оплаты по консигнации",
                    neutral_border_colors,
                ):
                    return
            raise AssertionError(
                "Save confirm chiqmadi, lekin aniq error dialog ham topilmadi. "
                "Invalid konsignatsiya sanasi uchun explicit validation assert kerak."
            )
    raise AssertionError("30 kundan katta konsignatsiya sanasi qabul qilindi")


def _click_consignment_add_button(page):
    label = page.get_by_text("Дата оплаты по консигнации", exact=True).first
    expect(label).to_be_visible()
    add_button = page.locator('button[ng-click="addConsignment()"]:visible').first
    expect(add_button).to_be_visible()
    add_button.click()


def _open_order_settings(page):
    base = BasePage(page)
    base.navigate_to(tab="Главное", name="Настройки системы")
    base.expect_page(heading="Настройки системы")
    page.get_by_role("link", name="Заказ").click()
    expect(page.get_by_text("Разрешить выдачу консигнации", exact=True)).to_be_visible()


def _enable_consignment_for_orders(page):
    _open_order_settings(page)
    base = BasePage(page)

    base.checkbox(label="Разрешить выдачу консигнации", checked=True)
    base.input(label="Лимит консигнации (в днях)", value="30", expect_value="30", press_tab=True)

    page.get_by_role("button", name="Сохранить").first.click()
    _save_visible_confirm_if_open(page)

    base.checkbox(label="Разрешить выдачу консигнации", expect_checked=True)
    base.input(label="Лимит консигнации (в днях)", expect_value="30")


def _cancel_existing_client_orders_if_any(page, code):
    flow_open_order_list(page)

    for _ in range(20):
        if not _page_text_is_present(page, f"natural_client-pw{code}", timeout=2_000):
            break

        flow_order_list(page, find_row=f"natural_client-pw{code}", status="Отменен")
        flow_open_order_list(page)

    if _page_text_is_present(page, f"natural_client-pw{code}", timeout=2_000):
        raise AssertionError(f"natural_client-pw{code} uchun active orderlar tozalanmadi")


def _consignment_day_limit(page):
    """
    Order final (3-) formasidagi AngularJS scope'dan haqiqiy konsignatsiya kun limitini o'qiydi.

    Limit DOM textida yoki date input atributida ko'rinmaydi — u faqat scope'dagi
    `q.consignment_day_limit` da turadi (MCP bilan tasdiqlangan). Eski stub `today + 30` ni
    `delivery_date + 30` bilan solishtirib, ikki sana mos kelmaganda flaky fail berardi.
    """
    limit = page.evaluate(
        """() => {
            if (typeof angular === 'undefined') return null;
            const el = Array.from(document.querySelectorAll('input[ng-model="item.consignment_date"]'))
                .find(node => node.offsetParent !== null);
            if (!el) return null;
            let scope = angular.element(el).scope();
            while (scope) {
                if (scope.q && scope.q.consignment_day_limit !== undefined && scope.q.consignment_day_limit !== '') {
                    return String(scope.q.consignment_day_limit);
                }
                scope = scope.$parent;
            }
            return null;
        }"""
    )
    if not limit:
        raise AssertionError(
            "Konsignatsiya kun limiti (q.consignment_day_limit) order final formasida topilmadi"
        )
    return limit


def run_b_group_create_order_with_consignment_limit(page, code, save_data, login=True):
    """
    Testcase:
    1. User sifatida tizimga kirish.
    2. Главное > Настройки системы > Заказ tabida Разрешить выдачу консигнации yoqiladi.
    3. Лимит консигнации (в днях) qiymati 30 qilib saqlanadi.
    4. Mavjud active orderlar bo'lsa Отменен statusga o'tkazilib, product booking tozalanadi.
    5. Yangi order yaratiladi va 3-formada konsignatsiya kartasi ko'rinishi tekshiriladi.
    6. Konsignatsiya limiti 30 kun ekanligi max date orqali tekshiriladi.
    7. Konsignatsiya date/amount, payment type va status to'ldirilib 5 dona order saqlanadi.
    8. Order viewda asosiy ma'lumotlar va Консигнация tabidagi date/amount tekshiriladi.
    """
    base = BasePage(page)
    if login:
        with allure.step("1 - User tizimga muvaffaqiyatli kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - Order settingsda konsignatsiya yoqiladi va limit 30 kun qilinadi"):
        _enable_consignment_for_orders(page)

    with allure.step("3 - Mavjud active orderlar bo'lsa Отменен statusga o'tkazilib, product booking tozalanadi"):
        _cancel_existing_client_orders_if_any(page, code)

    with allure.step("4 - Yangi zakaz asosiy va TMC qadamlaridan o'tkaziladi"):
        flow_order_list(page, add=True)
        deal_time = base.input(label="Дата заказа", return_value=True)
        delivery_date = base.input(label="Дата отгрузки", return_value=True)
        flow_order_main_page(
            page,
            check_form=True,
            deal_time=deal_time,
            delivery_date=delivery_date,
            room=f"room-pw{code}",
            robot=f"robot-pw{code}",
            natural_client=f"natural_client-pw{code}",
            next_page=True,
        )
        flow_order_product_page(
            page,
            product=f"product-pw{code}",
            quantity="5",
            next_page=True,
        )

    with allure.step("5 - 3-formada konsignatsiya kartasi va 30 kunlik limit tekshiriladi"):
        _expect_text_visible(page, "Дата оплаты по консигнации")
        _expect_text_visible(page, "Сумма консигнации")
        _expect_text_visible(page, "ИТОГО")

        consignment_day_limit = _consignment_day_limit(page)
        if consignment_day_limit != "30":
            raise AssertionError(f"Expected consignment day limit 30, got {consignment_day_limit!r}")
        # Max valid konsignatsiya sanasi formadagi haqiqiy delivery_date'dan hisoblanadi
        # (today emas) — limit kunini ham scope'dan o'qilgan qiymatdan olamiz.
        expected_limit_date = (
            datetime.strptime(delivery_date, "%d.%m.%Y") + timedelta(days=int(consignment_day_limit))
        ).strftime("%d.%m.%Y")

    with allure.step("6 - Konsignatsiya date/amount, tip oplati va status to'ldirilib saqlanadi"):
        base.input(
            label="Дата оплаты по консигнации",
            value=expected_limit_date,
            expect_value=expected_limit_date,
            press_tab=True,
        )

        base.input(
            label="Сумма консигнации",
            value="35000",
            expect_value="35 000",
            press_tab=True,
        )

        flow_order_final_page(
            page,
            payment_type="Наличные деньги",
            status="Черновик",
            save=True,
        )
        expect(page).to_have_url(re.compile(r".*/order_list"))
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

    with allure.step("7 - Zakaz view oynasida asosiy ma'lumotlar tekshiriladi"):
        flow_order_list(page, find_row=f"natural_client-pw{code}", view=True)
        expect(page).to_have_url(re.compile(r".*/order_view"))
        _expect_text_visible(page, f"natural_client-pw{code}")
        _expect_text_visible(page, f"room-pw{code}")
        _expect_text_visible(page, f"robot-pw{code}")
        _expect_text_visible(page, "Наличные деньги")
        _expect_text_visible(page, "Черновик")
        _expect_text_visible(page, f"product-pw{code}")
        _expect_text_visible(page, "35 000")
        _expect_text_visible(page, "Ответственный за консигнацию")
        _expect_text_visible(page, "Согласование консигнации")

    with allure.step("8 - Viewdagi Консигнация tabida date va summa tekshiriladi"):
        _click_visible_text(page, "Консигнация")
        _expect_text_visible(page, expected_limit_date)
        _expect_text_visible(page, "35 000")

    with allure.step("9 - B-group konsignatsiya order id saqlanadi"):
        save_data("b_group_consignment_order_client", f"natural_client-pw{code}")
        save_data(
            "b_group_consignment_order_id",
            _order_id_from_current_url(page),
        )
        page.get_by_role("button", name="Закрыть").click()
        expect(page).to_have_url(re.compile(r".*/order_list"))


def run_b_group_edit_order_with_consignment_limit(page, code, load_data, save_data, login=True):
    """
    Testcase:
    1. User sifatida tizimga kirish.
    2. test_b_group_create_order_with_consignment_limit yaratgan active order listda topiladi.
    3. Order edit qilinib quantity 5 dan 4 ga kamaytiriladi.
    4. Eski konsignatsiya summasi order totalidan katta bo'lgani uchun error chiqishi va konsignatsiya clear bo'lishi tekshiriladi.
    5. 30 kundan katta konsignatsiya sanasi kiritilib, save confirm chiqmasligi tekshiriladi.
    6. Konsignatsiya summasi + orqali 2 ta sanaga bo'linadi va order saqlanadi.
    7. Order viewda 28 000 total hamda ikki konsignatsiya sana/summa tekshiriladi.
    """
    base = BasePage(page)
    if login:
        with allure.step("1 - User tizimga muvaffaqiyatli kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - B-group create testi yaratgan active order listda topiladi"):
        created_order_client = load_data("b_group_consignment_order_client") or f"natural_client-pw{code}"
        flow_open_order_list(page)
        if not _page_text_is_present(page, created_order_client):
            raise AssertionError(
                "Konsignatsiyali active order topilmadi. "
                "Avval test_b_group_create_order_with_consignment_limit ni run qiling."
            )

    with allure.step("3 - Order edit qilinib quantity 5 dan 4 ga kamaytiriladi"):
        flow_order_list(page, find_row=created_order_client, edit=True)
        expect(page).to_have_url(re.compile(r".*/order\+edit"))
        delivery_date = base.input(label="Дата отгрузки", return_value=True)
        delivery_date_value = datetime.strptime(delivery_date, "%d.%m.%Y")
        first_split_date = (delivery_date_value + timedelta(days=15)).strftime("%d.%m.%Y")
        limit_date = (delivery_date_value + timedelta(days=30)).strftime("%d.%m.%Y")
        invalid_date = (delivery_date_value + timedelta(days=31)).strftime("%d.%m.%Y")

        page.get_by_role("button", name="Далее").click()
        flow_order_product_page(
            page,
            quantity="4",
            next_page=True,
        )

    with allure.step("4 - Eski konsignatsiya order totalidan katta bo'lgani uchun error chiqadi va clear bo'ladi"):
        _close_error_dialog(
            page,
            "Общая сумма консигнаций не должна быть больше суммы заказа",
        )
        base.input(label="Дата оплаты по консигнации", expect_value="")
        base.input(label="Сумма консигнации", expect_value="")
        _expect_text_visible(page, "ИТОГО")
        _expect_text_visible(page, "28 000")

    with allure.step("5 - 30 kundan katta konsignatsiya sanasi save qilinmaydi"):
        base.input(
            label="Дата оплаты по консигнации",
            value=invalid_date,
            expect_value=invalid_date,
            press_tab=True,
        )
        base.input(
            label="Сумма консигнации",
            value="28000",
            expect_value="28 000",
            press_tab=True,
        )
        _assert_save_blocked_without_confirm(page, expected_date=invalid_date)
        expect(page).to_have_url(re.compile(r".*/order\+edit"))

    with allure.step("6 - Konsignatsiya + orqali 2 ta sanaga bo'linadi"):
        base.input(
            label="Дата оплаты по консигнации",
            value=first_split_date,
            expect_value=first_split_date,
            press_tab=True,
        )
        base.input(
            label="Сумма консигнации",
            value="14000",
            expect_value="14 000",
            press_tab=True,
        )

        _click_consignment_add_button(page)
        base.input(
            label="Дата оплаты по консигнации",
            value=limit_date,
            expect_value=limit_date,
            index=1,
            press_tab=True,
        )
        base.input(
            label="Сумма консигнации",
            value="14000",
            expect_value="14 000",
            index=1,
            press_tab=True,
        )

    with allure.step("7 - Order save qilinadi"):
        _save_order_from_final_page(page)
        expect(page).to_have_url(re.compile(r".*/order_list"))
        expect(page.get_by_role("heading")).to_contain_text("Заказы")

    with allure.step("8 - Order viewda split qilingan konsignatsiya tekshiriladi"):
        flow_order_list(page, find_row=created_order_client, view=True)
        expect(page).to_have_url(re.compile(r".*/order_view"))
        _expect_text_visible(page, created_order_client)
        _expect_text_visible(page, f"product-pw{code}")
        _expect_text_visible(page, "28 000")
        _click_visible_text(page, "Консигнация")
        _expect_text_visible(page, first_split_date)
        _expect_text_visible(page, limit_date)
        if _page_text_occurrences(page, "14 000") < 2:
            raise AssertionError("Viewda ikkita 14 000 konsignatsiya summasi ko'rinmadi")

    with allure.step("9 - Edit qilingan order ma'lumotlari saqlanadi"):
        save_data("b_group_consignment_order_split_first_date", first_split_date)
        save_data("b_group_consignment_order_split_second_date", limit_date)
        page.get_by_role("button", name="Закрыть").click()
        expect(page).to_have_url(re.compile(r".*/order_list"))


def run_b_group_order_invoice_reports(page, code, load_data):
    """
    Testcase:
    1. B-group sessiyasida oldingi test yaratgan draft order listdan topiladi.
    2. Order row menu ichidagi Накладные dropdown ochiladi.
    3. Dropdowndagi kutilgan report optionlari ko'rinishi tekshiriladi.
    4. Scope bo'yicha report optionlar birma-bir ochilib, report sahifasi va asosiy order ma'lumotlari tekshiriladi.
    5. Экспортировать заказ optioni fayl yuklashini tekshiradi.
    """
    created_order_client = load_data("b_group_consignment_order_client") or f"natural_client-pw{code}"
    created_order_id = str(load_data("b_group_consignment_order_id") or "")
    expected_data = {
        "client": created_order_client,
        "product": f"product-pw{code}",
        "order_id": created_order_id,
        "total": "28 000",
    }
    opened_reports = {}
    downloaded_files = {}

    with allure.step("1 - B-group draft order listda topiladi"):
        flow_open_order_list(page)
        if not _page_text_is_present(page, created_order_client, timeout=10_000):
            raise AssertionError(
                "B-group draft order listda topilmadi. "
                "Avval B-01 va B-02 testlari shu group sessiyada muvaffaqiyatli yurishi kerak."
            )
        _expect_text_visible(page, "Черновик")
        _expect_text_visible(page, "28 000")

    with allure.step("2 - Order row menu ichida Накладные dropdown optionlari tekshiriladi"):
        _open_order_invoice_dropdown(page, created_order_client)
        _assert_invoice_dropdown_options(page)

    with allure.step("3 - Накладные report optionlari ochilishi va order datasi tekshiriladi"):
        for option_name in B_GROUP_ORDER_INVOICE_REPORT_OPTIONS:
            with allure.step(f"Накладные: {option_name} reporti ochiladi"):
                opened_reports[option_name] = _open_invoice_report_and_assert(
                    page,
                    created_order_client,
                    option_name,
                    expected_data,
                )

    with allure.step("4 - Экспортировать заказ fayl yuklashi tekshiriladi"):
        for option_name in B_GROUP_ORDER_INVOICE_DOWNLOAD_OPTIONS:
            with allure.step(f"Накладные: {option_name} download tekshiriladi"):
                downloaded_files[option_name] = _download_invoice_export_and_assert(
                    page,
                    created_order_client,
                    option_name,
                )

    with allure.step("5 - Ochilgan report URLlari va downloadlar Allurega yoziladi"):
        allure.attach(
            json.dumps(opened_reports, ensure_ascii=False, indent=2),
            name="b-group-invoice-report-urls",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            json.dumps(downloaded_files, ensure_ascii=False, indent=2),
            name="b-group-invoice-downloads",
            attachment_type=allure.attachment_type.JSON,
        )
        flow_open_order_list(page)
        expect(page.locator("#kt_content")).to_contain_text(created_order_client, timeout=120_000)
