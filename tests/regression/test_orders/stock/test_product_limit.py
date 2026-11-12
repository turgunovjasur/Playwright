"""Kunlik TMZ limiti: ikki order 6+4 → birinchisini bekor qilish → ikkinchisi 10.

Dalil: artifacts/order-full-20261026/609–631. Faqat positive oqim;
limitdan ortiq miqdorni rad etish bu case qamroviga kirmaydi.
"""
from decimal import Decimal

from tests.regression.retry.checkpoints import reuse, verified
import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.flows.order import (existing_order, saved_quantities,
    open_new_order, select_order_product, save_order_by_reference,
    save_edited_order, reopen_order_goods,
)
from tests.regression.test_orders.flows.order_status import cancel_order
from tests.regression.test_orders.flows.settlement import _columns
from tests.regression.test_orders.flows.stock import read_stock
from tests.regression.test_orders.preparations.test_product_limit import persist
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.retry.reconcile import is_retry
from tests.regression.retry.state import RetryBlocked
from tests.regression.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive]


def _record(case, directory):
    persist(case.workflow, directory)
    case.checkpoint()


def _stock(case, expected_reserved):
    data = case.workflow
    before = {key: Decimal(value) for key, value in data["stock_before"].items()}
    actual = read_stock(case, "Основной склад", product_id=data["product"]["id"])
    expected = {"physical": before["physical"],
                "booked": before["booked"] + Decimal(expected_reserved),
                "available": before["available"] - Decimal(expected_reserved)}
    case.check(f"Own mahsulot: fizik qoldiq o‘zgarmaydi; umumiy rezerv {expected_reserved} dona", expected, actual)


