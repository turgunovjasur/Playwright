"""Order payment UI gatewaylari; biznes summalari va kutilmalar leaflarda.

A2 evidence: order-full-20261026/904-offset5000-settled-before-post.txt,
order-promotions-20261030/575-period572089-partial-offset5000-target.txt,
286-stacking-cashin5000-before-post-offset-off.txt va
289-cashin5000-posted-view-id.txt (abgular test artefaktlari).
Status triggeri 191-weight-shipped-list.txtda «Изменить статус»;
184-copy-status-new-confirm.txtda oddiy status tasdig'i qayd etilgan.
Status menyusi, cashin va offset kataklari 02.11.2026 runner/debug ijrosida
UI orqali tekshirildi; qayta foydalanishda exact ID va summa tekshiriladi.
Legacy locator fallback yoki API biznes amali yo'q.
"""

import re
from decimal import Decimal
from urllib.parse import parse_qs, urlparse, unquote
from weakref import WeakKeyDictionary

import allure
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from tests.shared.navigation import open_form_from_list
from utils.base_pages.auto_base_page import AutoBasePage
from utils.base_pages.angular_base_page import _lookup_query_finished

CURRENCY = "Узбекский сум"
_SEARCH_CONFIGURED = WeakKeyDictionary()


def _number(value):
    return Decimal(re.sub(r"\s+", "", value).replace(",", "."))


def _amount(value):
    """Decimal('63000.00')ni UI uchun 63000 ko'rinishida beradi."""
    return format(Decimal(value).normalize(), "f")


def _columns(page, fields, *, search_name=None):
    """Joriy headerlardan indeks oladi; faqat yetishmagan ustunni yoqadi.

    A2 header DOMi AngularBasePage.grid_setting bilan bir xil. Indekslar
    cache qilinmaydi: sozlamadan keyin barcha indekslar qayta o'qiladi.
    Search maydoni har page/route uchun bir marta mavjud API orqali yoqiladi.
    """
    base = AutoBasePage(page)
    grid = page.locator("smt-data-table:visible").first
    expect(grid).to_be_visible()
    base.wait_for_loader()
    headers = grid.locator(".smt-grid-header").first.locator(":scope > div[data-smt-col-key]")

    def labels():
        return [" ".join(label.split()) for label in headers.all_text_contents()]

    configured = _SEARCH_CONFIGURED.setdefault(page, set())
    search_key = (urlparse(page.url).path, search_name)
    if search_name is not None and search_key not in configured:
        base.grid_setting(menu_name="Настройка таблицы", field_name=search_name, search_name=search_name)
        configured.add(search_key)
    for label in fields.values():
        if label not in labels():
            base.grid_setting(menu_name="Настройка таблицы", field_name=label)
    current = labels()
    result = {}
    for key, label in fields.items():
        if current.count(label) != 1:
            raise AssertionError(f"Ustun yagona emas yoki topilmadi: {label}; headers={current}")
        result[key] = current.index(label)
    return result


