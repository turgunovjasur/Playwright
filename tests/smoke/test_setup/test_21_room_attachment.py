import re

import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def run_room_attachment(page, code):
    """Testcase: oldingi setup testlari yaratgan narsalarni ish zonasiga (room) ulash.

    1. User sifatida kirish.
    2. Рабочие зоны ro'yxatini ochish.
    3. room-pw{code} ning Прикрепление sahifasini ochish.
    4. To'lov turlarini (Типы оплат) ulash.
    5. Omborni (Склады) ulash.
    6. Kassani (Кассы) ulash.
    7. Mijozni (Физические лица: natural_client-pw{code}) ulash.
    8. Тип цены bo'limini ochish.
    9. "Акция" available bo'lmasa, Доступные ro'yxatini ochish.
    10. "Акция" katalogda ham bo'lmasa, Цены (прикрепление) sahifasini ochish.
    11. Katalogdan "Акция"ni ulash; katalog ochiq qolsa yopib, Тип цены bo'limiga qaytish.
    12. "Доступные" tabidan "Акция" narx turini roomga ulash va tekshirish — aksiya chegirmasi order'da
       ishlashi uchun zarur (room'ga ulanmasa, order'da aksiya chiqmaydi).
    13. Sahifani yopib, Рабочие зоны ro'yxatiga qaytishni tekshirish.

    Qayta-runda available ro'yxatlar bo'sh bo'lsa, tegishli qiymatlar
    "Прикрепленные" gridlarida mavjudligi tekshiriladi.
    A2 bo'limlari aktiv tab va ko'rinadigan grid orqali, legacy bo'limlari
    esa link va bo'lim sarlavhasi orqali tekshiriladi.
    """
    base = AutoBasePage(page)
    room_name = f"room-pw{code}"
    client_name = f"natural_client-pw{code}"

    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        authorization(page, who="user", code=code)

    with allure.step("2 - Ish zonalari ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны", url="trade/trf/room_list")

    with allure.step("3 - Ish zonasining biriktirish sahifasini ochish"):
        base.grid(room_name, click=True)
        base.click(name="Прикрепление", exact=True)
        base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")

    with allure.step("4 - To'lov turlarini ulash"):
        base.tab(name="Типы оплат", section=True)
        base.tab(name="Доступные")
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 4?")
            base.wait_for_loader()

        base.tab(name="Прикрепленные")
        base.wait_for_loader()

        base.grid("Наличные деньги")
        base.grid("Терминал")
        base.grid("Перечисление")
        base.grid("Чековая книжка")

    with allure.step("5 - Omborni ulash"):
        base.tab(name="Склады", section=True)
        base.tab(name="Доступные")
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.tab(name="Прикрепленные")
        base.wait_for_loader()

        base.grid("Основной склад")

    with allure.step("6 - Kassani ulash"):
        base.tab(name="Кассы", section=True)
        base.tab(name="Доступные")
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.tab(name="Прикрепленные")
        base.wait_for_loader()

        base.grid("Основная касса")

    with allure.step("7 - Mijozni ulash"):
        base.tab(name="Физические лица", section=True)
        base.tab(name="Доступные")
        base.wait_for_loader()

        if base.grid(client_name, return_bool=True):
            base.grid(client_name, click=True)
            base.click(name="Прикрепить")
            base.confirm_biruni(f"Прикрепить {client_name}?")
            base.wait_for_loader()

        base.tab(name="Прикрепленные")
        base.wait_for_loader()

        base.grid(client_name)

    with allure.step("8 - Narx turlari bo'limini ochish"):
        base.tab(name="Тип цены", section=True)

    price_attached = base.grid("Акция", return_bool=True)
    if not price_attached:
        with allure.step("9 - Mavjud narx turlarini ochish"):
            base.tab(name="Доступные")
            base.wait_for_loader()

        if not base.grid("Акция", return_bool=True):
            with allure.step("10 - Global narx turlari katalogini ochish"):
                base.click(name="Создать тип цены", exact=True)
                base.expect_page(heading="Цены (прикрепление)", url=re.compile(r"anor/mkr/price_type_list(?:\+|%2[bB])attach(?:[?#]|$)"))

            with allure.step("11 - 'Акция'ni katalogdan ulab, narx turlariga qaytish"):
                base.grid_controller(search="Акция")
                base.grid("Акция", click=True)
                base.action(name="Прикрепить", menu="Изменить")
                base.confirm_biruni("Прикрепить Акция?")
                base.wait_for_loader()
                if not re.search(r"/room_attachment(?:[?#]|$)", page.url):
                    base.click(name="Закрыть", exact=True)
                base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")
                base.tab(name="Тип цены", section=True)

    with allure.step("12 - 'Акция' narx turini roomga ulash va tekshirish"):
        if not price_attached:
            base.tab(name="Доступные")
            base.wait_for_loader()
            base.grid("Акция", click=True)
            base.click(name="Прикрепить", exact=True)
            base.confirm_biruni("Прикрепить Акция?")
            base.wait_for_loader()

            base.tab(name="Прикрепленные")
            base.wait_for_loader()

        base.grid("Акция")

    with allure.step("13 - Sahifani yopib, ish zonalari ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Рабочие зоны", url="trade/trf/room_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasiga kerakli kataloglarni ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