def _saved(case, order, quantity, *, status="Новый"):
    base, page = AutoBasePage(case.page), case.page
    amount = Decimal(quantity) * Decimal(case.workflow["price"]["unit_price"])
    for label, value in (("ИД заказа", order["id"]), ("Клиент", case.client),
                         ("Статус", status), ("Номер ТТН", order["reference"]),
                         ("Тип оплаты", "Наличные деньги")):
        base.form_view(label=label, expect_value=value)
    case.check("Saqlangan order summasi", amount,
               Decimal(base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)))
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, case.price_type, "Основной склад", root=grid)
    headers = [" ".join(text.split()) for text in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество продажи", Decimal(quantity)), ("Цена", Decimal("7000")), ("Итого", amount)):
        if headers.count(label) != 1:
            raise AssertionError(f"TMZ limit orderida {label} ustuni yagona emas: {headers}")
        raw = base.grid_cell(row, headers.index(label), return_value=True, remove_spaces=True)
        case.check(f"Saqlangan mahsulot — {label}", expected, Decimal(raw.replace(",", ".")))
    expect(page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)


def run_create_limit_order(case, directory, *, key, quantity, reserved_before, reserved_after):
    """1. Own SKU rezervi. 2. Same room/date order. 3. Save/view/reopen. 4. Aggregate rezerv."""
    data, base = case.workflow, AutoBasePage(case.page)
    if data.get("status") != "passed" or Decimal(data["limit"]["quantity"]) != 10:
        raise AssertionError("Oldin same room + own SKU uchun saqlangan kunlik limit10 kerak")
    if key in data["orders"]:
        raise AssertionError("Bu runner bosqichi orderni takroran yaratmasligi kerak")
    with allure.step(f"1 - Yangi orderdan oldin own TMZ umumiy rezervi {reserved_before}"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        if not reuse("limit_before_create:" + key):
            _stock(case, reserved_before)
            verified("limit_before_create:" + key)
    identity = existing_order(case)
    if not identity:
        require_available(case, quantity, bonus_quantity=0)
        open_new_order(case.page)
        with allure.step(f"2 - Bir xil xona va limit sanasida {quantity} dona order"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            # Daily quota uchun order va jo‘natish kuni tayyorlov bilan bir xil.
            # 569-limit-order-main27oct.txt: Дата заказа date+time, jo‘natish date-only.
            base.input(label="Дата заказа", value=f"{data['date']} 10:00", press_tab=True)
            base.input(label="Дата отгрузки", value=data["date"], press_tab=True)
            base.input(label="Дата заказа", expect_value=f"{data['date']} 10:00")
            base.input(label="Дата отгрузки", expect_value=data["date"])
            base.click(name="Далее", exact=True)
            select_order_product(case.page, case.product, case.price_type)
            base.input(label="Кол-во", value=str(quantity), press_tab=True)
        with allure.step("3 - Chegirma va bonussiz Новый orderni saqlashga tayyorlash"):
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value=str(quantity * 7000))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Новый")
        identity = save_order_by_reference(case.page, case.reference)
    order = {"id": identity, "reference": case.reference, "quantity": str(quantity),
             "amount": str(quantity * 7000), "status": "Новый", "stage": "saved"}
    data["orders"][key] = order
    case.remember_order(identity)
    _record(case, directory)
    with allure.step("4 - Aynan saqlangan order: ID, miqdor, narx, summa va bonussiz tarkib"):
        _saved(case, order, quantity)
    reopen_order_goods(case.page)
    with allure.step("5 - Qayta ochilgan orderda own mahsulot va miqdor saqlangan"):
        base.b_input(label="Название", expect_value=case.product)
        base.input(label="Кол-во", expect_value=str(quantity))
    with allure.step(f"6 - Ikkala orderning umumiy rezervi {reserved_after} dona"):
        _stock(case, reserved_after)
    order["stage"] = "verified"
    _record(case, directory)


def run_cancel_first_limit_order(case, directory):
    """1. Ikki order: 6+4=10. 2. Birinchi 6 dona bekor. 3. Rezerv 4 qoladi."""
    data = case.workflow
    first, second = data["orders"]["first"], data["orders"]["second"]
    if any(order["stage"] != "verified" for order in (first, second)):
        raise AssertionError("Bekor qilishdan oldin ikkala order saqlanib tekshirilishi kerak")
    with allure.step("1 - Ikki order bo‘yicha 10 dona umumiy rezerv"):
        if not reuse("limit_before_cancel"):
            _stock(case, 10)
            verified("limit_before_cancel")
    case.remember_order(first["id"])
    cancel_order(case.page, order_id=first["id"], client=case.client, amount=first["amount"])
    first.update(status="Отменен", stage="cancelled")
    _record(case, directory)
    with allure.step("2 - Bekor qilingan 6 dona rezerv qaytadi; ikkinchi orderning 4 donasi qoladi"):
        _stock(case, 4)
    first["stage"] = "cancel_verified"
    _record(case, directory)


def run_reuse_released_product_limit(case, directory):
    """1. Ikkinchi order IDsi. 2. Miqdor 4→10. 3. Save/view/reopen. 4. Rezerv 10."""
    data, page, base = case.workflow, case.page, AutoBasePage(case.page)
    first, second = data["orders"]["first"], data["orders"]["second"]
    if first["stage"] != "cancel_verified" or second["stage"] != "verified":
        raise AssertionError("Avval birinchi 6 dona order bekor qilinishi kerak")
    case.remember_order(second["id"])
    with allure.step("1 - Ikkinchi orderni aniq ID bilan topish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        col = _columns(page, {"id": "ИД заказа"}, search_name="ИД заказа")["id"]
        base.grid_controller(search=second["id"])
        row = base.grid(second["id"], click=True)
        expect(base.grid_cell(row, col)).to_have_text(second["id"])
    with allure.step("2 - Saqlangan ikkinchi order viewini ochish"):
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
    actual = saved_quantities(page, case.product, case.price_type, ["Основной склад"])
    if is_retry() and actual == (Decimal(10),):
        if not reuse("product_limit_before_edit"):
            raise RetryBlocked("10 dona saqlangan, lekin oldingi 4 dona tekshiruvi dalili yo‘q")
    else:
        _saved(case, second, 4)
        verified("product_limit_before_edit")
        reopen_order_goods(page)
        with allure.step("3 - Bo‘shagan 6 dona limitni qayta ishlatish: ikkinchi order 4→10"):
            base.b_input(label="Название", expect_value=case.product)
            base.input(label="Кол-во", expect_value="4")
            base.input(label="Кол-во", value="10", press_tab=True)
            base.click(name="Далее", exact=True)
            base.input(label="ИТОГО", expect_value="70000")
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.ui_select(label="Статус", expect_value="Новый")
        save_edited_order(page, second["id"], second["reference"])
    second.update(quantity="10", amount="70000", stage="resaved")
    _record(case, directory)
    with allure.step("4 - Aynan ikkinchi order 10 dona va 70 000 so‘m bo‘lib saqlangan"):
        _saved(case, second, 10)
    reopen_order_goods(page)
    with allure.step("5 - Qayta ochilganda ham miqdor 10"):
        base.b_input(label="Название", expect_value=case.product)
        base.input(label="Кол-во", expect_value="10")
    with allure.step("6 - Jismoniy qoldiq o‘zgarmaydi, jami rezerv yana 10 dona"):
        _stock(case, 10)
    second["stage"] = "reuse_verified"
    data["result"] = "passed"
    _record(case, directory)


def verify_resume_state(case):
    """No mutations: validate the saved daily quota, both orders and reserve."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from tests.regression.test_orders.preparations.test_product_limit import verify_saved_limit

    data, page, base = case.workflow, case.page, AutoBasePage(case.page)
    with allure.step("Resume: sana, oldingi orderlar va boshlang‘ich holat mosligini tekshirish"):
        if data["date"] != datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%d.%m.%Y"):
            raise AssertionError("Kunlik TMZ limiti boshqa sanaga tegishli; avtomatik davom ettirish to‘xtatildi")
        first, second = data["orders"]["first"], data["orders"]["second"]
        if first["stage"] not in ("verified", "cancel_verified") or second["stage"] != "verified":
            raise AssertionError("Resume uchun order checkpoint bosqichlari mos emas")
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    with allure.step("Resume: aynan saqlangan limit, xona, sana va 10 dona saqlangan"):
        verify_saved_limit(case)
    for key, quantity in (("first", 6), ("second", 4)):
        order = data["orders"][key]
        with allure.step(f"Resume: {order['id']} orderning serverdagi saqlangan holati"):
            base.open_route("trade/tdeal/order/order_view?deal_id=" + order["id"], heading="Заказ / Просмотр")
            if key == "first" and first["stage"] == "cancel_verified":
                _saved(case, order, quantity, status="Отменен")
                continue
            _saved(case, order, quantity)
            base.click(name="Редактировать", exact=True)
            base.expect_page(heading="Заказ (изменение)", url="order")
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", expect_value=case.client)
            base.input(label="Дата заказа", expect_value=f"{data['date']} 10:00")
            base.input(label="Дата отгрузки", expect_value=data["date"])
    with allure.step("Resume: ikkala orderning amaldagi umumiy rezervi"):
        _stock(case, 4 if first["stage"] == "cancel_verified" else 10)
