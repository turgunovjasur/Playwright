"""Read the actual server before reusing a preparation write.

No response replay: existing IDs come from a fresh exact-key table query.
Consumers still run their saved-model/value assertions. Unknown writes stop.
"""
import json
from urllib.parse import parse_qs, unquote, urlsplit
from tests.regression.retry.state import ACTIVE, RetryBlocked, digest

# These table/column contracts are already used by the preparation tests.
CREATES = {
    "anor/mr/person/natural_person+add$save": ("anor/mrf/client_list:table", "client_id", "name", "first_name"),
    "anor/mr/product/inventory+add$save": ("anor/mr/product/inventory_list:table", "product_id", "name", "name"),
    "anor/mcg/action+add$save": ("anor/mcg/action_list:table", "action_id", "name", "name"),
    "anor/mkr/price_type+add:save": ("anor/mkr/price_type_list:table", "price_type_id", "name", "name"),
    "anor/mkw/init_balance/init_inventory_balance+add$save": (
        "anor/mkw/init_balance/init_inventory_balance_list:table", "balance_id", "balance_number", "balance_number"),
}
READ_ACTIONS = {"model", "table", "query", "find", "find_extra_data", "run", "session"}
AUTH = {"biruni/s$log_in", "biruni/m:session"}
UI_IDENTITIES = {
    "anor/mdeal/order/order+add$save": "delivery_number",
    "anor/mdeal/return/return+add$save": "delivery_number",
    "trade/tcs/cashin+add$save_post": "cashin_number",
    "anor/mcg/order_product_limit/order_product_limit+add$save": "name",
    "anor/mkw/warehouse+add$save": "name",
    "anor/mdeal/return/return_reason+add$save": "name",
}
READ_ACTIONS.update({"items", "rooms", "inventory_products", "payment_type", "persons", "robots",
                     "payment_types", "warehouses", "return_reasons", "balances", "cashboxes", "clients",
                     "currencies", "humidity_type", "natural_persons", "temperature_type", "warehouse_types",
                     "announcements", "notifications", "plugin_session", "extensions", "ui_pages",
                     "load_grid_data", "load_user_large_setting", "save_user_large_setting", "gen_delivery_date"})
READ_SPECIAL = {"anor/mdeal/order/order+add$get_last_purchase_prices",
                "anor/mdeal/order/order+edit$get_last_purchase_prices", "biruni/m$telegram_channel_info"}


def endpoint_path(value):
    path = unquote(urlsplit(value).path)
    return path.split("/b/", 1)[-1].lstrip("/")


def read_only(endpoint, method="POST"):
    endpoint = endpoint_path(endpoint)
    if endpoint in AUTH or endpoint in READ_SPECIAL:
        return True
    if "$" in endpoint:
        return False
    if ":" in endpoint:
        action = endpoint.rsplit(":", 1)[1]
        return action in READ_ACTIONS or action.startswith(("table_", "query_", "find_", "get_"))
    return method in ("GET", "HEAD", "OPTIONS")


def one_row(data, columns, field, value):
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise RetryBlocked("Qidiruv table kontraktiga mos emas; create bajarilmaydi")
    rows = data["data"]
    try:
        count = int(data["count"])
    except (KeyError, TypeError, ValueError):
        raise RetryBlocked("Qidiruv count qiymati yo‘q; create bajarilmaydi") from None
    if count != len(rows) or count not in (0, 1):
        raise RetryBlocked("Qidiruv noaniq yoki bir nechta yozuv topildi; create bajarilmaydi")
    if count == 0:
        return None
    if not isinstance(rows[0], list) or len(rows[0]) != len(columns):
        raise RetryBlocked("Qidiruv ustunlari javobga mos emas")
    row = dict(zip(columns, rows[0]))
    if str(row[field]) != str(value):
        raise RetryBlocked("Topilgan yozuvning belgisi test belgisiga mos emas")
    return row


