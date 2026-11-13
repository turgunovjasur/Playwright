"""SCN-005: order yaratilishidan oldingi avans aynan shu orderga ajratiladi."""
from decimal import Decimal

import allure

from tests.regression.helpers.retry.checkpoints import reuse, verified
from tests.regression.test_orders.helpers.flows.settlement import allocate_to_order, post_cashin, read_settlement, verify_order_offset
from tests.regression.test_orders.helpers.flows.settlement_order import create_and_archive, verify_balances


def run_post_advance(case):
    """1. Boshlang'ich balans nol. 2. Ordersiz kirim. 3. Avans 20 000, qarz nol."""
    if not reuse("empty_client"):
        verify_balances(case, debt=0, prepayment=0, debts={})
        verified("empty_client")
    with allure.step("Order yaratilishidan avval 20 000 so‘m avans o‘tkazish"):
        receipt = post_cashin(case.page, client=case.client, number=case.reference + "-ADV",
                              amount=Decimal(20000))
        case.payments[:] = [receipt]
        case.checkpoint()
    verify_balances(case, debt=0, prepayment=20000, debts={})


def run_archive_after_advance(case):
    """1. Oldingi avans tasdiqlanadi. 2. Yangi order arxivlanadi. 3. Qarz IDsi tekshiriladi."""
    if not reuse("advance_before_order"):
        verify_balances(case, debt=0, prepayment=20000, debts={})
        verified("advance_before_order")
    order_id = create_and_archive(case, key="order", quantity=2, amount=14000)
    verify_balances(case, debt=14000, prepayment=20000, debts={order_id: Decimal(14000)})


def run_apply_advance(case):
    """1. Order va avans tekshiriladi. 2. 14 000 ajratiladi. 3. 6 000 avans qoladi."""
    order_id = case.workflow["order"]["id"]
    receipt = case.payments[0]
    if not reuse("offset_returned"):
        if not reuse("before_offset"):
            verify_balances(case, debt=14000, prepayment=20000, debts={order_id: Decimal(14000)})
            verified("before_offset")
        # The debt detail check navigates away from the list used by the allocation action.
        read_settlement(case.page, case.client)
        with allure.step("Oldingi kirimdan faqat shu order qarziga 14 000 so‘m ajratish"):
            allocate_to_order(case.page, client=case.client, order_id=order_id,
                              amount=Decimal(14000), remaining_debt=Decimal(14000))
        verified("offset_returned")
    verify_balances(case, debt=0, prepayment=6000, debts={})
    offset_id = verify_order_offset(case, order_id=order_id, amount=14000)
    case.allocations[:] = [{"order_id": order_id, "cashin_id": receipt["id"], "offset_id": offset_id,
                            "amount": "14000", "state": "verified_in_history"}]
    case.checkpoint()
