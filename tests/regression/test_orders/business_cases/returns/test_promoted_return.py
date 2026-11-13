"""To'langan bonus+skidkali orderni qisman va qolgan qismiga qaytarish.

Runner har bir run_* ni alohida case sifatida qat'iy tartibda chaqiradi.
Hisoblar: 10 × 7 000 − 10% = 63 000; bonus bepul. Qaytarish kreditlari
12 600 va 50 400. Pul kassadan chiqmaydi: klient predoplatasi 63 000 bo'ladi.
"""
from decimal import Decimal
import re
from urllib.parse import unquote, urlsplit

import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.flows.order import existing_order, open_new_order, promotion_card, save_order_by_reference, select_order_product
from tests.regression.test_orders.helpers.flows.returns import _return_lot_row, archive_return, fill_return_items, finish_return, open_return_from_order, open_return_view, save_return_draft
from tests.regression.test_orders.helpers.flows.settlement import allocate_to_order, change_order_status, post_cashin, read_debts, read_settlement, _number
from tests.regression.test_orders.helpers.flows.stock import read_stock
from tests.shared.navigation import open_form_from_list
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.retry.checkpoints import value as retry_value, reuse, verified
from tests.regression.helpers.retry.state import RetryBlocked

pytestmark = [pytest.mark.regression, pytest.mark.regression_requires_setup, pytest.mark.order_positive]
WAREHOUSE = "Основной склад"
ZERO = {key: Decimal("0") for key in ("debt", "prepayment", "open_order", "booked_prepayment", "balance")}


def _stock(case, goods_out, bonus_out):
    """UI snapshotni original stock bilan solishtiradi; biznes miqdorlar argumentda."""
    for kind, product_id, delta in (("goods", case.baseline["product_id"], goods_out), ("bonus", case.baseline["product_id_usa"], bonus_out)):
        before = {key: Decimal(value) for key, value in case.workflow["stock_before"][kind].items()}
        expected = {**before, "physical": before["physical"] - Decimal(delta), "available": before["available"] - Decimal(delta)}
        case.check(f"{kind}: ombor miqdori va rezerv", expected, read_stock(case, WAREHOUSE, product_id=product_id))


def _settlement(case, *, debt=0, prepayment=0):
    actual = read_settlement(case.page, case.client)
    expected = {**ZERO, "debt": Decimal(debt), "prepayment": Decimal(prepayment), "balance": Decimal(prepayment) - Decimal(debt)}
    case.check('Klient qarzi, avansi, ochiq order summasi va bronlangan avansi', expected, actual)
    source = case.workflow["source_order"]["id"]
    case.check('Aynan dastlabki orderning qarzi', {source: Decimal(debt)} if debt else {}, read_debts(case.page, case.client, settlement=actual))


def _saved_return_items(case, goods_quantity, bonus_quantity, net_amount, allocations):
    page, base = case.page, AutoBasePage(case.page)
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(len(allocations))
    total_quantity, total_amount = Decimal(0), Decimal(0)
    unit_net = Decimal(net_amount) / Decimal(goods_quantity)
    for allocation in allocations:
        identity = {k: allocation[k] for k in ("card_code", "expiry_date", "serial_number")}
        row = _return_lot_row(page, grid, case.product, identity)
        quantity = _number(row.locator('[data-smt-col-key="quantity"]').inner_text())
        amount = _number(row.locator('[data-smt-col-key="amount_with_margin"]').inner_text())
        case.check(f"Saved partiya {identity}: miqdor", Decimal(allocation["quantity"]), quantity)
        case.check(f"Saved partiya {identity}: sof summa", Decimal(allocation["quantity"]) * unit_net, amount)
        total_quantity += quantity
        total_amount += amount
    case.check("Qaytarishdagi barcha partiyalarning jami miqdori", Decimal(goods_quantity), total_quantity)
    case.check("Qaytarishdagi barcha partiyalarning jami sof summasi", Decimal(net_amount), total_amount)
    base.tab(name="Акция")
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1 if bonus_quantity else 0)
    if bonus_quantity:
        row = base.grid(case.bonus_product, root=grid)
        labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Кол-во", bonus_quantity),):
            if labels.count(label) != 1:
                raise AssertionError(f"Saved Return bonus: {label} ustuni yagona emas: {labels}")
            case.check(f"Saqlangan bepul bonus: {label}", Decimal(value), _number(base.grid_cell(row, labels.index(label), return_value=True)))
    # Возврат narxi va qayta baholash bir-birini qoplashi mumkin.
    # Bepul bonus uchun biznes kutilmasi — klientga qaytadigan sof pul 0.
    total = page.get_by_text(re.compile(r"Итого сумма:\s*[-\d\s,.]+$"))
    expect(total).to_have_count(1)
    match = re.search(r"Итого сумма:\s*([-\d\s,.]+)$", total.inner_text())
    case.check("Qaytarilgan bepul bonusning sof summasi", Decimal("0"), _number(match.group(1)))


