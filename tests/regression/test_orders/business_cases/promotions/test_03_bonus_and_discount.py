"""ORD-BIZ-04 ning saqlash qismi: bonus va chegirma bir orderda."""
import re
import allure
import pytest
from playwright.sync_api import expect
from tests.regression.test_orders.helpers.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference, promotion_card, reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Order biznes flowlari"), allure.story("Bonus va chegirma birga")]


def run_bonus_and_discount(case):
    """1. Setup mahsulotidan 10 dona order yaratish.
    2. 10% chegirma va boshqa mahsulot bonusini birga tanlash.
    3. Draftni saqlab 63 000 so'm va bepul bonusni tekshirish.
    4. Qayta ochilganda ikkala aksiya tanlovi saqlanganini tekshirish.

    Jo'natish va to'lov bu testcase qamroviga kirmaydi; alohida flow bo'ladi.
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
        with allure.step("2 - Bonus va 10% chegirmani birga olish"):
            base.tab(name=re.compile(r"^Акции"))
            for key in ("bonus", "discount"):
                base.checkbox(locator=promotion_card(page, case.promotions[key]["name"]).get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(2)
            base.click(name="Далее", exact=True)
            base.input(label="ИТОГО", expect_value="63000")
            case.check("Saqlashdan oldingi order jami (so'm)", "63000", re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))
            base.input(label="Сумма скидки/наценки", expect_value="-7000")
            case.check("Bonus va chegirmali order chegirmasi (so'm)", "-7000", re.sub(r"\s+", "", base.input(label="Сумма скидки/наценки", return_value=True)))
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    with allure.step("3 - Saqlangan summa va boshqa mahsulot bonusi"):
        base.form_view(label="Сумма заказа", expect_value="63000", remove_spaces=True)
        case.check("Saqlangan order jami (so'm)", "63000", base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        paid_grid = page.locator("smt-table:visible").last
        expect(paid_grid.locator(".smt-data-row")).to_have_count(1)
        paid_row = base.grid(case.product, root=paid_grid)
        paid_labels = [text.strip() for text in paid_grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество заказа", r"10"), ("Цена", r"7\s*000"), ("Итого", r"63\s*000")):
            expect(base.grid_cell(paid_row, paid_labels.index(label))).to_have_text(re.compile(r"^\s*" + value + r"\s*$"))
            expected_cells = {"Количество заказа": ("Mahsulot miqdori (dona)", "10"), "Цена": ("Mahsulot narxi (so'm)", "7000"), "Итого": ("Chegirmadan keyingi mahsulot summasi (so'm)", "63000")}
            caption, expected_cell = expected_cells[label]
            case.check(caption, expected_cell, base.grid_cell(paid_row, paid_labels.index(label), return_value=True, remove_spaces=True))
        base.tab(name="Акция")
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=grid)
        labels = [text.strip() for text in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество продажи", "1"), ("Цена", "0"), ("Итого", "0")):
            expect(base.grid_cell(row, labels.index(label))).to_have_text(value)
            caption = {"Количество продажи": "Bonus miqdori (dona)", "Цена": "Bonus narxi (so'm)", "Итого": "Bonus summasi (so'm)"}[label]
            case.check(caption, value, base.grid_cell(row, labels.index(label), return_value=True, remove_spaces=True))
    reopen_order_goods(page)
    with allure.step("4 - Ikkala aksiya va 63 000 so'm qayta ochilganda saqlanishi"):
        base.tab(name=re.compile(r"^Акции"))
        for key in ("bonus", "discount"):
            base.checkbox(locator=promotion_card(page, case.promotions[key]["name"]).get_by_role("switch"), expect_checked=True)
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(2)
        base.click(name="Далее", exact=True)
        base.input(label="ИТОГО", expect_value="63000")
        case.check("Qayta ochilgan order jami (so'm)", "63000", re.sub(r"\s+", "", base.input(label="ИТОГО", return_value=True)))


@allure.title("OB-03: Bitta orderda bonus va 10% chegirma")
def test_bonus_and_discount(promoted_order):
    run_bonus_and_discount(promoted_order)
