"""Guruhga tegishli xizmatlar va ularning 1 200 so‘mlik narxlari."""
from decimal import Decimal

import allure

from tests.api.client import positive_id, require_fields
from tests.regression.helpers.retry.reconcile import exact_row
from tests.regression.helpers.retry.state import RetryBlocked, stable_uuid
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def run_prepare_services(baseline, workflow, directory, *, count):
    """1. Guruh xizmatlarini yaratish. 2. ID va kodni tekshirish. 3. Narxni qayta o‘qish."""
    state = RegressionSetupState(directory / "services-state.json", dict(baseline))
    table = "anor/mr/product/service_list:table"
    price_id = str(baseline["price_type_id_uzb"])
    services = []
    try:
        api = state.user()
        measure = api.one("anor/mr/product/service+add:measures", ["measure_id", "short_name"],
                          filters=["short_name", "=", "шт"])
        for index in range(count):
            code = "svc-" + stable_uuid(f"service-{index}").hex[:12]
            name = "Order service " + code
            with allure.step(f"{index + 1}-xizmatni guruh sektorida tayyorlash"):
                match = exact_row(api, table, "product_id", "code", code)
                if match is None:
                    api.call("anor/mr/product/service+add$save", {
                        "name": name, "code": code, "state": "A", "measure_id": positive_id(measure["measure_id"]),
                        "sector_ids": [baseline["sector_id"]], "supplier_ids": [],
                        "group_type_id": {}, "photos": [], "files": [], "barcodes": [],
                    })
                row = api.one(table, ["product_id", "code", "name"], filters=["code", "=", code])
                require_fields(row, name=name, code=code)
                service_id = positive_id(row["product_id"])
            with allure.step(f"{name} uchun narxni belgilash va aynan shu narx turidan qayta o‘qish"):
                def current_price():
                    rows = api.model("anor/mr/product/product_set_price", product_id=service_id)["prices"]
                    values = [r[5] for r in rows if str(r[0]) == price_id and str(r[3]) == "-1"]
                    if len(values) > 1:
                        raise RetryBlocked("Xizmat narxi takrorlangan")
                    return Decimal(str(values[0])) if values and values[0] not in (None, "") else None

                if current_price() is None:
                    api.call("anor/mr/product/product_set_price$save", {
                        "product_id": service_id,
                        "prices": [{"price_type_id": price_id, "card_id": "-1", "price": "1200"}],
                    })
                if current_price() != Decimal(1200):
                    raise RetryBlocked("Xizmat narxi 1 200 so‘mga mos emas")
            services.append({"id": service_id, "name": name, "code": code})
        workflow["services"] = services
    finally:
        state.close()