def run_prepare_reason(case):
    """1. Qaytarish sabablarini ochish.
    2. Faqat shu runner uchun aktiv sabab yaratish.
    3. Own nom va kod bilan saqlangan qatorni tasdiqlash.
    """
    page, base = case.page, AutoBasePage(case.page)
    reason = {"name": f"QA_RETURN_{case.reference}", "code": f"RET_{case.reference}"}
    with allure.step("1 - Qaytarish ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Возвраты")
        base.expect_page(heading="Возвраты", url="return_list")
    with allure.step("2 - Qaytarish sabablari katalogini ochish"):
        base.page_link(name="Причины возврата")
        base.expect_page(heading="Причины возврата", url="return_reason_list")
        from tests.regression.helpers.retry.reconcile import is_retry, ui_row, allow_absent_ui_write
        existing = ui_row(page, "anor/mdeal/return/return_reason_list:table", ["reason_id", "name"], "name", reason["name"]) if is_retry() else None
    with allure.step('3 - Qaytarish sababini mavjudidan olish yoki yo‘q bo‘lsa yaratish'):
        case.workflow["return_reason"] = {**reason, "state": "pending"}
        case.checkpoint()
        if not existing:
            allow_absent_ui_write("anor/mdeal/return/return_reason+add$save", identity={"name": reason["name"]})
            open_form_from_list(base.page, heading="Причина возврата (создание)", url=re.compile(r"return_reason(?:\+|%2[bB])add"))
            base.input(label="Название", value=reason["name"])
            base.input(label="Код", value=reason["code"])
            base.checkbox(label="Активный", checked=True)
            base.click(name="Сохранить", exact=True)
            base.expect_page(heading="Причины возврата", url="return_reason_list")
        base.grid_controller(search=reason["name"])
        row = base.grid(reason["name"])
        base.text(reason["code"], root=row)
        case.workflow["return_reason"].update(state="saved", source=page.url)
        case.checkpoint()


def run_create_promoted_order(case):
    """1. Own klient balansi nol va ikkala SKU stockini qayd etish.
    2. A10 × 7 000, 10% chegirma, B1 bepul bonus bilan Draft yaratish.
    3. Saqlangan 63 000 summa va bepul bonusni tekshirish.
    """
    page, base = case.page, AutoBasePage(case.page)
    order_id = existing_order(case)
    if not order_id:
        with allure.step("1 - Alohida test klienti va mahsulotlarning boshlang'ich holati"):
            case.check('Qaytarish testidan oldingi klient balansi 0', ZERO, read_settlement(page, case.client))
            case.check('Test mahsulotining narxi 7 000 so‘m', Decimal("7000"), Decimal(case.promotions["unit_price"]))
            case.workflow["stock_before"] = {}
            for kind, product_id, required in (("goods", case.baseline["product_id"], 10), ("bonus", case.baseline["product_id_usa"], 1)):
                stock = read_stock(case, WAREHOUSE, product_id=product_id)
                if stock["available"] < required:
                    raise AssertionError(f"Return tayyorlovi: {kind} uchun {required} dona mavjud bo'lishi kerak")
                case.workflow["stock_before"][kind] = {key: str(value) for key, value in stock.items()}
            retry_value("return_initial_stock", case.workflow["stock_before"])
            case.checkpoint()
        open_new_order(page)
        with allure.step('2 - Test klientiga 10 dona mahsulotdan order yaratish'):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="10", press_tab=True)
        with allure.step('3 - Boshqa mahsulotdan 1 dona bepul bonus va 10% chegirma aksiyalarini yoqish'):
            with page.expect_response(lambda response: response.request.method == "POST" and unquote(urlsplit(response.url).path).endswith("/order/order+add:find_extra_data")) as offers:
                base.tab(name=re.compile(r"^Акции"))
            case.check("Aksiyalar yuklandi", 200, offers.value.status)
            offers.value.finished()
            base.wait_for_loader()
            for key in ("bonus", "discount"):
                base.checkbox(locator=promotion_card(page, case.promotions[key]["name"]).get_by_role("switch"), checked=True)
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(2)
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value="63000")
            base.input(label="Сумма скидки/наценки", expect_value="-7000")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        order_id = save_order_by_reference(page, case.reference)
    else:
        stock_before = retry_value("return_initial_stock")
        if stock_before is None:
            raise RetryBlocked("Saqlangan source order bor, lekin boshlang‘ich qoldiq dalili yo‘q")
        case.workflow["stock_before"] = stock_before
    case.remember_order(order_id)
    case.workflow["source_order"] = {"id": order_id, "reference": case.reference, "amount": "63000", "state": "draft", "source": page.url}
    case.checkpoint()
    with allure.step('4 - Qoralama orderda saqlangan miqdor, chegirmali summa va bepul bonus'):
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="63000", remove_spaces=True)
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.product, root=grid)
        labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество продажи", 10), ("Цена", 7000), ("Итого", 63000)):
            case.check(f"Dastlabki order mahsuloti: {label}", Decimal(value), _number(base.grid_cell(row, labels.index(label), return_value=True)))
        base.tab(name="Акция")
        grid = page.locator("smt-table:visible").last
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=grid)
        labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        for label, value in (("Количество продажи", 1), ("Цена", 0), ("Итого", 0)):
            case.check(f"Dastlabki order bonusi: {label}", Decimal(value), _number(base.grid_cell(row, labels.index(label), return_value=True)))
    _stock(case, 0, 0)


