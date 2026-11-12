"""Bir SKU ikki omborda: qoralama, rezerv, qayta taqsimlash va Cancel.

A2 dalili: order-ui-elements-20261028/1408, 1410–1426.
Mahsulot/ombor/klient tayyorlovi alohida runner qadamlarida bajariladi.
"""
from decimal import Decimal
import re

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.flows.order import (existing_order, saved_quantities,
    open_new_order, reopen_order_goods, save_edited_order,
    save_order_by_reference, select_order_product,
)
from tests.regression.test_orders.flows.order_status import cancel_order
from tests.regression.test_orders.flows.settlement import _columns, change_order_status
from tests.regression.test_orders.flows.stock import read_stock
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.retry.reconcile import is_retry
from tests.regression.retry.state import RetryBlocked
from tests.regression.retry.checkpoints import reuse, verified, value as retry_value


pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Bitta orderda ikki ombor")]
UNIT_PRICE = Decimal("7000")
TOTAL = Decimal("35000")


def _metadata(case):
    metadata = case.workflow.get("two_warehouses", {})
    if metadata.get("status") != "passed" or len(metadata.get("warehouses", [])) != 2:
        raise AssertionError("Ikki ombor va ularning qoldiq tayyorlovi to'liq tasdiqlanmagan")
    return metadata


def _goods_row(case, warehouse):
    row = case.page.locator("smt-table:visible .smt-data-row").filter(
        has=case.page.get_by_text(warehouse, exact=True)
    ).filter(has=case.page.get_by_text(case.price_type, exact=True))
    expect(row).to_have_count(1)
    expect(row).to_be_visible()
    return row


def _quantity_input(case, row):
    # Column keys are read from the observed A2 header, never invented.
    table = row.locator("xpath=ancestor::smt-table[1]")
    header = table.locator(".smt-grid-header [data-smt-col-key]").filter(
        has_text=re.compile(r"^\s*Кол-во\s*$")
    )
    expect(header).to_have_count(1)
    key = header.get_attribute("data-smt-col-key")
    field = row.locator(f'[data-smt-col-key="{key}"] input').filter(visible=True)
    expect(field).to_have_count(1)
    return field