def query_payload(columns, field, value):
    return {"p": {"column": columns, "filter": [field, "=", value],
                  "sort": [], "offset": 0, "limit": 2}}


def exact_row(api, table, identity, field, value):
    columns = [identity, field]
    return one_row(api.call(table, query_payload(columns, field, value)), columns, field, value)


def api_send(original, api, endpoint, *, payload=None, form=None, timeout=None):
    journal = ACTIVE.get()
    if journal is None or read_only(endpoint):
        return original(api, endpoint, payload=payload, form=form, timeout=timeout)
    natural = CREATES.get(endpoint)
    fingerprint = {natural[3]: (payload or {}).get(natural[3])} if natural else payload
    key = "api:" + endpoint + ":" + digest(fingerprint)
    if endpoint in {"anor/mr/product/product_set_price$save", "anor/mkw/init_balance/init_inventory_balance_list:post"} or endpoint.startswith("anor/mrf/room_attachment$attach_"):
        journal.data.setdefault("contracts", {})[key] = {"endpoint": endpoint, "expected": payload}
        journal.save()
    if natural:
        fields = {
            "anor/mr/product/inventory+add$save": ("name", "code", "state"),
            "anor/mr/person/natural_person+add$save": ("first_name", "code", "state"),
            "anor/mcg/action+add$save": ("name", "code", "state", "calc_kind", "start_date", "end_date", "bonus_warehouse_id", "forced", "condition_operator", "conditions", "room_ids", "price_type_id", "payment_type_id", "bonus_limits"),
            "anor/mkr/price_type+add:save": ("name", "code", "state", "currency_id"),
        }.get(endpoint)
        if fields:
            journal.data.setdefault("contracts", {})[key] = {
                "endpoint": endpoint, "expected": {k: payload[k] for k in fields if k in payload}}
            journal.save()
    prior = journal.source.get("operations", {}).get(key)
    absent_confirmed = False
    if journal.source and (prior or endpoint in CREATES or endpoint.startswith("anor/mrf/room_attachment$attach_")):
        if endpoint in CREATES:
            table, identity, field, payload_field = CREATES[endpoint]
            value = (payload or {}).get(payload_field)
            if not value:
                raise RetryBlocked("Tayyorlov yozuvining yagona belgisi saqlanmagan")
            row = exact_row(api, table, identity, field, value)
            if row:
                journal.intent(key, endpoint=endpoint, transport="api")
                journal.confirm(key, entity_id=row[identity], reused=True)
                journal.event("existing_preparation_reused", endpoint=endpoint, entity_id=str(row[identity]))
                response_identity = "person_id" if identity == "client_id" else identity
                return {response_identity: row[identity]}
            if prior:
                # A timed-out server write may commit after a zero-row lookup.
                row = exact_row(api, table, identity, field, value)
                if row:
                    journal.confirm(key, entity_id=row[identity], reused=True)
                    response_identity = "person_id" if identity == "client_id" else identity
                    return {response_identity: row[identity]}
                raise RetryBlocked("Oldingi Save yakuni noaniq; bo‘sh qidiruv yangi Save uchun yetarli emas: " + endpoint)
            journal.event("confirmed_absent", endpoint=endpoint)
            absent_confirmed = True
        elif endpoint == "anor/mkw/init_balance/init_inventory_balance_list:post":
            identity = str(payload["balance_id"])
            row = api.one("anor/mkw/init_balance/init_inventory_balance_list:table",
                          ["balance_id", "posted"], filters=["balance_id", "=", identity])
            if str(row["balance_id"]) != identity or row["posted"] not in ("Y", "N"):
                raise RetryBlocked("Kirimning ID yoki posted holati noaniq")
            if row["posted"] == "Y":
                journal.intent(key, endpoint=endpoint, transport="api")
                journal.confirm(key, entity_id=identity, posted="Y", reused=True)
                return None
        elif endpoint.startswith("anor/mrf/room_attachment$attach_"):
            kind = endpoint.rsplit("$attach_", 1)[1]
            keys = {"natural_person": "person_id", "price_type": "price_type_id", "warehouse": "warehouse_id", "margin": "margin_id"}
            if kind not in keys:
                raise RetryBlocked("Xona bog‘lanishi uchun tekshirish kontrakti yo‘q")
            field = keys[kind]
            rows = api.table("anor/mrf/room_attachment:table_" + kind, [field],
                             data={"room_id": payload["room_id"], "attached": "Y"})
            wanted = payload[field] if isinstance(payload[field], list) else [payload[field]]
            if {str(x) for x in wanted}.issubset({str(row[field]) for row in rows}):
                journal.intent(key, endpoint=endpoint, transport="api")
                journal.confirm(key, membership_verified=True, reused=True)
                journal.verify(key)
                return None
            absent_confirmed = True
        elif endpoint == "anor/mr/product/product_set_price$save":
            # Absolute values on existing product/price IDs; no entity creation.
            pass
        else:
            raise RetryBlocked(f"Oldingi yozish amalini serverdan tekshirish adapteri yo‘q: {endpoint}. Takroriy yozish yuborilmadi")
    if journal.source and not prior and not absent_confirmed and endpoint not in CREATES and endpoint != "anor/mr/product/product_set_price$save" and any(op.get("endpoint") == endpoint and op.get("transport") == "api"
                                            for op in journal.source.get("operations", {}).values()):
        # Changed payload/identity is not permission to create another entity.
        raise RetryBlocked("Retrydagi yozish qiymatlari oldingi urinishdan farq qildi; yangi yozuv yaratilmaydi: " + endpoint)
    journal.intent(key, endpoint=endpoint, transport="api")
    result = original(api, endpoint, payload=payload, form=form, timeout=timeout)
    journal.complete(key)
    if natural and isinstance(result, dict):
        identity = "person_id" if natural[1] == "client_id" else natural[1]
        if result.get(identity):
            journal.confirm(key, entity_id=result[identity])
    if natural and journal.data["operations"][key]["state"] == "returned":
        table, identity, field, payload_field = natural
        value = (payload or {}).get(payload_field)
        if value:
            row = exact_row(api, table, identity, field, value)
            if row:
                journal.confirm(key, entity_id=row[identity])
    return result


