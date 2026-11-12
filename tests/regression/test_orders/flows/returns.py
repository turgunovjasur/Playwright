"""Orderdan qaytarish: A2 UI orqali own source va own returnni bog'lash.

Dalil: order-full-20261026/1439,1440,1444,1445,1450,1454,1467;
status/confirmation ketma-ketligi test_16_return_roundtrip.py'da saqlangan.
Net pul va stock kutilmalari consumer leafda; bu modul UI harakatlaridir.
"""
import re
from decimal import Decimal

import allure
from playwright.sync_api import expect

from tests.regression.test_orders.flows.settlement import _columns, _number
from utils.base_pages.auto_base_page import AutoBasePage


NET_LABEL = "Итоговая сумма возврата с учетом общей скидки/наценки к заказу"


def open_return_from_order(page, *, order_id, client, warehouse):
    base = AutoBasePage(page)
    with allure.step("Arxivdan qaytariladigan orderni aniq ID bilan topish"):
        base.navigate_to(tab="Продажа", name="Архив заказов")
        base.expect_page(heading="Архив заказов", url="order_history_list")
        columns = _columns(page, {"id": "ИД заказа", "client": "Клиент"}, search_name="ИД заказа")
        base.grid_controller(search=order_id)
        row = base.grid(order_id, client, click=True)
        expect(base.grid_cell(row, columns["id"])).to_have_text(order_id)
        expect(base.grid_cell(row, columns["client"])).to_have_text(client)
    with allure.step("Shu orderdan qisman qaytarish formasini ochish"):
        base.click(name="Возврат", exact=True)
        base.expect_page(heading="Возврат (создание)", url=re.compile(r"return(?:\+|%2[bB])add"))
        base.input(label="ИД заказа", expect_value=re.compile(rf"^{re.escape(order_id)}\s*/"))
        base.b_input(label="Клиент", expect_value=client)
        base.b_input(label="Валюта", expect_value="Узбекский сум")
        base.b_input(label="Склад", value=warehouse, clear=True)
        base.input(label="Дата отгрузки", value=base.date("today"), press_tab=True)
        base.checkbox(label="Частичный возврат", checked=True)


def return_lot_identity(page, row):
    """Trace-confirmed Return lot identity; drawer fields can be readonly inputs."""
    values = {}
    for key in ("card_code", "expiry_date", "serial_number"):
        cell = row.locator(f'[data-smt-col-key="{key}"]')
        expect(cell).to_have_count(1)
        inputs = cell.locator("input")
        values[key] = (inputs.input_value() if inputs.count() else cell.inner_text()).strip()
    return values


def _return_lot_row(page, grid, product, identity):
    rows = grid.locator(".smt-data-row").filter(has=page.get_by_text(product, exact=True))
    matches = [row for row in rows.all() if return_lot_identity(page, row) == identity]
    if len(matches) != 1:
        raise AssertionError(f"Qaytarish partiyasi yagona emas: {product}; {identity}; soni={len(matches)}")
    matches[0].scroll_into_view_if_needed()
    return matches[0]


def fill_return_items(page, *, product, bonus_product, goods_quantity, bonus_quantity):
    """Allocate requested total across exact source lots, then verify each selected row."""
    base = AutoBasePage(page)
    allocations = []
    with allure.step("Qaytarishdagi mahsulotlar bosqichini ochish"):
        base.click(name="Далее →", exact=True)
        base.text("Кол-во заказа", "Кол-во возврата")
    with allure.step("Qisman qaytarish mahsulotini Подбор orqali tanlash"):
        base.click(name="Подбор", exact=True)
        drawer = page.locator("app-type-d-drawer-host").filter(
            has=page.get_by_role("heading", name="Возврат (подбор)", exact=True))
        expect(drawer).to_be_visible()
        rows = drawer.locator(".smt-data-row").filter(has=page.get_by_text(product, exact=True))
        expect(rows.first).to_be_visible()
        remaining = Decimal(str(goods_quantity))
        for row in rows.all():
            row.scroll_into_view_if_needed()
            identity = return_lot_identity(page, row)
            available = _number(row.locator('[data-smt-col-key="order_quantity"]').inner_text())
            take = min(remaining, available)
            if take > 0:
                allocations.append({**identity, "quantity": str(take)})
                remaining -= take
            if remaining == 0:
                break
        if remaining:
            raise AssertionError(f"{product}: {goods_quantity} dona so‘raldi, {remaining} dona qaytarish qoldig‘i yetmaydi")
        for index, allocation in enumerate(allocations):
            identity = {k: allocation[k] for k in ("card_code", "expiry_date", "serial_number")}
            row = _return_lot_row(page, drawer, product, identity)
            field = row.locator('[data-smt-col-key="quantity"] input').filter(visible=True)
            expect(field).to_have_count(1)
            base.input(locator=field, value=allocation["quantity"], press_tab=True)
            count_before = rows.count()
            base.click(name="Действия", exact=True, root=row)
            if index + 1 < len(allocations):
                # The picker removes the selected lot asynchronously.
                expect(rows).to_have_count(count_before - 1)
        base.click(name="Закрыть", exact=True, root=drawer)
        expect(drawer).to_have_count(0)
    with allure.step(f"Asosiy mahsulotdan jami {goods_quantity} dona — har partiyani tekshirish"):
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(len(allocations))
        for allocation in allocations:
            identity = {k: allocation[k] for k in ("card_code", "expiry_date", "serial_number")}
            row = _return_lot_row(page, grid, product, identity)
            field = row.locator('[data-smt-col-key="quantity"] input').filter(visible=True)
            expect(field).to_have_count(1)
            base.input(locator=field, value=allocation["quantity"], press_tab=True)
            base.input(locator=field, expect_value=allocation["quantity"])
    with allure.step(f"Bepul bonusdan {bonus_quantity} dona qaytarish"):
        base.tab(name="Акция")
        grid = page.locator("smt-table:visible").last
        if bonus_quantity:
            expect(grid.locator(".smt-data-row")).to_have_count(1)
            row = base.grid(bonus_product, root=grid)
            labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
            if labels.count("Кол-во") != 1:
                raise AssertionError(f"Return bonus miqdor ustuni yagona emas: {labels}")
            field = base.grid_cell(row, labels.index("Кол-во")).locator("input").filter(visible=True)
            expect(field).to_have_count(1)
            base.input(locator=field, value=str(bonus_quantity), press_tab=True)
        else:
            expect(grid.locator(".smt-data-row")).to_have_count(0)
    return allocations


