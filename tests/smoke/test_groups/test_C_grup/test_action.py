import re

import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_order.flow_order_add import (
    auto_filled_order_dates,
    flow_order_final_page,
    flow_order_product_page,
)
from tests.smoke.flows.flow_order.flow_order_list import flow_open_order_list, flow_order_list
from utils.base_page import BasePage

pytestmark = [allure.epic("C Group"), allure.feature("Marketing"), allure.story("Action")]


# ----------------------------------------------------------------------------------------------------------------------

def run_c_group_create_action(page, code, login=True):
    """C-01: 10 dona olinganda 10% chegirma beruvchi aksiya yaratish.

    Qadamlar:
      1. Справочники -> Маркетинг -> Акции ro'yxatiga o'tish
      2. Создать -> asosiy maydonlar: nom, рабочие зоны, бонусный склад (Тип акции = Кол-во)
      3. Далее -> Условие: shart producti = product-pw{code}, Мин. значение = 10
      4. Бонус: Тип бонуса = Скидка, product Значение(%) = 10
      5. Завершить -> "Сохранить?" tasdiqlash
      6. Ro'yxatda yaratilgan aksiya va "Активный" statusi tekshiriladi
    """
    base = BasePage(page)
    action_name = f"Скидка 10% на 10 товаров pw{code}"

    if login:
        authorization(page, who="user", code=code)

    with allure.step("1 - Aksiyalar ro'yxatiga o'tish"):
        base.navigate_to(tab="Справочники", name="Акции")
        base.expect_page(heading="Акции")

    with allure.step("2 - Yangi aksiya formasi: asosiy maydonlar"):
        page.get_by_role("button", name="Создать").click()
        # Aksiya formasi wizard — bir nechta ko'rinadigan heading bor (Главное, Условия),
        # shuning uchun forma sarlavhasi aniq nom bilan nishonlanadi.
        expect(page.get_by_role("heading", name="Акция (создание)")).to_be_visible()

        page.locator("#anor718-input-text-name").get_by_role("textbox").fill(action_name)

        rooms = page.locator("#anor718-input-b_input-rooms")
        rooms.get_by_role("textbox", name="Поиск").click()
        page.get_by_text(f"room-pw{code}", exact=True).click()

        warehouse = page.locator("#anor718-input-b_input-bonus_warehouse")
        warehouse.get_by_role("textbox", name="Поиск").click()
        page.get_by_text("Основной склад", exact=True).click()

        # Тип акции = Кол-во (default qoldiriladi)
        page.get_by_role("button", name="Далее").click()
        expect(page.get_by_role("heading", name="Условия")).to_be_visible()

    with allure.step("3 - Условие: shart producti product-pw{code} va Мин. значение = 10"):
        # MUHIM: aksiya orderда ishlashi uchun Условие (shart) productini "Все ТМЦ" holatida
        # qoldirmasdan, aniq product-pw{code} qilib tanlash SHART. Aks holda orderdagi "Акции"
        # tabida "Тип цены акции не прикреплен..." xatosi chiqib, chegirma qo'llanmaydi
        # (MCP bilan 2026-06-16 da tasdiqlangan).
        rule_search = page.locator("#rule_products").get_by_role("textbox", name="Поиск")
        rule_search.click()
        rule_search.fill(f"product-pw{code}")
        page.locator("#rule_products").get_by_text(f"product-pw{code}", exact=True).first.click()
        expect(page.locator("#rule_products")).to_contain_text(f"product-pw{code}")
        page.locator('input[ng-model="rule.main_value"]').fill("10")

    with allure.step("4 - Бонус: Скидка turi, productga 10% chegirma"):
        page.locator('[ng-model="bonus.bonus_kind"]').click()
        page.get_by_role("option", name="Скидка", exact=True).click()

        bonus_search = page.locator("#bonus_products").get_by_role("textbox", name="Поиск")
        bonus_search.click()
        bonus_search.fill(f"product-pw{code}")
        page.locator("#bonus_products").get_by_text(f"product-pw{code}", exact=True).first.click()

        page.locator('input[ng-model="product.value"]').fill("10")

    with allure.step("5 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Завершить", exact=True).first.click()
        base.confirm_biruni("Сохранить?")
        base.wait_for_loader()
        base.expect_page(heading="Акции")
        page.get_by_role("searchbox", name="Поиск").fill(action_name)
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        row = page.locator("b-grid .tbl-row").filter(has_text=action_name).first
        expect(row).to_be_visible()
        expect(row).to_contain_text("Активный")


# ----------------------------------------------------------------------------------------------------------------------

