"""Aksiya setup testlaridagi umumiy forma ochish va asosiy maydonlar."""

import allure

from utils.base_pages.base_page import BasePage


def open_action_form(page):
    """Aksiyalar ro'yxatidan yangi aksiya formasini ochadi."""
    base = BasePage(page)
    with allure.step("Aksiyalar ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Акции")
        base.expect_page(heading="Акции", url="anor/mcg/action_list")
    with allure.step("Yangi aksiya formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Акция (создание)", url="anor/mcg/action+add")


def fill_action_scope(page, *, name, action_code, room, price_type, start_date, end_date):
    """Besh aksiya uchun umumiy qo'llanish doirasini to'ldiradi."""
    base = BasePage(page)
    with allure.step("Aksiya rekvizitlari va qo'llanish doirasini to'ldirish"):
        base.input(label="Название", value=name)
        base.input(label="Код акции", value=action_code)
        base.input(label="Дата начала", value=start_date, press_tab=True)
        base.input(label="Срок действия", value=end_date, press_tab=True)
        base.multiselect(label="Рабочие зоны", value=room)
        base.b_input(label="Бонусный склад", value="Основной склад")
        base.multiselect(label="Тип цены", value=price_type)
        base.ui_select(label="Статус", value="Активный")
        base.ui_select(label="Обязательная", value="Нет")
        base.ui_select(label="Бонусы за заказ", value="Множественный")
        base.ui_select(label="Ограничение по количеству заказов", expect_value="Нет")
        base.ui_select(label="Ограничения по времени", expect_value="Нет")
        base.ui_select(label="Кумулятивная акция", expect_value="Нет")
        base.ui_select(label="Установить лимит бонусов", expect_value="Нет")
        base.ui_select(label="Рассчитать уровень скидки", expect_value="1")
