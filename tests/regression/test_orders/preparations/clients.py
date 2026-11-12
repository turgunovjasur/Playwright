"""Order guruhlari uchun alohida klient API tayyorlovi.

Faqat natural_client va room $attach_natural_person kontraktlari ishlatiladi.
Shared baseline, user/litsenziya, narxlar va mavjud xona bog'lanishlari
o'zgartirilmaydi. Yangi klientlar qayta tekshirish uchun saqlanadi.
"""

import json
from copy import deepcopy
from pathlib import Path
from tests.regression.retry.state import stable_uuid as uuid4

import allure

from tests.api.client import APIError, positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.test_orders.auth_recovery import RegressionSetupState


def prepare_order_client(baseline, *, purpose, kind, directory):
    """Own klient yaratadi, qayta o'qiydi va setup xonasiga qo'shadi.

    1. Baseline va xona bog'lanishlarining boshlang'ich snapshotini olish.
    2. Unique aktiv klient yaratish; IDni darhol artefaktga saqlash.
    3. Model hamda klient listida aynan shu ID/nomni tekshirish.
    4. Faqat yangi klientni xonaga qo'shish va mavjud bog'lanishlarni tekshirish.
    """
    allowed = {"payment": {"ordinary", "promoted", "auto-offset", "prepayment-first"}, "bonus-limit": {"first", "second"},
               "returns": {"promoted"}, "multi-payment": {"shared"}, "discounts": {"manual"}, "statuses": {"cycle"}, "two-warehouses": {"reserve"}, "product-limit": {"shared"}}
    if purpose not in allowed or kind not in allowed[purpose]:
        raise ValueError("Order klient tayyorlovi uchun purpose/kind juftligi noma’lum")
    required = ("code", "url", "company_code", "filial_id", "user_id", "room_id")
    if not isinstance(baseline, dict) or any(baseline.get(key) in (None, "") for key in required):
        raise APIError("Order klient tayyorlovi uchun tekshirilgan API baseline kerak")
    run_id = uuid4("client").hex[:12]
    directory = Path(directory) / f"{purpose}-client-{kind}-{run_id}"
    directory.mkdir(parents=True, exist_ok=False)
    state = RegressionSetupState(directory / "state.json", deepcopy(baseline))
    metadata = {
        "status": "process", "kind": kind, "run_id": run_id,
        "baseline_code": str(baseline["code"]), "url": baseline["url"],
        "company_code": baseline["company_code"], "filial_id": str(baseline["filial_id"]),
        "room_id": str(baseline["room_id"]),
        "name": f"order-{purpose}-{kind}-pw{baseline['code']}-{run_id}",
        "code": f"{purpose}-{kind}-{baseline['code']}-{run_id}",
        "retention": "retained", "stage": "planned",
    }
    attachment_keys = {
        "natural_person": "person_id", "payment_type": "payment_type_id",
        "warehouse": "warehouse_id", "cashbox": "cashbox_id", "price_type": "price_type_id",
    }
    route = "anor/mrf/room_attachment"

    def persist(stage):
        metadata["stage"] = stage
        text = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        temporary = directory / "client.json.tmp"
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(directory / "client.json")
        label = {"payment": "Payment klient", "bonus-limit": "Bonus limiti klienti",
                 "returns": "Qaytarish klienti", "multi-payment": "Ikki order klienti",
                 "discounts": "Chegirmalar klienti", "statuses": "Status zanjiri klienti", "two-warehouses": "Ikki ombor klienti", "product-limit": "TMZ limiti klienti"}[purpose]
        allure.attach(text, f"{label} — {kind}: {stage}", allure.attachment_type.JSON)

    def attachments(api):
        return {attachment_kind: {
            positive_id(row[id_field]): row["name"]
            for row in api.table(route + ":table_" + attachment_kind, [id_field, "name"],
                                 data={"room_id": state["room_id"], "attached": "Y"})
        } for attachment_kind, id_field in attachment_keys.items()}

    persist("planned")
    try:
        with allure.step("1 - Setup xonasining mavjud klient, to'lov, ombor, kassa va narx bog'lanishlarini o'qish"):
            api = state.user()
            before = attachments(api)
            metadata["attachments_before"] = before
            persist("room_snapshot")
        with allure.step(f"2 - {purpose}/{kind} uchun alohida aktiv klient yaratish"):
            payload = state.payload("natural_client")
            payload.update(first_name=metadata["name"], code=metadata["code"])
            result = api.call(CONTRACTS["natural_client"]["endpoint"], payload)
            metadata["person_id"] = positive_id(result["person_id"])
            persist("created")
        with allure.step("3 - Yangi klientning saved modeli va klient listidagi aynan shu IDni tekshirish"):
            view = api.model("anor/mr/person/natural_person_view", person_id=metadata["person_id"])
            require_fields(view, name=metadata["name"], code=metadata["code"], state="A")
            client_row = api.one("anor/mrf/client_list:table", ["client_id", "name"],
                                 filters=["client_id", "=", metadata["person_id"]])
            require_fields(client_row, client_id=metadata["person_id"], name=metadata["name"])
            persist("client_verified")
        with allure.step("4 - Faqat yangi klientni mavjud xonaga qo'shish"):
            # Additive endpoint: barcha IDlarni qayta save/replace qilmaydi.
            api.call(route + "$attach_natural_person",
                     api.context(room_id=state["room_id"], person_id=metadata["person_id"]))
            persist("attached")
        with allure.step("5 - Yangi membership va barcha oldingi bog'lanishlar saqlanganini qayta o'qish"):
            after = attachments(api)
            metadata["attachments_after"] = after
            expected = deepcopy(before)
            expected["natural_person"][metadata["person_id"]] = metadata["name"]
            if after != expected:
                persist("membership_mismatch")
                raise APIError("Xona bog'lanishlari expected eski membership + bitta yangi klientga mos emas")
            metadata["status"] = "passed"
            persist("verified")
        return metadata
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error_type"] = type(error).__name__
        persist(metadata["stage"])
        raise
    finally:
        state.close()
