"""Real saves with deliberate interruption, followed by the standard one-round retry.

Only this opt-in runner injects failures. It never mocks a Smartup business reply.
Initial failures are expected evidence; final checks still must pass independently.
"""
from copy import deepcopy
import allure
import pytest
from tests.api.client import positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.helpers.preparation.models import PreparationSpec, PreparationResult
from tests.regression.helpers.preparation.registry import Registry
from tests.regression.helpers.preparation.ensure import ensure_preparation
from tests.regression.helpers.retry.state import ACTIVE, digest, RetryBlocked
from tests.regression.helpers.retry.reconcile import exact_row, confirm_entity, is_retry
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.setup_cases.test_catalog_stock import run_prepare_catalog, run_prepare_prices, run_prepare_stock
from tests.regression.test_orders.helpers.flows.order import open_new_order, select_order_product, save_order_by_reference
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("recovery"),
              allure.epic("Regression"), allure.feature("Retry mexanizmi — boshqariladigan uzilishlar")]


class VerificationInterruption(AssertionError):
    """An explicitly authorized integration failure; normal suites never raise it."""


def _product(baseline, directory, key, *, interrupt=None, monkeypatch=None):
    registry = Registry(baseline)
    spec = PreparationSpec(key, "verification-common", {"kind": "product"})
    suffix = digest({"root": registry.data["root_run"], "key": key})[:12]
    name, code = "Recovery product-" + suffix, "rc-" + suffix
    state = RegressionSetupState(directory / "verification-api-state.json", deepcopy(baseline))
    journal = ACTIVE.get()
    try:
        api = state.user()
        def probe(entry):
            row = exact_row(api, "anor/mr/product/inventory_list:table", "product_id", "code", code)
            if not row:
                return PreparationResult("missing")
            identity = positive_id(row["product_id"])
            require_fields(api.model("anor/mr/product/inventory_view", product_id=identity), name=name, code=code, state="A")
            confirm_entity("product", code, identity, verified=True)
            return PreparationResult("ready", {"product_id": identity, "code": code}, "Exact code bo‘yicha aynan 1 ta TMZ")
        def prepare(entry):
            if interrupt == "before_save" and not is_retry():
                raise VerificationInterruption("NAZORATLI UZILISH: Save hali yuborilmagan")
            payload = state.payload("product")
            payload.update(name=name, code=code)
            if interrupt == "after_commit" and not is_retry():
                original = journal.confirm
                def stop_before_id(operation, **fields):
                    if operation.startswith("api:anor/mr/product/inventory+add$save:"):
                        raise VerificationInterruption("NAZORATLI UZILISH: server javob berdi, lokal ID checkpointi yozilmadi")
                    return original(operation, **fields)
                with monkeypatch.context() as context:
                    context.setattr(journal, "confirm", stop_before_id)
                    result = api.call(CONTRACTS["product"]["endpoint"], payload)
            else:
                result = api.call(CONTRACTS["product"]["endpoint"], payload)
            registry.checkpoint(spec, product_id=positive_id(result["product_id"]), code=code)
            if interrupt == "after_id" and not is_retry():
                raise VerificationInterruption("NAZORATLI UZILISH: ID yozildi, yakuniy tekshiruv hali bajarilmadi")
        with allure.step("Real server: exact lookup → mavjudidan davom etish yoki bitta Save → saved oracle"):
            result = ensure_preparation(spec, registry=registry, probe=probe, prepare=prepare)
        writes = [v for v in journal.data["operations"].values() if v.get("endpoint") == CONTRACTS["product"]["endpoint"] and not v.get("reused")]
        if is_retry() and interrupt in {"after_commit", "after_id"} and writes:
            raise AssertionError("Oldin saqlangan TMZ uchun retry yangi Save yubordi")
        return result
    finally:
        state.close()


@allure.title("Recovery tayyorlovi: UI order uchun own TMZ")
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "recovery")


@allure.title("Recovery tayyorlovi: narx")
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "recovery")


@allure.title("Recovery tayyorlovi: ikki payment uchun 4 dona qoldiq")
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "recovery")


@allure.title("Save oldidan uzilish → retry aynan bitta TMZ yaratadi")
@pytest.mark.order_requires()
def test_03_before_save(business_baseline, regression_case_dir):
    _product(business_baseline, regression_case_dir, "before-save", interrupt="before_save")


@allure.title("Server saqlagach ID checkpointidan oldin uzilish → dublikat yo‘q")
@pytest.mark.order_requires()
def test_04_commit_before_id(business_baseline, regression_case_dir, monkeypatch):
    _product(business_baseline, regression_case_dir, "commit-before-id", interrupt="after_commit", monkeypatch=monkeypatch)