def _payload(request):
    raw = request.post_data or ""
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        values = parse_qs(raw)
        for key in ("data", "p"):
            if key in values:
                try:
                    return json.loads(values[key][0])
                except (ValueError, TypeError):
                    pass
        return values


def _contains_identity(value, fields):
    """Match exact observed payload fields, including nested document items."""
    def found(item, key, expected):
        if isinstance(item, dict):
            actual = item.get(key)
            if actual is not None and (str(actual) == str(expected) or
                    isinstance(actual, list) and str(expected) in {str(x) for x in actual}):
                return True
            return any(found(child, key, expected) for child in item.values())
        return isinstance(item, list) and any(found(child, key, expected) for child in item)
    return bool(fields) and all(found(value, key, expected) for key, expected in fields.items())


def _identity(value, field):
    if isinstance(value, dict):
        if field in value and not isinstance(value[field], (dict, list)):
            return {field: str(value[field])}
        for child in value.values():
            result = _identity(child, field)
            if result:
                return result
    elif isinstance(value, list):
        for child in value:
            result = _identity(child, field)
            if result:
                return result
    return {}


def bind_browser(context, journal):
    """Unknown UI writes cannot be replayed. Read requests and fresh writes pass.

    This guard is regression-only. Routes are installed before the first page.
    A failed lookup never authorizes another write.
    """
    def guard(route, request):
        endpoint = endpoint_path(request.url)
        journal.ui_root = request.url.split("/b/", 1)[0]
        journal.ui_headers = {key: value for key, value in request.all_headers().items()
                              if key.lower() in {"company_id", "filial_id", "user_id", "project_code", "lang_code", "x-requested-with"}}
        if read_only(endpoint, request.method):
            route.continue_()
            return
        key = "ui:" + endpoint + ":" + digest(request.post_data or "")
        identity = _identity(_payload(request), UI_IDENTITIES.get(endpoint, "deal_id"))
        previous = [op for op in journal.source.get("operations", {}).values()
                    if op.get("transport") == "ui" and op.get("endpoint") == endpoint
                    and (not op.get("identity") or not identity or op["identity"] == identity)]
        allowed = getattr(journal, "allowed_ui", [])
        permission = next((entry for entry in allowed if entry["endpoint"] == endpoint
                           and _contains_identity(_payload(request), entry["identity"])), None)
        if previous and permission is None:
            journal.blocked_reason = "Oldingi UI yozuvi serverdan tasdiqlanmagan; takroriy yozish yuborilmadi: " + endpoint
            journal.event("write_blocked", endpoint=endpoint,
                          reason="Oldingi UI yozuvi bor; saqlangan targetni tekshirmasdan takrorlanmaydi")
            route.abort("blockedbyclient")
            return
        if permission:
            allowed.remove(permission)
        journal.intent(key, endpoint=endpoint, transport="ui",
                       identity=identity, logical_key=permission["operation"] if permission else None)
        route.continue_()
    def response_received(response):
        request = response.request
        endpoint = endpoint_path(request.url)
        if read_only(endpoint, request.method):
            return
        key = "ui:" + endpoint + ":" + digest(request.post_data or "")
        if key in journal.data["operations"]:
            # Only a successful empty offset reply proves server acknowledgement.
            try:
                acknowledged = response.status == 200 and response.text().strip() == ""
                journal.complete(key, http_status=response.status, empty_success=acknowledged)
            except Exception:
                journal.event("response_unverified", endpoint=endpoint)
    context.route("**/b/**", guard)
    context.on("response", response_received)


