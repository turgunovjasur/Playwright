import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization, USER_PASS, user_email_for
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
    """
    base = BasePage(page)
    room_name = f"room-pw{code}"
    client_name = f"natural_client-pw{code}"

    with allure.step("1 - Foydalanuvchi sifatida kirish va ish zonasini ochish"):
        authorization(page, email=user_email_for(code), password=USER_PASS)
        base.navigate_to(tab="Справочники", name="Рабочие зоны")
        base.expect_page(heading="Рабочие зоны")
        base.grid(room_name, click=True)
        page.get_by_role("button", name="Прикрепление").click()
        expect(page.locator("#kt_content")).to_contain_text(f"Рабочая зона (прикрепление): {room_name}")

    with allure.step("2 - To'lov turlarini ulash"):
        page.get_by_role("link", name="Типы оплат").click()
        expect(page.locator("b-page")).to_contain_text("Типы оплат")
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        expect(page.locator('b-grid[name="table_payment_type"]')).to_be_visible()
        base.checkbox(check_all=True, grid_name="table_payment_type", checked=True)
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni("Прикрепить 4?")
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("3 - Skladni ulash"):
        page.get_by_role("link", name="Склады").click()
        expect(page.locator("b-page")).to_contain_text("Склады")
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        expect(page.locator('b-grid[name="table_warehouse"]')).to_be_visible()
        base.checkbox(check_all=True, grid_name="table_warehouse", checked=True)
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni("Прикрепить 1?")
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("4 - Kassani ulash"):
        page.get_by_role("link", name="Кассы").click()
        expect(page.locator("b-page")).to_contain_text("Кассы")
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        expect(page.locator('b-grid[name="table_cashbox"]')).to_be_visible()
        base.checkbox(check_all=True, grid_name="table_cashbox", checked=True)
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni("Прикрепить 1?")
        expect(page.locator("b-page")).to_contain_text("нет данных")

    with allure.step("5 - Mijozni ulash"):
        page.get_by_role("link", name="Физические лица").click()
        expect(page.locator("b-page")).to_contain_text("Физические лица")
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        base.grid(client_name, click=True)
        page.get_by_role("button", name="Прикрепить").click()
        base.confirm_biruni(f"Прикрепить {client_name}?")
        page.get_by_role("button", name="Прикрепленные").click()
        expect(page.locator("b-page")).to_contain_text(client_name)

    with allure.step("6 - 'Акция' narx turini ulash (Тип цены tab)"):
        # "Акция" narx turi C-group aksiya chegirmasi orderda ishlashi uchun room'ga ulanadi.
        # Ulanish 2 bosqichli: avval "Создать тип цены" orqali "Доступные" ro'yxatiga qo'shiladi,
        # so'ng "Доступные"da belgilab "Прикрепить" qilinadi (MCP bilan 2026-06-16 tasdiqlangan).
        page.get_by_role("link", name="Тип цены").click()
        expect(page.locator("b-page")).to_contain_text("Тип цены")

        # 1) Katalogdan "Акция"ni room "Доступные" ro'yxatiga qo'shish
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        page.get_by_role("button", name="Создать тип цены").click()
        base.expect_page(heading="Цены (прикрепление)")
        base.wait_for_loader()
        page.get_by_text("Акция", exact=True).first.click()
        page.get_by_role("button", name="Прикрепить", exact=True).click()
        base.confirm_biruni("Прикрепить Акция?")
        base.wait_for_loader()

        # 2) "Доступные"da "Акция"ni belgilab "Прикрепить" -> "Прикрепленные"ga o'tadi
        page.get_by_role("link", name="Тип цены").click()
        page.get_by_role("button", name="Доступные").click()
        base.wait_for_loader()
        page.get_by_text("Акция", exact=True).first.click()
        page.get_by_role("button", name="Прикрепить", exact=True).click()
        base.confirm_biruni("Прикрепить Акция?")
        base.wait_for_loader()

        page.get_by_role("button", name="Прикрепленные").click()
        base.wait_for_loader()
        expect(page.locator("b-page")).to_contain_text("Акция")

    with allure.step("7 - Sahifani yopish"):
        page.get_by_role("button", name="Закрыть").click()
        base.expect_page(heading="Рабочие зоны")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Ish zonasiga to'lov, sklad, kassa va mijoz ulash")
def test_room_attachment(page, code):
    run_room_attachment(page, code)
