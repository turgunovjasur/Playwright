"""``Справочники`` tabidagi legacy formalarni user-visible yo'llar orqali tekshirish.

Live inventar: ``skills/smartup-guide/references/legacy-form-navigation.md``.
Aktiv qamrov — jami 88 ta navigatsiya: operatsion filialda 33 direct menu
forma, 35 page-link/sub-page-link va 14 ``Создать`` dropdown forma;
``Администрирование`` filialida 1 direct, 2 page-link va 3 ``Создать``
dropdown forma. ``Продавцы`` (8 yo'l) va ``Публикация в бот`` (4 yo'l)
parentlariga tegishli 12 ta yo'l vaqtincha qamrovdan chiqarilgan. Har bir
aktiv forma Allure va terminalda filial, tab, menu, forma, kutilgan URL va
haqiqiy URL bilan hisobot qilinadi.
"""

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.flow import (
    first_operational_filial,
    run_form_cases,
    switch_forms_filial,
)
from tests.smoke.test_forms.form_monitor import (
    FormMonitor,
    build_form_case_inventory,
)


pytestmark = [
    pytest.mark.smoke_group(
        "Forms",
        independent=True,
        setup_independent=True,
    ),
    allure.epic("Smoke"),
    allure.feature("Legacy Forms"),
    allure.story("Справочники menu formalarini ochish"),
]

NAVBAR_TAB = "Справочники"


OPERATIONAL_DIRECT_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "path": "anor/mr/product/inventory_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "path": "anor/mkr/price_type_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Услуги",
        "path": "anor/mr/product/service_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Скидки/наценки",
        "path": "anor/mkr/margin_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Производители",
        "path": "anor/mr/product/producer_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Типы фото-отчетов",
        "path": "core/mvt/photo_type_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Типы видео-отчетов",
        "path": "core/mvt/video_type_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Комментарии",
        "path": "core/mvt/comment_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Опросники",
        "path": "anor/mqzm/quiz_set_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Регионы",
        "title": "Страны",
        "path": "anor/mr/region_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Вопросы двойного визита",
        "path": "core/mqz/dv_quiz_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Опросники двойных визитов",
        "path": "core/mqz/dv_quiz_set_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Презентации",
        "path": "trade/tr/presentation_list",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "path": "trade/tr/store_seller_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "path": "anor/mr/person/natural_person_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "path": "anor/mr/person/legal_person_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Отделы",
        "path": "anor/mhr/division_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Должности",
        "path": "anor/mhr/job_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Рабочие зоны",
        "path": "trade/trf/room_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Штат",
        "path": "anor/mrf/robot_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Клиенты",
        "path": "anor/mrf/client_list",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Уведомления",
        "path": "trade/tr/notification_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Акции",
        "path": "anor/mcg/action_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Нагрузки",
        "path": "anor/mcg/overload_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Рекомендации",
        "path": "anor/mcg/recommend_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Правила ограничений",
        "path": "anor/mcg/order_restriction_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Продуктовая корзина",
        "path": "anor/mrf/product_set_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Сеты ТМЦ",
        "path": "anor/mr/product_kit_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Лимитирование ТМЦ",
        "path": "anor/mcg/order_product_limit/order_product_limit_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Вопросы категоризации",
        "path": "anor/mcg/categorization/quiz_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Категоризация физических лиц",
        "path": "anor/mcg/categorization/natural_person_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Категоризация юридических лиц",
        "path": "anor/mcg/categorization/legal_person_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Результат категоризации",
        "path": "anor/mcg/categorization/result_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Отчет по результату категоризации",
        "path": "anor/rep/mcg/category_results",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Публикация в бот",
        "path": "trade/txs/telegram/notification_list",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Минимальные обязательные ассортименты",
        "path": "anor/mcg/mml_list",
    },
]


