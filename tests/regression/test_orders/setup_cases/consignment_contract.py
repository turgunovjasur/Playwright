"""Konsignatsiya uchun aynan guruh xonasi, mijozi va UZSga bog‘langan shartnoma."""
from urllib.parse import unquote, urlsplit

import allure

from tests.api.client import positive_id, require_fields
from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, confirm_entity, one_row, query_payload
from tests.regression.helpers.retry.state import ACTIVE, RetryBlocked
from utils.base_pages import A2_DOCUMENT_TIMEOUT_MS
from tests.regression.test_orders.helpers.navigation import OrderPage


def _open_list(case, route, heading):
    page = case.page
    with allure.step(f"«{heading}» ro‘yxatini guruh filialida ochish"):
        endpoint = "/b/" + route + "_list:table"
        with page.expect_response(lambda r: unquote(urlsplit(r.url).path).endswith(endpoint),
                                  timeout=A2_DOCUMENT_TIMEOUT_MS) as loaded:
            OrderPage(page).open_route(route + "_list", heading=heading, timeout=A2_DOCUMENT_TIMEOUT_MS)
        request = loaded.value.request
        headers = {k: v for k, v in request.all_headers().items()
                   if k in {"filial_id", "company_id", "user_id", "project_code", "lang_code", "x-requested-with"}}
        if loaded.value.status != 200 or (headers.get("filial_id"), headers.get("user_id")) != (
                str(case.baseline["filial_id"]), str(case.baseline["user_id"])):
            raise RetryBlocked("Ro‘yxat guruh filiali va foydalanuvchisida ochilmadi")
        return request.url.split("/b/", 1)[0] + "/b/", headers


def _read(page, session, endpoint, payload):
    root, headers = session
    response = page.request.post(root + endpoint, headers=headers, data=payload, max_retries=0)
    try:
        if not response.ok:
            raise RetryBlocked(f"{endpoint}: HTTP {response.status}, saqlangan tayyorlov tasdiqlanmadi")
        return response.json()
    finally:
        response.dispose()


def _saved_entity(case, *, route, heading, id_key, key, code, fill_form, fields, rooms=None):
    page, base = case.page, OrderPage(case.page)
    name = fields["name"]
    is_contract = id_key == "contract_id"
    session = _open_list(case, route, heading)
    columns = [id_key, "code"]
    query = query_payload(columns, "code", code)
    if is_contract:
        query["d"] = {"person_id": ""}  # The contract list requires its person context.

    def lookup():
        return one_row(_read(page, session, route + "_list:table", query), columns, "code", code)

    row = lookup()
    journal = ACTIVE.get()
    prior = journal.previous(f"entity:{key}:{code}") if journal else None
    previous_id = case.workflow.get(key + "_id") or (prior or {}).get("entity_id")
    if previous_id and (not row or str(row[id_key]) != str(previous_id)):
        raise RetryBlocked(f"{heading}: oldingi ID va shu guruh kodi mos kelmadi")
    if not row:
        endpoint = route + ("+add$save" if is_contract else "+add:save")
        allow_absent_ui_write(endpoint, identity={"code": code})
        with allure.step("Guruh uchun yaratish formasini ochish"):
            base.click(name="Создать", exact=True)
            base.expect_page(heading="Договор (создание)" if is_contract else "Проект (создание)",
                             url=route)
        with allure.step(f"«{name}» uchun kod va bog‘lanishlarni saqlash"):
            base.input(label="Код", value=code)
            fill_form(base)
            base.input(label="Название", value=name)
            with page.expect_response(lambda r: unquote(urlsplit(r.url).path).endswith("/b/" + endpoint)) as saved:
                base.click(name="Сохранить", exact=True)
            if saved.value.status != 200:
                raise RetryBlocked(f"{heading}: Save HTTP {saved.value.status}")
            row = lookup()
            if not row:
                raise RetryBlocked(f"{heading}: Save’dan keyin aynan guruh kodi bo‘yicha yozuv topilmadi")

    with allure.step(f"«{name}» saqlangan modelini ID bo‘yicha qayta o‘qish"):
        identity = positive_id(row[id_key])
        envelope = _read(page, session, route + "+edit:model", {id_key: identity})
        if not isinstance(envelope, list) or len(envelope) < 3 or envelope[0] != "(^_^)" or not isinstance(envelope[2], dict):
            raise RetryBlocked(f"{heading}: saqlangan model javobi yaroqsiz")
        model = envelope[2]
        require_fields(model, **{id_key: identity}, code=code, state="A", **fields)
        if rooms is not None:
            case.check("Loyiha faqat guruhning ish zonasiga biriktirilgan", rooms, model["rooms"])
        confirm_entity(key, code, identity, verified=True)
        case.workflow.update({key: name, key + "_id": identity})
        case.checkpoint()
        return identity


def run_prepare_consignment_project_contract(case):
    """1. Guruh xonasiga loyiha biriktirish. 2. Shu mijoz uchun UZS shartnomasi.
    3. Ikkala yozuv IDsi, faol holati va saqlangan bog‘lanishlarini tekshirish.
    """
    client = case.workflow["client"]
    require_fields(client, name=case.client, room_id=case.baseline["room_id"],
                   kind="due-dates", status="passed")
    suffix = client["run_id"]
    project = "QA consign project " + suffix
    currency = "Узбекский сум"
    project_id = _saved_entity(
        case, route="anor/mrf/subfilial", heading="Проекты", id_key="subfilial_id",
        key="consignment_project", code="CP" + suffix, fields={"name": project},
        fill_form=lambda base: base.multiselect(label="Рабочие зоны", value=case.room),
        rooms=[[str(case.baseline["room_id"]), case.room]],
    )

    def fill_contract(base):
        base.input(label="Номер", value="CC" + suffix)
        base.radio("Физическое лицо", click=True)
        for key, value in (("person_id", case.client), ("currency_id", currency), ("subfilial_id", project)):
            field = case.page.locator(f"smt-data-select[smtkeyfield={key}]")
            base.b_input(placeholder="Поиск...", root=field, value=value)
        base.input(label="Лимит консигнации (в днях)", value="2", press_tab=True)

    _saved_entity(
        case, route="anor/mkf/contract", heading="Договоры", id_key="contract_id",
        key="consignment_contract", code="CC" + suffix, fill_form=fill_contract,
        fields={"name": "QA consign contract " + suffix, "contract_number": "CC" + suffix,
                "person_id": client["person_id"], "person_name": case.client, "person_kind": "N",
                "currency_id": case.baseline["currency_id_uzb"], "currency_name": currency,
                "subfilial_id": project_id, "subfilial_name": project, "consignment_day_limit": "2"},
    )
