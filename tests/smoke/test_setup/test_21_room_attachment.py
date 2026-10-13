import re

import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Room")]

# ----------------------------------------------------------------------------------------------------------------------

def _open_attachment_section(page, name):
    """Room attachment bo'limini ochib, legacy heading yoki A2 aktiv tabni tekshiradi."""
    base = AutoBasePage(page)
    if "/a2/" in page.url:
        tab = base.click(name=name, role="tab", exact=True)
        expect(tab.locator("button")).to_have_class(re.compile(r"\bborder-b-brand-600\b"))
        base.wait_for_loader()
    else:
        base.click(name=name, role="link")
        base.expect_page(heading=name, root="b-page")

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
    11. Katalogdan "Акция"ni ulash; A2 katalogini yopib, Тип цены bo'limiga qaytish.
    12. "Акция" narx turini roomga ulash va tekshirish — aksiya chegirmasi order'da
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
        base.expect_page(heading="Рабочие зоны")

    with allure.step("3 - Ish zonasining biriktirish sahifasini ochish"):
        base.grid(room_name, click=True)
        base.click(name="Прикрепление", exact=True)
        base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")

    state_tab_role = "tab" if "/a2/" in page.url else "button"

    with allure.step("4 - To'lov turlarini ulash"):
        _open_attachment_section(page, "Типы оплат")
        base.click(name="Доступные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 4?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        base.grid("Наличные деньги")
        base.grid("Терминал")
        base.grid("Перечисление")
        base.grid("Чековая книжка")

    with allure.step("5 - Omborni ulash"):
        _open_attachment_section(page, "Склады")
        base.click(name="Доступные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        base.grid("Основной склад")

    with allure.step("6 - Kassani ulash"):
        _open_attachment_section(page, "Кассы")
        base.click(name="Доступные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        if not base.grid(state="empty", return_bool=True):
            base.grid(checkbox="all")
            base.click(name="Прикрепить")
            base.confirm_biruni("Прикрепить 1?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        base.grid("Основная касса")

    with allure.step("7 - Mijozni ulash"):
        _open_attachment_section(page, "Физические лица")
        base.click(name="Доступные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        if base.grid(client_name, return_bool=True):
            base.grid(client_name, click=True)
            base.click(name="Прикрепить")
            base.confirm_biruni(f"Прикрепить {client_name}?")
            base.wait_for_loader()

        base.click(name="Прикрепленные", role=state_tab_role, exact=True)
        base.wait_for_loader()

        base.grid(client_name)

    with allure.step("8 - Narx turlari bo'limini ochish"):
        _open_attachment_section(page, "Тип цены")

    price_attached = base.grid("Акция", return_bool=True)
    if not price_attached:
        with allure.step("9 - Mavjud narx turlarini ochish"):
            base.click(name="Доступные", role=state_tab_role, exact=True)
            base.wait_for_loader()

        if not base.grid("Акция", return_bool=True):
            with allure.step("10 - Global narx turlari katalogini ochish"):
                base.click(name="Создать тип цены", exact=True)
                base.expect_page(heading="Цены (прикрепление)")

            with allure.step("11 - 'Акция'ni katalogdan ulab, narx turlariga qaytish"):
                base.grid_controller(search="Акция")
                base.grid("Акция", click=True)
                if "/a2/" in page.url:
                    price_actions = page.locator("smt-dropdown-button").filter(
                        has=page.get_by_role("button", name="Изменить", exact=True)
                    )
                    base.click(locator=price_actions.locator('button[aria-haspopup="menu"]'))
                    base.click(name="Прикрепить", role="menuitem", exact=True)
                else:
                    base.click(name="Прикрепить", exact=True)
                base.confirm_biruni("Прикрепить Акция?")
                if "/a2/" in page.url:
                    base.wait_for_loader()
                    base.click(name="Закрыть", exact=True)
                base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")
                _open_attachment_section(page, "Тип цены")

    with allure.step("12 - 'Акция' narx turini roomga ulash va tekshirish"):
        if not price_attached:
            base.grid("Акция", click=True)
            base.click(name="Прикрепить", exact=True)
            base.confirm_biruni("Прикрепить Акция?")
            base.wait_for_loader()

            base.click(name="Прикрепленные", role=state_tab_role, exact=True)
            base.wait_for_loader()

        base.grid("Акция")

    with allure.step("13 - Sahifani yopib, ish zonalari ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasiga kerakli kataloglarni ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
