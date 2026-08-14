"""``Склад`` navbarining legacy va A2 forma inventorysi."""

from tests.smoke.test_forms.inventory.constants import OPERATIONAL_PLACEHOLDER


A2_REPORT_FORMS = [
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по внутр. перемещениям",
        "path": "anor/rep/mbi/mkw/movement",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по запросам на закуп",
        "path": "anor/rep/mbi/mkw/purchase_request",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по закупкам",
        "path": "anor/rep/mbi/mkw/purchase",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по поступлениям",
        "path": "anor/rep/mbi/mkw/input",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по списанию",
        "path": "anor/rep/mbi/mkw/writeoff",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по запросам на межорг. перемещения",
        "path": "anor/rep/mbi/mfm/movement_request",
        "shell": "a2",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по межорг. перемещениям",
        "path": "anor/rep/mbi/mfm/movement",
        "shell": "a2",
    },
]


OPERATIONAL_DIRECT_FORMS = [
    {
        "menu_column": "Документы",
        "menu_item": "Ввод начальных остатков ТМЦ",
        "path": "anor/mkw/init_balance/init_inventory_balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Запросы на закупку",
        "path": "anor/mkw/purchase/purchase_request_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Заказы на закупку",
        "path": "anor/mkw/purchase/order_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Закупки",
        "path": "anor/mkw/purchase/purchase_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Дополнительные расходы",
        "path": "anor/mkw/extra_cost_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "path": "anor/mkw/input/input_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Возвраты поставщику",
        "path": "anor/mkw/return/return_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Списания",
        "path": "anor/mkw/writeoff/writeoff_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "path": "anor/mkw/stocktaking/stocktaking_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Переоценки себестоимости ТМЦ",
        "path": "anor/mkw/revaluation/revaluation_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Взаиморасчеты с поставщиками",
        "path": "anor/mkw/purchase/offset/offset_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Пересчет приходных цен",
        "path": "anor/mkw/recalculate_input",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Прогноз для закупки",
        "path": "anor/mfc/forecast_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Запросы на внутр. перемещения",
        "path": "anor/mkw/movement/movement_request_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Внутренние перемещения",
        "path": "anor/mkw/movement/movement_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Запросы на межорг. перемещ.: отправка",
        "path": "anor/mfm/from_movement_request_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Запросы на межорг. перемещ.: прием",
        "path": "anor/mfm/to_movement_request_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Межорг. перемещения: отправка",
        "path": "anor/mfm/from_movement_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Межорг. перемещения: прием",
        "path": "anor/mfm/to_movement_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Архив межорг. перемещений",
        "path": "anor/mfm/from_movement_history_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Отмененные межорг. перемещения",
        "path": "anor/mfm/cancelled_from_movement_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Поставщики",
        "path": "anor/mkw/supplier_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Автотранспорт",
        "path": "anor/mrf/van_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Склады",
        "path": "anor/mkw/warehouse_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Остатки ТМЦ",
        "path": "anor/mkw/balance/balance_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Логистика",
        "path": "trade/tdeal/logistics_list",
        "shell": "a2",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Рекламное оборудование",
        "path": "anor/mkw/product_serials",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Документы WMS",
        "path": "anor/mxsx/wms/document_list",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Материальный отчет",
        "path": "anor/rep/mkw/warehouse_inventories",
    },
    {
        "menu_column": "Отчеты",
        "menu_item": "Общий отчет по складам",
        "path": "anor/rep/mkw/warehouse_balance/warehouse_balance",
    },
    *A2_REPORT_FORMS,
    {
        "menu_column": "Отчеты",
        "menu_item": "Отчёт по отгрузкам и оплатам",
        "path": "trade/rep/warehouse_and_delivery",
    },
]


