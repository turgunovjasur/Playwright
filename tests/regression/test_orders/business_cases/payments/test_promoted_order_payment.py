"""Bonus va chegirmali order: 63 000 so'mni 25 000 + 38 000 bilan yopish."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.flows.order import existing_order, select_order_product, open_new_order, promotion_card, save_order_by_reference
from tests.regression.test_orders.helpers.flows.settlement import (
    allocate_to_order, change_order_status, post_cashin, read_debts, read_settlement,
)
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.helpers.retry.checkpoints import value as retry_value, reuse as reuse_step, verified as verify_step, decimal_map

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup,
              pytest.mark.order_positive, allure.epic("Regression"),
              allure.feature("Order"), allure.story("Aksiya va chegirmali order to'lovi")]


def run_promoted_order_payment(case):
    """1. Boshlang'ich balans va boshqa order qarzlarini yozib olish.
    2. A10 × 7 000, 10% skidka va bepul B1 bilan 63 000 so'm order yaratish.
    3. Saqlangan narx, miqdor, 63 000 total va B1/0 so'mni tekshirish.
    4. Bevosita Черновик → Архив: qarz aynan 63 000 bo‘ladi.
    5. Auto-offsetsiz 63 000 so'm own cashin yaratish va o'tkazish.
    6. Faqat own orderga 25 000, keyin 38 000 ajratib qarzni yopish.
    7. Bonus uchun qarz chiqmasligi va boshqa qarzlar o'zgarmasligini tekshirish.
    """
    page, base = case.page, AutoBasePage(case.page)
    balance_labels = {"debt": "Qarzdorlik", "prepayment": "Predoplata", "open_order": "Ochiq orderlar summasi", "booked_prepayment": "Bronlangan predoplata", "balance": "Balans"}
    gross = Decimal("10") * Decimal(case.promotions["unit_price"])
    discount = gross * Decimal("0.10")
    amount = gross - discount
    if amount != Decimal("63000"):
        raise AssertionError("Payment setup narxi 7 000 so'm va skidka 10% bo'lishi kerak")
    with allure.step("1 - Predoplata nol va boshqa order qarzlarini qayd etish"):
        saved_baseline = retry_value("payment_baseline")
        if saved_baseline:
            before = decimal_map(saved_baseline["balances"])
            debts_before = decimal_map(saved_baseline["debts"])
        else:
            before = read_settlement(page, case.client)
            case.check("Boshlang'ich predoplata (so'm)", Decimal("0"), before["prepayment"])
            case.check("Boshlang'ich bronlangan predoplata (so'm)", Decimal("0"), before["booked_prepayment"])
            if before["prepayment"] != 0 or before["booked_prepayment"] != 0:
                raise AssertionError("Payment setup uchun predoplata va bronlangan predoplata 0 bo'lishi kerak; alohida klient setup case kerak.")
            debts_before = read_debts(page, case.client, settlement=before)
            retry_value("payment_baseline", {"balances": before, "debts": debts_before})
    order_id = existing_order(case)
    if not order_id:
        require_available(case, 10, bonus_quantity=1)
        open_new_order(page)
        with allure.step("2 - Own orderda 10 dona setup mahsuloti"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="10", press_tab=True)
            expect(page.locator("smt-table:visible .smt-data-row [data-smt-col-key=price]").first).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
        with allure.step("3 - B1 bonus va 10% skidkani tanlash; jami 63 000"):
            base.tab(name=re.compile(r"^Акции"))
            for key in ("bonus", "discount"):
                card = promotion_card(page, case.promotions[key]["name"])
                base.checkbox(locator=card.get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(2)
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value="63000")
            base.input(label="Сумма скидки/наценки", expect_value="-7000")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    with allure.step("4 - Saqlangan own order va bonusning bepul ekanini tekshirish"):
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Валюта", expect_value="Узбекский сум")
        base.form_view(label="Сумма заказа", expect_value="63000", remove_spaces=True)
        case.check("Saqlangan bonus va chegirmali order jami (so'm)", "63000", base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        paid_grid = page.locator("smt-table:visible").last
        expect(paid_grid.locator(".smt-data-row")).to_have_count(1)
        paid_row = base.grid(case.product, root=paid_grid)
        labels = [s.strip() for s in paid_grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество заказа", r"10"), ("Цена", r"7\s*000"), ("Итого", r"63\s*000")):
            expect(base.grid_cell(paid_row, labels.index(label))).to_have_text(re.compile(r"^\s*" + value + r"\s*$"))
            expected_cells = {"Количество заказа": ("Mahsulot miqdori (dona)", "10"), "Цена": ("Mahsulot narxi (so'm)", "7000"), "Итого": ("Chegirmadan keyingi mahsulot summasi (so'm)", "63000")}
            caption, expected_cell = expected_cells[label]
            case.check(caption, expected_cell, base.grid_cell(paid_row, labels.index(label), return_value=True, remove_spaces=True))
        base.tab(name="Акция")
        bonus_grid = page.locator("smt-table:visible").last
        expect(bonus_grid.locator(".smt-data-row")).to_have_count(1)
        bonus_row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=bonus_grid)
        labels = [s.strip() for s in bonus_grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество продажи", "1"), ("Цена", "0"), ("Итого", "0")):
            expect(base.grid_cell(bonus_row, labels.index(label))).to_have_text(value)
            caption = {"Количество продажи": "Bonus miqdori (dona)", "Цена": "Bonus narxi (so'm)", "Итого": "Bonus summasi (so'm)"}[label]
            case.check(caption, value, base.grid_cell(bonus_row, labels.index(label), return_value=True, remove_spaces=True))
    with allure.step("5 - Bonus va skidkali orderni bevosita Черновик → Архив o‘tkazish"):
        change_order_status(page, order_id, current="Черновик", target="Архив")
    archived = {**before, "debt": before["debt"] + amount, "balance": before["balance"] - amount}
    debts = {**debts_before, order_id: amount}
    if not reuse_step("payment_archive_verified"):
        with allure.step("6 - Bonus uchun qo'shimcha qarz yo'q: own qarz aynan 63 000"):
            archived = read_settlement(page, case.client)
            expected = {**before, "debt": before["debt"] + amount, "balance": before["balance"] - amount}
            for key, value in expected.items():
                case.check(f"Order arxivlangandan keyin: {balance_labels[key]} (so'm)", value, archived[key])
            if archived != expected:
                raise AssertionError(f"Archive balans: expected={expected}; actual={archived}")
            debts = read_debts(page, case.client, settlement=archived)
            case.check("Arxivdan keyingi order IDlari va qarzlari (so'm)", {**debts_before, order_id: amount}, debts)
            if debts != {**debts_before, order_id: amount}:
                raise AssertionError(f"Archive qarz IDlari/summalari noto'g'ri: {debts}")
        verify_step("payment_archive_verified")
    payment = {"number": f"{case.reference}-PAY", "order_id": order_id, "state": "pending"}
    case.payments.append(payment)
    case.checkpoint()
    with allure.step("7 - 63 000 so'm own cashinni avtomatik qarz yopishsiz o'tkazish"):
        payment.update(post_cashin(page, client=case.client, number=payment["number"], amount=Decimal("63000"), order_id=order_id))
        payment["state"] = "posted"
        case.checkpoint()
        if not reuse_step("payment_cashin_verified"):
            posted = read_settlement(page, case.client)
            expected = {**archived, "prepayment": amount, "balance": archived["balance"] + amount}
            for key, value in expected.items():
                case.check(f"Kirim o'tkazilgandan keyin: {balance_labels[key]} (so'm)", value, posted[key])
            if posted != expected:
                raise AssertionError(f"Cashin balans: expected={expected}; actual={posted}")
            posted_debts = read_debts(page, case.client, settlement=posted)
            case.check("Avtomatik qarz yopishsiz kirimdan keyingi order qarzlari (so'm)", debts, posted_debts)
            if posted_debts != debts:
                raise AssertionError("Auto-offset o'chiq bo'lsa ham order qarzi o'zgardi")
            verify_step("payment_cashin_verified")
    for step, installment, remaining in ((8, Decimal("25000"), Decimal("38000")),
                                         (9, Decimal("38000"), Decimal("0"))):
        stage = "payment_offset_verified:" + str(installment)
        if reuse_step(stage):
            continue
        with allure.step(f"{step} - Own orderga {installment} so'm ajratish; qolgan qarz {remaining}"):
            read_settlement(page, case.client)
            allocation = {"order_id": order_id, "cashin_id": payment["id"],
                          "amount": str(installment), "state": "pending"}
            case.allocations.append(allocation)
            case.checkpoint()
            allocate_to_order(page, client=case.client, order_id=order_id,
                              amount=installment, remaining_debt=remaining + installment)
            after = read_settlement(page, case.client)
            expected = {**before, "debt": before["debt"] + remaining,
                        "prepayment": remaining, "balance": before["balance"]}
            for key, value in expected.items():
                case.check(f"{installment} so'm qarz yopilgandan keyin: {balance_labels[key]} (so'm)", value, after[key])
            if after != expected:
                raise AssertionError(f"{installment} offsetdan keyin: expected={expected}; actual={after}")
            actual_debts = read_debts(page, case.client, settlement=after)
            expected_debts = {**debts_before, **({order_id: remaining} if remaining else {})}
            case.check(f"{installment} so'm to'lovdan keyingi order IDlari va qarzlari (so'm)", expected_debts, actual_debts)
            if actual_debts != expected_debts:
                raise AssertionError(f"Boshqa order qarzi o'zgardi yoki own qarz noto'g'ri: expected={expected_debts}; actual={actual_debts}")
            allocation["state"] = "verified_by_order_debt_and_balance"
            case.checkpoint()
            verify_step(stage)

    with allure.step("Yakuniy holat: order qarzi yopiq, eski qarzlar va balans saqlangan"):
        final = read_settlement(page, case.client)
        case.check("Yakuniy klient balansi", before, final)
        case.check("Yakuniy boshqa order qarzlari", debts_before,
                   read_debts(page, case.client, settlement=final))


@allure.title("ORD-BIZ-04: A10 + B1 bonus + 10% skidka → 25 000 + 38 000 to'lov")
def test_promoted_order_payment(promoted_payment_order):
    run_promoted_order_payment(promoted_payment_order)
