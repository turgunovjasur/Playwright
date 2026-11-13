"""SCN-002: kirimni o'tkazishning o'zi aynan bitta order qarzini yopadi."""
from decimal import Decimal

import allure

from tests.regression.helpers.retry.checkpoints import reuse, verified
from tests.regression.test_orders.helpers.flows.settlement import post_cashin, verify_order_offset
from tests.regression.test_orders.helpers.flows.settlement_order import create_and_archive, verify_balances


def run_archive_order(case):
    """1. Klientda balans nol. 2. Order arxivlanadi. 3. ID bo'yicha qarz tekshiriladi."""
    with allure.step("Yangi klient qarzsiz va avanssiz"):
        if not reuse("empty_client"):
            verify_balances(case, debt=0, prepayment=0, debts={})
            verified("empty_client")
    order_id = create_and_archive(case, key="order", quantity=2, amount=14000)
    verify_balances(case, debt=14000, prepayment=0, debts={order_id: Decimal(14000)})


def run_post_auto_offset(case):
    """1. Bitta ochiq qarz. 2. Avtomatik hisob-kitobli kirim. 3. Yakuniy balans."""
    order_id = case.workflow["order"]["id"]
    with allure.step("To‘lov oldida yagona qarz shu orderga tegishli"):
        if not reuse("before_cashin"):
            verify_balances(case, debt=14000, prepayment=0, debts={order_id: Decimal(14000)})
            verified("before_cashin")
    with allure.step("14 000 so‘mlik kirimni avtomatik hisob-kitob bilan o‘tkazish"):
        receipt = post_cashin(case.page, client=case.client, number=case.reference + "-PAY",
                              amount=Decimal(14000), order_id=order_id, auto_offset=True)
        case.payments[:] = [receipt]
        case.checkpoint()
    with allure.step("Kirim o‘tkazilgach qarz, avans va balans nol"):
        verify_balances(case, debt=0, prepayment=0, debts={})
    offset_id = verify_order_offset(case, order_id=order_id, amount=14000)
    case.allocations[:] = [{"order_id": order_id, "cashin_id": receipt["id"], "offset_id": offset_id,
                            "amount": "14000", "state": "verified_in_history"}]
    case.checkpoint()
