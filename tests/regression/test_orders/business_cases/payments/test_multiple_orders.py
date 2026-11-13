"""Bitta klient, ikki order, bitta kirim: exact ID bo'yicha qarzni taqsimlash."""
from decimal import Decimal
from tests.regression.helpers.retry.checkpoints import reuse, verified
import allure
from tests.regression.test_orders.helpers.flows.settlement import read_settlement, post_cashin, allocate_to_order
from tests.regression.test_orders.helpers.flows.settlement_order import create_and_archive, verify_balances


def run_first_order(case):
    """1. Own klient balansi0. 2. 14000order yaratish. 3. Jo'natish/arxiv. 4. Exactqarz14000."""
    with allure.step("1 - Yangi klientda qarz va avans yo'q"):
        if not reuse("multi_before_first"):
            verify_balances(case, debt="0", prepayment="0", debts={})
            verified("multi_before_first")
    identity = create_and_archive(case, key="first", quantity=2, amount=14000)
    with allure.step("2 - Birinchi orderning qarzi aynan 14 000"):
        verify_balances(case, debt="14000", prepayment="0", debts={identity:Decimal("14000")})


def run_second_order(case):
    """1. Birinchi qarz14000. 2. Ikkinchi21000order. 3. IkkalaIDqarz, jami35000."""
    first=case.workflow["first"]["id"]
    with allure.step("1 - Oldingi order qarzi o'zgarmagan"):
        if not reuse("multi_before_second"):
            verify_balances(case,debt="14000",prepayment="0",debts={first:Decimal("14000")})
            verified("multi_before_second")
    second=create_and_archive(case,key="second",quantity=3,amount=21000)
    case.check("Ikki order alohida IDga ega",True,first!=second)
    with allure.step("2 - Ikki orderning qarzi: 14 000 va 21 000"):
        verify_balances(case,debt="35000",prepayment="0",debts={first:Decimal("14000"),second:Decimal("21000")})


def run_shared_cashin(case):
    """1. Ikkalaqarz35000. 2. Bitta40000kirim, autooffsetOFF. 3. Qarz35000,avans40000."""
    first,second=case.workflow["first"]["id"],case.workflow["second"]["id"]
    debts={first:Decimal("14000"),second:Decimal("21000")}
    with allure.step('1 - Kirimdan oldin avans 0 va ikkala order qarzi saqlangan'):
        if not reuse("multi_before_cashin"):
            verify_balances(case,debt="35000",prepayment="0",debts=debts)
            verified("multi_before_cashin")
    payment={"number":case.reference+"-PAY","state":"pending"}
    case.payments.append(payment);case.checkpoint()
    payment.update(post_cashin(case.page,client=case.client,number=payment["number"],amount=Decimal("40000"),order_id=first))
    payment["state"]="posted";case.checkpoint()
    with allure.step('2 - Bitta 40 000 so‘mlik kirim ikkala order qarzini avtomatik yopmagan'):
        case.check('Test davomida yangi klient uchun yaratilgan kirimlar soni',1,len(case.payments))
        verify_balances(case,debt="35000",prepayment="40000",debts=debts)


def _allocate(case, *, key, amount, before_debt, after_debt, prepayment, expected_debts):
    identity=case.workflow[key]["id"]
    read_settlement(case.page,case.client)
    record={"order_id":identity,"cashin_id":case.payments[0]["id"],"amount":str(amount),"state":"pending"}
    case.allocations.append(record);case.checkpoint()
    allocate_to_order(case.page,client=case.client,order_id=identity,amount=Decimal(amount),remaining_debt=Decimal(before_debt))
    verify_balances(case,debt=after_debt,prepayment=prepayment,debts=expected_debts)
    record["state"]="verified_by_order_debt_and_balance";case.checkpoint()


def run_partial_first(case):
    """1. BirinchiIDga6000. 2. Qarzlar8000va21000. 3. Avans34000."""
    with allure.step('1 - Birinchi orderga 6 000 so‘m ajratiladi; ikkinchi order qarzi o‘zgarmaydi'):
        _allocate(case,key="first",amount="6000",before_debt="14000",after_debt="29000",prepayment="34000",expected_debts={case.workflow["first"]["id"]:Decimal("8000"),case.workflow["second"]["id"]:Decimal("21000")})


def run_finish_first(case):
    """1. Birinchiqolgan8000. 2. Faqatikkinchiqarz21000. 3. Avans26000."""
    with allure.step('1 - Birinchi order to‘liq yopiladi; ikkinchi orderning 21 000 so‘m qarzi qoladi'):
        _allocate(case,key="first",amount="8000",before_debt="8000",after_debt="21000",prepayment="26000",expected_debts={case.workflow["second"]["id"]:Decimal("21000")})


def run_finish_second(case):
    """1. Ikkinchiorder21000to'lanadi. 2. Qarz0. 3. Ortiqcha5000avansda qoladi."""
    with allure.step('1 - Ikkinchi order yopiladi; ortiqcha 5 000 so‘m klient balansida qoladi'):
        _allocate(case,key="second",amount="21000",before_debt="21000",after_debt="0",prepayment="5000",expected_debts={})
