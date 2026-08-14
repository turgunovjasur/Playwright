"""``Главное`` navbarining legacy va A2 forma inventorysi."""

from tests.smoke.test_forms.inventory.constants import OPERATIONAL_PLACEHOLDER


OPERATIONAL_DIRECT_FORMS = [
    {
        "menu_column": "Основное",
        "menu_item": "Организации",
        "path": "anor/mr/filial_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Пользователи",
        "path": "anor/mr/user_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Проекты",
        "path": "anor/mrf/subfilial_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Шаблоны накладных",
        "path": "anor/mr/template_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Настройки системы",
        "path": "trade/pref/system_setting",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "История изменений",
        "path": "biruni/md/audit_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "path": "trade/tph/role_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Настройки интеграции со сторонним ПО",
        "path": "trade/txs/external_settings",
        "shell": "a2",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Объекты",
        "path": "biruni/kdyn/entity_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Динамичные поля",
        "path": "biruni/kdyn/field_list",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Отчeты",
        "path": "anor/rep/report_list",
    },
]


OPERATIONAL_PAGE_LINK_FORMS = [
    {
        "menu_column": "Основное",
        "menu_item": "Пользователи",
        "page_links": ["Все пользователи"],
        "path": "anor/mr/all_users_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Пользователи",
        "page_links": ["Роли"],
        "path": "trade/tr/role_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Пользователи",
        "page_links": ["Роли", "Пользователи"],
        "path": "anor/mr/user_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Пользователи",
        "page_links": ["Роли", "Запросы на доступ к действиям"],
        "path": "biruni/md/access_request_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Настройки системы",
        "page_links": ["Аппараты фискализации"],
        "path": "anor/mrf/fiscal_cash_register_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Настройки системы",
        "page_links": ["Настройки сервисов доставки"],
        "path": "trade/txs/delivery_service_setting",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Пользователи"],
        "path": "anor/mr/user_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Пользователи", "Все пользователи"],
        "path": "anor/mr/all_users_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Пользователи", "Роли"],
        "path": "trade/tr/role_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Пользователи", "Роли", "Пользователи"],
        "path": "anor/mr/user_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": [
            "Пользователи",
            "Роли",
            "Запросы на доступ к действиям",
        ],
        "path": "biruni/md/access_request_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Роли"],
        "path": "trade/tr/role_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Роли", "Пользователи"],
        "path": "anor/mr/user_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Роли", "Пользователи", "Все пользователи"],
        "path": "anor/mr/all_users_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Роли", "Пользователи", "Роли"],
        "path": "trade/tr/role_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Шаги визита",
        "page_links": ["Роли", "Запросы на доступ к действиям"],
        "path": "biruni/md/access_request_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Настройки интеграции со сторонним ПО",
        "page_links": ["Экспорт заказа"],
        "path": "trade/txso/order_export",
    },
]


ADMIN_ONLY_FORMS = [
    {
        "menu_column": "Основное",
        "menu_item": "Лицензии",
        "path": "biruni/kl/license_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Подключения к системе",
        "path": "biruni/kauth/session_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Клиенты OAuth2 сервера для компании",
        "path": "biruni/kauth/company_client_list",
        "shell": "a2",
        "ready": "app-company-client-list",
        "screenshot_mask": "company-client",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Регистры вебхуков",
        "path": "core/kwh/register_list",
    },
    {
        "menu_column": "Дополнительное",
        "menu_item": "Регистры вебхуков",
        "page_links": ["Логи вебхуков"],
        "path": "core/kwh/log_list",
    },
]


FORM_BUCKETS = (
    {
        "forms": [*OPERATIONAL_DIRECT_FORMS, *OPERATIONAL_PAGE_LINK_FORMS],
        "filial": OPERATIONAL_PLACEHOLDER,
        "section": "operational",
    },
    {
        "forms": ADMIN_ONLY_FORMS,
        "filial": "Администрирование",
        "section": "admin",
    },
)