def read_settlement(page, client):
    """Aynan klient/UZS agregatlarini o'qiydi; boshqa valyutani nol demaydi."""
    base = AutoBasePage(page)
    fields = {"client": "Клиент", "currency": "Валюта", "debt": "Задолженность",
              "prepayment": "Предоплата", "open_order": "Заказ",
              "booked_prepayment": "Забронированная предоплата", "balance": "Баланс"}
    with allure.step("Klient o'zaro hisob-kitoblari ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
        base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
    with allure.step("Aynan klient va UZS bo'yicha boshlang'ich/joriy balansni o'qish"):
        cols = _columns(page, fields, search_name="Клиент")
        def searched(response):
            return (response.status == 200
                    and unquote(urlparse(response.url).path).endswith('/anor/mdeal/order/offset/offset_list:table')
                    and _lookup_query_finished(response.request, client, "person_name"))

        # Returning to this list can restore the same query. The UI dedupes
        # identical searches, so explicitly refresh that query instead.
        current_query = base.input(
            locator=page.locator("main input[type='search']:visible").first,
            return_value=True,
        )
        # Do not decide empty/non-empty from the dataset preceding this read.
        with page.expect_response(searched) as search_response:
            if current_query == client:
                base.grid_controller(reload=True)
            else:
                base.grid_controller(search=client)
        search_response.value.finished()
        base.wait_for_loader()
        if not base.grid(client, return_bool=True):
            base.grid(state="empty")
            return {key: Decimal("0") for key in fields if key not in {"client", "currency"}}
        row = base.grid(re.compile(rf"(?=.*{re.escape(client)})(?=.*{re.escape(CURRENCY)}).*", re.DOTALL))
        expect(base.grid_cell(row, cols["client"])).to_have_text(client)
        expect(base.grid_cell(row, cols["currency"])).to_have_text(CURRENCY)
        # Offset list nol summani bo'sh katak bilan ko'rsatadi (return kreditidan
        # keyingi UI va footer bilan tasdiqlangan). Faqat shu jadvalda bo'sh
        # summa 0; umumiy _number boshqa noto'g'ri qiymatlarni rad etadi.
        result = {}
        for key in fields:
            if key in {"client", "currency"}:
                continue
            value = base.grid_cell(row, cols[key], return_value=True).strip()
            result[key] = _number(value) if value else Decimal("0")
        return result


def open_debt_details(page, client):
    """Hozirgi settlement listdan exact klient/UZS qarz detallariga o'tish."""
    base = AutoBasePage(page)
    with allure.step("Klientning UZS qarz detallarini ochish"):
        row = base.grid(re.compile(rf"(?=.*{re.escape(client)})(?=.*{re.escape(CURRENCY)}).*", re.DOTALL), click=True)
        base.click(name="Детали", exact=True)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")


def read_debts(page, client, *, settlement):
    """Barcha ko'rinadigan own-client qarz IDlarini oladi, paginationni tekshiradi.

1000dan ko'p qator bo'lsa partial snapshot qaytarmaydi: Next enabled bo'lsa
test to'xtaydi. Nol agregat bo'lsa detailga o'tish shart emas.
"""
    if settlement["debt"] == 0:
        return {}
    base = AutoBasePage(page)
    open_debt_details(page, client)
    with allure.step("Klientning barcha mavjud order qarzlarini ID va summa bilan qayd etish"):
        cols = _columns(page, {"id": "ИД заказа", "debt": "Сумма задолженности",
                               "client": "Клиент", "currency": "Валюта"})
        base.grid_controller(search="")
        if page.get_by_role("button", name="Next pages", exact=True).is_enabled():
            base.grid_controller(expand="1000")
        expect(page.get_by_role("button", name="Next pages", exact=True)).to_be_disabled()
        expect(page.get_by_role("button", name="Previous pages", exact=True)).to_be_disabled()
        rows = page.locator("smt-data-table:visible .smt-data-row")
        result = {}
        for row in rows.all():
            expect(base.grid_cell(row, cols["client"])).to_have_text(client)
            expect(base.grid_cell(row, cols["currency"])).to_have_text(CURRENCY)
            order_id = base.grid_cell(row, cols["id"], return_value=True).strip()
            if not order_id.isdigit() or order_id in result:
                raise AssertionError(f"Qarz snapshotida noto'g'ri/takroriy order ID: {order_id}")
            result[order_id] = _number(base.grid_cell(row, cols["debt"], return_value=True))
        if sum(result.values(), Decimal("0")) != settlement["debt"]:
            raise AssertionError(f"Detail qarzlari agregatga teng emas: {result}; {settlement}")
        return result


def _open_saved_order(page, base, view_url, order_id):
    for attempt in (1, 2):
        step = (f"Saqlangan order {order_id} sahifasini ochish" if attempt == 1 else
                f"Sahifa yuklanmadi: order {order_id} ni bir marta qayta ochish")
        with allure.step(step):
            try:
                page.goto(view_url)
            except PlaywrightError as error:
                timed_out = isinstance(error, PlaywrightTimeoutError) or "net::ERR_TIMED_OUT" in str(error)
                if attempt == 2 or not timed_out:
                    raise
                continue

            try:
                base.expect_page(heading="Заказ / Просмотр", url="order_view")
            except (AssertionError, PlaywrightTimeoutError) as error:
                if attempt == 2 or page.url != view_url:
                    raise
                gate = getattr(error, "_smartup_expectation_gate", None)
                if gate == "heading":
                    # A populated page with the wrong heading is a real mismatch.
                    if not page.evaluate("() => !document.body?.innerText.trim()"):
                        raise
                elif gate != "loader":
                    raise
                continue
            return


def change_order_status(page, order_id, *, current, target):
    """Exact ID/current status → UI action → freshly opened saved target status."""
    base = AutoBasePage(page)
    from tests.regression.helpers.retry.reconcile import is_retry, allow_absent_ui_write
    if is_retry():
        with allure.step("Retry: orderning amaldagi statusini o‘qish"):
            base.open_route("trade/tdeal/order/order_view?deal_id=" + str(order_id), heading="Заказ / Просмотр")
            base.form_view(label="ИД заказа", expect_value=str(order_id))
            actual = base.form_view(label="Статус", return_value=True).strip()
            if actual == target:
                return
            if actual != current:
                raise AssertionError(f"Order statusi {actual}; {current} yoki {target} kutilgan. Status qayta o‘zgartirilmadi")
            allow_absent_ui_write("trade/tdeal/order/order_list:change_status", identity={"deal_id": str(order_id)})
    with allure.step(f"Order {order_id} uchun ro'yxatni ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        columns = _columns(page, {"id": "ИД заказа", "status": "Статус"}, search_name="ИД заказа")
        base.grid_controller(search=order_id)
        row = base.grid(order_id)
        expect(base.grid_cell(row, columns["id"])).to_have_text(order_id)
        expect(base.grid_cell(row, columns["status"])).to_have_text(current)
        # Derive the known sibling A2 view route from the observed list URL.
        parsed = urlparse(page.url)
        if not parsed.path.endswith("/order_list") or not str(order_id).isdigit():
            raise ValueError("Order status readback uchun list route va raqamli ID kerak")
        view_url = parsed._replace(
            path=parsed.path.removesuffix("order_list") + "order_view",
            query="deal_id=" + str(order_id), fragment="",
        ).geturl()
    with allure.step(f"Order {order_id}: {current} → {target}"):
        base.click(name="Изменить статус", exact=True, root=row)
        base.click(name=target, role="menuitem", exact=True)
        base.confirm_biruni(f"Изменить статус на {target}?")
        base.wait_for_loader()
        if target == "Архив":
            base.grid(state="empty")
        else:
            row = base.grid(order_id)
            expect(base.grid_cell(row, columns["status"])).to_have_text(target)
    with allure.step(f"Order {order_id} viewini qayta ochib {target} statusini tekshirish"):
        _open_saved_order(page, base, view_url, order_id)
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Статус", expect_value=target)


def post_cashin(page, *, client, number, amount, order_id=None, auto_offset=False):
    """Unique cashin UI orqali o'tkazilib ID/view qiymatlari qayta o'qiladi."""
    base = AutoBasePage(page)
    amount_text = _amount(amount)
    with allure.step("Klient to'lovlari ro'yxatini ochish"):
        base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
        base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
    from tests.regression.helpers.retry.reconcile import is_retry, ui_row, allow_absent_ui_write
    existing = None
    if is_retry():
        with allure.step("Retry: aynan shu to‘lov raqami bilan kirimni serverdan qidirish"):
            existing = ui_row(page, "trade/tcs/cashin_list:table",
                              ["cashin_id", "cashin_number", "amount", "client_name", "posted"],
                              "cashin_number", number)
            if existing and (_number(existing["amount"]) != Decimal(amount)
                             or existing["client_name"] != client or existing["posted"] != "Y"):
                raise AssertionError("Mavjud kirim klienti, summasi yoki posted holati mos emas; yangi kirim yaratilmadi")
            if not existing:
                allow_absent_ui_write("trade/tcs/cashin+add$save_post", identity={"cashin_number": number})
    if existing:
        from tests.regression.helpers.retry.state import ACTIVE
        page.goto(ACTIVE.get().ui_root + "/a2/trade/tcs/cashin_view?cashin_id=" + str(existing["cashin_id"]))
    else:
        with allure.step("Yangi kassa kirimi formasini ochish"):
            open_form_from_list(base.page, heading="Оплата от клиента / Создание", url=re.compile(r"cashin(?:\+|%2[bB])add"))
        note = f"Order {order_id}; payment {number}" if order_id else f"Order oldidan avans {number}"
        with allure.step(f"{number}: {amount_text} so‘m kirimni to‘ldirish"):
            base.input(label="Номер оплаты", value=number)
            base.b_input(label="Валюта", value=CURRENCY, clear=True)
            base.b_input(label="Клиент", value=client)
            base.input(label="Сумма", value=amount_text, press_tab=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги")
            base.b_input(label="Касса", value="Основная касса")
            base.checkbox(label="Провести взаимозачёт", checked=auto_offset)
            base.checkbox(label="Провести взаимозачёт", expect_checked=auto_offset)
            if auto_offset:
                for label in ("По договору", "По типу оплаты", "По проекту"):
                    base.checkbox(label=label, checked=True)
                base.checkbox(label="С учётом консигнации", checked=False)
            base.input(label="Примечание", value=note)
        with allure.step("Kassa kirimini o'tkazish"):
            base.click(name="Провести", exact=True)
            base.confirm_biruni("Провести?")
            base.expect_page(heading="Оплата от клиента / Создание", url=re.compile(r"cashin(?:\+|%2[bB])add"))
        with allure.step("O'tkazilgan own to'lovni raqami bilan listdan topish"):
            base.click(name="Закрыть", exact=True)
            base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
            number_col = _columns(page, {"number": "Номер оплаты"}, search_name="Номер оплаты")["number"]
            base.grid_controller(search=number)
            expect(page.locator("smt-data-table:visible .smt-data-row")).to_have_count(1)
            row = base.grid(number, client, click=True)
            expect(base.grid_cell(row, number_col)).to_have_text(number)
    with allure.step("Cashin view orqali ID, klient, summa va Проведен holatini tekshirish"):
        if not existing:
            base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Оплата от клиента / Просмотр", url="cashin_view")
        cashin_id = parse_qs(urlparse(page.url).query)["cashin_id"][0]
        from tests.regression.helpers.retry.reconcile import confirm_entity
        confirm_entity("cashin", number, cashin_id)
        base.form_view(label="ИД оплаты", expect_value=cashin_id)
        base.form_view(label="Номер оплаты", expect_value=number)
        base.form_view(label="Клиент", expect_value=client)
        base.form_view(label="Валюта", expect_value=CURRENCY)
        base.form_view(label="Проведено", expect_value="Проведен")
        actual_amount = base.form_view(label="Сумма", return_value=True)
        if _number(actual_amount) != Decimal(amount):
            raise AssertionError(f"Cashin summa: expected={amount_text}; actual={actual_amount}")
        confirm_entity("cashin", number, cashin_id, verified=True)
        return {"id": cashin_id, "number": number, "amount": amount_text, "order_id": order_id}


def allocate_to_order(page, *, client, order_id, amount, remaining_debt):
    """Qarz detailidan faqat exact orderga berilgan summani ajratish.

Bu forma cashin tanlatmaydi. Consumer boshlang'ich prepayment=0 va yangi
cashinning yagona mablag' ekanini oldin isbotlashi shart.
"""
    base = AutoBasePage(page)
    from tests.regression.helpers.retry.state import ACTIVE, digest, RetryBlocked
    from tests.regression.helpers.retry.reconcile import is_retry, allow_absent_ui_write
    journal = ACTIVE.get()
    operation = "offset:" + digest({"order_id": str(order_id), "amount": str(amount), "before": str(remaining_debt)})
    if is_retry():
        settlement = read_settlement(page, client)
        debts = read_debts(page, client, settlement=settlement)
        actual = debts.get(str(order_id), Decimal("0"))
        prior = journal.source.get("operations", {}).get(operation)
        prior_request = any(op.get("transport") == "ui" and
                            op.get("endpoint") == "anor/mdeal/order/offset/offset$post" and
                            (op.get("logical_key") == operation or
                             not op.get("logical_key") and (not op.get("identity") or op["identity"] == {"deal_id": str(order_id)}))
                            for op in journal.source.get("operations", {}).values())
        if prior or prior_request:
            raise RetryBlocked("Oldingi qarz yopish amali yuborilgan bo‘lishi mumkin; transaction ID bilan tasdiqlanmaguncha qarz o‘zgarmagan bo‘lsa ham ikkinchi to‘lov yuborilmaydi")
        if actual != Decimal(remaining_debt):
            raise RetryBlocked("Order qarzi oldingi yoki tasdiqlangan keyingi holatga mos emas; pul ikkinchi marta ajratilmadi")
        read_settlement(page, client)
    # Bind every real POST, including the first attempt, to this exact installment.
    allow_absent_ui_write("anor/mdeal/order/offset/offset$post", identity={"deal_id": str(order_id)}, operation=operation)
    if journal:
        journal.intent(operation, order_id=str(order_id), amount=str(amount), before=str(remaining_debt), transport="logical")
    # Consumer read_settlementdan so'ng chaqiradi; client-wide autoOffset yo'q.
    open_debt_details(page, client)
    with allure.step(f"Order {order_id} uchun predoplata hisob-kitobini ochish"):
        id_col = _columns(page, {"id": "ИД заказа"})["id"]
        row = base.grid(order_id, click=True)
        expect(base.grid_cell(row, id_col)).to_have_text(order_id)
        base.click(name="Перерасчет", exact=True)
        base.expect_page(heading="Взаиморасчет по предоплате", url=re.compile(r"/offset/offset(?:[?#]|$)"))
    with allure.step(f"Faqat order {order_id} uchun {amount} so'mni ajratish"):
        cols = _columns(page, {"id": "ИД заказа", "client": "Клиент",
                               "debt": "Сумма задолженности", "amount": "Сумма взаиморасчета"})
        # Exact detail action faqat tanlangan orderni ochishi talab qilinadi.
        rows = page.locator("smt-data-table:visible .smt-data-row")
        expect(rows).to_have_count(1)
        row = base.grid(order_id)
        expect(base.grid_cell(row, cols["id"])).to_have_text(order_id)
        expect(base.grid_cell(row, cols["client"])).to_have_text(client)
        actual = _number(base.grid_cell(row, cols["debt"], return_value=True))
        if actual != remaining_debt:
            raise AssertionError(f"Offset oldidagi own order qarzi: {actual}, expected={remaining_debt}")
        # Evidence confirms one editable amount in this column; no ng-model.
        amount_input = base.grid_cell(row, cols["amount"]).locator("input").filter(visible=True)
        expect(amount_input).to_have_count(1)
        base.input(locator=amount_input, value=_amount(amount), press_tab=True)
    with allure.step("Exact order bo'yicha hisob-kitobni o'tkazish"):
        base.click(name="Провести", exact=True)
        base.expect_page(heading="Детали задолженности", url="offset_detail_list")
    if journal:
        journal.complete(operation)



def verify_order_offset(case, *, order_id, amount):
    """Bitta hisob-kitobli yangi klientning real tarix qatorini orderga bog'laydi."""
    page = case.page
    base = AutoBasePage(page)
    with allure.step("Klient hisob-kitoblari tarixini ochish"):
        base.open_route("anor/mdeal/order/offset/offset_history_list", heading="История взаиморасчетов")
    with allure.step("Yagona tarix qatoridagi order IDsi, klient, valyuta va summani tekshirish"):
        columns = _columns(page, {
            "order": "ИД заказа", "offset": "ИД взаиморасчета", "client": "Клиент",
            "currency": "Валюта", "amount": "Сумма",
        }, search_name="Клиент")
        base.grid_controller(search=case.client)
        # Wait for the new client's row before counting. The previous results may still be visible.
        row = base.grid(case.client, str(order_id))
        expect(base.grid_cell(row, columns["order"])).to_have_text(str(order_id))
        expect(base.grid_cell(row, columns["client"])).to_have_text(case.client)
        expect(base.grid_cell(row, columns["currency"])).to_have_text(CURRENCY)
        expect(page.locator("smt-data-table:visible .smt-data-row")).to_have_count(1)
        expect(page.get_by_role("button", name="Next pages", exact=True)).to_be_disabled()
        expect(page.get_by_role("button", name="Previous pages", exact=True)).to_be_disabled()
        offset_id = base.grid_cell(row, columns["offset"], return_value=True).strip()
        case.check("Hisob-kitob IDsi musbat", True, offset_id.isdecimal() and int(offset_id) > 0)
        actual_amount = base.grid_cell(row, columns["amount"], return_value=True)
        case.check("Orderga ajratilgan summa", Decimal(amount), _number(actual_amount))
        return offset_id
