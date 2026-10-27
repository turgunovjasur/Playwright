"""Order regression: besh ssenariy, har testcase alohida pytest item.

Runner faqat leaf funksiyalarni yig'adi. Case'lar faqat setup baseline'ga
bog'liq; har biri function-scoped order_case orqali o'z ma'lumotini yaratadi.
Bir case xatosi keyingi mustaqil caselarni skip qilmaydi.
"""

import allure
import pytest

from tests.regression.test_orders.test_01_create_edit_order import run_create_edit_order
from tests.regression.test_orders.test_02_copy_discard_order import run_copy_discard_order
from tests.regression.test_orders.test_03_order_validations import run_order_validations
from tests.regression.test_orders.test_04_discount_calculation import run_discount_calculation
from tests.regression.test_orders.test_05_podbor import run_podbor
from tests.regression.test_orders.test_06_import_valid import run_import_valid
from tests.regression.test_orders.test_07_import_invalid import run_import_invalid
from tests.regression.test_orders.test_08_import_duplicates_range import run_import_duplicates_range
from tests.regression.test_orders.test_09_status_cycle import run_status_cycle
from tests.regression.test_orders.test_10_cancel_restore import run_cancel_restore
from tests.regression.test_orders.test_11_archive_restore import run_archive_restore
from tests.regression.test_orders.test_12_quantity_promotion import run_quantity_promotion
from tests.regression.test_orders.test_13_amount_promotion import run_amount_promotion
from tests.regression.test_orders.test_14_cyclic_promotion import run_cyclic_promotion
from tests.regression.test_orders.test_15_payment_roundtrip import run_payment_roundtrip
from tests.regression.test_orders.test_16_return_roundtrip import run_return_roundtrip
from tests.regression.test_orders.test_17_invoice_consistency import run_invoice_consistency

pytestmark = [
    pytest.mark.regression,
    pytest.mark.regression_requires_setup,
    allure.epic("Regression"),
    allure.feature("Order"),
]


class Test01OrderEditing:
    """Ssenariy: order yaratish, tahrirlash, nusxalash va hisoblash."""

    pytestmark = [*pytestmark, allure.story("Order yaratish va tahrirlash")]

    @allure.title("ORD-01: Draft yaratish, tahrirlash va qayta ochish")
    def test_01_create_edit_order(self, page, order_case):
        run_create_edit_order(page, order_case)

    @allure.title("ORD-02: Order nusxasi va saqlanmagan o'zgarishlarni tashlash")
    def test_02_copy_discard_order(self, page, order_case):
        run_copy_discard_order(page, order_case)

    @allure.title("ORD-03: Bo'sh order va noto'g'ri miqdor validatsiyalari")
    def test_03_order_validations(self, page, order_case):
        run_order_validations(page, order_case)

    @allure.title("ORD-04: Per-unit satr chegirmasi va bir martalik hujjat chegirmasi")
    def test_04_discount_calculation(self, page, order_case):
        run_discount_calculation(page, order_case)


class Test02ProductSelection:
    """Ssenariy: podbor va Excel orqali mahsulotlarni orderga o'tkazish."""

    pytestmark = [*pytestmark, allure.story("Podbor va Excel import")]

    @allure.title("ORD-05: Podbor qo'shish, olib tashlash va orderga o'tkazish")
    def test_05_podbor(self, page, order_case):
        run_podbor(page, order_case)

    @allure.title("ORD-06: Valid Excel import va saqlangan order")
    def test_06_import_valid(self, page, order_case):
        run_import_valid(page, order_case)

    @allure.title("ORD-07: Bo'sh fayl, noma'lum mahsulot va manfiy import miqdori")
    def test_07_import_invalid(self, page, order_case):
        run_import_invalid(page, order_case)

    @allure.title("ORD-08: Importdagi takroriy mahsulot va qator oralig'i")
    @pytest.mark.parametrize("ending_row,expected_quantities,expected_total", [pytest.param("", ("1", "2"), "300", id="duplicate_rows"), pytest.param("1", ("1",), "100", id="first_row_only")])
    def test_08_import_duplicates_range(self, page, order_case, ending_row, expected_quantities, expected_total):
        run_import_duplicates_range(page, order_case, ending_row, expected_quantities, expected_total)


class Test03OrderStatuses:
    """Ssenariy: statuslar va ularning qoldiq hamda qarzga ta'siri."""

    pytestmark = [*pytestmark, allure.story("Order statuslari")]

    @allure.title("ORD-09: Draftdan Deliveredgacha status, qoldiq va ochiq buyurtma")
    def test_09_status_cycle(self, page, order_case):
        run_status_cycle(page, order_case)

    @allure.title("ORD-10: Cancel va Restore rezervni bir marta qaytaradi")
    def test_10_cancel_restore(self, page, order_case):
        run_cancel_restore(page, order_case)

    @allure.title("ORD-11: Archive va Restore qarz hamda statusni qaytaradi")
    def test_11_archive_restore(self, page, order_case):
        run_archive_restore(page, order_case)


class Test04Promotions:
    """Ssenariy: har case o'z aksiyasini yaratib chegara qiymatlarini tekshiradi."""

    pytestmark = [*pytestmark, allure.story("Order aksiyalari")]

    @allure.title("ORD-12: Miqdor aksiyasi va optional bonus chegaralari")
    def test_12_quantity_promotion(self, page, order_case):
        run_quantity_promotion(page, order_case)

    @allure.title("ORD-13: Summa aksiyasi va chegirma chegaralari")
    def test_13_amount_promotion(self, page, order_case):
        run_amount_promotion(page, order_case)

    @allure.title("ORD-14: Siklik bonus, rezerv va bekor qilish")
    def test_14_cyclic_promotion(self, page, order_case):
        run_cyclic_promotion(page, order_case)


class Test05SettlementAndReports:
    """Ssenariy: order to'lovi, qaytarish va invoice izchilligi."""

    pytestmark = [*pytestmark, allure.story("To'lov, qaytarish va report")]

    @allure.title("ORD-15: To'lov, exact orderga ajratish va bekor qilish")
    def test_15_payment_roundtrip(self, page, order_case):
        run_payment_roundtrip(page, order_case)

    @allure.title("ORD-16: Orderdan Return, Archive va qaytarishni bekor qilish")
    def test_16_return_roundtrip(self, page, order_case):
        run_return_roundtrip(page, order_case)

    @allure.title("ORD-17: Invoice va saqlangan order summalari izchilligi")
    def test_17_invoice_consistency(self, page, order_case):
        run_invoice_consistency(page, order_case)