@allure.title("ID checkpointidan keyin uzilish → aynan shu IDdan davom etadi")
@pytest.mark.order_requires()
def test_05_after_id(business_baseline, regression_case_dir):
    _product(business_baseline, regression_case_dir, "after-id", interrupt="after_id")


@allure.title("Umumiy tayyorlovni birinchi consumer yaratadi")
@pytest.mark.order_requires()
def test_06_shared_create(business_baseline, regression_case_dir):
    _product(business_baseline, regression_case_dir, "shared-product")


@allure.title("Mustaqil consumer umumiy tayyorlovni qayta yaratmaydi")
@pytest.mark.order_requires()
def test_07_shared_reuse(business_baseline, regression_case_dir):
    _product(business_baseline, regression_case_dir, "shared-product")
    writes = [v for v in ACTIVE.get().data["operations"].values() if v.get("endpoint") == CONTRACTS["product"]["endpoint"]]
    if writes:
        raise AssertionError("Mavjud umumiy TMZ uchun ikkinchi create bajarildi")


@allure.title("UI order saqlangach uzilish → retry o‘sha IDni tekshiradi")
@pytest.mark.order_requires('test_002_stock')
def test_08_order_saved(ordinary_order):
    """Real UI Save, injected failure, exact TTN reconciliation and saved values."""
    case = ordinary_order
    page, base = case.page, AutoBasePage(case.page)
    journal = ACTIVE.get()
    key = "entity:order:" + case.reference
    previous = journal.source.get("operations", {}).get(key)
    if previous:
        with allure.step("Retry: Add ochmasdan oldingi orderni aniq ID bilan ko‘rish"):
            base.open_route("trade/tdeal/order/order_view?deal_id=" + previous["entity_id"], heading="Заказ / Просмотр")
            identity = base.form_view(label="ИД заказа", expect_value=previous["entity_id"], return_value=True).strip()
    else:
        open_new_order(page)
        with allure.step("2 dona × 7000 so‘mlik oddiy Draft"):
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value="2", press_tab=True)
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value="Черновик")
        identity = save_order_by_reference(page, case.reference)
        confirm_entity("order", case.reference, identity)
        case.remember_order(identity)
        if not is_retry():
            raise VerificationInterruption("NAZORATLI UZILISH: UI order saqlandi, saved summani tekshirish oldidan to‘xtadi")
    with allure.step("O‘sha saved order: TTN, klient, Draft va 14000 so‘m"):
        base.form_view(label="Номер ТТН", expect_value=case.reference)
        base.form_view(label="Клиент", expect_value=case.client)
        base.form_view(label="Статус", expect_value="Черновик")
        base.form_view(label="Сумма заказа", expect_value="14000", remove_spaces=True)
        confirm_entity("order", case.reference, identity, verified=True)
        case.remember_order(identity)
    from tests.regression.helpers.retry.reconcile import ui_row
    row = ui_row(page, "trade/tdeal/order/order_list:table", ["deal_id", "delivery_number"], "delivery_number", case.reference)
    case.check("Exact TTN bo‘yicha yagona saved order", str(identity), str(row["deal_id"]))


@allure.title("Recovery tayyorlovi: to‘lov uchun alohida klient")
@pytest.mark.order_requires('test_001_prices')
def test_09_prepare_payment_client(business_baseline, payment_clients, regression_case_dir):
    from tests.regression.test_orders.setup_cases.test_payment_clients import run_ordinary_payment_client
    run_ordinary_payment_client(business_baseline, payment_clients, regression_case_dir)


@allure.title("Recovery tayyorlovi: ikkinchi installment testi uchun alohida klient")
@pytest.mark.order_requires('test_001_prices')
def test_09b_prepare_second_client(business_baseline, payment_clients, regression_case_dir):
    from tests.regression.test_orders.setup_cases.test_payment_clients import run_promoted_payment_client
    run_promoted_payment_client(business_baseline, payment_clients, regression_case_dir)


@pytest.fixture
def second_recovery_payment(order_user_page, business_baseline, payment_clients, regression_case_dir, request):
    from tests.regression.test_orders.conftest import _context
    with _context(order_user_page, business_baseline, {"unit_price": "7000"}, regression_case_dir,
                  request.node, client=payment_clients["promoted"]) as case:
        yield case


