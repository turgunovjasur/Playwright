"""\`\`Продажа\`\` legacy navbarining deklarativ forma inventorysi."""

from tests.smoke.test_forms.inventory.constants import OPERATIONAL_PLACEHOLDER


OPERATIONAL_DIRECT_FORMS = [
    {
        "menu_column": "Визиты",
        "menu_item": "Визиты",
        "path": "trade/tvt/visit_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Архив визитов",
        "path": "trade/tvt/visit_history_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание пользователей",
        "path": "trade/tvt/user_locations",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание мобильных представителей",
        "path": "trade/tph/user_tracking",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Планирование визитов",
        "path": "trade/tvt/plan/room_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Планы",
        "path": "trade/tvt/plan/plan_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Автоформирование плана визитов",
        "path": "trade/tvt/auto_gen_visit_plan",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "path": "trade/tvt/equipment_review_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Фото- и видеоотчеты",
        "path": "trade/tvt/photo_video_gallery",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "path": "trade/tdeal/order/order_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Архив заказов",
        "path": "trade/tdeal/order/order_history_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Отмененные заказы",
        "path": "trade/tdeal/order/order_cancelled_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Возвраты",
        "path": "anor/mdeal/return/return_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "path": "anor/mdeal/order/offset/offset_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Лиды",
        "path": "anor/mdeal/order/lead_list",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд",
        "path": "trade/tdeal/sales_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "path": "trade/tdeal/sales_dashboard_two",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам (БЕТА)",
        "title": "Дашборд по продажам (БЕТА)(GWS_QLIK_001)",
        "path": "trade/tdeal/qlik_sales_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Конструктор отчётов по продажам",
        "path": "trade/rep/mbi/tdeal/order",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Общий отчет по продажам (организации)",
        "path": "trade/rep/tdeal/sales",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Задолженность покупателей по срокам задолженности",
        "title": "Задолженность покупателей по срокам задолженности(FIN00001)",
        "path": "anor/rep/analytics/debtor_clients",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Расчет бонуса за оплату долга",
        "path": "trade/rep/tdeal/sales_discount",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Коммерческий дашборд",
        "path": "trade/tdeal/commercial_dashboard",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Конструктор отчётов по визитам",
        "path": "trade/rep/mbi/tvt/visit",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Отчет по визитам",
        "path": "trade/rep/tvt/visits",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Анализ маршрута",
        "path": "trade/rep/route_analysis",
    },
    {
        "menu_column": "Отчеты по визитам",
        "menu_item": "Отчёт о маршруте пользователей",
        "path": "trade/rep/path_visit_user",
    },
]


OPERATIONAL_PAGE_LINK_FORMS = [
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "page_links": ["Архив"],
        "path": "trade/tvt/equipment_review_history_list",
    },
    {
        "menu_column": "Визиты",
        "menu_item": "Отслеживание оборудования",
        "page_links": ["Архив", "Отслеживание оборудования"],
        "path": "trade/tvt/equipment_review_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Отказы"],
        "path": "anor/mdeal/order/sales_return_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Детали задолженности"],
        "path": "anor/mdeal/order/offset/offset_detail_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": ["Детали задолженности", "История взаиморасчетов"],
        "path": "anor/mdeal/order/offset/offset_history_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Заказы",
        "page_links": [
            "Детали задолженности",
            "История взаиморасчетов",
            "Детали задолженности",
        ],
        "path": "anor/mdeal/order/offset/offset_detail_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Возвраты",
        "page_links": ["Причины возврата"],
        "path": "anor/mdeal/return/return_reason_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты"],
        "path": "anor/mku/offset/offset_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты", "Парные счета"],
        "path": "anor/mku/coa_twin_list",
    },
    {
        "menu_column": "Продажа",
        "menu_item": "Взаиморасчеты с клиентами",
        "page_links": ["Взаиморасчеты", "Парные счета", "Взаиморасчеты"],
        "path": "anor/mku/offset/offset_list",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "page_links": ["Дашборд команды продаж"],
        "path": "trade/tdeal/sales_team_dashboard",
    },
    {
        "menu_column": "Отчеты по продажам",
        "menu_item": "Дашборд по продажам",
        "page_links": ["Дашборд команды продаж", "Дашборд по продажам"],
        "path": "trade/tdeal/sales_dashboard_two",
    },
]


FORM_BUCKETS = (
    {
        "forms": [*OPERATIONAL_DIRECT_FORMS, *OPERATIONAL_PAGE_LINK_FORMS],
        "filial": OPERATIONAL_PLACEHOLDER,
        "section": "operational",
    },
)
