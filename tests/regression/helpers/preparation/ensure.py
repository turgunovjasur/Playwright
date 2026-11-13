"""Probe → bounded preparation → probe, used only by explicit setup tests."""
import json
import allure
from tests.regression.helpers.retry.state import RetryBlocked


def ensure_preparation(spec, *, registry, probe, prepare):
    entry = registry.entry(spec)
    registry.recover_journal(spec)
    for prerequisite in spec.requires:
        matches = [r for r in registry.data["entries"].values()
                   if r["scope"] == spec.scope and r["key"] == prerequisite]
        if len(matches) != 1 or matches[0]["status"] != "ready":
            raise RetryBlocked("Tayyorlov prerequisite tayyor emas: " + prerequisite)
    result = probe(entry)
    if result.status not in {"ready", "missing", "partial"}:
        raise RetryBlocked("Tayyorlov probe holati noma’lum: " + str(result.status))
    action = "reused"
    if result.status != "ready":
        if entry["attempts"] >= 2:
            raise RetryBlocked("Tayyorlovning bitta tiklash urinishi sarflangan: " + spec.key)
        entry["attempts"] += 1
        entry["status"] = "process"
        action = "created" if entry["attempts"] == 1 else "repaired"
        registry.event(spec, "prepare_intent", attempt=entry["attempts"])
        registry.remember_journal(spec)
        try:
            prepare(entry)
            result = probe(entry)
            if result.status != "ready":
                raise RetryBlocked("Tayyorlovdan keyingi tekshiruv o‘tmadi: " + result.detail)
        except Exception:
            entry["status"] = "partial"
            registry.event(spec, "preparation_incomplete")
            raise
    entry.update(status="ready", entities={**entry["entities"], **result.entities},
                 evidence=result.evidence, detail=result.detail)
    registry.event(spec, action, evidence=result.evidence)
    label = {"reused": "Mavjud ma’lumot tekshirildi", "created": "Tayyorlov yaratildi",
             "repaired": "Yetishmagan tayyorlov tugatildi"}[action]
    allure.attach(json.dumps({"result": label, "key": spec.key, "scope": spec.scope,
                             "entities": entry["entities"], "detail": result.detail,
                             "evidence": result.evidence}, ensure_ascii=False, indent=2),
                  label, allure.attachment_type.JSON)
    return result
