"""Branch-owned QA settlement account and temporary transfer mapping for consignment."""
from collections import Counter
import json
import re
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from tests.api.client import positive_id
from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.helpers.retry.state import stable_uuid
from utils.base_pages.auto_base_page import AutoBasePage


ROOM = "anor/mrf/room_attachment"
ROOM_ACCOUNTS = ROOM + ":table_bank_account"
FINANCE = "trade/pref/finance_setting"
PAYMENT_ACCOUNTS = "trade/tcs/offset/order_payment:bank_accounts"
CURRENCY = "Узбекский сум"
TRANSFER = "Перечисление"
BANK = "Центр расчетов Центрального банка по г. Ташкенту"
TRIPLE = ("payment_type_id", "currency_id", "bank_account_id")


def _matches(response, endpoint):
    return urlsplit(response.url).path.endswith("/b/" + endpoint)


def _branch_headers(request, baseline):
    headers = {k: v for k, v in request.all_headers().items()
               if k in {"company_id", "filial_id", "user_id", "lang_code", "project_code", "x-requested-with"}}
    if (headers.get("filial_id") != str(baseline["filial_id"]) or headers.get("user_id") != str(baseline["user_id"])
            or headers.get("project_code") != "trade" or not headers.get("company_id")):
        raise AssertionError("Bank tayyorlovida faol filial yoki foydalanuvchi mos kelmadi")
    return headers


def _model_object(raw, endpoint):
    if isinstance(raw, list) and len(raw) >= 3 and raw[0] == "(^_^)":
        raw = raw[2]
    if not isinstance(raw, dict) or "error" in raw or "errors" in raw:
        raise RuntimeError(f"{endpoint} javobi kutilgan shaklda kelmadi")
    return raw


def _read(page, baseline, endpoint, headers, data):
    # Finance preferences may include credentials. This unreported read returns only
    # to the caller's memory; do not include response bodies in errors or fixtures.
    response = page.request.post(baseline["url"].rstrip("/") + "/b/" + endpoint,
                                 headers=headers, data=data, max_retries=0)
    try:
        if response.status != 200:
            raise RuntimeError(f"{endpoint} HTTP {response.status}")
        return _model_object(response.json(), endpoint)
    finally:
        response.dispose()


def _rows(page, baseline, endpoint, headers, data, columns, filters=()):
    result = []
    while True:
        payload = {"d": data, "p": {"column": columns, "filter": list(filters), "sort": [],
                                     "offset": len(result), "limit": 1000}}
        data_page = _read(page, baseline, endpoint, headers, payload)
        chunk = data_page["data"]
        result.extend(dict(zip(columns, row, strict=True)) for row in chunk)
        if len(result) == int(data_page["count"]):
            return result
        if not chunk or len(result) > int(data_page["count"]):
            raise AssertionError("Bank hisoblari ro‘yxati to‘liq olinmadi")


def _open_room(case):
    page = case.page
    base = AutoBasePage(page)
    base.open_route(f'{ROOM}?room_id={case.baseline["room_id"]}', heading=f"Рабочая зона (прикрепление): {case.room}")
    with page.expect_response(lambda r: _matches(r, ROOM_ACCOUNTS)) as pending:
        base.tab(name="Расчетные счета", section=True)
    return _branch_headers(pending.value.request, case.baseline)


def _room_accounts(case, headers, attached):
    rows = _rows(case.page, case.baseline, ROOM_ACCOUNTS, headers,
                 {"room_id": case.baseline["room_id"], "attached": attached},
                 ["bank_account_id", "name", "currency_name"])
    return {positive_id(row["bank_account_id"]): row for row in rows}


