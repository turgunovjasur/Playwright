"""SCN-018. Kelajakdagi ikkita qarz, alohida to‘lovlar va order jurnali."""
from contextlib import contextmanager
from urllib.parse import parse_qs, urlsplit

import allure
from playwright.sync_api import expect

from tests.regression.helpers.retry.checkpoints import reuse, value, verified
from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.helpers.retry.state import ACTIVE, RetryBlocked
from tests.regression.test_orders.helpers.discounts import parse_amount
from tests.regression.test_orders.helpers.flows.settlement import _columns, change_order_status
from utils.base_pages.auto_base_page import AutoBasePage
from utils.date_utils import format_date, resolve_date

DEBTS = "anor/mdeal/order/offset/offset_detail_list"
CURRENCY = "Узбекский сум"
TRANSFER = "Перечисление"


@contextmanager
def _debt_table(page):
    def matches(response):
        return (urlsplit(response.url).path.endswith("/" + DEBTS + ":table")
                and response.request.method == "POST"
                and "column" in response.request.post_data_json.get("p", {}))

    with page.expect_response(matches) as loaded:
        yield loaded
    if loaded.value.status != 200:
        raise AssertionError(f"Qarzlar ro‘yxatini yuklash HTTP {loaded.value.status}")
    loaded.value.finished()


def _apply_order_filter(case, order_id, *, remove_cutoff):
    page, base = case.page, AutoBasePage(case.page)
    base.grid_controller(open_filter=True)
    dialog = page.get_by_role("dialog")
    number = dialog.get_by_placeholder("Введите число...", exact=True)
    due = dialog.get_by_role("button", name="Удалить фильтр Срок оплаты", exact=True)
    if remove_cutoff:
        if due.count():
            due.click()
    else:
        expect(due.locator("..").get_by_placeholder("До", exact=True)).to_have_value(format_date())
    edited = "".join(number.input_value().split()) != order_id
    if edited:
        number.click()
        number.press("ControlOrMeta+A")
        number.press_sequentially(order_id)
        # Live A2 can show all digits but send its previous debounced model.
        # A single bounded wait allows the model to settle; the server-bound
        # query and the reopened UI below independently prove the applied ID.
        stable = number.evaluate(r"""async (el, expected) => {
            const matches = () => el.isConnected && el.value.replace(/\s/g, '') === expected;
            if (!matches()) return false;
            await new Promise(resolve => setTimeout(resolve, 1000));
            return matches();
        }""", order_id)
        case.check("ID kiritish tugadi", True, stable)

    with _debt_table(page) as applied:
        if edited:
            number.press("Enter")
        else:
            dialog.get_by_role("button", name="Применить", exact=True).click()
    response = applied.value
    applied_filter = response.request.post_data_json["p"]["filter"]
    terms = applied_filter[1] if applied_filter[0] == "and" else [applied_filter]
    case.check("Serverga berilgan aniq order IDsi", [["deal_id", "=", order_id]],
               [term for term in terms if term[0] == "deal_id"])
    cutoffs = [term for term in terms if term[0] == "expiry_date_for_filter"]
    if remove_cutoff:
        case.check("Server so‘rovida muddat chegarasi olib tashlangan", [], cutoffs)
    else:
        today = format_date()
        case.check("Server muddatni bugungi kun oxirigacha chekladi", True,
                   cutoffs in ([["expiry_date_for_filter", "<=", today]],
                               [["expiry_date_for_filter", "<=", today + " 23:59:59"]]))
    expect(dialog).to_be_hidden()
    base.wait_for_loader()
    # Read the applied Smartup filters again. An empty grid alone cannot prove zero debt.
    base.grid_controller(open_filter=True)
    case.check("Tatbiq etilgan aniq order filtri", order_id, "".join(number.input_value().split()))
    if remove_cutoff:
        expect(due).to_have_count(0)
    else:
        expect(due.locator("..").get_by_placeholder("До", exact=True)).to_have_value(format_date())
    dialog.get_by_role("button", name="Применить", exact=True).click()
    base.wait_for_loader()


def _debts(case, order_id):
    page, base = case.page, AutoBasePage(case.page)
    grid = page.locator("main:visible smt-table:visible")
    rows = grid.locator(".smt-data-row")
    fields = {"order": "ИД заказа", "client": "Клиент", "day": "Срок оплаты", "currency": "Валюта",
              "advance": "Предоплата", "debt": "Сумма задолженности", "status": "Статус"}
    columns = _columns(page, fields)
    amounts = {}
    if not rows.count():
        expect(grid.get_by_text("Нет результатов", exact=True)).to_be_visible()
    for row in rows.all():
        for key, expected in (("order", order_id), ("client", case.client), ("currency", CURRENCY), ("status", "Архив")):
            expect(base.grid_cell(row, columns[key])).to_have_text(expected)
        day = base.grid_cell(row, columns["day"], return_value=True).strip()
        if day in amounts:
            raise AssertionError(f"Bir xil muddat bo‘yicha takroriy qarz qatori: {day}")
        case.check(f"{day} predoplata", 0, parse_amount(base.grid_cell(row, columns["advance"], return_value=True)))
        amounts[day] = parse_amount(base.grid_cell(row, columns["debt"], return_value=True))
    expect(page.get_by_role("button", name="Next pages", exact=True)).to_be_disabled()
    return amounts


