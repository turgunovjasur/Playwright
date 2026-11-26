"""SCN-001 · Order statuslari. To‘rtta tayyorlovdan keyin bir buyurtma arxivgacha tekshiriladi."""
from dataclasses import dataclass
from decimal import Decimal

import allure
import pytest

from tests.regression.helpers.retry.checkpoints import decimal_map, reuse, value as retry_value, verified
from tests.regression.test_orders.groups import GROUP_FEATURES
from tests.regression.test_orders.helpers.discounts import open_discount_goods, save_discount_draft
from tests.regression.test_orders.helpers.flows.order import existing_order, open_order_summary
from tests.regression.test_orders.helpers.flows.settlement import change_order_status, read_debts, read_settlement
from tests.regression.test_orders.helpers.flows.stock import read_stock
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.reporting import order_report_case
from tests.regression.test_orders.setup_cases.catalog_stock import (
    run_prepare_catalog, run_prepare_prices, run_prepare_stock,
)
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [
    pytest.mark.regression, pytest.mark.order_positive, pytest.mark.order_group("statuses"),
    allure.epic("Regression"), allure.feature(GROUP_FEATURES["statuses"]),
]


@dataclass(frozen=True, kw_only=True)
class ExpectedStatus:
    name: str
    shipped: int = 0
    reserved: int = 0
    open_amount: int = 0
    debt: int = 0


STATUS_CYCLE = (
    ExpectedStatus(name="Черновик"),
    ExpectedStatus(name="Новый", reserved=2, open_amount=14000),
    ExpectedStatus(name="В обработке", reserved=2, open_amount=14000),
    ExpectedStatus(name="В ожидании", reserved=2, open_amount=14000),
    ExpectedStatus(name="Отгружен", shipped=2, open_amount=14000),
    ExpectedStatus(name="Доставлен", shipped=2, open_amount=14000),
    ExpectedStatus(name="Архив", shipped=2, debt=14000),
)
ZERO_SETTLEMENT = dict.fromkeys(("debt", "prepayment", "open_order", "booked_prepayment", "balance"), Decimal(0))


# Tayyorlov
@order_report_case
@pytest.mark.order_requires()
def test_000_catalog(business_baseline, catalog_data, regression_case_dir):
    """API orqali guruh mahsulotini kodi bilan topish yoki yaratish va faol holatini tekshirish."""
    run_prepare_catalog(business_baseline, catalog_data, regression_case_dir, "statuses")


@order_report_case
@pytest.mark.order_requires('test_000_catalog')
def test_001_prices(business_baseline, catalog_data, regression_case_dir):
    """API orqali shu mahsulot narxini 7 000 so‘mga tayyorlash va tekshirish."""
    run_prepare_prices(business_baseline, catalog_data, regression_case_dir, "statuses")


@order_report_case
@pytest.mark.order_requires('test_001_prices')
def test_002_stock(catalog_order, catalog_data, regression_case_dir):
    """2 dona kirimni API orqali tayyorlash va brauzerda ombor qoldig‘ini tekshirish."""
    run_prepare_stock(catalog_order, catalog_data, regression_case_dir, "statuses")


@order_report_case
@pytest.mark.order_requires()
def test_00_prepare_client(business_baseline, workflow_data, regression_case_dir):
    """Faol mijozni API orqali yaratish va ish zonasiga biriktirish."""
    workflow_data["client"] = prepare_order_client(
        business_baseline, purpose="statuses", kind="cycle", directory=regression_case_dir,
    )


# Biznes testi
@order_report_case
@pytest.mark.order_requires('test_002_stock', 'test_00_prepare_client')
def test_01_status_cycle(workflow_order):
    """Bir buyurtmada rezerv, jo‘natish va arxivdagi qarzni har statusda tekshirish."""
    case = workflow_order
    before = _initial_stock(case)
    order_id = _get_or_create_draft(case)

    current = "Черновик"
    for expected in STATUS_CYCLE:
        checkpoint = "status_verified:" + expected.name
        if expected.name != "Архив" and reuse(checkpoint):
            current = expected.name
            continue
        if current != expected.name:
            change_order_status(case.page, order_id, current=current, target=expected.name)
        with allure.step(f"{expected.name}: saqlangan order, summa, rezerv, fizik qoldiq va qarz"):
            _check_order_and_balances(case, order_id, before, expected)
            verified(checkpoint)
        current = expected.name


def _initial_stock(case):
    """Retry oldingi urinishdan avvalgi qoldiq bilan solishtiradi."""
    with allure.step("Status testi klientining balansi va boshlang‘ich ombor qoldig‘i"):
        retained = retry_value("status_initial_stock")
        if retained is not None:
            return decimal_map(retained)
        case.check("Yangi klientning boshlang‘ich saldosi", ZERO_SETTLEMENT, read_settlement(case.page, case.client))
        before = read_stock(case, "Основной склад")
        case.check("Ikki dona uchun erkin qoldiq yetarli", True, before["available"] >= 2)
        retry_value("status_initial_stock", before)
        return before


def _get_or_create_draft(case):
    order_id = existing_order(case)
    if order_id:
        case.remember_order(order_id)
        return order_id
    with allure.step("Ikki dona mahsulotdan 14 000 so‘mlik qoralama yaratish"):
        open_discount_goods(case, 2)
        open_order_summary(case.page, expected_total=14000)
        AutoBasePage(case.page).input(label="Сумма скидки/наценки", expect_value="0")
        return save_discount_draft(case, 14000)


def _check_order_and_balances(case, order_id, before, expected):
    page = case.page
    base = AutoBasePage(page)
    base.form_view(label="ИД заказа", expect_value=order_id)
    case.check("Saqlangan status", expected.name, base.form_view(label="Статус", return_value=True))
    total = base.form_view(label="Сумма заказа", return_value=True, remove_spaces=True)
    case.check("Status almashganda summa saqlanadi", "14000", total)

    stock = {
        "physical": before["physical"] - expected.shipped,
        "booked": before["booked"] + expected.reserved,
        "available": before["available"] - expected.shipped - expected.reserved,
    }
    case.check(f"{expected.name}: ombor qoldig‘i va rezerv", stock, read_stock(case, "Основной склад"))
    balance = {
        **ZERO_SETTLEMENT,
        "open_order": Decimal(expected.open_amount),
        "debt": Decimal(expected.debt),
        "balance": -Decimal(expected.open_amount + expected.debt),
    }
    actual = read_settlement(page, case.client)
    case.check(f"{expected.name}: klient saldosi", balance, actual)
    if expected.name == "Архив":
        case.check("Arxivdan keyin aynan shu orderning qarzi", {order_id: Decimal(expected.debt)},
                   read_debts(page, case.client, settlement=actual))
