"""Explicit repair branch for selected setup tests; preserve final business fixtures."""
import allure
from tests.regression.helpers.preparation.models import PreparationSpec, PreparationResult
from tests.regression.helpers.preparation.registry import Registry
from tests.regression.helpers.preparation.ensure import ensure_preparation
from tests.regression.helpers.preparation.readiness import verify_contract, PreparationRepairRequired
from tests.regression.helpers.retry.state import digest, RetryBlocked
from tests.regression.helpers.runtime import case_directory
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def execute_selected_repair(item):
    plan = getattr(item.config, "_retry_plan", {})
    if item.nodeid not in plan.get("repairs", []):
        return None
    baseline = item.funcargs.get("business_baseline") or item.funcargs.get("api_business_baseline")
    if not baseline:
        raise RetryBlocked("Explicit repair uchun baseline fixture topilmadi")
    registry = Registry(baseline)
    state = RegressionSetupState(case_directory(item) / "explicit-repair-state.json", dict(baseline))
    try:
        api = state.user()
        # Recheck the repair's own prerequisites before any write. An old PASS
        # cannot authorize a price/member repair on a changed or missing entity.
        for contract in plan.get("readiness", {}).get(item.nodeid, {}).values():
            verify_contract(api, baseline, contract)
        with allure.step("Oldingi PASS tayyorlov: faqat yetishmagan narx/bog‘lanishni tiklash"):
            for contract in plan["preparation_contracts"][item.nodeid].values():
                spec = PreparationSpec("contract_repair", item.nodeid, {"contract": digest(contract)})
                entry = registry.entry(spec)
                if entry["attempts"] == 0:
                    # The original explicit setup already consumed its initial write attempt.
                    entry["attempts"] = 1
                    registry.save()
                def probe(_entry):
                    try:
                        verify_contract(api, baseline, contract)
                        return PreparationResult("ready", detail="Joriy server qiymati tasdiqlandi")
                    except PreparationRepairRequired:
                        return PreparationResult("partial", detail="Narx yoki membership yetishmayapti")
                def prepare(_entry):
                    endpoint = contract["endpoint"]
                    if endpoint != "anor/mr/product/product_set_price$save" and not endpoint.startswith("anor/mrf/room_attachment$attach_"):
                        raise RetryBlocked("Bu tayyorlovni avtomatik tiklash ruxsat etilmagan")
                    api.call(endpoint, contract["expected"])
                ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        # Do not call the original wrapper: it may clear final client/action/order dictionaries.
        return True
    finally:
        state.close()
