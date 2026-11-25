"""The historical-price scenario deliberately supersedes one setup price."""
from tests.regression.helpers.retry.state import digest

PRICE_CHANGE_GROUPS = {"catalog_price_history", "order_xml"}
CHANGE_CASE = "test_02_change_catalog_price"
PRICE_SAVE = "anor/mr/product/product_set_price$save"


def price_payload(product_id, price_type_id, price):
    return {"product_id": str(product_id), "prices": [
        {"price_type_id": str(price_type_id), "card_id": "-1", "price": str(price)},
    ]}


def price_change_attempted(journal, payload):
    """Only a recorded write attempt on this exact SKU, card, price type and price."""
    key = "api:" + PRICE_SAVE + ":" + digest(payload)
    operation = journal.get("operations", {}).get(key, {})
    return operation.get("endpoint") == PRICE_SAVE and operation.get("transport") == "api"


def retry_price_contract(contract, state, price_type_id, change_journal):
    """Preserve other SKUs and price contracts, including their normal repair rules."""
    if contract["endpoint"] != PRICE_SAVE:
        return contract
    product_id = state.get("catalog_data", {}).get("goods", {}).get("id")
    if not product_id or contract["expected"] != price_payload(product_id, price_type_id, 1000):
        return contract
    changed = price_payload(product_id, price_type_id, 1500)
    if state.get("workflow_data", {}).get("verified_catalog_price") == changed:
        return {**contract, "expected": changed, "price_in_transition": True}
    if price_change_attempted(change_journal, changed):
        # The server may have committed the new value before the original readback.
        # The change test still converges to exactly 1500 before its consumers run.
        return {**contract, "price_in_transition": True, "pending_price": "1500"}
    return contract
