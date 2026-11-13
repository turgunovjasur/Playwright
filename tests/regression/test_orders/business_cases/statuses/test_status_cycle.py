"""Bir orderda olti status o‘tishi, rezerv, chiqim va qarz."""
from decimal import Decimal
import allure
import pytest
from tests.regression.test_orders.helpers.flows.order import existing_order, open_new_order, select_order_product, save_order_by_reference
from tests.regression.test_orders.helpers.flows.settlement import change_order_status, read_settlement, read_debts
from tests.regression.test_orders.helpers.flows.stock import read_stock
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.helpers.retry.checkpoints import value as retry_value, reuse, verified, decimal_map

pytestmark = [pytest.mark.regression, pytest.mark.order_positive]


def run_status_cycle(case):
    """1. Own klient va omborning boshlang‘ich holatini olish.
    2. 2 dona × 7 000 = 14 000 so‘mlik Draft yaratish.
    3. New → Processing → Waiting: rezerv 2, fizik qoldiq o‘zgarmaydi.
    4. Shipped → Delivered: fizik chiqim faqat 2, rezerv tiklanadi.
    5. Archive: aynan shu order qarzi 14 000, ochiq order summasi 0.
    Har statusda saved ID/status, summa, stock va saldo UI orqali tekshiriladi.
    """
    page, base = case.page, AutoBasePage(case.page)
    zero = {key: Decimal(0) for key in ("debt", "prepayment", "open_order", "booked_prepayment", "balance")}
    with allure.step("1 - Status testi klientining balansi va boshlang‘ich ombor qoldig‘i"):
        retained = retry_value("status_initial_stock")
        if retained is not None:
            before = decimal_map(retained)
        else:
            case.check("Yangi klientning boshlang‘ich saldosi", zero, read_settlement(page, case.client))
            before = read_stock(case, "Основной склад")
            case.check("Ikki dona uchun erkin qoldiq yetarli", True, before["available"] >= 2)
            retry_value("status_initial_stock", before)
    order_id = existing_order(case)
    if not order_id:
        require_available(case, 2, bonus_quantity=0)
        open_new_order(page)
        with allure.step("2 - Status testi uchun 14 000 so‘mlik qoralama"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="2", press_tab=True)
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value="14000")
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    current = "Черновик"
    # Deltas relative to the observed stock, never a hard-coded warehouse total.
    states = (
        ("Черновик", 0, 0, 0, 0),
        ("Новый", 0, 2, 14000, 0),
        ("В обработке", 0, 2, 14000, 0),
        ("В ожидании", 0, 2, 14000, 0),
        ("Отгружен", 2, 0, 14000, 0),
        ("Доставлен", 2, 0, 14000, 0),
        ("Архив", 2, 0, 0, 14000),
    )
    for status, sold, reserved, open_amount, debt in states:
        if status != "Архив" and reuse("status_verified:" + status):
            current = status
            continue
        if status != current:
            change_order_status(page, order_id, current=current, target=status)
            current = status
        with allure.step(f"{status}: saqlangan order, summa, rezerv, fizik qoldiq va qarz"):
            base.form_view(label="ИД заказа", expect_value=order_id)
            case.check("Saqlangan status", status, base.form_view(label="Статус", return_value=True))
            case.check("Status almashganda summa saqlanadi", "14000", base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
            stock = {"physical": before["physical"] - sold,
                     "booked": before["booked"] + reserved,
                     "available": before["available"] - sold - reserved}
            case.check(f"{status}: ombor qoldig‘i va rezerv", stock, read_stock(case, "Основной склад"))
            balance = {**zero, "open_order": Decimal(open_amount), "debt": Decimal(debt),
                       "balance": -Decimal(open_amount + debt)}
            actual = read_settlement(page, case.client)
            case.check(f"{status}: klient saldosi", balance, actual)
            if status == "Архив":
                case.check("Arxivdan keyin aynan shu orderning qarzi", {order_id: Decimal(14000)}, read_debts(page, case.client, settlement=actual))
            verified("status_verified:" + status)