OPERATIONAL_PAGE_LINK_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Характеристики ТМЦ"],
        "path": "anor/mr/product/inventory_group_list",
        "label": "ТМЦ → Характеристики ТМЦ",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Производители"],
        "path": "anor/mr/product/producer_list",
        "label": "ТМЦ → Производители",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Единицы измерения"],
        "path": "anor/mr/product/measure_list",
        "label": "ТМЦ → Единицы измерения",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Тип кейса (1 уровень)"],
        "path": "anor/mr/product/box_type_list",
        "label": "ТМЦ → Тип кейса (1 уровень)",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Наборы ТМЦ"],
        "path": "anor/mr/sector_list",
        "label": "ТМЦ → Наборы ТМЦ",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "page_links": ["Типы оплат"],
        "path": "anor/mkr/payment_type_list",
        "label": "Цены → Типы оплат",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "page_links": ["Скидки/наценки"],
        "path": "anor/mkr/margin_list",
        "label": "Цены → Скидки/наценки",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Услуги",
        "page_links": ["Характеристики услуг"],
        "path": "anor/mr/product/service_group_list",
        "label": "Услуги → Характеристики услуг",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Регионы",
        "page_links": ["Регионы"],
        "path": "anor/mfk/regions",
        "label": "Регионы → Регионы",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": ["Пользователи"],
        "path": "anor/mr/user_list",
        "label": "Продавцы → Пользователи",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": ["Штат"],
        "path": "anor/mrf/robot_list",
        "label": "Продавцы → Штат",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "page_links": ["Характеристики физических лиц"],
        "path": "anor/mr/person/natural_person_group_list",
        "label": "Физические лица → Характеристики физических лиц",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "page_links": ["Регионы"],
        "title": "Страны",
        "path": "anor/mr/region_list",
        "label": "Физические лица → Регионы",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "page_links": ["Графики доставки"],
        "path": "anor/mr/person/delivery_schedule_list",
        "label": "Физические лица → Графики доставки",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Характеристики юридических лиц"],
        "path": "anor/mr/person/legal_person_group_list",
        "label": "Юридические лица → Характеристики юридических лиц",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Договоры"],
        "path": "anor/mkf/contract_list",
        "label": "Юридические лица → Договоры",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Регионы"],
        "title": "Страны",
        "path": "anor/mr/region_list",
        "label": "Юридические лица → Регионы",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Должности"],
        "path": "anor/mr/person/contact_position_list",
        "label": "Юридические лица → Должности",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Организационно-правовые формы"],
        "path": "anor/mr/legal_form_list",
        "label": "Юридические лица → Организационно-правовые формы",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Виды деятельности"],
        "path": "anor/mr/person/activity_list",
        "label": "Юридические лица → Виды деятельности",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Графики доставки"],
        "path": "anor/mr/person/delivery_schedule_list",
        "label": "Юридические лица → Графики доставки",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Отделы",
        "page_links": ["Группы отделов"],
        "path": "anor/mhr/division_group_list",
        "label": "Отделы → Группы отделов",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Должности",
        "page_links": ["Группы должностей"],
        "path": "anor/mhr/job_group_list",
        "label": "Должности → Группы должностей",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Рабочие зоны",
        "page_links": ["Тип рабочей зоны"],
        "path": "anor/mrf/room_type_list",
        "label": "Рабочие зоны → Тип рабочей зоны",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Акции",
        "page_links": ["Конструктор отчетов по акциям"],
        "path": "anor/rep/mbi/mcg/action",
        "label": "Акции → Конструктор отчетов по акциям",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Правила ограничений",
        "page_links": ["Ограничения по клиенту"],
        "path": "anor/mcg/client_order_restriction_list",
        "label": "Правила ограничений → Ограничения по клиенту",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Продуктовая корзина",
        "page_links": ["Продуктовые корзины по клиентам"],
        "path": "anor/mrf/client_product_set_list",
        "label": "Продуктовая корзина → Продуктовые корзины по клиентам",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Продуктовая корзина",
        "page_links": ["Продуктовые корзины по рабочим местам"],
        "path": "anor/mrf/room_product_set_list",
        "label": "Продуктовая корзина → Продуктовые корзины по рабочим местам",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Продуктовая корзина",
        "page_links": ["Продуктовые корзины по штатам"],
        "path": "anor/mrf/robot_product_set_list",
        "label": "Продуктовая корзина → Продуктовые корзины по штатам",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Публикация в бот",
        "page_links": ["Пользователи телеграмм"],
        "path": "trade/txs/telegram/user_list",
        "label": "Публикация в бот → Пользователи телеграмм",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Публикация в бот",
        "page_links": ["Сообщения клиентов"],
        "path": "trade/txs/telegram/person_message_list",
        "label": "Публикация в бот → Сообщения клиентов",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Публикация в бот",
        "page_links": ["Регистрации через бот"],
        "path": "trade/txs/telegram/registered_person_list",
        "label": "Публикация в бот → Регистрации через бот",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Минимальные обязательные ассортименты",
        "page_links": ["Дашборд по MML"],
        "path": "anor/mcg/mml_dashboard",
        "label": "Минимальные обязательные ассортименты → Дашборд по MML",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Наборы ТМЦ", "ТМЦ"],
        "path": "anor/mr/product/inventory_list",
        "label": "ТМЦ → Наборы ТМЦ → ТМЦ",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Услуги",
        "page_links": ["Характеристики услуг", "Услуги"],
        "path": "anor/mr/product/service_list",
        "label": "Услуги → Характеристики услуг → Услуги",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "page_links": ["Регионы", "Регионы"],
        "title": "Регионы",
        "path": "anor/mfk/regions",
        "label": "Физические лица → Регионы → Регионы",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Регионы", "Регионы"],
        "title": "Регионы",
        "path": "anor/mfk/regions",
        "label": "Юридические лица → Регионы → Регионы",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": ["Пользователи", "Все пользователи"],
        "path": "anor/mr/all_users_list",
        "label": "Продавцы → Пользователи → Все пользователи",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": ["Пользователи", "Роли"],
        "path": "trade/tr/role_list",
        "label": "Продавцы → Пользователи → Роли",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "page_links": ["Договоры", "Дополнительные договоры"],
        "path": "anor/mkf/sub_contract_list",
        "label": "Юридические лица → Договоры → Дополнительные договоры",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Отделы",
        "page_links": ["Группы отделов", "Отделы"],
        "path": "anor/mhr/division_list",
        "label": "Отделы → Группы отделов → Отделы",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Правила ограничений",
        "page_links": ["Ограничения по клиенту", "Правила ограничений"],
        "path": "anor/mcg/order_restriction_list",
        "label": "Правила ограничений → Ограничения по клиенту → Правила ограничений",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": ["Пользователи", "Роли", "Пользователи"],
        "title": "Пользователи",
        "path": "anor/mr/user_list",
        "label": "Продавцы → Пользователи → Роли → Пользователи",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Продавцы",
        "page_links": [
            "Пользователи",
            "Роли",
            "Запросы на доступ к действиям",
        ],
        "path": "biruni/md/access_request_list",
        "label": "Продавцы → Пользователи → Роли → Запросы на доступ к действиям",
    },
]


