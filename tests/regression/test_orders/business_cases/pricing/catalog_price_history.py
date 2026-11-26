"""Order narxi: katalog almashganda eski qoralama va bo‘sh Подбор qiymatni saqlaydi."""
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.api.client import require_fields
from tests.regression.helpers.preparation.catalog_price_history import (
    PRICE_SAVE, price_change_attempted, price_payload,
)
from tests.regression.helpers.retry.state import ACTIVE, RetryBlocked
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.flows.order import open_order_summary, reopen_order_goods
from tests.regression.test_orders.helpers.flows.price_draft import check_edit_price, check_saved_price_draft
from utils.base_pages.auto_base_page import AutoBasePage


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
    check_saved_price_draft(case, case.workflow["original_draft"], 1000)
    reopen_order_goods(page)
    with allure.step("Tahrirda tanlovdan oldin ham 2 × 1 000 = 2 000"):
        check_edit_price(case, 1000)
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
        check_edit_price(case, 1000)
    open_order_summary(page, expected_total=2000)
