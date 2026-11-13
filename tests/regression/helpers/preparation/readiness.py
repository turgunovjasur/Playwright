"""Current prerequisite contracts; read-only probes never create or top up data."""
from copy import deepcopy
from decimal import Decimal
import allure
from tests.api.client import require_fields
from tests.api.promotion import verify_promotion
from tests.regression.helpers.retry.reconcile import CREATES, exact_row
from tests.regression.helpers.retry.state import RetryBlocked
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


class PreparationRepairRequired(RetryBlocked):
    """Only an explicit preparation test may restore this missing relation/value."""


def verify_contract(api, baseline, contract):
    endpoint, expected = contract["endpoint"], contract["expected"]
    if endpoint == "anor/mr/product/product_set_price$save":
        rows = api.model("anor/mr/product/product_set_price", product_id=expected["product_id"])["prices"]
        for wanted in expected["prices"]:
            matches = [r for r in rows if str(r[0]) == str(wanted["price_type_id"]) and str(r[3]) == str(wanted["card_id"])]
            if len(matches) > 1:
                raise RetryBlocked("Narx qatori yagona emas")
            actual = matches[0][5] if matches else None
            if actual in (None, ""):
                raise PreparationRepairRequired("Own TMZning oldin tasdiqlangan narxi hozir yo‘q")
            if Decimal(str(actual)) != Decimal(str(wanted["price"])):
                raise RetryBlocked("TMZ narxi boshqa qiymatga o‘zgargan; ustidan yozilmaydi")
        return
    if endpoint.startswith("anor/mrf/room_attachment$attach_"):
        kind = endpoint.rsplit("$attach_", 1)[1]
        field = {"natural_person": "person_id", "price_type": "price_type_id", "warehouse": "warehouse_id", "margin": "margin_id"}[kind]
        rows = api.table("anor/mrf/room_attachment:table_" + kind, [field], data={"room_id": expected["room_id"], "attached": "Y"})
        wanted = expected[field] if isinstance(expected[field], list) else [expected[field]]
        if not {str(v) for v in wanted}.issubset({str(r[field]) for r in rows}):
            raise PreparationRepairRequired("Oldin tasdiqlangan xona bog‘lanishi yetishmayapti: " + kind)
        return
    if endpoint == "anor/mkw/init_balance/init_inventory_balance_list:post":
        row = api.one("anor/mkw/init_balance/init_inventory_balance_list:table", ["balance_id", "posted"], filters=["balance_id", "=", expected["balance_id"]])
        if row["posted"] != "Y":
            raise RetryBlocked("Ishlatilgan kirim holati o‘zgargan; stock qayta kirim qilinmaydi")
        return
    table, id_field, field, payload_field = CREATES[endpoint]
    row = exact_row(api, table, id_field, field, expected[payload_field])
    if not row or (contract.get("entity_id") and str(row[id_field]) != str(contract["entity_id"])):
        raise RetryBlocked("Oldin tasdiqlangan entity yo‘q yoki IDsi o‘zgargan: " + str(expected[payload_field]))
    identity = str(row[id_field])
    if "action+add" in endpoint:
        verify_promotion(api, identity, expected)
        model = api.model("anor/mcg/action+edit", action_id=identity)
        if "forced" in expected:
            require_fields(model, forced=expected["forced"])
        for field, payload_key in (("rooms", "room_ids"), ("price_types", "price_type_id"), ("payment_types", "payment_type_id")):
            if payload_key in expected and {str(r[0]) for r in model[field]} != {str(v) for v in expected[payload_key]}:
                raise RetryBlocked("Aksiya bog‘lanishi o‘zgargan: " + field)
        # used_quant is business state; never compare it to the initial zero.
        for wanted in expected.get("bonus_limits", []):
            matches = [r for r in model.get("bonus_limits", []) if str(r[0]) == str(wanted["product_id"])]
            if len(matches) != 1 or Decimal(str(matches[0][4])) != Decimal(str(wanted["limit_quant"])):
                raise RetryBlocked("Aksiyaning belgilangan bonus limiti o‘zgargan")
    elif "natural_person" in endpoint:
        require_fields(api.model("anor/mr/person/natural_person_view", person_id=identity), name=expected["first_name"], code=expected["code"], state="A")
    elif "inventory+add" in endpoint:
        require_fields(api.model("anor/mr/product/inventory_view", product_id=identity), **expected)
    elif "price_type" in endpoint:
        # View exposes currency_name; the list exposes the persisted currency_id.
        saved = api.one(table, [id_field, *expected], filters=[id_field, "=", identity])
        require_fields(saved, **{id_field: identity}, **expected)


def verify_retry_preparations(case, node, directory):
    plan = getattr(node.config, "_retry_plan", {})
    inline = getattr(node, "_order_inline_source", None)
    if not plan and not inline:
        return
    contracts = dict(plan.get("readiness", {}).get(node.nodeid, {}))
    if inline:
        requirements = node.config._order_requirements
        pending = list(requirements[node.nodeid])
        visited = set()
        owners = getattr(node.config, "_order_preparation_contracts", {})
        while pending:
            prerequisite = pending.pop()
            if prerequisite in visited:
                continue
            visited.add(prerequisite)
            if prerequisite not in node.config._order_passed:
                raise RetryBlocked("Retry prerequisite PASS holatini yo‘qotgan: " + prerequisite)
            contracts.update(owners.get(prerequisite, {}))
            pending.extend(requirements[prerequisite])
    state = RegressionSetupState(directory / "readiness-state.json", deepcopy(case.baseline))
    try:
        api = state.user()
        with allure.step("Retry: faqat shu biznes testning zarur tayyorlovlarini tekshirish"):
            for contract in contracts.values():
                verify_contract(api, case.baseline, contract)
    finally:
        state.close()
