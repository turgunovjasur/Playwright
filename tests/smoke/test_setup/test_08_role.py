import re

import allure
from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("User")]

ROLE_PERMISSIONS = (
    "Заказ",
    "Предоплата",
    "Возврат",
    "Доставка",
    "Отслеживание пользователя",
    "Поступление на склад",
    "Внутреннее перемещение (отправка)",
    "Внутреннее перемещение (прием)",
    "Отгрузка и возврат маркированных товаров",
    "Ввод начальных остатков",
    "Списание",
    "Дезагрегация",
    "Инвентаризация",
    "Двойной визит",
    "Категоризация",
    "Закупка",
    "Списание при закупке",
    "Заявки на оборудование",
    "Управление заявками на оборудование",
    "Заявка на ремонт оборудования",
    "Управление заявками на ремонт оборудования",
    "Дезагрегация в автотранспорте",
    "Производственное задание",
    "Обмен ТМЦ",
    "Создание заявки на денежный поток",
    "Подписание заявки на денежный поток",
    "Согласование консигнации",
    "Внутренняя агрегация",
    "Согласование промо",
    "Визит",
    "Визит менеджера",
    "Звонки",
)

# ----------------------------------------------------------------------------------------------------------------------

def run_role(page):
    """Testcase: Admin roliga barcha ruxsatlarni (switchlarni) yoqish.

    1. Пользователи ro'yxatini ochish.
    2. Роли ro'yxatini ochish.
    3. "Админ" rolining edit formasini ochish.
    4. Barcha "нет" switchlarini ketma-ket yoqish.
    5. Saqlab, Роли ro'yxatiga qaytishni tekshirish.
    6. Edit formasini qayta ochib, barcha ruxsatlar saqlanganini tekshirish.
    7. Formani yopib, Роли ro'yxatiga qaytish.
    """
    base = AutoBasePage(page)
    with allure.step("1 - Foydalanuvchilar ro'yxatini ochish"):
        base.navigate_to(tab="Главное", name="Пользователи")
        base.expect_page(heading="Пользователи", url="anor/mr/user_list")

    with allure.step("2 - Rollar ro'yxatini ochish"):
        base.click(name="Роли", role="link")
        base.expect_page(heading="Роли", url="trade/tr/role_list")

    with allure.step("3 - Admin rolining edit formasini ochish"):
        base.grid("Админ", click=True)
        base.click(name="Изменить")
        base.expect_page(heading="Роль (изменение)", url=re.compile(r"/role(?:\+|%2[bB])edit(?:[?#]|$)"))

    with allure.step("4 - Barcha ruxsat switchlarini yoqish"):
        base.hide_ui("#onboarding-launcher, .b24-widget-button-popup, .b24-widget-button-popup-image")

        for permission in ROLE_PERMISSIONS:
            base.checkbox(label=permission, checked=True)

    with allure.step("5 - Rolni saqlab, ro'yxatga qaytish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Роли", url="role_list", timeout=600_000)

    with allure.step("6 - Saqlangan barcha ruxsatlarni qayta tekshirish"):
        base.grid("Админ", click=True)
        base.click(name="Изменить")
        base.expect_page(heading="Роль (изменение)", url=re.compile(r"/role(?:\+|%2[bB])edit(?:[?#]|$)"))
        for permission in ROLE_PERMISSIONS:
            base.checkbox(label=permission, expect_checked=True)

    with allure.step("7 - Rollar ro'yxatiga qaytish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="Роли", url="role_list")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Admin rolini sozlash (barcha ruxsatlar)")
def test_role(page):
    authorization(page, who="admin")
    run_role(page)