def finish_return(page, *, reason, reference, net_amount):
    base = AutoBasePage(page)
    with allure.step("Qaytarishning qo'shimcha ma'lumotlarini ochish"):
        base.click(name="Далее →", exact=True)
        base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
        base.b_input(label="Причина возврата", value=reason)
        base.input(label="Номер товарно-транспортной накладной", value=reference)
    with allure.step("Qaytarishni yakunlash: asl chegirmadan keyingi net summani tekshirish"):
        base.click(name="Далее →", exact=True)
        base.ui_select(label="Статус", value="Черновик")
        # A2 dalilida total readonly input emas, label va son bir text blokda.
        digits = r"\s*".join(str(net_amount))
        expect(page.get_by_text(re.compile(re.escape(NET_LABEL) + r"\s*" + digits + r"\s*$"))).to_have_count(1)


def find_return(page, *, reference, source_id):
    base = AutoBasePage(page)
    with allure.step("Order IDsi orqali qidirib, aynan kerakli TTNli qaytarishni topish"):
        base.navigate_to(tab="Продажа", name="Возвраты")
        base.expect_page(heading="Возвраты", url="return_list")
        columns = _columns(page, {
            "reference": "Номер товарно-транспортной накладной",
            "source_id": "ИД заказа",
        }, search_name="ИД заказа")
        base.grid_controller(search=source_id)
        # Bir orderdan bir nechta qaytarish bo'lishi mumkin; target TTN yagona.
        matches = page.locator("smt-data-table:visible .smt-data-row").filter(has_text=reference)
        expect(matches).to_have_count(1)
        row = base.grid(reference, click=True)
        expect(base.grid_cell(row, columns["reference"])).to_have_text(reference)
        expect(base.grid_cell(row, columns["source_id"])).to_have_text(source_id)
        return row


def open_return_view(page, *, reference, source_id, client, status, net_amount, return_id=None):
    base = AutoBasePage(page)
    row = find_return(page, reference=reference, source_id=source_id)
    with allure.step("Qaytarish ro'yxatidagi net summa va saqlangan IDni tekshirish"):
        columns = _columns(page, {"total": "ИТОГО"})
        actual = _number(base.grid_cell(row, columns["total"], return_value=True))
        if actual != _number(str(net_amount)):
            raise AssertionError(f"Return ro'yxatidagi net summa: expected={net_amount}, actual={actual}")
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="Возврат (просмотр)", url="return_view")
        found_id = base.form_view(label="ИД возврата", expect_value=return_id or re.compile(r"^\d+$"), return_value=True).strip()
        for label, value in (("ИД заказа", source_id), ("Клиент", client), ("Статус", status), ("Валюта", "Узбекский сум"), ("Склад", "Основной склад")):
            base.form_view(label=label, expect_value=value)
        return found_id


def save_return_draft(page):
    base = AutoBasePage(page)
    from tests.regression.retry.reconcile import is_retry, ui_row, allow_absent_ui_write, confirm_entity
    from tests.regression.retry.state import ACTIVE, RetryBlocked
    record = ACTIVE.get().case.returns[-1]
    if is_retry():
        existing = ui_row(page, "anor/mdeal/return/return_list:table",
                          ["deal_id", "delivery_number", "order_deal_id"], "delivery_number", record["reference"])
        if existing:
            if str(existing["order_deal_id"]) != str(record["source_order_id"]):
                raise AssertionError("Mavjud qaytarish boshqa orderga tegishli")
            base.open_route("anor/mdeal/return/return_list", heading="Возвраты")
            confirm_entity("return", record["reference"], existing["deal_id"])
            return str(existing["deal_id"])
        allow_absent_ui_write("anor/mdeal/return/return+add$save", identity={"delivery_number": record["reference"]})
    with allure.step("Qaytarish draftini saqlash"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        # Source Archive qatoridan ochilgan return Save source listga qaytadi.
        base.expect_page(heading="Архив заказов", url="order_history_list")
        existing = ui_row(page, "anor/mdeal/return/return_list:table",
                          ["deal_id", "delivery_number", "order_deal_id"], "delivery_number", record["reference"])
        if not existing or str(existing["order_deal_id"]) != str(record["source_order_id"]):
            raise RetryBlocked("Return Save’dan keyingi exact ID/source tasdiqlanmadi; ikkinchi Save yuborilmadi")
        confirm_entity("return", record["reference"], existing["deal_id"])
        return str(existing["deal_id"])


def archive_return(page, *, reference, source_id):
    base = AutoBasePage(page)
    row = find_return(page, reference=reference, source_id=source_id)
    with allure.step("Own qaytarishni arxivga o'tkazish"):
        # 328/335/338 A2 snapshot: row popup accessible nomi «Статус».
        base.click(name="Статус", exact=True, root=row)
        base.click(name="Архив", role="menuitem", exact=True)
        base.confirm_biruni("Изменить на Архив?")
        base.wait_for_loader()
