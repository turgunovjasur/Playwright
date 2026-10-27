"""Validate promotion rules against the server's persisted edit model."""

from tests.api.client import APIError, require_fields


def verify_promotion(api, action_id, payload):
    model = api.model("anor/mcg/action+edit", action_id=action_id)
    require_fields(model, **{key: payload[key] for key in
                             ("name", "code", "state", "calc_kind", "start_date", "end_date", "bonus_warehouse_id")})
    conditions = model["conditions"]
    if len(conditions) != 1 or len(conditions[0]["rules"]) != 1 or len(conditions[0]["bonuses"]) != 1:
        raise APIError("Promotion did not persist its single setup condition/rule/bonus")
    rule = conditions[0]["rules"][0]
    expected_rule = payload["conditions"][0]["rules"][0]
    require_fields(rule, **{key: expected_rule[key] for key in ("rule_kind", "required_count", "main_value")})
    if {(str(p["product_id"]), p["inventory_kind"]) for p in rule["products"]} != {
        (str(product_id), "G") for product_id in expected_rule["product_ids"]
    }:
        raise APIError("Promotion rule points to different products")
    bonus = conditions[0]["bonuses"][0]
    expected_bonus = payload["conditions"][0]["bonuses"][0]
    require_fields(bonus, bonus_kind=expected_bonus["bonus_kind"])
    if len(bonus["products"]) != 1:
        raise APIError("Promotion did not persist its setup bonus product")
    require_fields(bonus["products"][0], **{key: expected_bonus["products"][0][key]
                                         for key in ("product_id", "inventory_kind", "value")})
