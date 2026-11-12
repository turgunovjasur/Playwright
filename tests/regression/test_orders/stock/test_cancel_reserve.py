"""Order New → Cancel: shu orderning ombor rezervi qaytadi.

A2 UI dalili: order-ui-elements-20261028/1414, 1418, 1419 va 1420.
Tovar viewidagi Остатки barcha lot qatorlari bo'yicha o'qiladi. Mahsulot yoki
ombor yaratish bu testda yo'q; API setup baseline va existing UI ishlatiladi.
"""

from decimal import Decimal
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference
from tests.regression.test_orders.flows.stock import read_stock as _read_stock
from tests.regression.test_orders.flows.order_status import cancel_order
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.preparation.stock_guard import require_available
from tests.regression.retry.checkpoints import value as retry_value, reuse, verified, decimal_map

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.epic("Regression"), allure.feature("Order ombor rezervi"), allure.story("Bekor qilishda rezerv qaytishi")]


def run_cancel_reserve(case):
    """1. Setup mahsuloti/omborning fresh qoldig'ini UI orqali o'qish.
    2. 2 dona mahsulotli own orderni Новый holatda saqlash.
    3. Physical o'zgarmasligi, rezerv +2 va available −2 ni tekshirish.
    4. Exact orderni Клиент отменил sababi bilan bekor qilish.
    5. Canceled viewda shu ID va status; qoldiq baselinega qaytishi.

    Bu case shipment, limit, saldo va restore testlarini o'z ichiga olmaydi.
    Order saqlanadi (Отменен), avtomatik delete/cleanup yo'q.
    """
    page, base = case.page, AutoBasePage(case.page)
    warehouse, quantity = "Основной склад", Decimal("2")
    # Har qanday qo'shimcha forma readbackidan oldin asosiy order listdan boshlash.
    with allure.step("1 - Oddiy orderlar ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    with allure.step("2 - Ombordagi fresh boshlang'ich qoldiq va yetarli mahsulot"):
        retained = retry_value("reserve_initial_stock")
        if retained is None:
            before = _read_stock(case, warehouse)
            case.check("Kamida 2 dona mahsulot mavjud", True, before["available"] >= quantity)
            retry_value("reserve_initial_stock", before)
        else:
            before = decimal_map(retained)
    order_id = existing_order(case)
    if not order_id:
        require_available(case, quantity, bonus_quantity=0)
        open_new_order(page)
        with allure.step("3.1 - Setup klientidan mahsulotlar bosqichiga o'tish"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            base.text("Название", "Кол-во")
        with allure.step("3.2 - 2 dona mahsulot; baseline narx turi va omborni tasdiqlash"):
            goods_row = select_order_product(page, case.product, case.price_type)
            base.b_input(label="Название", expect_value=case.product)
            base.input(label="Кол-во", value="2", press_tab=True)
            # A2 goods gridda ombor/narx turi mahsulot ostidagi matn. Manual
            # 1408 dalili shu ko'rinishni tasdiqlaydi; yashirin dropdown o'ylab
            # topilmaydi. Boshqa saved setting qolgan bo'lsa precondition FAIL.
            base.text(warehouse, case.price_type, root=goods_row)
            expect(goods_row.locator("[data-smt-col-key=price]")).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
        with allure.step("3.3 - Yakunlash bosqichida 14 000 so'm va Новый holati"):
            base.click(name="Далее", exact=True)
            base.text("ИТОГО", "Тип оплаты")
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value="14000")
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Новый")
        order_id = save_order_by_reference(page, case.reference)
    case.remember_order(order_id)
    if not reuse("reserve_new_verified"):
        with allure.step("4 - Saqlangan own order ID, klient, summa va Новый statusi"):
            base.form_view(label="ИД заказа", expect_value=order_id)
            base.form_view(label="Клиент", expect_value=case.client)
            base.form_view(label="Статус", expect_value="Новый")
            base.form_view(label="Сумма заказа", expect_value="14000", remove_spaces=True)
            case.check("Saqlangan order summasi (so'm)", "14000", base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True))
        with allure.step("5 - Новый order faqat 2 dona rezerv yaratadi, physical chiqim yo'q"):
            after_new = _read_stock(case, warehouse)
            case.check("Новый: omborda jismonan mavjud miqdor", before["physical"], after_new["physical"])
            case.check("Новый: bronlangan miqdor", before["booked"] + quantity, after_new["booked"])
            case.check("Новый: sotish mumkin bo'lgan miqdor", before["available"] - quantity, after_new["available"])
        verified("reserve_new_verified")
    cancel_order(page, order_id=order_id, client=case.client, amount="14000")
    with allure.step("11 - Bekor qilish aynan 2 dona rezervni qaytaradi; oldingi rezerv saqlanadi"):
        after_cancel = _read_stock(case, warehouse)
        case.check("Cancel: omborda jismonan mavjud miqdor", before["physical"], after_cancel["physical"])
        case.check("Cancel: bronlangan miqdor boshlang'ich holatga qaytdi", before["booked"], after_cancel["booked"])
        case.check("Cancel: sotish mumkin bo'lgan miqdor boshlang'ich holatga qaytdi", before["available"], after_cancel["available"])


@allure.title("OS-01: Новый orderni bekor qilishda ombor rezervi qaytadi")
def test_cancel_reserve(ordinary_order):
    run_cancel_reserve(ordinary_order)
