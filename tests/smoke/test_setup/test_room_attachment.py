import allure

from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def run_room_attachment(page, code):
    """Testcase: oldingi setup testlari yaratgan narsalarni ish zonasiga (room) ulash.

    1. User sifatida kirib, room-pw{code} ning "Прикрепление" sahifasini ochish.
    2. To'lov turlarini (Типы оплат) ulash.
    3. Omborni (Склады) ulash.
    4. Kassani (Кассы) ulash.
    5. Mijozni (Физические лица: natural_client-pw{code}) ulash.
    6. "Акция" narx turini (Тип цены) ulash — bu C-group aksiya chegirmasi order'da
       ishlashi uchun zarur (room'ga ulanmasa, order'da aksiya chiqmaydi).
    7. Sahifani yopib, "Рабочие зоны" ro'yxatiga qaytishni tekshirish.

    Qayta-runda available ro'yxatlar bo'sh bo'lsa, tegishli qiymatlar
    "Прикрепленные" gridlarida mavjudligi tekshiriladi.
    """
    base = BasePage(page)
    room_name = f"room-pw{code}"
    client_name = f"natural_client-pw{code}"

    with allure.step("1 - Foydalanuvchi sifatida kirish va ish zonasini ochish"):
        authorization(page, who="user", code=code)
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны")
        base.grid(room_name, click=True)
        page.get_by_role("button", name="Прикрепление", exact=True).click()
        base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", root="#kt_content")

    with allure.step("2 - To'lov turlarini ulash"):
        page.get_by_role("link", name="Типы оплат").click()
        base.expect_page(heading="Типы оплат", root="b-page")
        page.get_by_role("button", name="Доступные", exact=True).click()
        base.wait_for_loader()

        payment_grid = 'b-grid[name="table_payment_type"]'
        if not base.grid(is_empty=True, root=payment_grid):
            base.grid(checkbox="all", root=payment_grid)
            page.get_by_role("button", name="Прикрепить").click()
            base.confirm_biruni("Прикрепить 4?")
            base.wait_for_loader()

        page.get_by_role("button", name="Прикрепленные", exact=True).click()
        base.wait_for_loader()

        base.grid("Наличные деньги", root=payment_grid)
        base.grid("Терминал", root=payment_grid)
        base.grid("Перечисление", root=payment_grid)
        base.grid("Чековая книжка", root=payment_grid)

    with allure.step("3 - Omborni ulash"):
        page.get_by_role("link", name="Склады").click()
        base.expect_page(heading="Склады", root="b-page")
        page.get_by_role("button", name="Доступные", exact=True).click()
        base.wait_for_loader()

        warehouse_grid = 'b-grid[name="table_warehouse"]'
        if not base.grid(is_empty=True, root=warehouse_grid):
            base.grid(checkbox="all", root=warehouse_grid)
            page.get_by_role("button", name="Прикрепить").click()
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        page.get_by_role("button", name="Прикрепленные", exact=True).click()
        base.wait_for_loader()

        base.grid("Основной склад", root=warehouse_grid)

    with allure.step("4 - Kassani ulash"):
        page.get_by_role("link", name="Кассы").click()
        base.expect_page(heading="Кассы", root="b-page")
        page.get_by_role("button", name="Доступные", exact=True).click()
        base.wait_for_loader()

        cashbox_grid = 'b-grid[name="table_cashbox"]'
        if not base.grid(is_empty=True, root=cashbox_grid):
            base.grid(checkbox="all", root=cashbox_grid)
            page.get_by_role("button", name="Прикрепить").click()
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        page.get_by_role("button", name="Прикрепленные", exact=True).click()
        base.wait_for_loader()

        base.grid("Основная касса", root=cashbox_grid)

    with allure.step("5 - Mijozni ulash"):
        page.get_by_role("link", name="Физические лица").click()
        base.expect_page(heading="Физические лица", root="b-page")
        page.get_by_role("button", name="Доступные", exact=True).click()
        base.wait_for_loader()

        if base.grid(client_name, is_visible=True):
            base.grid(client_name, click=True)
            page.get_by_role("button", name="Прикрепить").click()
            base.confirm_biruni(f"Прикрепить {client_name}?")
            base.wait_for_loader()

        page.get_by_role("button", name="Прикрепленные", exact=True).click()
        base.wait_for_loader()

        base.grid(client_name)

    with allure.step("6 - 'Акция' narx turini ulash (Тип цены tab)"):
        page.get_by_role("link", name="Тип цены").click()
        base.expect_page(heading="Тип цены", root="b-page")

        if not base.grid("Акция", is_visible=True):
            page.get_by_role("button", name="Доступные", exact=True).click()
            base.wait_for_loader()

            if not base.grid("Акция", is_visible=True):
                page.get_by_role("button", name="Создать тип цены", exact=True).click()
                base.expect_page(heading="Цены (прикрепление)")
                base.grid("Акция", click=True)
                page.get_by_role("button", name="Прикрепить", exact=True).click()
                base.confirm_biruni("Прикрепить Акция?")
                base.expect_page(heading="Тип цены", root="b-page")

            base.grid("Акция", click=True)
            page.get_by_role("button", name="Прикрепить", exact=True).click()
            base.confirm_biruni("Прикрепить Акция?")
            base.wait_for_loader()

            page.get_by_role("button", name="Прикрепленные", exact=True).click()
            base.wait_for_loader()

        base.grid("Акция")

    with allure.step("7 - Sahifani yopish"):
        page.get_by_role("button", name="Закрыть", exact=True).click()
        base.expect_page(heading="Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasiga kerakli kataloglarni ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
