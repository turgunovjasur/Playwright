"""Order narxi: katalog almashganda eski qoralama va bo‘sh Подбор qiymatni saqlaydi."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.api.client import require_fields
from tests.regression.helpers.preparation.catalog_price_history import (
    PRICE_SAVE, price_change_attempted, price_payload,
)
from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.helpers.retry.state import ACTIVE, RetryBlocked
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.discounts import parse_amount, save_discount_draft
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, open_order_summary, reopen_order_goods,
    select_client_product,
)
from utils.base_pages.auto_base_page import AutoBasePage


def _check_goods(case, grid, row, columns, expected):
    expect(row).to_have_count(1)
    headers = [" ".join(text.split()) for text in
               grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    base = AutoBasePage(case.page)
    for label, value in zip(columns, expected, strict=True):
        if headers.count(label) != 1:
            raise AssertionError(f"Mahsulot jadvalida {label!r} ustuni yagona emas")
        actual = base.grid_cell(row, headers.index(label), return_value=True)
        case.check(f"Mahsulot — {label}", Decimal(value), parse_amount(actual))


def _open_saved(case, order, price):
    base = AutoBasePage(case.page)
    with allure.step("Aynan saqlangan qoralamani ID bo‘yicha qayta ochish"):
        base.open_route("trade/tdeal/order/order_view?deal_id=" + order["id"], heading="Заказ / Просмотр")
        for label, value in (("ИД заказа", order["id"]), ("Номер ТТН", order["reference"]),
                             ("Клиент", case.client), ("Статус", "Черновик")):
            base.form_view(label=label, expect_value=value)
        total = base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)
        case.check("Qoralamaning saqlangan jami", Decimal(2 * price), parse_amount(total))
        grid = case.page.locator("smt-table:visible").filter(has=case.page.get_by_text(case.product, exact=True))
        expect(grid).to_have_count(1)
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.product, case.price_type, "Основной склад", root=grid)
        _check_goods(case, grid, row, ("Количество продажи", "Цена", "Итого"), (2, price, 2 * price))


def _check_edit_goods(case, price):
    page = case.page
    grid = page.locator("smt-table:visible").filter(has=page.get_by_text(case.price_type, exact=True))
    row = grid.locator(".smt-data-row").filter(has=page.get_by_text(case.price_type, exact=True))
    expect(row).to_have_count(1)
    AutoBasePage(page).b_input(placeholder="Выберите...", root=row, expect_value=case.product)
    _check_goods(case, grid, row, ("Кол-во", "Цена", "Сумма к оплате"), (2, price, 2 * price))


def run_create_price_draft(case, *, key, price, payment_type="Наличные деньги"):
    """1. Qoralamani saqlash. 2. Viewni o‘qish. 3. Yangi narxni fresh Editda tekshirish."""
    order_id = existing_order(case)
    if order_id:
        case.remember_order(order_id)
    else:
        require_available(case, 2)
        open_new_order(case.page)
        select_client_product(case.page, case.client, case.product, case.price_type)
        AutoBasePage(case.page).input(label="Кол-во", value="2", press_tab=True)
        open_order_summary(case.page, expected_total=2 * price)
        save_discount_draft(case, 2 * price, payment_type=payment_type)
        order_id = case.orders[-1]
    order = {"id": order_id, "reference": case.reference}
    if key == "new_draft":
        case.check("Yangi qoralama alohida ID oldi", True, order_id != case.workflow["original_draft"]["id"])
    case.workflow[key] = order
    case.checkpoint()
    _open_saved(case, order, price)
    if key == "new_draft":
        reopen_order_goods(case.page)
        with allure.step("Yangi qoralamaning Editida 2 dona × 1 500 = 3 000 saqlangan"):
            _check_edit_goods(case, price)
        open_order_summary(case.page, expected_total=2 * price)


def run_change_catalog_price(baseline, catalog, workflow, directory):
    """1. Own SKUni tasdiqlash. 2. 1 000 → 1 500. 3. Katalogdan qayta o‘qish."""
    product = catalog["goods"]
    price_type_id = str(baseline["price_type_id_uzb"])
    state = RegressionSetupState(directory / "catalog-price-state.json", dict(baseline))
    try:
        api = state.user()
        require_fields(api.model("anor/mr/product/inventory_view", product_id=product["id"]),
                       name=product["name"], code=product["code"], state="A")

        def read_price():
            prices = api.model("anor/mr/product/product_set_price", product_id=product["id"])["prices"]
            rows = [row for row in prices if str(row[0]) == price_type_id and str(row[3]) == "-1"]
            if len(rows) != 1 or rows[0][5] in ("", None):
                raise AssertionError("Own SKUning kartasiz katalog narxi yagona emas yoki bo‘sh")
            return Decimal(str(rows[0][5]))

        with allure.step("Birinchi order saqlangach faqat guruh SKU narxini 1 500 qilish"):
            prior = read_price()
            changed = price_payload(product["id"], price_type_id, 1500)
            if prior == 1000:
                api.call(PRICE_SAVE, changed)
            else:
                journal = ACTIVE.get()
                previous = journal.source if journal else {}
                if prior != 1500 or not price_change_attempted(previous, changed):
                    raise RetryBlocked("Katalog narxi kutilmaganda o‘zgargan; ustidan yozilmadi")
            if read_price() != 1500:
                raise AssertionError("Own SKU katalogida 1 500 so‘m saqlanmadi")
            workflow["verified_catalog_price"] = changed
    finally:
        state.close()


def run_original_and_picker(case):
    """1. Eski View/Editni o‘qish. 2. Bo‘sh Подборni yopish. 3. Eski qator va jami."""
    page, base = case.page, AutoBasePage(case.page)
    _open_saved(case, case.workflow["original_draft"], 1000)
    reopen_order_goods(page)
    with allure.step("Tahrirda tanlovdan oldin ham 2 × 1 000 = 2 000"):
        _check_edit_goods(case, 1000)
    with allure.step("Подборni ochish va ombor hamda narx turi bo‘shligini tekshirish"):
        base.click(name="Подбор", exact=True)
        heading = page.get_by_role("heading", name="Заказ (подбор)", exact=True)
        expect(heading).to_be_visible()
        picker = page.locator("main:visible").filter(has=page.get_by_role("button", name="Закрыть", exact=True))
        expect(picker).to_have_count(1)
        fields = picker.get_by_role("textbox", name="Выберите...", exact=True)
        expect(fields).to_have_count(2)
        expect(fields.nth(0)).to_have_value("")
        expect(fields.nth(1)).to_have_value("")
    with allure.step("Hech narsani tanlamasdan yopish va saqlangan narxni solishtirish"):
        base.click(name="Закрыть", exact=True, root=picker)
        expect(heading).to_be_hidden()
        _check_edit_goods(case, 1000)
    open_order_summary(page, expected_total=2000)