@allure.title("Cashin saqlangach uzilish → bitta kirimdan qisman va to‘liq qarz yopish")
@pytest.mark.order_requires('test_002_stock', 'test_09_prepare_payment_client')
def test_10_cashin_saved(ordinary_payment_order, workflow_data, monkeypatch):
    from tests.regression.test_orders.business_cases.payments import test_partial_full_payment as flow
    original = flow.verify_step
    def interrupt_after_cashin(name):
        original(name)
        if name == "payment_cashin_verified" and not is_retry():
            raise VerificationInterruption("NAZORATLI UZILISH: 14000 so‘m cashin saqlandi; offset hali yuborilmadi")
    with monkeypatch.context() as context:
        context.setattr(flow, "verify_step", interrupt_after_cashin)
        flow.run_partial_full_payment(ordinary_payment_order)
    from tests.regression.helpers.retry.reconcile import ui_row
    payment = ordinary_payment_order.payments[-1]
    row = ui_row(ordinary_payment_order.page, "trade/tcs/cashin_list:table",
                 ["cashin_id", "cashin_number"], "cashin_number", payment["number"])
    ordinary_payment_order.check("Retrydan keyin exact raqamli cashin yagona", payment["id"], str(row["cashin_id"]))
    workflow_data["payment_order"] = ordinary_payment_order.orders[-1]


@allure.title("Noaniq offset dalili bo‘lsa pul qayta yuborilmaydi")
@pytest.mark.order_requires('test_10_cashin_saved')
def test_11_unknown_offset(ordinary_payment_order, workflow_data):
    """Control-only uncertain journal state; real debt is read, no fake server reply."""
    from decimal import Decimal
    from tests.regression.test_orders.helpers.flows.settlement import allocate_to_order
    journal = ACTIVE.get()
    order_id = workflow_data["payment_order"]
    operation = "offset:" + digest({"order_id": str(order_id), "amount": "1", "before": "0"})
    journal.source.setdefault("operations", {})[operation] = {"state": "intent", "transport": "logical"}
    with pytest.raises(RetryBlocked, match="ikkinchi to‘lov yuborilmaydi"):
        allocate_to_order(ordinary_payment_order.page, client=ordinary_payment_order.client,
                          order_id=order_id, amount=Decimal(1), remaining_debt=Decimal(0))
    assert not any(op.get("endpoint") == "anor/mdeal/order/offset/offset$post" for op in journal.data["operations"].values()), "Unknown offset yangi POST yubormasligi kerak"


@allure.title("Klient saqlangan, room attachment oldida uzilish → mavjud klientni biriktirish")
@pytest.mark.order_requires('test_001_prices')
def test_12_partial_attachment(business_baseline, regression_case_dir, monkeypatch):
    from tests.api.client import SmartupAPI
    from tests.regression.test_orders.helpers.preparations.payment_clients import prepare_payment_client
    original = SmartupAPI.call
    def interrupt_before_attachment(api, endpoint, *args, **kwargs):
        if endpoint == "anor/mrf/room_attachment$attach_natural_person" and not is_retry():
            raise VerificationInterruption("NAZORATLI UZILISH: klient mavjud, xona attachmenti hali yuborilmagan")
        return original(api, endpoint, *args, **kwargs)
    with monkeypatch.context() as context:
        context.setattr(SmartupAPI, "call", interrupt_before_attachment)
        result = prepare_payment_client(business_baseline, kind="promoted", directory=regression_case_dir)
    assert result["status"] == "passed"
    journal = ACTIVE.get()
    if is_retry():
        assert not any(op.get("endpoint") == "anor/mr/person/natural_person+add$save" and not op.get("reused")
                       for op in journal.data["operations"].values()), "Roomga ulash uchun klient qayta yaratilmasligi kerak"


@allure.title("Qidiruv javobi noaniq yoki ko‘p bo‘lsa create qarori bloklanadi")
@pytest.mark.order_requires()
def test_13_ambiguous_lookup():
    """Protocol guard control; these synthetic replies are never business PASS evidence."""
    from tests.regression.helpers.retry.reconcile import one_row
    for reply in ({"count": 2, "data": [["1", "same"], ["2", "same"]]}, {"data": []}, {"count": 1, "data": []}):
        with pytest.raises(RetryBlocked):
            one_row(reply, ["id", "name"], "name", "same")


@allure.title("Birinchi offsetdan keyin uzilish → faqat qolgan installment davom etadi")
@pytest.mark.order_requires('test_002_stock', 'test_09b_prepare_second_client')
def test_14_between_installments(second_recovery_payment, monkeypatch):
    from tests.regression.test_orders.business_cases.payments import test_partial_full_payment as flow
    original = flow.verify_step
    def interrupt_after_first_offset(name):
        original(name)
        if name == "payment_offset_verified:6000" and not is_retry():
            raise VerificationInterruption("NAZORATLI UZILISH: birinchi 6000 to‘landi; qolgan 8000 hali yuborilmadi")
    with monkeypatch.context() as context:
        context.setattr(flow, "verify_step", interrupt_after_first_offset)
        flow.run_partial_full_payment(second_recovery_payment)
    if is_retry():
        offsets = [op for op in ACTIVE.get().data["operations"].values()
                   if op.get("endpoint") == "anor/mdeal/order/offset/offset$post"]
        assert len(offsets) == 1, "Retry faqat ikkinchi installmentni yuborishi kerak"