def _saved_lines(case, quantities, status):
    """Har qatorning ombor identitysi, miqdori va mustaqil summasini tekshiradi."""
    base = AutoBasePage(case.page)
    metadata = _metadata(case)
    order = metadata["order"]
    base.form_view(label="ИД заказа", expect_value=order["id"])
    base.form_view(label="Номер ТТН", expect_value=order["reference"])
    base.form_view(label="Клиент", expect_value=case.client)
    base.form_view(label="Статус", expect_value=status)
    base.form_view(label="Валюта", expect_value="Узбекский сум")
    case.check("Ikki omborli orderning saqlangan jami", TOTAL,
               Decimal(base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)))
    grid = case.page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(2)
    headers = [" ".join(value.split()) for value in
               grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for warehouse, quantity in zip(metadata["warehouses"], quantities):
        row = _goods_row(case, warehouse["name"])
        base.text(case.product, case.price_type, root=row)
        for label, expected in (("Количество продажи", Decimal(quantity)), ("Цена", UNIT_PRICE),
                                ("Сумма скидки/наценки", Decimal("0")),
                                ("Итого", Decimal(quantity) * UNIT_PRICE)):
            if headers.count(label) != 1:
                raise AssertionError(f"Ikki ombor viewida ustun yagona emas: {label}")
            actual = base.grid_cell(row, headers.index(label), return_value=True, remove_spaces=True)
            case.check(f'{warehouse["name"]}: saqlangan {label}', expected,
                       Decimal(actual.replace(",", ".")))
    case.check("Bir xil SKU ikki alohida ombor qatorida saqlangan", 2,
               grid.locator(".smt-data-row").count())


def _stock_delta(case, quantities, stage):
    metadata = _metadata(case)
    for warehouse, quantity in zip(metadata["warehouses"], quantities):
        before = {key: Decimal(value) for key, value in
                  metadata["stock_before"][warehouse["id"]].items()}
        expected = {**before, "booked": before["booked"] + Decimal(quantity),
                    "available": before["available"] - Decimal(quantity)}
        case.check(f'{stage}: {warehouse["name"]} fizik qoldiq va rezerv', expected,
                   read_stock(case, warehouse["name"]))


def _open_view(case):
    order = _metadata(case)["order"]
    base = AutoBasePage(case.page)
    with allure.step("Own ikki omborli orderni exact ID bo'yicha ro'yxatdan topish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        column = _columns(case.page, {"id": "ИД заказа"}, search_name="ИД заказа")["id"]
        base.grid_controller(search=order["id"])
        row = base.grid(order["id"], click=True)
        expect(base.grid_cell(row, column)).to_have_text(order["id"])
    with allure.step("Aynan shu ikki omborli order viewini ochish"):
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="ИД заказа", expect_value=order["id"])


def run_create_two_warehouses(case):
    """1. Listdan boshlab ikkala omborning fresh baseline qoldig'ini olish.
    2. Bitta SKU: asosiy ombordan 2, own ikkinchi ombordan 3 dona tanlash.
    3. 5 × 7 000 = 35 000 so'mlik Черновик saqlash.
    4. View va reopened editda ikkala qatorni alohida tekshirish.
    5. Draft ikkala omborning fizik/rezerv/available qiymatini o'zgartirmaydi.
    """
    metadata = _metadata(case)
    page, base = case.page, AutoBasePage(case.page)
    with allure.step("1 - Orderlar ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    with allure.step("2 - Ikkala omborning boshlang‘ich fizik, rezerv va erkin qoldig‘i"):
        retained = retry_value("two_warehouses_initial_stock")
        if retained is not None:
            metadata["stock_before"] = retained
        else:
            from tests.regression.retry.state import ACTIVE
            if ACTIVE.get().previous("entity:order:" + case.reference):
                raise RetryBlocked("Order mavjud, lekin original ikki ombor qoldig‘i dalili yo‘q")
            metadata["stock_before"] = {}
            for warehouse in metadata["warehouses"]:
                stock = read_stock(case, warehouse["name"])
                case.check(f'{warehouse["name"]}: kamida 3 dona erkin qoldiq', True, stock["available"] >= 3)
                metadata["stock_before"][warehouse["id"]] = {key: str(value) for key, value in stock.items()}
            retry_value("two_warehouses_initial_stock", metadata["stock_before"])
            case.checkpoint()
    identity = existing_order(case)
    if not identity:
        open_new_order(page)
        with allure.step("3 - Own klient bilan mahsulotlar bosqichiga o'tish"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            base.text("Название", "Кол-во")
        with allure.step("4 - Bitta SKU uchun ikki ombor variantini alohida tanlash"):
            for index, (warehouse, quantity) in enumerate(zip(metadata["warehouses"], (2, 3))):
                row = select_order_product(page, case.product, case.price_type,
                                           warehouse=warehouse["name"], index=index)
                base.input(locator=_quantity_input(case, row), value=str(quantity), press_tab=True)
                expect(row.locator("[data-smt-col-key=price]")).to_have_text(re.compile(r"^\s*7\s*000\s*$"))
        with allure.step("5 - 35 000 so'm, chegirma 0 va Черновик holati"):
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value=str(TOTAL))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        identity = save_order_by_reference(page, case.reference)
    metadata["order"] = {"id": identity, "reference": case.reference,
                         "quantities": [2, 3], "status": "Черновик"}
    case.remember_order(identity)
    with allure.step("6 - Saved viewda ikkala omborning qatori va summalari"):
        _saved_lines(case, (2, 3), "Черновик")
    reopen_order_goods(page)
    with allure.step("7 - Reopened editda ombor identitylari va 2/3 dona saqlangan"):
        for index, (warehouse, quantity) in enumerate(zip(metadata["warehouses"], (2, 3))):
            row = _goods_row(case, warehouse["name"])
            base.input(locator=_quantity_input(case, row), expect_value=str(quantity))
    with allure.step("8 - Draft ikkala omborning qoldig'ini o'zgartirmagan"):
        _stock_delta(case, (0, 0), "Черновик")


def run_reserve_two_warehouses(case):
    """1. Shu Draftni Новыйga o'tkazish. 2. Viewda 2/3 qator saqlangan.
    3. Asosiy ombor +2, ikkinchi +3 rezerv; fizik qoldiq o'zgarmaydi.
    """
    metadata = _metadata(case)
    order = metadata["order"]
    change_order_status(case.page, order["id"], current="Черновик", target="Новый")
    order["status"] = "Новый"
    case.checkpoint()
    with allure.step("1 - Новый orderda ikkala ombor identitysi va 35 000 jami"):
        _saved_lines(case, (2, 3), "Новый")
    with allure.step("2 - Ikkala omborda mustaqil 2/3 rezerv va fizik chiqim yo'qligi"):
        _stock_delta(case, (2, 3), "Новый")


def run_reallocate_two_warehouses(case):
    """1. Own Новый orderni tahrirga qayta ochish.
    2. 2/3 taqsimotni 3/2ga almashtirish; umumiy 5 dona va 35 000 saqlanadi.
    3. Save/view/reopen; rezervlar 3/2 bo'ladi, jismoniy qoldiq o'zgarmaydi.
    """
    metadata = _metadata(case)
    base = AutoBasePage(case.page)
    _open_view(case)
    actual = saved_quantities(case.page, case.product, case.price_type, [w["name"] for w in metadata["warehouses"]])
    order = metadata["order"]
    if is_retry() and actual == (Decimal(3), Decimal(2)):
        if not reuse("two_warehouses_before_edit"):
            raise RetryBlocked("3/2 saqlangan, lekin oldingi 2/3 tekshiruvi dalili yo‘q")
    else:
        _saved_lines(case, (2, 3), "Новый")
        verified("two_warehouses_before_edit")
        reopen_order_goods(case.page)
        with allure.step("1 - Omborlar o'rtasida 2/3 miqdorni 3/2ga qayta taqsimlash"):
            for warehouse, quantity in zip(metadata["warehouses"], (3, 2)):
                row = _goods_row(case, warehouse["name"])
                base.input(locator=_quantity_input(case, row), value=str(quantity), press_tab=True)
        with allure.step("2 - O'zgarmagan jami 35 000 va Новый statusini tekshirish"):
            base.click(name="Далее", exact=True)
            base.input(label="ИТОГО", expect_value=str(TOTAL))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.ui_select(label="Статус", expect_value="Новый")
        order = metadata["order"]
        identity = save_edited_order(case.page, order["id"], order["reference"])
        case.check("Tahrirda ayni order ID saqlanadi", order["id"], identity)
    order["quantities"] = [3, 2]
    case.checkpoint()
    with allure.step("3 - Saved viewda yangi 3/2 taqsimot"):
        _saved_lines(case, (3, 2), "Новый")
    reopen_order_goods(case.page)
    with allure.step("4 - Reopened editda ikkala miqdor 3/2 saqlangan"):
        for warehouse, quantity in zip(metadata["warehouses"], (3, 2)):
            base.input(locator=_quantity_input(case, _goods_row(case, warehouse["name"])),
                       expect_value=str(quantity))
    with allure.step("5 - Har omborning yangi rezervi 3/2; physical o'zgarmagan"):
        _stock_delta(case, (3, 2), "Tahrirlangan Новый")


def run_cancel_two_warehouses(case):
    """1. Aynan own orderni bekor qilish. 2. Viewda ikki qator va ID saqlanadi.
    3. Ikkala ombor qoldig'i baselinega qaytadi; avvalgi rezervlar saqlanadi.
    """
    metadata = _metadata(case)
    order = metadata["order"]
    cancel_order(case.page, order_id=order["id"], client=case.client, amount=str(TOTAL))
    order["status"] = "Отменен"
    case.checkpoint()
    with allure.step("1 - Bekor qilingan own orderning ikki ombor qatori saqlangan"):
        _saved_lines(case, order["quantities"], "Отменен")
    with allure.step("2 - Ikkala omborning physical, booked va available qiymatlari baselinega qaytdi"):
        _stock_delta(case, (0, 0), "Отменен")
