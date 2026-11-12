"""Oddiy order: jo'natish → cashin → 6 000 + 8 000 so'm qarz yopish."""

import re
from decimal import Decimal

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference
from tests.regression.test_orders.flows.settlement import (
    allocate_to_order, change_order_status, post_cashin, read_debts, read_settlement,
)
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.preparation.stock_guard import require_available
from tests.regression.retry.checkpoints import value as retry_value, reuse as reuse_step, verified as verify_step, decimal_map

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup,
              pytest.mark.order_positive, allure.epic("Regression"),
              allure.feature("Order"), allure.story("Qisman va to'liq to'lov")]


def run_partial_full_payment(case):
    """1. Klient boshlang'ich balansini va boshqa order qarzlarini yozib olish.
    2. 2 × 7 000 = 14 000 so'm own order yaratish va bevosita arxivlash.
    3. Auto-offsetsiz 14 000 so'm own cashinni o'tkazish; qarz saqlanadi.
    4. Aynan shu orderga 6 000 ajratish: qolgan qarz/predoplata 8 000.
    5. Qolgan 8 000 ajratish: own qarz yopiladi, boshlang'ich balans qaytadi.
    6. Har bosqichda boshqa order qarzlari o'zgarmaganini tekshirish.

    API faqat tashqi setupda. Yaratilgan order/to'lovlar saqlanadi, cleanup yo'q.
    """
    page, base = case.page, AutoBasePage(case.page)
    amount = Decimal("14000")
    balance_labels = {"debt": "Qarzdorlik", "prepayment": "Predoplata", "open_order": "Ochiq orderlar summasi", "booked_prepayment": "Bronlangan predoplata", "balance": "Balans"}
    with allure.step("1 - Bir to'lov manbai uchun predoplata nol; boshqa qarzlarni qayd etish"):
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
        require_available(case, 2, bonus_quantity=0)
        open_new_order(page)
        with allure.step("2 - Setup klienti uchun 2 dona mahsulot va 14 000 so'm order"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="2", press_tab=True)
            expect(page.locator("smt-table:visible .smt-data-row [data-smt-col-key=price]").first).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value=str(amount))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    with allure.step("3 - Saqlangan own order ID, klient, valyuta va summa"):
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Валюта", expect_value="Узбекский сум")
        base.form_view(label="Сумма заказа", expect_value=str(amount), remove_spaces=True)
        case.check("Saqlangan oddiy order jami (so'm)", str(amount), base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
    with allure.step("4 - Orderni bevosita Черновик → Архив o‘tkazish"):
        change_order_status(page, order_id, current="Черновик", target="Архив")
    archived = {**before, "debt": before["debt"] + amount, "balance": before["balance"] - amount}
    debts = {**debts_before, order_id: amount}
    if not reuse_step("payment_archive_verified"):
        with allure.step("5 - Own qarz 14 000; boshqa orderlar va boshlang'ich ochiq order summasi saqlanadi"):
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
    with allure.step("6 - Own 14 000 so'm cashinni auto-offsetsiz o'tkazish"):
        payment.update(post_cashin(page, client=case.client, number=payment["number"], amount=amount, order_id=order_id))
        payment["state"] = "posted"
        case.checkpoint()
    with allure.step("7 - Cashin qarzni o'zgartirmaydi, predoplatani 14 000 oshiradi"):
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
    for step, installment, remaining in ((8, Decimal("6000"), Decimal("8000")),
                                         (9, Decimal("8000"), Decimal("0"))):
        stage = "payment_offset_verified:" + str(installment)
        if reuse_step(stage):
            continue
        with allure.step(f"{step} - Own orderga {installment} so'm ajratish; qolgan qarz {remaining}"):
            # Ushbu o'qish listni ochadi; exact order detaili shundan tanlanadi.
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


@allure.title("ORD-BIZ-01: Oddiy order → 6 000 qisman → 8 000 to'liq to'lov")
def test_partial_full_payment(ordinary_payment_order):
    run_partial_full_payment(ordinary_payment_order)
