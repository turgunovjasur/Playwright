import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

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
    11. Katalogdan "Акция"ni ulab, Тип цены bo'limiga qaytish.
    12. "Акция" narx turini roomga ulash va tekshirish — aksiya chegirmasi order'da
       ishlashi uchun zarur (room'ga ulanmasa, order'da aksiya chiqmaydi).
    13. Sahifani yopib, Рабочие зоны ro'yxatiga qaytishni tekshirish.

    Qayta-runda available ro'yxatlar bo'sh bo'lsa, tegishli qiymatlar
    "Прикрепленные" gridlarida mavjudligi tekshiriladi.
    """
    base = BasePage(page)
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
        base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", root="#kt_content")

    with allure.step("4 - To'lov turlarini ulash"):
        base.click(name="Типы оплат", role="link")
        base.expect_page(heading="Типы оплат", root="b-page")
        base.click(name="Доступные", exact=True)
        base.wait_for_loader()

        payment_grid = 'b-grid[name="table_payment_type"]'
        if not base.grid(state="empty", return_bool=True, root=payment_grid):
            base.grid(checkbox="all", root=payment_grid)
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 4?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", exact=True)
        base.wait_for_loader()

        base.grid("Наличные деньги", root=payment_grid)
        base.grid("Терминал", root=payment_grid)
        base.grid("Перечисление", root=payment_grid)
        base.grid("Чековая книжка", root=payment_grid)

    with allure.step("5 - Omborni ulash"):
        base.click(name="Склады", role="link")
        base.expect_page(heading="Склады", root="b-page")
        base.click(name="Доступные", exact=True)
        base.wait_for_loader()

        warehouse_grid = 'b-grid[name="table_warehouse"]'
        if not base.grid(state="empty", return_bool=True, root=warehouse_grid):
            base.grid(checkbox="all", root=warehouse_grid)
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", exact=True)
        base.wait_for_loader()

        base.grid("Основной склад", root=warehouse_grid)

    with allure.step("6 - Kassani ulash"):
        base.click(name="Кассы", role="link")
        base.expect_page(heading="Кассы", root="b-page")
        base.click(name="Доступные", exact=True)
        base.wait_for_loader()

        cashbox_grid = 'b-grid[name="table_cashbox"]'
        if not base.grid(state="empty", return_bool=True, root=cashbox_grid):
            base.grid(checkbox="all", root=cashbox_grid)
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", exact=True)
        base.wait_for_loader()

        base.grid("Основная касса", root=cashbox_grid)

    with allure.step("7 - Mijozni ulash"):
        base.click(name="Физические лица", role="link")
        base.expect_page(heading="Физические лица", root="b-page")
        base.click(name="Доступные", exact=True)
        base.wait_for_loader()

        if base.grid(client_name, return_bool=True):
            base.grid(client_name, click=True)
            base.click(name="Прикрепить")
            base.confirm_biruni(f"Прикрепить {client_name}?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", exact=True)
        base.wait_for_loader()

        base.grid(client_name)

    with allure.step("8 - Narx turlari bo'limini ochish"):
        base.click(name="Тип цены", role="link")
        base.expect_page(heading="Тип цены", root="b-page")

    price_attached = base.grid("Акция", return_bool=True)
    if not price_attached:
        with allure.step("9 - Mavjud narx turlarini ochish"):
            base.click(name="Доступные", exact=True)
            base.wait_for_loader()

        if not base.grid("Акция", return_bool=True):
            with allure.step("10 - Global narx turlari katalogini ochish"):
                base.click(name="Создать тип цены", exact=True)
                base.expect_page(heading="Цены (прикрепление)")

            with allure.step("11 - 'Акция'ni katalogdan ulab, narx turlariga qaytish"):
                base.grid("Акция", click=True)
                base.click(name="Прикрепить", exact=True)
                base.confirm_biruni("Прикрепить Акция?")
                base.expect_page(heading="Тип цены", root="b-page")

    with allure.step("12 - 'Акция' narx turini roomga ulash va tekshirish"):
        if not price_attached:
            base.grid("Акция", click=True)
            base.click(name="Прикрепить", exact=True)
            base.confirm_biruni("Прикрепить Акция?")
            base.wait_for_loader()

            base.click(name="Прикрепленные", exact=True)
            base.wait_for_loader()

        base.grid("Акция")

    with allure.step("13 - Sahifani yopib, ish zonalari ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasiga kerakli kataloglarni ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
