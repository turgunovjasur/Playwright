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
    11. Katalogdan "Акция"ni qidirib ulash va Тип цены bo'limiga qaytish.
    12. "Акция" narx turini roomga ulash va tekshirish — aksiya chegirmasi order'da
       ishlashi uchun zarur (room'ga ulanmasa, order'da aksiya chiqmaydi).
    13. Sahifani yopib, Рабочие зоны ro'yxatiga qaytishni tekshirish.

    Qayta-runda available ro'yxatlar bo'sh bo'lsa, tegishli qiymatlar
    "Прикрепленные" gridlarida mavjudligi tekshiriladi.
    """
    base = AutoBasePage(page)
    room_name = f"room-pw{code}"
    client_name = f"natural_client-pw{code}"

    with allure.step("1 - Foydalanuvchi sifatida kirish"):
        authorization(page, who="user", code=code)

    with allure.step("2 - Ish zonalari ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны")

    with allure.step("3 - Ish zonasining biriktirish sahifasini ochish"):
        base.grid(room_name, click=True)
        base.click(name="Прикрепление", exact=True)
        base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")

    with allure.step("4 - To'lov turlarini ulash"):
        _open_detached_section(base, "Типы оплат")
        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить")
            base.wait_for_loader()

        _open_attached_tab(base)
        base.grid("Наличные деньги")
        base.grid("Терминал")
        base.grid("Перечисление")
        base.grid("Чековая книжка")

    with allure.step("5 - Omborni ulash"):
        _open_detached_section(base, "Склады")
        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить")
            base.wait_for_loader()

        _open_attached_tab(base)
        base.grid("Основной склад")

    with allure.step("6 - Kassani ulash"):
        _open_detached_section(base, "Кассы")
        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить")
            base.wait_for_loader()

        _open_attached_tab(base)
        base.grid("Основная касса")

    with allure.step("7 - Mijozni ulash"):
        _open_detached_section(base, "Физические лица")
        if base.grid(client_name, return_bool=True):
            base.grid(client_name, checkbox="row")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить")
            base.wait_for_loader()

        _open_attached_tab(base)
        base.grid(client_name)

    with allure.step("8 - Narx turlari bo'limini ochish"):
        base.click(name="Тип цены", role="tab")
        base.wait_for_loader()
        base.grid_controller(search="Акция")

    price_attached = base.grid("Акция", return_bool=True)
    if not price_attached:
        with allure.step("9 - Mavjud narx turlarini ochish"):
            base.click(name="Доступные", role="tab")
            base.wait_for_loader()

        if not base.grid("Акция", return_bool=True):
            with allure.step("10 - Global narx turlari katalogini ochish"):
                base.click(name="Создать тип цены", exact=True)
                base.expect_page(heading="Цены (прикрепление)")

            with allure.step("11 - 'Акция'ni katalogdan ulab, narx turlariga qaytish"):
                base.grid_controller(search="Акция")
                base.grid("Акция", checkbox="row")
                base.click(name="Прикрепить")
                base.confirm_biruni("Прикрепить")
                base.click(name="Закрыть")
                base.expect_page(url="room_attachment")
                base.click(name="Тип цены", role="tab")
                base.wait_for_loader()
                base.click(name="Доступные", role="tab")
                base.wait_for_loader()

    with allure.step("12 - 'Акция' narx turini roomga ulash va tekshirish"):
        if not price_attached:
            base.grid_controller(search="Акция")
            if base.grid("Акция", return_bool=True):
                base.grid("Акция", checkbox="row")
                base.click(name="Прикрепить")
                base.confirm_biruni("Прикрепить")
                base.wait_for_loader()
            _open_attached_tab(base)
            base.grid_controller(search="Акция")

        base.grid("Акция")

    with allure.step("13 - Sahifani yopib, ish zonalari ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------

def _open_detached_section(base: AutoBasePage, tab_name: str) -> None:
    base.click(name=tab_name, role="tab")
    base.wait_for_loader()
    base.click(name="Доступные", role="tab")
    base.wait_for_loader()


def _open_attached_tab(base: AutoBasePage) -> None:
    base.click(name="Прикрепленные", role="tab")
    base.wait_for_loader()


@allure.title("Ish zonasiga kerakli kataloglarni ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
