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
        "path": "trade/tr/store_seller_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Пользователи",
        "path": "anor/mr/user_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Штат",
        "path": "anor/mrf/robot_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Все пользователи",
        "path": "anor/mr/all_users_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Роли",
        "path": "trade/tr/role_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Запросы на доступ к действиям",
        "path": "biruni/md/access_request_list",
        "reason": SELLERS_SKIP_REASON,
    },
    {
        "name": "Публикация в бот",
        "path": "trade/txs/telegram/notification_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Пользователи телеграмм",
        "path": "trade/txs/telegram/user_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Сообщения клиентов",
        "path": "trade/txs/telegram/person_message_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Регистрации через бот",
        "path": "trade/txs/telegram/registered_person_list",
        "reason": BOT_SKIP_REASON,
    },
    {
        "name": "Инвентаризация КМ",
        "path": "anor/mkw/marking_stocktaking/marking_stocktaking_list",
        "reason": "Joriy test muhitida formaga dostup yo'q.",
    },
    {
        "name": "Дашборд по продажам (БЕТА)",
        "path": "trade/tdeal/qlik_sales_dashboard",
        "reason": QLIK_BETA_SKIP_REASON,
    },
]

SKIPPED_FORM_PATHS = frozenset(item["path"] for item in SKIPPED_FORMS)

if len(SKIPPED_FORM_PATHS) != len(SKIPPED_FORMS):
    raise ValueError("SKIPPED_FORMS registry'sida takrorlangan path bor")


def is_form_skipped(definition):
    """Definition canonical pathi skip registry'da borligini qaytaradi."""
    path = definition.get("expected_path") or definition.get("path")
    return path in SKIPPED_FORM_PATHS
