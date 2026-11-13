"""Hisob-kitob testlari uchun arxiv order va klient balansi tekshiruvi."""
from decimal import Decimal
import allure
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available
from tests.regression.test_orders.helpers.flows.order import existing_order, open_new_order, select_order_product, save_order_by_reference
from tests.regression.test_orders.helpers.flows.settlement import read_settlement, read_debts, change_order_status


def verify_balances(case, *, debt, prepayment, debts):
    actual = read_settlement(case.page, case.client)
    expected = {"debt": Decimal(debt), "prepayment": Decimal(prepayment),
                "open_order": Decimal(0), "booked_prepayment": Decimal(0),
                "balance": Decimal(prepayment)-Decimal(debt)}
    case.check("Klient balansi: qarz, avans, ochiq order, bronlangan avans, balans", expected, actual)
    case.check("Har bir orderning alohida qarzi", debts,
               read_debts(case.page, case.client, settlement=actual))


def create_and_archive(case, *, key, quantity, amount):
    page, base = case.page, AutoBasePage(case.page)
    identity = existing_order(case)
    if not identity:
        require_available(case, quantity, bonus_quantity=0)
        open_new_order(page)
        with allure.step(f"Order: {quantity} dona × 7 000 = {amount} so'm"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value=str(quantity), press_tab=True)
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value=str(amount))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        identity = save_order_by_reference(page, case.reference)
    case.remember_order(identity)
    case.workflow[key] = {"id": identity, "amount": str(amount), "quantity": quantity}
    case.checkpoint()
    with allure.step("Saqlangan order ID, klient, valyuta, miqdor va summa"):
        base.form_view(label="ИД заказа", expect_value=identity)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Валюта", expect_value="Узбекский сум")
        case.check("Saqlangan order jami", str(amount), base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        grid = page.locator("smt-table:visible").last
        headers = [x.strip() for x in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        row = base.grid(case.product, root=grid)
        case.check("Saqlangan mahsulot miqdori", str(quantity), base.grid_cell(row, headers.index("Количество продажи"), return_value=True, remove_spaces=True))
    change_order_status(page, identity, current="Черновик", target="Архив")
    return identity
