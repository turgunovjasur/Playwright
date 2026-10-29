"""Group-0 settlement jadvalidagi ustunlarni UI orqali tayyorlash."""

import allure

from utils.base_pages.auto_base_page import AutoBasePage


def settlement_columns(page):
    """Legacy va A2 jadval indekslarini ko'rinadigan ustun nomidan oladi."""
    base = AutoBasePage(page)
    fields = {
        "client": "Клиент",
        "currency": "Валюта",
        "debt": "Задолженность",
        "prepayment": "Предоплата",
        "order": "Заказ",
        "reserved_prepayment": "Забронированная предоплата",
        "balance": "Баланс",
    }
    with allure.step("Settlement ustunlari va klient qidiruvini tayyorlash"):
        return {
            key: base.grid_setting(
                menu_name="Настройка таблицы",
                field_name=label,
                search_name="Клиент" if key == "client" else None,
            )
            for key, label in fields.items()
        }