def _post_payment(case, order_id, day, remaining_dates):
    page, base = case.page, AutoBasePage(case.page)
    row = page.locator("main:visible smt-table:visible .smt-data-row").filter(
        has=page.get_by_text(day, exact=True)).filter(has=page.get_by_text(order_id, exact=True))
    with allure.step(f"{day} muddatning yagona qarz qatorini tanlab to‘lovni ochish"):
        expect(row).to_have_count(1)
        row.click()
        cb = row.get_by_role("checkbox", name="Выбрать строку")
        if cb.get_attribute("aria-checked") != "true":
            cb.click()
        expect(cb).to_have_attribute("aria-checked", "true")
        base.click(name="Оплатить за 1", exact=True)
        base.expect_page(heading="Взаиморасчет по новому платежу", url="order_payment")
    with allure.step("Order, klient, loyiha, to‘lov turi va qarz sanalarini tekshirish"):
        row = page.locator("main:visible smt-table:visible .smt-data-row")
        expect(row).to_have_count(1)
        for field in (order_id, case.client, case.workflow["consignment_project"], CURRENCY, *remaining_dates):
            expect(row.get_by_text(field, exact=True)).to_be_visible()
        base.b_input(root=row.locator("smt-data-select[smtkeyfield=payment_type_id]"),
                     placeholder="Поиск", expect_value=TRANSFER)
        bank = row.locator("smt-data-select[smtkeyfield=bank_account_id]")
        base.b_input(placeholder="Поиск", root=bank, value=case.workflow["consignment_bank_name"])
        base.b_input(placeholder="Поиск", root=bank, expect_value=case.workflow["consignment_bank_name"])
        note = f"{case.workflow['consignment_order']['reference']} {day}"
        base.input(label="Примечание", value=note)
        amount = row.locator("[data-smt-col-key=payment_amount] input")
        base.input(locator=amount, value="1000", press_tab=True)
        case.check(f"{day} tanlangan to‘lov", 1000, parse_amount(amount.input_value()))
        expect(page.get_by_role("article").filter(has_text=TRANSFER)).to_contain_text("1 000")
    with allure.step(f"Aynan {order_id} orderga {day} uchun 1 000 so‘m to‘lash"):
        if is_retry():
            allow_absent_ui_write("trade/tcs/offset/order_payment$post", identity={"note": note})
        base.click(name="Провести", exact=True)
        value("consignment_post:" + day, True)
        with _debt_table(page):
            base.confirm_biruni("Провести платеж?")
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")


def _check_journal(case, report, order_id, offset, dates):
    query = parse_qs(urlsplit(report.url).query)
    case.check("Jurnal order IDsi", [order_id], query.get("deal_id"))
    case.check("Jurnal hisob-kitob IDsi", [offset], query.get("offset_id"))
    expect(report.get_by_role("cell", name=f"Журнал документов: Заказ: {order_id}")).to_be_visible()
    postings = report.get_by_role("row").filter(has=report.get_by_role("cell", name="6310", exact=True)).filter(
        has=report.get_by_role("cell", name="4010", exact=True))
    expect(postings).to_have_count(2)
    days = []
    for entry in postings.all():
        cells = entry.get_by_role("cell").all_inner_texts()
        case.check("Debet, kredit va klient", ["6310", case.client, "4010", case.client], cells[2:6])
        case.check("Hisob-kitob provodkasi", 1000, parse_amount(cells[-1]))
        details = entry.locator("xpath=following-sibling::tr")
        contract = case.workflow["consignment_contract"]
        case.check("Debet va kredit shartnomalari hamda valyuta", [contract, contract, CURRENCY],
                   details.nth(0).get_by_role("cell").all_inner_texts()[:3])
        case.check("Debet va kredit to‘lov turlari", [TRANSFER, TRANSFER],
                   details.nth(1).get_by_role("cell").all_inner_texts()[:2])
        project, day = details.nth(2).get_by_role("cell").all_inner_texts()[:2]
        case.check("Provodka loyihasi", case.workflow["consignment_project"], project)
        expect(details.nth(3).get_by_role("cell", name=order_id, exact=True)).to_be_visible()
        days.append(day)
    case.check("Jurnalning ikkita alohida konsignatsiya muddati", sorted(dates), sorted(days))


