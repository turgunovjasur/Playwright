"""Forms smoke coverage'idan vaqtincha chiqarilgan formalar registry'si."""


SELLERS_SKIP_REASON = (
    "'Продавцы' parenti foydalanuvchi qarori bilan vaqtincha chiqarilgan."
)
BOT_SKIP_REASON = (
    "'Публикация в бот' parenti foydalanuvchi qarori bilan vaqtincha chiqarilgan."
)
QLIK_BETA_SKIP_REASON = (
    "'Дашборд по продажам (БЕТА)' foydalanuvchi qarori bilan vaqtincha "
    "chiqarilgan: joriy muhitda Qlik litsenziyasi yo'q."
)

SKIPPED_FORMS = [
    {
        "name": "Продавцы",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "trade/tr/store_seller_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Пользователи",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "anor/mr/user_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Штат",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "anor/mrf/robot_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Все пользователи",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "anor/mr/all_users_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Роли",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "trade/tr/role_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Запросы на доступ к действиям",
        "navbar_tab": "Справочники",
        "menu_item": "Продавцы",
        "path": "biruni/md/access_request_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Публикация в бот",
        "navbar_tab": "Справочники",
        "menu_item": "Публикация в бот",
        "path": "trade/txs/telegram/notification_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Пользователи телеграмм",
        "navbar_tab": "Справочники",
        "menu_item": "Публикация в бот",
        "path": "trade/txs/telegram/user_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Сообщения клиентов",
        "navbar_tab": "Справочники",
        "menu_item": "Публикация в бот",
        "path": "trade/txs/telegram/person_message_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Регистрации через бот",
        "navbar_tab": "Справочники",
        "menu_item": "Публикация в бот",
        "path": "trade/txs/telegram/registered_person_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Инвентаризация КМ",
        "navbar_tab": "Склад",
        "menu_item": "Инвентаризации",
        "path": "anor/mkw/marking_stocktaking/marking_stocktaking_list",
        "reason": "Joriy test muhitida formaga dostup yo'q.",
    },
    {
        "name": "Дашборд по продажам (БЕТА)",
        "navbar_tab": "Продажа",
        "menu_item": "Дашборд по продажам (БЕТА)",
        "path": "trade/tdeal/qlik_sales_dashboard",
        "reason": QLIK_BETA_SKIP_REASON,
    },
]

SKIPPED_FORM_KEYS = frozenset(
    (item["navbar_tab"], item["menu_item"], item["path"])
    for item in SKIPPED_FORMS
)
SKIPPED_FORM_PATHS = frozenset(item["path"] for item in SKIPPED_FORMS)

if len(SKIPPED_FORM_KEYS) != len(SKIPPED_FORMS):
    raise ValueError("SKIPPED_FORMS registry'sida takrorlangan trace bor")


def _matches_skip(item, definition, *, navbar_tab=None):
    path = definition.get("expected_path") or definition.get("path")
    effective_tab = definition.get("navbar_tab") or navbar_tab
    return (
        item["path"] == path
        and item["navbar_tab"] == effective_tab
        and item["menu_item"] == definition.get("menu_item")
    )


def is_form_skipped(definition, *, navbar_tab=None):
    """Definitionning exact navbar/menu/path trace'i skip ekanini qaytaradi."""
    return any(
        _matches_skip(item, definition, navbar_tab=navbar_tab)
        for item in SKIPPED_FORMS
    )


def skipped_form(definition, *, navbar_tab=None):
    """Definition uchun skip metadata nusxasini qaytaradi, aks holda ``None``."""
    return next(
        (
            dict(item)
            for item in SKIPPED_FORMS
            if _matches_skip(item, definition, navbar_tab=navbar_tab)
        ),
        None,
    )