def run_ship_order(case):
    """1. Source orderni bevosita Черновик → Архив o‘tkazish.
    2. Mahsulot −10, bonus −1 va qarz 63 000 ekanini tekshirish.
    """
    source = case.workflow["source_order"]
    with allure.step("1 - Dastlabki orderni bevosita Черновик → Архив o‘tkazish"):
        change_order_status(case.page, source["id"], current="Черновик", target="Архив")
        source["state"] = "Архив"
        case.checkpoint()
    with allure.step('2 - Ombor qoldig‘i kamayishi, rezerv va orderning 63 000 so‘m qarzini tekshirish'):
        _stock(case, 10, 1)
        _settlement(case, debt=63000)


def run_pay_order(case):
    """1. 63 000 so'mni avtomatik offsetsiz qabul qilish.
    2. Aynan source orderga to'liq ajratish.
    3. Qarz va ishlatilmagan predoplata nol ekanini tekshirish.
    """
    source = case.workflow["source_order"]
    if not reuse("return_before_payment"):
        _settlement(case, debt=63000)
        verified("return_before_payment")
    payment = {"number": f"{source['reference']}-PAY", "order_id": source["id"], "state": "pending"}
    case.payments.append(payment)
    case.checkpoint()
    with allure.step('1 - Test klientidan 63 000 so‘m kirim qilish'):
        payment.update(post_cashin(case.page, client=case.client, number=payment["number"], amount=Decimal("63000"), order_id=source["id"]))
        payment["state"] = "posted"
        case.workflow["payment"] = payment
        case.checkpoint()
        if not reuse("return_cashin_verified"):
            _settlement(case, debt=63000, prepayment=63000)
            verified("return_cashin_verified")
    with allure.step('2 - 63 000 so‘mni aynan dastlabki order qarzini yopishga ajratish'):
        allocation = {"order_id": source["id"], "cashin_id": payment["id"], "amount": "63000", "state": "pending"}
        case.allocations.append(allocation)
        case.checkpoint()
        read_settlement(case.page, case.client)
        allocate_to_order(case.page, client=case.client, order_id=source["id"], amount=Decimal("63000"), remaining_debt=Decimal("63000"))
        _settlement(case)
        allocation["state"] = "verified_by_order_debt_and_balance"
        source["state"] = "paid"
        case.checkpoint()


