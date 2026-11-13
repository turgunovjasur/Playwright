"""Return runneri uchun mavjud «Возврат» narxini filial va xonaga ulash.

Additive mutation kontrakti: tests/api/setup/test_21_room_attachment.py.
Yangi narx turi yaratilmaydi; boshqa narx, klient va shtat bog'lanishi yozilmaydi.
"""
from copy import deepcopy
import json
from pathlib import Path

import allure
import pytest

from tests.api.client import APIError, positive_id, require_fields
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Orderdan qaytarish"),
              allure.story("Возврат narxini tayyorlash")]


def run_prepare_return_price(baseline, data, directory):
    """1. Filial va ish zonasining mavjud narx IDlarini qayd etish.
    2. Mavjud tizim «Возврат» narxini topib, kerak bo'lsa filialga ulash.
    3. Shu IDni kerak bo'lsa ish zonasiga ulash.
    4. Saved model va oldingi barcha narx bog'lanishlari saqlanganini tekshirish.

    Qayta ishlatish idempotent: mavjud bog'lanish qayta yozilmaydi.
    Faqat API21da mavjud ikkita additive attach endpoint ishlatiladi.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    state = RegressionSetupState(directory / "return-price-state.json", deepcopy(baseline))
    metadata = {
        "status": "process", "stage": "planned", "name": "Возврат",
        "baseline_code": str(baseline["code"]),
        "filial_id": str(baseline["filial_id"]), "room_id": str(baseline["room_id"]),
        "filial_attachment_added": False, "room_attachment_added": False,
        "retention": "existing_system_price_and_attachments_retained",
    }
    data["return_price"] = metadata
    room_route = "anor/mrf/room_attachment"
    columns = ["price_type_id", "name"]
    room_data = {"room_id": metadata["room_id"], "attached": "Y"}

    def persist(stage):
        metadata["stage"] = stage
        path = directory / "return-price-setup.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)

    persist("planned")
    try:
        api = state.user()
        with allure.step("1 - Filial va xonaning mavjud narx IDlarini saqlash"):
            filial_rows = api.table("anor/mkr/price_type_list:table", columns)
            room_rows = api.table(room_route + ":table_price_type", columns, data=room_data)
            filial_before = {positive_id(row["price_type_id"]) for row in filial_rows}
            room_before = {positive_id(row["price_type_id"]) for row in room_rows}
            metadata["filial_price_ids_before"] = sorted(filial_before)
            metadata["room_price_ids_before"] = sorted(room_before)
            persist("membership_snapshot")
        with allure.step("2 - Mavjud Возврат narxini topish va filialga zarur bo'lsa biriktirish"):
            matches = [row for row in filial_rows if row["name"] == metadata["name"]]
            if len(matches) > 1:
                raise APIError("Filialda Возврат nomli bir nechta narx bor; tizim narxi aniq emas")
            if matches:
                selected = matches[0]
            else:
                selected = api.one("anor/mkr/price_type_list+attach:table", columns,
                                   filters=["name", "=", metadata["name"]])
            require_fields(selected, name=metadata["name"])
            metadata["id"] = positive_id(selected["price_type_id"])
            persist("identified")
            if metadata["id"] not in filial_before:
                api.call("anor/mkr/price_type_list+attach$attach",
                         api.context(room_id=metadata["room_id"], price_type_id=metadata["id"]))
                metadata["filial_attachment_added"] = True
                persist("filial_attached")
            filial_after_rows = api.table("anor/mkr/price_type_list:table", columns)
            filial_after = {positive_id(row["price_type_id"]) for row in filial_after_rows}
            metadata["filial_price_ids_after"] = sorted(filial_after)
            if filial_after != filial_before | {metadata["id"]}:
                raise APIError("Filial narx IDlari oldingi ro'yxat + Возврат IDsi bilan mos emas")
            require_fields(next(row for row in filial_after_rows if str(row["price_type_id"]) == metadata["id"]),
                           price_type_id=metadata["id"], name=metadata["name"])
            persist("filial_verified")
        with allure.step("3 - Aynan shu Возврат narxini xonaga zarur bo'lsa biriktirish"):
            if metadata["id"] not in room_before:
                available = api.table(room_route + ":table_price_type", columns,
                                      data={**room_data, "attached": "N"})
                matches = [row for row in available if str(row["price_type_id"]) == metadata["id"]]
                if len(matches) != 1:
                    raise APIError("Filialdagi Возврат IDsi xonaning Доступные narxlari ichida topilmadi")
                require_fields(matches[0], price_type_id=metadata["id"], name=metadata["name"])
                persist("room_available")
                api.call(room_route + "$attach_price_type",
                         api.context(room_id=metadata["room_id"], price_type_id=metadata["id"]))
                metadata["room_attachment_added"] = True
                persist("room_attached")
        with allure.step("4 - Narx nomi, xona membershipi va barcha oldingi narx bog'lanishlarini tekshirish"):
            saved = api.model("anor/mkr/price_type_view", price_type_id=metadata["id"])
            require_fields(saved, name=metadata["name"])
            room_after_rows = api.table(room_route + ":table_price_type", columns, data=room_data)
            room_after = {positive_id(row["price_type_id"]) for row in room_after_rows}
            metadata["room_price_ids_after"] = sorted(room_after)
            if room_after != room_before | {metadata["id"]}:
                raise APIError("Xona narx IDlari oldingi ro'yxat + Возврат IDsi bilan mos emas")
            require_fields(next(row for row in room_after_rows if str(row["price_type_id"]) == metadata["id"]),
                           price_type_id=metadata["id"], name=metadata["name"])
            final_filial = {positive_id(row["price_type_id"]) for row in api.table("anor/mkr/price_type_list:table", columns)}
            metadata["filial_price_ids_after"] = sorted(final_filial)
            if final_filial != filial_before | {metadata["id"]}:
                raise APIError("Xonaga ulashdan keyin filialdagi boshqa narx bog'lanishi o'zgardi")
            metadata["status"] = "passed"
            persist("verified")
    except Exception as error:
        metadata.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        try:
            persist(metadata["stage"])
            allure.attach(json.dumps(metadata, ensure_ascii=False), "Возврат narxi — ID va bog'lanishlar", allure.attachment_type.JSON)
        finally:
            state.close()


@allure.title("Qaytarish uchun Возврат narxini filial va xonaga biriktirish")
def test_prepare_return_price(business_baseline, workflow_data, regression_case_dir):
    run_prepare_return_price(business_baseline, workflow_data, regression_case_dir)