OPERATIONAL_PAGE_LINK_FORMS = [
    {
        "menu_column": "Документы",
        "menu_item": "Ввод начальных остатков ТМЦ",
        "page_links": ["Ввод начального баланса счетов"],
        "path": "anor/mku/init_balance/init_balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Ввод начальных остатков ТМЦ",
        "page_links": ["Ввод начального баланса клиентов"],
        "path": "anor/mku/init_balance/init_client_balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Ввод начальных остатков ТМЦ",
        "page_links": ["Ввод начального баланса поставщиков"],
        "path": "anor/mku/init_balance/init_supplier_balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Ввод начальных остатков ТМЦ",
        "page_links": ["Ввод начальных остатков оборудования клиентов"],
        "path": "anor/mkw/init_balance/init_client_inventory_balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Запросы на закупку",
        "page_links": ["Причины запросов на закупку"],
        "path": "anor/mkw/purchase/purchase_request_reason_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Запросы на закупку",
        "page_links": ["Заказы на закупку"],
        "path": "anor/mkw/purchase/order_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Заказы на закупку",
        "page_links": ["Закупки"],
        "path": "anor/mkw/purchase/purchase_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Закупки",
        "page_links": ["Поступления ТМЦ на склад"],
        "path": "anor/mkw/input/input_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Закупки",
        "page_links": ["Списания при закупке"],
        "path": "anor/mkw/purchase/purchase_writeoff_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Закупки",
        "page_links": ["Статус закупок"],
        "path": "anor/mkw/purchase/purchase_status_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Закупки",
        "page_links": ["Прогноз для закупки"],
        "path": "anor/mfc/forecast_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Дополнительные расходы",
        "page_links": ["Виды движения"],
        "path": "anor/mkw/corr_template_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Закупки"],
        "path": "anor/mkw/purchase/purchase_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Поставщики"],
        "path": "anor/mkw/supplier_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Дополнительные расходы"],
        "path": "anor/mkw/extra_cost_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Внутренние перемещения"],
        "path": "anor/mkw/movement/movement_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Списания"],
        "path": "anor/mkw/writeoff/writeoff_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Поступления ТМЦ на склад",
        "page_links": ["Инвентаризации"],
        "path": "anor/mkw/stocktaking/stocktaking_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Возвраты поставщику",
        "page_links": ["Причины возвратов поставщику"],
        "path": "anor/mkw/return/return_reason_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Списания",
        "page_links": ["Причины списаний"],
        "path": "anor/mkw/writeoff/reason_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Списания",
        "page_links": ["Виды движения"],
        "path": "anor/mkw/corr_template_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Списания",
        "page_links": ["Внутренние перемещения"],
        "path": "anor/mkw/movement/movement_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Списания",
        "page_links": ["Инвентаризации"],
        "path": "anor/mkw/stocktaking/stocktaking_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Причины инвентаризации"],
        "path": "anor/mkw/stocktaking/reason_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Виды движения"],
        "path": "anor/mkw/corr_template_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Внутренние перемещения"],
        "path": "anor/mkw/movement/movement_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Списания"],
        "path": "anor/mkw/writeoff/writeoff_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Остатки ТМЦ"],
        "path": "anor/mkw/balance/balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Инвентаризация склада"],
        "path": "anor/mkw/stocktaking/stocktaking_ban_period_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Внутренние перемещения",
        "page_links": ["Списания"],
        "path": "anor/mkw/writeoff/writeoff_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Внутренние перемещения",
        "page_links": ["Инвентаризации"],
        "path": "anor/mkw/stocktaking/stocktaking_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Внутренние перемещения",
        "page_links": ["Причины перемещений"],
        "path": "anor/mkw/movement/movement_reason_list",
    },
    {
        "menu_column": "Перемещения",
        "menu_item": "Межорг. перемещения: отправка",
        "page_links": ["Причины перемещений"],
        "path": "anor/mfm/movement_reason_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Склады",
        "page_links": ["Типы складов"],
        "path": "anor/mkw/warehouse_type_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Остатки ТМЦ",
        "page_links": ["Настройки сроков годности"],
        "path": "anor/pref/expiration_date",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Остатки ТМЦ",
        "page_links": ["Рекламное оборудование"],
        "path": "anor/mkw/product_serials",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Остатки ТМЦ",
        "page_links": ["Рекомендованные остатки"],
        "path": "anor/mkw/balance/recommended_balance_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Рекламное оборудование",
        "page_links": ["Остатки ТМЦ"],
        "path": "anor/mkw/balance/balance_list",
    },
    {
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Инвентаризация КМ"],
        "path": "anor/mkw/marking_stocktaking/marking_stocktaking_list",
        "shell": "a2",
    },
]


FORM_BUCKETS = (
    {
        "forms": [*OPERATIONAL_DIRECT_FORMS, *OPERATIONAL_PAGE_LINK_FORMS],
        "filial": OPERATIONAL_PLACEHOLDER,
        "section": "operational",
    },
)