def _return(case, *, key, goods, bonus, credit, previous_credit, goods_remaining):
    source = case.workflow["source_order"]
    # Qaytarish TTN maydoni UI maxlength=10; ikkala hujjat uchun alohida kod.
    reference = source["reference"][-8:] + ("R1" if key == "partial_return" else "R2")
    from tests.regression.helpers.retry.reconcile import is_retry, ui_row, confirm_entity
    base = AutoBasePage(case.page)
    saved = None
    if is_retry():
        base.navigate_to(tab="Продажа", name="Возвраты")
        base.expect_page(heading="Возвраты", url="return_list")
        saved = ui_row(case.page, "anor/mdeal/return/return_list:table",
                       ["deal_id", "delivery_number", "order_deal_id"], "delivery_number", reference)
    if saved:
        if str(saved["order_deal_id"]) != str(source["id"]):
            raise RetryBlocked("Return boshqa source orderga tegishli")
        record = retry_value("return_record:" + key)
        if not record or not record.get("allocations"):
            raise RetryBlocked("Return saqlangan, lekin oldingi partiya tanlovining dalili yo‘q")
        record = {**record, "id": str(saved["deal_id"])}
        base.open_route("anor/mdeal/return/return_view?deal_id=" + record["id"], heading="Возврат (просмотр)")
        status = base.form_view(label="Статус", return_value=True).strip()
        if status not in {"Черновик", "Архив"}:
            raise RetryBlocked("Return statusi tiklash bosqichiga mos emas: " + status)
        if status == "Архив" and not reuse("return_draft_verified:" + key):
            raise RetryBlocked("Return arxivlangan, lekin Draft tekshiruvlari oldin tasdiqlanmagan; tarixiy assertion PASS qilinmadi")
    else:
        _settlement(case, prepayment=previous_credit)
        open_return_from_order(case.page, order_id=source["id"], client=case.client, warehouse=WAREHOUSE)
        allocations = fill_return_items(case.page, product=case.product, bonus_product=case.bonus_product, goods_quantity=goods, bonus_quantity=bonus)
        finish_return(case.page, reason=case.workflow["return_reason"]["name"], reference=reference, net_amount=credit)
        record = {"reference": reference, "source_order_id": source["id"], "goods_quantity": goods, "bonus_quantity": bonus, "net_amount": str(credit), "allocations": allocations, "state": "pending"}
        retry_value("return_record:" + key, record)
        case.returns.append(record)
        case.checkpoint()
        record["id"] = save_return_draft(case.page)
        status = "Черновик"
    if record not in case.returns:
        case.returns.append(record)
    allocations = record["allocations"]
    case.workflow[key] = record
    case.checkpoint()
    open_return_view(case.page, reference=reference, source_id=source["id"], client=case.client, status=status, net_amount=credit, return_id=record["id"])
    _saved_return_items(case, goods, bonus, credit, allocations)
    if status == "Черновик":
        with allure.step('Qoralama qaytarish hujjati pul va ombor qoldig‘ini o‘zgartirmasligini tekshirish'):
            _stock(case, goods_remaining + goods, bonus)
            _settlement(case, prepayment=previous_credit)
        verified("return_draft_verified:" + key)
        archive_return(case.page, reference=reference, source_id=source["id"])
    open_return_view(case.page, reference=reference, source_id=source["id"], client=case.client, status="Архив", net_amount=credit, return_id=record["id"])
    _saved_return_items(case, goods, bonus, credit, allocations)
    confirm_entity("return", reference, record["id"], verified=True)
    with allure.step('Arxivlangach mahsulot omborga, chegirmadan keyingi summa klient avansiga qaytishini tekshirish'):
        _stock(case, goods_remaining, 0)
        _settlement(case, prepayment=previous_credit + credit)
        record["state"] = "archived_and_verified"
        case.checkpoint()


def run_partial_return(case):
    """1. To'langan source orderdan 2 dona mahsulot va 1 bepul bonus qaytarish.
    2. Draftda stock va balans o'zgarmasligini tekshirish.
    3. Arxivdan keyin 12 600 avans va omborda qolgan −8 mahsulotni tekshirish.
    """
    _return(case, key="partial_return", goods=2, bonus=1, credit=12600, previous_credit=0, goods_remaining=8)


def run_remaining_return(case):
    """1. Qolgan 8 dona mahsulotni qaytarish; source bonus qolmaganini tekshirish.
    2. 50 400 net kredit va jami 63 000 predoplatani tekshirish.
    3. Ikkala SKU qoldig'i boshlang'ich miqdorga qaytganini tekshirish.
    """
    if case.workflow["partial_return"]["state"] != "archived_and_verified":
        raise AssertionError("Avval qisman qaytarish alohida runner qadamida yakunlanishi kerak")
    _return(case, key="remaining_return", goods=8, bonus=0, credit=50400, previous_credit=12600, goods_remaining=0)
