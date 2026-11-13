"""ORD-BIZ-02: boshqa SKUdan bepul bonusning saved/reopen tekshiruvi."""
import re
import allure
import pytest
from playwright.sync_api import expect
from tests.regression.test_orders.helpers.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference, promotion_card, reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Order biznes flowlari"), allure.story("Boshqa mahsulot bonusi")]


def run_other_product_bonus(case):
    """1. Setup mahsulotidan 10 dona orderga kiritish.
    2. Boshqa mahsulotdan 1 dona bonusni tanlash; chegirmani tanlamaslik.
    3. 70 000 so'mlik draftni saqlash va bonusning bepul ekanini tekshirish.
    4. Qayta ochishda bonus tanlovi va order summasini tekshirish.
    """
    page, base = case.page, AutoBasePage(case.page)
    order_id = existing_order(case)
    if not order_id:
        require_available(case, 10, bonus_quantity=1)
        open_new_order(page)
        with allure.step("1 - Setup klienti va mahsulotidan 10 dona"):
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="10", press_tab=True)
        with allure.step("2 - Faqat boshqa mahsulot bonusini yoqish"):
            base.tab(name=re.compile(r"^Акции"))
            bonus = promotion_card(page, case.promotions["bonus"]["name"])
            base.grid(case.bonus_product, "1", root=bonus)
            base.checkbox(locator=bonus.get_by_role("switch"), checked=True)
            base.checkbox(locator=promotion_card(page, case.promotions["discount"]["name"]).get_by_role("switch"), expect_checked=False)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
            base.click(name="Далее", exact=True)
            base.input(label="ИТОГО", expect_value="70000")
            case.check("Saqlashdan oldingi order jami (so'm)", "70000", re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            case.check("Faqat bonusli order chegirmasi (so'm)", "0", re.sub(r"\s+", "", base.input(label="Сумма скидки/наценки", return_value=True)))
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    with allure.step("3 - Saqlangan order 70 000; boshqa mahsulot bonus qatori bepul"):
        base.form_view(label="Сумма заказа", expect_value="70000", remove_spaces=True)
        case.check("Saqlangan order jami (so'm)", "70000", base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        paid_grid = page.locator("smt-table:visible").last
        expect(paid_grid.locator(".smt-data-row")).to_have_count(1)
        paid_row = base.grid(case.product, root=paid_grid)
        paid_labels = [text.strip() for text in paid_grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество заказа", r"10"), ("Цена", r"7\s*000"), ("Итого", r"70\s*000")):
            expect(base.grid_cell(paid_row, paid_labels.index(label))).to_have_text(re.compile(r"^\s*" + value + r"\s*$"))
            expected_cells = {"Количество заказа": ("Mahsulot miqdori (dona)", "10"), "Цена": ("Mahsulot narxi (so'm)", "7000"), "Итого": ("Mahsulot summasi (so'm)", "70000")}
            caption, expected_cell = expected_cells[label]
            case.check(caption, expected_cell, base.grid_cell(paid_row, paid_labels.index(label), return_value=True, remove_spaces=True))
        base.tab(name="Акция")
        base.grid(case.bonus_product, case.promotions["bonus"]["name"])
        # Viewda bonus qatorining miqdor/narx kataklari alohida tekshiriladi.
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.bonus_product, root=grid)
        headers = grid.locator(".smt-grid-header [data-smt-col-key]")
        labels = [text.strip() for text in headers.all_text_contents()]
        for label, value in (("Количество продажи", "1"), ("Цена", "0"), ("Итого", "0")):
            expect(base.grid_cell(row, labels.index(label))).to_have_text(value)
            caption = {"Количество продажи": "Bonus miqdori (dona)", "Цена": "Bonus narxi (so'm)", "Итого": "Bonus summasi (so'm)"}[label]
            case.check(caption, value, base.grid_cell(row, labels.index(label), return_value=True, remove_spaces=True))
    reopen_order_goods(page)
    with allure.step("4 - Bonus tanlovi qayta ochilganda saqlanishi"):
        base.tab(name=re.compile(r"^Акции"))
        base.checkbox(locator=promotion_card(page, case.promotions["bonus"]["name"]).get_by_role("switch"), expect_checked=True)
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1)
        base.click(name="Далее", exact=True)
        base.input(label="ИТОГО", expect_value="70000")
        case.check("Qayta ochilgan order jami (so'm)", "70000", re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))


@allure.title("OB-02: Boshqa mahsulotdan 1 dona bepul bonus")
def test_other_product_bonus(promoted_order):
    run_other_product_bonus(promoted_order)