def run_c_group_order_action_discount(page, code, login=True):
    """C-02: C-01 da yaratilgan aksiya orderda product tanlanganda ishlashini tekshirish.

    Old shart: setup'da room-pw{code} ga "Акция" narx turi prikrep qilingan va C-01 aksiyasi
    (shart producti product-pw{code}, 10 dona -> 10% skidka) yaratilgan bo'lishi kerak.

    Qadamlar:
      1. User sifatida kirish.
      2. Order yaratish: product-pw{code} x 10 (aksiya sharti = 10 dona).
      3. "Акции" tabida aksiya ko'rinishini tekshirib, "Получить" bonusni yoqish.
      4. "Товар" tabida Сумма скидки/наценки = -7 000 va ИТОГО = 63 000 (70 000 dan 10% skidka).
      5. Final sahifada chegirma va ИТОГО 63 000 ni tekshirib, status Новый bilan saqlash.
      6. View oynasida client, product, chegirma (-7 000) va 63 000 ni tekshirish.
    """
    base = BasePage(page)
    product = f"product-pw{code}"
    action_name = f"Скидка 10% на 10 товаров pw{code}"
    discount = re.compile(r"-\s*7\s*000")
    total_with_discount = re.compile(r"63\s*000")

    if login:
        with allure.step("1 - User tizimga kiradi"):
            authorization(page, who="user", code=code)
            expect(page.get_by_role("heading", name="Trade")).to_be_visible()

    with allure.step("2 - Order yaratish: main page (room/robot/client) va product x 10"):
        flow_open_order_list(page)
        flow_order_list(page, add=True)
        page.wait_for_url(re.compile(r".*/order\+add"))
        auto_filled_order_dates(page)
        # room/robot/client odatda auto-fill bo'ladi, lekin bu flaky — room'ni kafolatli tanlaymiz
        # (room tanlangach robot va client avtomatik to'ladi).
        room_input = page.locator("#anor279-input-b_input-room_name")
        room_search = room_input.get_by_role("textbox", name="Поиск")
        if (room_search.input_value() or "").strip() != f"room-pw{code}":
            room_search.click()
            room_search.fill(f"room-pw{code}")
            room_input.get_by_text(f"room-pw{code}", exact=True).first.click()
        expect(room_search).to_have_value(f"room-pw{code}")
        expect(page.locator("#anor279-input-b_input-robot_name").get_by_role("textbox", name="Поиск")).to_have_value(f"robot-pw{code}")
        expect(page.locator("#anor279-input-b_input-person_name").get_by_role("textbox", name="Поиск")).to_have_value(f"natural_client-pw{code}")
        page.get_by_role("button", name="Далее").click()
        flow_order_product_page(page, product=product, quantity="10", next_page=False)

    with allure.step("3 - 'Акции' tabida aksiyani yoqish (Получить bonus)"):
        # 'Акции' tab order kontentida (#kt_content) bo'ladi; yuqori menyu 'Акции' #kt_header da.
        page.locator("#kt_content").get_by_role("link", name="Акции").first.click()
        expect(page.locator("#kt_content")).to_contain_text(action_name)
        # 'Получить' toggle styled switch bilan yopilgan (oddiy/force click DOM checkboxni
        # bosmaydi). Native DOM .click() ishonchli toggle qiladi va ng-change orqali chegirma
        # qayta hisoblanadi (MCP bilan 2026-06-16 tasdiqlangan).
        get_toggle = page.locator('input[ng-model="condition.get"]').first
        page.evaluate(
            """() => {
                const cb = document.querySelector('input[ng-model="condition.get"]');
                if (cb && !cb.checked) cb.click();
            }"""
        )
        expect(get_toggle).to_be_checked()
        base.wait_for_loader()

    with allure.step("4 - 'Товар' tabida chegirma qo'llanganini tekshirish"):
        page.locator("#kt_content").get_by_role("link", name="Товар", exact=True).click()
        expect(page.locator("#kt_content")).to_contain_text(discount)
        expect(page.locator("#kt_content")).to_contain_text(total_with_discount)
        page.get_by_role("button", name="Далее").click()

    with allure.step("5 - Final sahifada chegirma va ИТОГО 63 000 ni tekshirib saqlash"):
        expect(page.locator("#kt_content")).to_contain_text(discount)
        expect(page.locator("#kt_content")).to_contain_text(total_with_discount)
        flow_order_final_page(page, status="Новый", save=True)
        expect(page).to_have_url(re.compile(r".*/order_list"))

    with allure.step("6 - View oynasida chegirma tekshiriladi"):
        row = page.locator("b-grid .tbl-row").filter(has_text=f"natural_client-pw{code}").first
        expect(row).to_be_visible()
        if "open" not in (row.get_attribute("class") or "").split():
            row.click()
        expect(row.locator(".tbl-row-menu")).to_be_visible()
        # Order view tugmasi UI versiyasiga qarab "Просмотр" yoki "Просмотреть" bo'lishi mumkin.
        row.get_by_role("button", name=re.compile(r"Просмотр")).first.click()
        expect(page).to_have_url(re.compile(r".*/order_view"))
        base.wait_for_loader()
        expect(page.locator("#kt_content")).to_contain_text(f"natural_client-pw{code}")
        expect(page.locator("#kt_content")).to_contain_text(product)
        expect(page.locator("#kt_content")).to_contain_text(discount)
        expect(page.locator("#kt_content")).to_contain_text(total_with_discount)
        page.get_by_role("button", name="Закрыть").click()
        expect(page).to_have_url(re.compile(r".*/order_list"))