OPERATIONAL_HIDDEN_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "action": "Прикрепление",
        "title": "Цены (прикрепление)",
        "path": "anor/mkr/price_type_list+attach",
        "label": "Цены → Создать dropdown → Прикрепление",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "action": "Импорт",
        "title": "Цены (импорт)",
        "path": "anor/mkf/product_price_import",
        "label": "Цены → Создать dropdown → Импорт",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "action": "Прикрепление",
        "title": "Физические лица (прикрепление)",
        "path": "anor/mr/person/natural_person_list+attach",
        "label": "Физические лица → Создать dropdown → Прикрепление",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "action": "Импорт",
        "title": "Физические лица (импорт)",
        "path": "anor/mr/person/natural_person_import",
        "label": "Физические лица → Создать dropdown → Импорт",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Физические лица",
        "action": "Установка локального кода",
        "title": "Физические лица (установка локального кода)",
        "path": "anor/mr/person/set_natural_person_local_code",
        "label": "Физические лица → Создать dropdown → Установка локального кода",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "action": "Прикрепление",
        "title": "Юридические лица (прикрепление)",
        "path": "anor/mr/person/legal_person_list+attach",
        "label": "Юридические лица → Создать dropdown → Прикрепление",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "action": "Импорт",
        "title": "Юридические лица (импорт)",
        "path": "anor/mr/person/legal_person_import",
        "label": "Юридические лица → Создать dropdown → Импорт",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Юридические лица",
        "action": "Установить локальный код",
        "title": "Юридические лица (установка локального кода)",
        "path": "anor/mr/person/set_legal_person_local_code",
        "label": "Юридические лица → Создать dropdown → Установить локальный код",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Рабочие зоны",
        "action": "Импорт рабочих зон",
        "title": "Рабочие зоны (импорт)",
        "path": "anor/mrf/room_import",
        "label": "Рабочие зоны → Создать dropdown → Импорт рабочих зон",
    },
    {
        "menu_column": "Основное",
        "menu_item": "Штат",
        "action": "Импорт",
        "title": "Штат (импорт)",
        "path": "anor/mrf/robot_import",
        "label": "Штат → Создать dropdown → Импорт",
    },
    {
        "menu_column": "Маркетинг",
        "menu_item": "Сеты ТМЦ",
        "action": "Прикрепление",
        "title": "Сет ТМЦ (прикрепление)",
        "path": "anor/mr/product_kit_list+attach",
        "label": "Сеты ТМЦ → Создать dropdown → Прикрепление",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "action": "Импорт",
        "page_links": ["Цены"],
        "title": "Цены",
        "path": "anor/mkr/price_type_list",
        "label": "Цены → Импорт → Цены",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "action": "Импорт",
        "page_links": ["Типы оплат"],
        "title": "Типы оплат",
        "path": "anor/mkr/payment_type_list",
        "label": "Цены → Импорт → Типы оплат",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Цены",
        "action": "Импорт",
        "page_links": ["Скидки/наценки"],
        "title": "Скидки/наценки",
        "path": "anor/mkr/margin_list",
        "label": "Цены → Импорт → Скидки/наценки",
    },
]