def run_prepare_consignment_bank(case):
    """Create or recover the own UZS account on the branch and attach it to this room."""
    page, base = case.page, AutoBasePage(case.page)
    key = stable_uuid("consignment_bank").hex[:10]
    bank = case.workflow.setdefault("consignment_bank", {
        "name": "QA consign account " + key, "number": "20208000" + f"{int(key, 16) % 10**12:012d}",
        "filial_id": str(case.baseline["filial_id"]), "room_id": str(case.baseline["room_id"]),
        "currency_id": str(case.baseline["currency_id_uzb"]),
    })
    case.checkpoint()
    if (bank["filial_id"], bank["room_id"], bank["currency_id"]) != tuple(
            str(case.baseline[k]) for k in ("filial_id", "room_id", "currency_id_uzb")):
        raise AssertionError("Saqlangan bank hisobi boshqa filial, xona yoki valyutaga tegishli")
    headers = _open_room(case)
    attached = _room_accounts(case, headers, "Y")
    available = _room_accounts(case, headers, "N")
    original_attached = set(attached)

    def own_id():
        matches = [i for i, row in (available | attached).items() if row["name"] == bank["name"]]
        if len(matches) > 1:
            raise AssertionError("Bir xil test nomli hisob takrorlangan")
        return matches[0] if matches else None

    identity = own_id()
    if bank.get("id") and bank["id"] != identity:
        raise AssertionError("Avval tayyorlangan bank hisobi o‘z IDsi bilan topilmadi")
    if not identity and bank.get("creating"):
        raise AssertionError("Oldingi filial hisobini saqlash natijasi noaniq, ikkinchi hisob yaratilmadi")
    base.tab(name="Доступные")
    legal_model = "anor/mr/person/legal_person+edit:model"
    with page.expect_response(lambda r: _matches(r, legal_model)) as opened:
        base.click(name="Создать расчетный счет", exact=True)
    model_request = opened.value.request
    owner_headers = _branch_headers(model_request, case.baseline)
    model_params = model_request.post_data_json
    def owner_model():
        return _read(page, case.baseline, legal_model, owner_headers, model_params)
    initial = _model_object(opened.value.json(), legal_model)
    page.wait_for_url(re.compile(r"/legal_person(?:%2[bB]|\+)edit\?"))
    if parse_qs(urlsplit(page.url).query).get("person_id") != [bank["filial_id"]]:
        raise AssertionError("Ochilgan yuridik shaxs shu filialga tegishli emas")
    previous_accounts = initial["bank_accounts"]
    matches = [row for row in previous_accounts if bank["number"] in row or bank["name"] in row]
    if identity and (len(matches) != 1 or not {identity, bank["number"], bank["name"]} <= set(map(str, matches[0]))):
        raise AssertionError("Filial kartasida aynan tayyorlangan bank nomi va raqami topilmadi")
    if not identity and matches:
        raise AssertionError("Filialda shu nom yoki raqamli hisob bor, yangi hisob yaratilmadi")
    base.tab(name="Расчетный счет")
    if not identity:
        base.click(name="Создать", exact=True, root=page.locator("main:visible").last)
        base.expect_page(heading="Создание расчетного счета")  # navigation: same-url - Bank account editor opens in a modal.
        modal = page.get_by_role("heading", name="Создание расчетного счета", exact=True).locator(
            "xpath=ancestor::*[.//button[normalize-space(.)='Создать и закрыть']][1]")
        expect(modal).to_have_count(1)
        base.input(label="Название счета", value=bank["name"], root=modal)
        base.input(label="Расчетный счет", value=bank["number"], root=modal)
        base.b_input(label="Банк", action="search", search_text="00001", root=modal)
        option = page.get_by_role("listitem").filter(has_text=BANK).filter(visible=True)
        expect(option).to_have_count(1)
        option.click()
        base.b_input(label="Валюта", expect_value=CURRENCY, root=modal)
        base.click(name="Создать и закрыть", exact=True, root=modal)
        expect(modal).to_be_hidden()
    base.grid(bank["name"], bank["number"], BANK)
    if not identity:
        if owner_model() != initial:
            raise AssertionError("Filial kartasi tahrir vaqtida o‘zgardi, hisob saqlanmadi")
        bank["creating"] = True
        case.checkpoint()
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(url=ROOM)
        actual = owner_model()
        saved_accounts = actual["bank_accounts"]
        saved_own = [row for row in saved_accounts if bank["name"] in row and bank["number"] in row]
        if (len(saved_own) != 1 or len(saved_accounts) != len(previous_accounts) + 1
                or any(row not in saved_accounts for row in previous_accounts)):
            raise AssertionError("Filial kartasida oldingi hisoblar va bitta yangi hisob tasdiqlanmadi")
        headers = _open_room(case)
        attached = _room_accounts(case, headers, "Y")
        available = _room_accounts(case, headers, "N")
        identity = own_id()
        if identity not in map(str, saved_own[0]):
            raise AssertionError("Xonadagi hisob IDsi filial kartasidagi yangi hisobga mos kelmadi")
    else:
        headers = _open_room(case)
    if not identity or (available | attached)[identity]["currency_name"] != CURRENCY:
        raise AssertionError("Filialning saqlangan UZS hisobi tasdiqlanmadi")
    bank.update(id=identity, creating=False)
    case.checkpoint()
    if identity not in attached:
        base.tab(name="Доступные")
        base.grid(bank["name"], CURRENCY, click=True)
        if is_retry():
            allow_absent_ui_write(ROOM + "$attach_bank_account",
                                  identity={"room_id": bank["room_id"], "bank_account_id": identity})
        base.click(name="Прикрепить", exact=True)
        with page.expect_response(lambda r: _matches(r, ROOM + "$attach_bank_account")) as attachment:
            base.confirm_biruni("Прикрепить " + bank["name"] + "?")
        if not attachment.value.ok:
            raise AssertionError(f"Bank hisobini biriktirish HTTP {attachment.value.status}")
    current = _room_accounts(case, headers, "Y")
    if not original_attached <= current.keys() or current.get(identity, {}).get("name") != bank["name"]:
        raise AssertionError("Filial hisobining xonaga biriktirilishi tasdiqlanmadi")
    case.workflow["consignment_bank_name"] = bank["name"]
    case.checkpoint()
    return bank["name"]