def _history(case, order_id, dates):
    page, base = case.page, AutoBasePage(case.page)
    with allure.step("Hisob-kitoblar tarixida aynan shu klient va order to‘lovlarini ochish"):
        base.page_link("История взаиморасчетов")
        base.expect_page(heading="История взаиморасчетов", url="offset_history_list")
        cols = _columns(page, {"order": "ИД заказа", "offset": "ИД взаиморасчета", "client": "Клиент",
                               "amount": "Сумма", "currency": "Валюта"}, search_name="Клиент")
        base.grid_controller(search=case.client)
        rows = page.locator("main:visible smt-table:visible .smt-data-row")
        expect(rows.filter(has=page.get_by_text(order_id, exact=True))).to_have_count(2)
        expect(rows).to_have_count(2)
        expect(page.get_by_role("button", name="Next pages", exact=True)).to_be_disabled()
        offsets = []
        for row in rows.all():
            for name, expected in (("order", order_id), ("client", case.client), ("currency", CURRENCY)):
                expect(base.grid_cell(row, cols[name])).to_have_text(expected)
            case.check("Tarixdagi alohida to‘lov", 1000, parse_amount(base.grid_cell(row, cols["amount"], return_value=True)))
            offsets.append(base.grid_cell(row, cols["offset"], return_value=True).strip())
        case.check("Ikkita musbat, alohida hisob-kitob IDsi", True,
                   len(set(offsets)) == 2 and all(i.isdecimal() and int(i) > 0 for i in offsets))
    for offset in offsets:
        with allure.step(f"{offset} hisob-kitobining order jurnalini ochish"):
            row = rows.filter(has=page.get_by_text(offset, exact=True))
            row.click()
            with page.expect_popup() as opened:
                base.click(name="Проводки", exact=True)
            report = opened.value
            try:
                report.wait_for_url("**/offset_history_list:transactions?**")
                _check_journal(case, report, order_id, offset, dates)
            finally:
                report.close()
    case.allocations[:] = [{"order_id": order_id, "offset_id": offset, "amount": "1000"} for offset in offsets]
    case.checkpoint()


def run_consignment_settlement(case):
    """1. Orderni ketma-ket arxivlash. 2. Filtr va qarz muddatlarini solishtirish.
    3. Har muddatni alohida to‘lash. 4. Nol qarz, tarix va ikki jurnalni tekshirish.
    """
    page, base = case.page, AutoBasePage(case.page)
    order = case.workflow["consignment_order"]
    order_id, dates = order["id"], case.workflow["consignment_dates"]
    with allure.step("1 - Saqlangan order statusini tekshirib arxivlash"):
        base.open_route("trade/tdeal/order/order_view?deal_id=" + order_id, heading="Заказ / Просмотр")
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Номер ТТН", expect_value=order["reference"])
        base.form_view(label="Клиент", expect_value=case.client)
        status = base.form_view(label="Статус", return_value=True).strip()
        stages = ["Черновик", "Новый", "Отгружен", "Архив"]
        if not is_retry():
            case.check("Boshlang‘ich order statusi", stages[0], status)
        for index in range(stages.index(status), len(stages) - 1):
            change_order_status(page, order_id, current=stages[index], target=stages[index + 1])
    with allure.step("2 - Order IDsi va to‘lov muddatining yuqori chegarasini tekshirish"):
        # Opening filters before the initial grid response leaves the dialog empty.
        with _debt_table(page):
            base.open_route(DEBTS, heading="Детали задолженности")
        if not reuse("consignment_cutoff_proved"):
            _apply_order_filter(case, order_id, remove_cutoff=False)
            expected = {day: 1000 for day in dates if resolve_date(day) <= resolve_date()}
            case.check("Bugungi sanagacha qarz", expected, _debts(case, order_id))
            verified("consignment_cutoff_proved")
        _apply_order_filter(case, order_id, remove_cutoff=True)
    for index, day in enumerate(dates):
        expected = {d: 1000 for d in dates[index:]}
        after = {d: 1000 for d in dates[index + 1:]}
        if reuse("consignment_paid:" + day):
            continue
        with allure.step(f"3 - {day} muddatli qarzdan oldingi va keyingi qoldiq"):
            observed = _debts(case, order_id)
            note = f"{order['reference']} {day}"
            submitted = False
            if value("consignment_post:" + day):
                previous = ACTIVE.get().source.get("operations", {})
                submitted = any(
                    op.get("endpoint") == "trade/tcs/offset/order_payment$post"
                    and op.get("transport") == "ui"
                    and (not op.get("identity") or op["identity"] == {"note": note})
                    for op in previous.values()
                )
            if submitted:
                if observed != after:
                    raise RetryBlocked("Avval yuborilgan to‘lov tasdiqlanmadi. Takroriy o‘tkazma yuborilmadi")
            else:
                case.check("To‘lovdan oldingi aniq muddatlar", expected, observed)
                _post_payment(case, order_id, day, dates[index:])
                _apply_order_filter(case, order_id, remove_cutoff=True)
                observed = _debts(case, order_id)
            case.check("To‘lovdan keyingi aniq muddatlar", after, observed)
            verified("consignment_paid:" + day)
    case.check("Arxiv orderining yakuniy qarzi", {}, _debts(case, order_id))
    _history(case, order_id, dates)
