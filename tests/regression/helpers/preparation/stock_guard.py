"""Fast read-only setup precondition before Add; business stock assertions stay in UI."""
from decimal import Decimal
import allure
from tests.regression.helpers.retry.state import ACTIVE, RetryBlocked
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState


def require_available(case, quantity, *, bonus_quantity=0, warehouse="Основной склад"):
    journal = ACTIVE.get()
    state = RegressionSetupState(journal.directory / "stock-precondition-state.json", dict(case.baseline))
    try:
        api = state.user()
        with allure.step("Add oldidan own TMZning hozirgi erkin qoldig‘ini tekshirish"):
            for field, needed in (("product_id", quantity), ("product_id_usa", bonus_quantity)):
                if not needed:
                    continue
                rows = api.table("anor/mr/product/inventory_view:balances",
                    ["warehouse_name", "quant_free", "quant_booked", "balance_quant"],
                    filters=["warehouse_name", "=", warehouse], data={"product_id": case.baseline[field]})
                available = sum((Decimal(str(r["quant_free"] or 0)) for r in rows), Decimal(0))
                journal.event("stock_precondition", product_id=str(case.baseline[field]), warehouse=warehouse,
                              required=str(needed), available=str(available))
                if available < Decimal(str(needed)):
                    raise RetryBlocked(f"Tayyorlov qoldig‘i yetmaydi: TMZ {case.baseline[field]}, {warehouse}; kerak {needed}, erkin {available}. Biznes test yashirin kirim qilmadi")
    finally:
        state.close()
