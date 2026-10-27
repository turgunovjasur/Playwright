"""Asosiy pytest runner: setup, mahsulotlar va mustaqil Order ssenariylari.

PyCharm'da faylni pytest bilan Run qilish mumkin. Alohida runnerlardagi
testlar qayta ishlatiladi: fixture, parametr va Allure title'lari saqlanadi.
Har case alohida pytest item; ichma-ich pytest yoki subprocess run yo'q.
"""

from tests.regression.test_setup import test_0_setup_runner as setup_runner
from tests.regression.test_products import test_0_products_runner as products_runner
from tests.regression.test_orders import test_0_orders_runner as orders_runner


class Test01Setup:
    """Bazaviy setup; alohida setup runnerining marker va testlari."""

    pytestmark = setup_runner.pytestmark

    test_00_company = staticmethod(setup_runner.test_00_company)
    test_01_legal_person = staticmethod(setup_runner.test_01_legal_person)
    test_02_filial = staticmethod(setup_runner.test_02_filial)
    test_03_room = staticmethod(setup_runner.test_03_room)
    test_04_robot = staticmethod(setup_runner.test_04_robot)
    test_05_natural_person = staticmethod(setup_runner.test_05_natural_person)
    test_06_user = staticmethod(setup_runner.test_06_user)
    test_07_user_attach_form = staticmethod(setup_runner.test_07_user_attach_form)
    test_08_role = staticmethod(setup_runner.test_08_role)
    test_09_role_attach_form = staticmethod(setup_runner.test_09_role_attach_form)
    test_10_buy_license = staticmethod(setup_runner.test_10_buy_license)
    test_11_attach_license = staticmethod(setup_runner.test_11_attach_license)
    test_12_change_password = staticmethod(setup_runner.test_12_change_password)
    test_13_price_type_uzb = staticmethod(setup_runner.test_13_price_type_uzb)
    test_14_price_type_usa = staticmethod(setup_runner.test_14_price_type_usa)
    test_15_currency = staticmethod(setup_runner.test_15_currency)
    test_16_payment_type = staticmethod(setup_runner.test_16_payment_type)
    test_17_sector = staticmethod(setup_runner.test_17_sector)
    test_18_natural_person_for_client = staticmethod(setup_runner.test_18_natural_person_for_client)
    test_19_room_attachment = staticmethod(setup_runner.test_19_room_attachment)
    test_20_warehouse = staticmethod(setup_runner.test_20_warehouse)


class Test02Products:
    """Setupdan keyingi ТМЦ caselari, original parametrlar bilan."""

    pytestmark = products_runner.pytestmark

    test_01_tmz_1 = staticmethod(products_runner.test_01_tmz_1)
    test_02_import_tmz = staticmethod(products_runner.test_02_import_tmz)


# Class aliaslari Order runnerdagi fixture, title va story markerlarini saqlaydi.
# Tartib report uchun; Order case'lari products case'lari natijasini ishlatmaydi.
Test03OrderEditing = orders_runner.Test01OrderEditing
Test04ProductSelection = orders_runner.Test02ProductSelection
Test05OrderStatuses = orders_runner.Test03OrderStatuses
Test06Promotions = orders_runner.Test04Promotions
Test07SettlementAndReports = orders_runner.Test05SettlementAndReports
