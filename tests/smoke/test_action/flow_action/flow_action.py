"""Aksiya setup testlaridagi umumiy forma ochish va asosiy maydonlar."""

import re
from urllib.parse import urlsplit

import allure
from playwright.sync_api import expect

from utils.base_pages.auto_base_page import AutoBasePage


def open_action_form(page):
    """Aksiyalar ro'yxatidan yangi aksiya formasini ochadi."""
    base = AutoBasePage(page)
    with allure.step("Aksiyalar ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="Акции")
        base.expect_page(heading="Акции", url="anor/mcg/action_list")
    with allure.step("Yangi aksiya formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Акция (создание)", url=re.compile(r"anor/mcg/action(?:\+|%2[bB])add(?:[?#]|$)"))


def fill_action_scope(page, *, name, action_code, room, price_type, start_date, end_date):
    """Besh aksiya uchun umumiy qo'llanish doirasini to'ldiradi."""
    base = AutoBasePage(page)
    with allure.step("Aksiya rekvizitlari va qo'llanish doirasini to'ldirish"):
        base.input(label="Название", value=name)
        base.input(label="Код акции", value=action_code)
        base.input(label="Дата начала", value=start_date)
        base.input(label="Срок действия", value=end_date)
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


def select_action_product(page, *, product_name, index):
    """Shart yoki bonusga mahsulot qo'shib, qayta ochilgan qidiruvni yopadi."""
    base = AutoBasePage(page)
    refresh_count = 0

    def selection_refreshed(request):
        nonlocal refresh_count
        if request.method != "POST" or not urlsplit(request.url).path.endswith("/action+add:products"):
            return False
        payload = request.post_data_json or {}
        # Empty-query refreshes exclude the product just selected in this panel.
        if not payload.get("d", {}).get("product_id"):
            return False
        if "esearch" in str(payload.get("p", {}).get("filter", [])):
            return False
        refresh_count += 1
        return refresh_count == 2

    with allure.step(f"Aksiya mahsulotini tanlash: {product_name}"):
        # A2 selection resets the query twice: immediately and after debounce.
        # Closing before the second response lets that response reopen the menu.
        with page.expect_event("requestfinished", predicate=selection_refreshed):
            search = base.b_input(
                placeholder="Поиск...", value=product_name, index=index, stop_after_select=True,
            )
        expect(search).to_have_value("")
        backdrop = page.locator(".cdk-overlay-container .cdk-overlay-backdrop")
        base.click(locator=backdrop)
        expect(backdrop).to_be_hidden()
