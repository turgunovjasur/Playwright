"""UI setupdagi payer, kontrakt va license qoidalari bilan HTTP xarid."""
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import allure
import pytest

from tests.api.client import APIError
from tests.smoke.test_setup.flow_setup.flow_license import license_policy_disabled, license_purchase_server_unsupported

pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Buy License")]


def run_buy_license(api_setup):
    s = api_setup
    if license_policy_disabled():
        pytest.skip("Licensing policy is disabled for the new company")
    if license_purchase_server_unsupported():
        pytest.skip("UI setup also skips license purchase on smartup.online")
    api = s.admin(head_filial=True)
    route = "biruni/kl/license_list"
    columns = ["license_id", "license_name", "status", "quant", "begin_date", "end_date"]
    with allure.step("1 - UI bilan bir xil to‘lovchi va kontraktni topish"):
        info = api.call(route + ":purchase_info", {})
        payers = [p for p in info["payers"] if p["name"] == "AUTOTEST GWS"]
        if len(payers) != 1:
            raise APIError("AUTOTEST GWS payer must be unique")
        payer = payers[0]
        # Some xtrade billing labels arrive as UTF-8 decoded as Latin-1.
        # Match the exact UI contract after decoding, never a hardcoded ID.
        contracts = []
        for candidate in payer["contracts"]:
            label = candidate["contract_name"]
            try:
                label = label.encode("latin-1").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
            if candidate["contract_number"] == "bn" and label == "Договор № bn от 01.01.2025":
                contracts.append(candidate)
        if len(contracts) != 1:
            raise APIError("The UI setup contract bn dated 01.01.2025 must be unique")
        contract = contracts[0]
        if Decimal(str(contract["available_amount"])) <= 0:
            raise APIError("License payer balance is not positive")
    with allure.step("2 - Majburiy 5 yoki oddiy 1 dona litsenziyani tanlash"):
        today = datetime.now(ZoneInfo("Asia/Tashkent")).date()
        services = [x for x in info["licenses"] if x["license_code"] == "ERP:USERS"]
        mandatory = [x for x in services if x.get("required_count")]
        uncovered = []
        for service in mandatory:
            covers = any(datetime.strptime(a, "%d.%m.%Y").date() <= today <= datetime.strptime(b, "%d.%m.%Y").date()
                         for a, b in service.get("periods", []))
            if not covers or Decimal(str(service.get("bought_quantity") or 0)) < Decimal(service["required_count"]):
                uncovered.append(service)
        choices = uncovered or [x for x in services if not x.get("required_count")]
        if len(choices) != 1:
            raise APIError("ERP users purchase service is ambiguous")
        service = choices[0]
        quantity = "5" if uncovered else "1"
        if uncovered and str(service["required_count"]) != "5":
            raise APIError("Mandatory license quantity differs from UI setup expectation (5)")
        begin = today.replace(day=1) if uncovered else today
        before = api.table(route + ":table_license", columns)
    with allure.step("3 - Litsenziya xaridini bir marta yuborish"):
        # Captured from the successful xtrade UI setup purchase on 2026-11-13.
        api.call(route + ":purchase", {
            "posted": "Y", "purchases": [{"begin_date": begin.strftime("%d.%m.%Y"),
            "end_date": today.strftime("%m.%Y"), "payer_id": payer["person_id"],
            "contract_id": contract["contract_id"], "is_demo": "N",
            "licenses": [{"service_id": service["service_id"], "quantity": quantity}]}],
            "autosign_faktura_enabled": info["autosign_faktura_enabled"]})
    with allure.step("4 - Yangi faol litsenziya va miqdorni qayta o‘qish"):
        previous = {str(row["license_id"]) for row in before}
        after = api.table(route + ":table_license", columns, sort=["-created_on"])
        purchased = [r for r in after if str(r["license_id"]) not in previous
                     and r["license_name"] == "ERP users" and r["status"] == "A"
                     and r["begin_date"] == begin.strftime("%d.%m.%Y")
                     and Decimal(str(r["quant"])) == Decimal(quantity)]
        if len(purchased) != 1:
            raise APIError("Purchase response received but a unique new active license was not verified; do not blindly repeat purchase")
        s.save_id("purchased_license_id", purchased[0]["license_id"])


@allure.title("API 10 - Buy License")
def test_10_buy_license(api_setup):
    run_buy_license(api_setup)