def ui_row(page, table, columns, field, value):
    """Fresh authenticated, read-only lookup; no HTTP error is treated as absence."""
    journal = ACTIVE.get()
    if journal is None:
        return None
    if not getattr(journal, "ui_root", None) or not getattr(journal, "ui_headers", None):
        raise RetryBlocked("Serverdan qidirish uchun joriy UI sessiyasi tayyor emas")
    result = page.request.post(journal.ui_root + "/b/" + table,
                               headers=journal.ui_headers,
                               data=query_payload(columns, field, value))
    if result.status != 200:
        raise RetryBlocked(f"Saqlangan yozuvni qidirish HTTP {result.status}; create bajarilmaydi")
    row = one_row(result.json(), columns, field, value)
    journal.event("ui_existing_found" if row else "ui_confirmed_absent", endpoint=table, field=field, value=str(value))
    return row


def allow_absent_ui_write(endpoint, *, identity, operation=None):
    journal = ACTIVE.get()
    if journal:
        operation = operation or endpoint + ":" + digest(identity)
        previous = [op for op in journal.source.get("operations", {}).values()
                    if op.get("transport") == "ui" and op.get("endpoint") == endpoint
                    and (not op.get("identity") or op["identity"] == identity)]
        if previous and ("+add" in endpoint):
            raise RetryBlocked("Oldingi UI Save yuborilgan, ammo yozuv topilmadi; kechikkan commit ehtimoli sabab qayta Save bloklandi")
        journal.allowed_ui = getattr(journal, "allowed_ui", [])
        journal.allowed_ui.append({"endpoint": endpoint, "identity": identity, "operation": operation})
        journal.event("write_permission", endpoint=endpoint, operation=operation, identity=identity)


def confirm_entity(kind, key, identity, *, verified=False):
    journal = ACTIVE.get()
    if journal:
        operation = f"entity:{kind}:{key}"
        journal.confirm(operation, entity_id=identity, kind=kind, natural_key=str(key))
        if verified:
            journal.verify(operation)


def is_retry():
    journal = ACTIVE.get()
    return bool(journal and journal.source)