def _mapping(model):
    return Counter((str(group["payment_type_id"]), str(row[2]), str(row[0]))
                   for group in model["payment_type_bank_accounts"] for row in group["bank_accounts"])


def _wire_triple(row):
    return tuple(str(row[k]) for k in TRIPLE)


def _comparable_finance_model(model):
    # Separate reads can return the same role options in a different order.
    return {**model, "roles": sorted(model["roles"], key=json.dumps)}


class ConsignmentBankBinding:
    """Temporarily add one payment mapping. Fresh authenticated, untraced pages only."""

    def __init__(self, open_page, baseline, workflow_data):
        self.open_page = open_page
        self.baseline = baseline
        self.workflow = workflow_data
        self.owned = None

    def ensure(self):
        self._change(adding=True)

    def close(self):
        if self.owned:
            self._change(adding=False)

    def _change(self, *, adding):
        if adding:
            bank = self.workflow["consignment_bank"]
            if bank["filial_id"] != str(self.baseline["filial_id"]):
                raise AssertionError("Moliya mappingi uchun filial mos emas")
        with self.open_page() as page:
            base = AutoBasePage(page)
            base.navigate_to(tab="Главное", name="Настройки системы")
            base.expect_page(url="trade/pref/system_setting")
            with page.expect_response(lambda r: _matches(r, FINANCE + ":model")) as pending:
                page.get_by_role("tab", name="Финансы", exact=True).click()
            headers = _branch_headers(pending.value.request, self.baseline)

            def read_model():
                return _read(page, self.baseline, FINANCE + ":model", headers, {})

            current = _model_object(pending.value.json(), FINANCE + ":model")
            if adding:
                transfer, = [group for group in current["payment_type_bank_accounts"] if group["payment_type_name"] == TRANSFER]
                if current["use_payment_type"] != "Y":
                    raise AssertionError("Filialda to‘lov turi bo‘yicha hisob tanlash yoqilmagan")
                target = (positive_id(transfer["payment_type_id"]), positive_id(bank["currency_id"]), positive_id(bank["id"]))
                if self.owned and self.owned != target:
                    raise AssertionError("Oldingi vaqtinchalik QA mappingi hali tiklanmagan")
            else:
                # A partial retry may have rolled workflow back to its pre-setup state.
                target = self.owned
            before = _mapping(current)
            if before[target] > 1:
                raise AssertionError("Hisob mappingi takrorlangan")
            if bool(before[target]) != adding:
                if adding:
                    self.owned = target  # Before Save, including timeout/uncertain commit.
                self._save(page, current, before, target, adding, read_model)
            if adding:
                rows = _rows(page, self.baseline, PAYMENT_ACCOUNTS, headers,
                             {"payment_type_id": target[0], "currency_id": target[1]},
                             ["bank_account_id", "name"])
                if [r["name"] for r in rows if str(r["bank_account_id"]) == target[2]] != [bank["name"]]:
                    raise AssertionError("O‘tkazma tanlovida QA hisobi topilmadi")
            else:
                self.owned = None

    def _save(self, page, model, before, target, adding, read_model):
        endpoint = FINANCE + ":save"
        url = self.baseline["url"].rstrip("/") + "/b/" + endpoint
        snapshot = _comparable_finance_model(model)
        send = []
        def adjust(route):
            wire = route.request.post_data_json
            rows = wire.get("payment_type_bank_account")
            if (not isinstance(rows, list) or Counter(map(_wire_triple, rows)) != before
                    or _comparable_finance_model(read_model()) != snapshot
                    or (model.get("bank_op_import_accounts") == [] and wire.get("bank_op_import_account_ids") != [])):
                # Stale form. This response is strictly local and no settings are sent.
                route.abort()
                return
            for key in wire.keys() & model.keys():
                if not isinstance(model[key], (dict, list)):
                    wire[key] = model[key]
            wire["payment_type_bank_account"] = (rows + [dict(zip(TRIPLE, target))] if adding
                                                else [row for row in rows if _wire_triple(row) != target])
            send.append(True)
            route.continue_(post_data=json.dumps(wire))

        page.route(url, adjust)
        try:
            with page.expect_response(lambda r: _matches(r, endpoint)) as saved:
                page.get_by_role("button", name="Сохранить", exact=True).click()
            if not send or saved.value.status != 200:
                raise RuntimeError("Moliya sozlamasini saqlash tasdiqlanmadi")
        finally:
            page.unroute(url, adjust)
        after = read_model()
        expected = before.copy()
        if adding:
            expected[target] = 1
        else:
            del expected[target]
        snapshot["payment_type_bank_accounts"] = after["payment_type_bank_accounts"]
        if _mapping(after) != expected or _comparable_finance_model(after) != snapshot:
            raise RuntimeError("Filial mappingi yoki uning boshqa sozlamalari readback’da farq qildi")