ADMIN_DIRECT_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "Вопросы",
        "path": "core/mqz/quiz_list",
    },
]


ADMIN_PAGE_LINK_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "page_links": ["Единицы измерения для Didox"],
        "path": "anor/mr/product/didox_measure_list",
        "label": "ТМЦ → Единицы измерения для Didox",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Вопросы",
        "page_links": ["Тип вопроса"],
        "path": "core/mqz/quiz_type_list",
        "label": "Вопросы → Тип вопроса",
    },
]


ADMIN_HIDDEN_FORMS = [
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "action": "Импорт",
        "title": "ТМЦ (импорт)",
        "path": "anor/mr/product/inventory_import",
        "label": "ТМЦ → Создать dropdown → Импорт",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "ТМЦ",
        "action": "Импорт фото",
        "title": "Импорт фото",
        "path": "anor/mr/product/inventory_photo_import",
        "label": "ТМЦ → Создать dropdown → Импорт фото",
    },
    {
        "menu_column": "Справочники",
        "menu_item": "Услуги",
        "action": "Импорт",
        "title": "Услуги (импорт)",
        "path": "anor/mr/product/service_import",
        "label": "Услуги → Создать dropdown → Импорт",
    },
]


def run_spravochniki_menu_forms(page, *, terminal_reporter=None):
    """Testcase: ``Справочники`` tabidagi barcha user-visible forma yo'llarini ochish.

    1. Birinchi operatsion filialni topib, 33 ta aktiv direct menu formani tekshirish.
    2. Operatsion filialdagi page-link, nested link va hidden formalarni tekshirish.
    3. ``Администрирование``ga o'tib, faqat shu filialga xos yo'llarni tekshirish.
    4. Jami 88 ta aktiv navigatsiya natijasini terminal va Allurega biriktirish.

    ``Продавцы`` va ``Публикация в бот`` parentlari ostidagi 12 ta yo'l
    umumiy ``SKIPPED_FORMS`` registry'si orqali test rejasiga qo'shilmaydi.
    """
    operational_placeholder = "<operatsion filial>"
    planned_cases = []
    skipped_cases = []
    number = 1
    for cases, filial, section in (
        (OPERATIONAL_DIRECT_FORMS, operational_placeholder, "operational-direct"),
        (OPERATIONAL_PAGE_LINK_FORMS, operational_placeholder, "operational-page-link"),
        (OPERATIONAL_HIDDEN_FORMS, operational_placeholder, "operational-hidden"),
        (ADMIN_DIRECT_FORMS, "Администрирование", "admin-direct"),
        (ADMIN_PAGE_LINK_FORMS, "Администрирование", "admin-page-link"),
        (ADMIN_HIDDEN_FORMS, "Администрирование", "admin-hidden"),
    ):
        inventory = build_form_case_inventory(
            cases,
            navbar_tab=NAVBAR_TAB,
            start_number=number,
            filial=filial,
            section=section,
        )
        planned = inventory["planned"]
        planned_cases.extend(planned)
        skipped_cases.extend(inventory["skipped"])
        number += len(planned)
    expected_count = len(planned_cases)

    monitor = FormMonitor(
        page,
        suite_name="Forms-01 — Справочники",
        planned_cases=planned_cases,
        skipped_cases=skipped_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id="test_forms_01_spravochniki",
    )
    try:
        monitor.precondition(
            "Admin avtorizatsiyasi",
            lambda: authorization(page, who="admin"),
            affected_case_number=1,
        )
        if monitor.blocked:
            return

        operational_filial = monitor.precondition(
            "Operatsion filialni aniqlash",
            lambda: first_operational_filial(page),
            affected_case_number=1,
        )
        if monitor.blocked:
            return
        monitor.update_filial(operational_placeholder, operational_filial)

        with allure.step(f"1 - '{operational_filial}' filialidagi direct menu formalar"):
            operational_direct_cases = monitor.cases(section="operational-direct")
            monitor.precondition(
                f"'{operational_filial}' filialiga o'tish",
                lambda: switch_forms_filial(page, operational_filial),
                affected_case_number=(
                    operational_direct_cases[0]["number"]
                    if operational_direct_cases
                    else None
                ),
            )
            if monitor.blocked:
                return
            run_form_cases(
                page,
                operational_direct_cases,
                monitor=monitor,
            )

        with allure.step(
            f"2 - '{operational_filial}' filialidagi page-link va hidden formalar"
        ):
            run_form_cases(
                page,
                monitor.cases(section="operational-page-link"),
                monitor=monitor,
            )
            run_form_cases(
                page,
                monitor.cases(section="operational-hidden"),
                monitor=monitor,
            )

        with allure.step("3 - 'Администрирование' filialiga xos formalar"):
            admin_direct_cases = monitor.cases(section="admin-direct")
            monitor.precondition(
                "'Администрирование' filialiga o'tish",
                lambda: switch_forms_filial(page, "Администрирование"),
                affected_case_number=(
                    admin_direct_cases[0]["number"] if admin_direct_cases else None
                ),
            )
            if monitor.blocked:
                return
            run_form_cases(
                page,
                admin_direct_cases,
                monitor=monitor,
            )
            run_form_cases(
                page,
                monitor.cases(section="admin-page-link"),
                monitor=monitor,
            )
            run_form_cases(
                page,
                monitor.cases(section="admin-hidden"),
                monitor=monitor,
            )
    finally:
        with allure.step(f"4 - {expected_count} ta navigatsiya natijasini tekshirish"):
            monitor.finish()


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("Справочники — menu, page-link va hidden formalarni ochish smoke")
def test_spravochniki_menu_forms(page, pytestconfig):
    run_spravochniki_menu_forms(
        page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
