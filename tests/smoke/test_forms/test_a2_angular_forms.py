"""Turli navbar'lardagi A2 Angular formalarni markaziy monitor orqali tekshirish.

Case ro'yxati bir xil ``FormCase`` modeliga aylantiriladi va ketma-ket loopda
real navbar → menu → page-link yo'li orqali ochiladi. Har forma title, URL,
readiness, loader, UI error va kontent holati bilan mustaqil tahlil qilinadi.
Allure, terminal progress va yakuniy JSON aynan shu monitor natijasidan quriladi.

A2 FORMALAR INVENTARI — kelajakdagi menu-track testlar uchun
==============================================================

Manba: ``test_a2_new_forms.py::A2_FORMS`` va ``new_forms.md``.
Jami: 54 | ✅ YOZILGAN: 22 | ⏸ VAQTINCHA SKIP: 1 | ⬜ QOLGAN: 31.

Status shu faylga nisbatan:
- ``✅ YOZILGAN`` — real menu/page-link yo'li shu testda mavjud va live o'tgan.
- ``⬜ QOLGAN`` — faqat URL diagnostikada bor; menu-track hali yozilmagan.
- ``direct/via_list/skip`` — ``test_a2_new_forms.py`` dagi ochilish mode'i.
- ``head`` — A2_FORMS profil klassifikatsiyasi; menu formalari baribir admin
  formalar, lekin ayrimlari faqat head kompaniyasida mavjud bo'lishi mumkin.

ADMIN profil → ``Администрирование`` filial (6 ta)
--------------------------------------------------

01. ✅ YOZILGAN | direct | ``biruni/kauth/company_client_list``
    Title: Клиенты OAuth2 сервера для компании
    User trace: Главное → Дополнительное → Клиенты OAuth2 сервера для компании

02. ⬜ QOLGAN | direct | ``biruni/kauth/company_client+add``
    Title: Клиенты OAuth2 сервера (создание)
    User trace: company_client_list → Создать

03. ⬜ QOLGAN | via_list | ``biruni/kauth/company_client+edit``
    Title: Клиенты OAuth2 сервера (изменение)
    Parent: ``biruni/kauth/company_client_list``
    User trace: company_client_list → qator → Изменить

04. ⬜ QOLGAN | direct | ``biruni/ker/head_template_list+attach``
    Title: Доступные шаблоны
    User trace: aniqlanmagan; URL-only diagnostika

05. ⬜ QOLGAN | direct | ``biruni/ker/setting+add``
    Title: Настройки шаблонов (создание)
    User trace: biruni proyektda ekan, trade proyektda chiqmaydi

06. ⬜ QOLGAN | skip | ``biruni/ker/setting+edit``
    Title: Настройки шаблонов (изменение)
    User trace: biruni proyektda ekan, trade proyektda chiqmaydi

ADMIN profil → operatsion filial (25 ta)
----------------------------------------

07. ⬜ QOLGAN | direct | ``biruni/md/company_audit_info_audit``
    Title: История изменений компании
    User trace:  head profilda chiqar ekan!

08. ⬜ QOLGAN | via_list | ``biruni/md/company_audit_info_audit_details``
    Title: Детали истории изменений компании
    Parent: ``biruni/md/company_audit_info_audit``
    User trace: head profilda chiqar ekan!

09. ✅ YOZILGAN | direct | ``biruni/plg/plugin_catalog``
    Title: Plugin Marketplace
    User trace: Плагин → Plugin Marketplace

10. ⏸ VAQTINCHA SKIP | direct | ``anor/mkw/marking_stocktaking/marking_stocktaking_list``
    Title: Инвентаризация КМ
    User trace: Склад → Документы → Инвентаризации → Инвентаризация КМ
    Skip sababi: joriy test muhitida formaga dostup yo'q; dostup berilgach skip registry'dan olib tashlanadi.

11. ✅ YOZILGAN | direct | ``anor/rep/mkr/pnl``
    Title: Отчет о прибылях и убытках
    User trace: Финансы → Отчеты → Отчет о прибылях и убытках

12. ✅ YOZILGAN | direct | ``trade/tvt/user_locations``
    Title: Отслеживание пользователей
    User trace: Продажа → Визиты → Отслеживание пользователей

13. ✅ YOZILGAN | direct | ``trade/tph/user_tracking``
    Title: Отслеживание мобильных представителей
    User trace: Продажа → Визиты → Отслеживание мобильных представителей

14. ✅ YOZILGAN | direct | ``trade/txs/external_settings``
    Title: Настройки интеграции со сторонним ПО
    User trace: Главное → Дополнительное → Настройки интеграции со сторонним ПО

15. ✅ YOZILGAN | direct | ``trade/tdeal/logistics_list``
    Title: Логистика
    User trace: Склад → Справочники → Логистика

16. ✅ YOZILGAN | direct | ``trade/tdeal/commercial_dashboard``
    Title: Коммерческий дашборд
    User trace: Продажа → Отчеты по продажам → Коммерческий дашборд

17. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkcs/operation``
    Title: Конструктор отчетов по финансам
    User trace: Финансы → Отчеты → Конструктор отчетов по финансам

18. ✅ YOZILGAN | direct | ``anor/rep/mku/balance_sheet``
    Title: Бухгалтерский баланс
    User trace: Финансы → Отчеты → Бухгалтерский баланс

19. ✅ YOZILGAN | direct | ``anor/rep/mbi/mcg/action``
    Title: Конструктор отчетов по акциям
    User trace: Справочники → Маркетинг → Акции → Конструктор отчетов по акциям

20. ✅ YOZILGAN | direct | ``anor/rep/mbi/mfm/movement``
    Title: Конструктор отчетов по межорг. перемещениям
    User trace: Склад → Отчеты → Конструктор отчетов по межорг. перемещениям

21. ✅ YOZILGAN | direct | ``anor/rep/mbi/mfm/movement_request``
    Title: Конструктор отчетов по запросам на межорг. перемещения
    User trace: Склад → Отчеты → Конструктор отчетов по запросам на межорг. перемещения

22. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/input``
    Title: Конструктор отчетов по поступлениям
    User trace: Склад → Отчеты → Конструктор отчетов по поступлениям

23. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/movement``
    Title: Конструктор отчетов по внутр. перемещениям
    User trace: Склад → Отчеты → Конструктор отчетов по внутр. перемещениям

24. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/purchase``
    Title: Конструктор отчетов по закупкам
    User trace: Склад → Отчеты → Конструктор отчетов по закупкам

25. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/purchase_request``
    Title: Конструктор отчетов по запросам на закуп
    User trace: Склад → Отчеты → Конструктор отчетов по запросам на закуп

26. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/writeoff``
    Title: Конструктор отчетов по списанию
    User trace: Склад → Отчеты → Конструктор отчетов по списанию

27. ✅ YOZILGAN | direct | ``anor/rep/mbi/mqpf/request``
    Title: Конструктор отчетов по заявкам на оборудование
    User trace: Оборудование → Дополнительное → Конструктор отчетов по заявкам на оборудование

28. ✅ YOZILGAN | direct | ``trade/rep/mbi/tmcg/shelf_share``
    Title: Конструктор отчётов по доле на полке
    User trace: Торговый маркетинг → Отчеты → Конструктор отчётов по доле на полке

29. ✅ YOZILGAN | direct | ``trade/rep/mbi/tvt/visit``
    Title: Конструктор отчётов по визитам
    User trace: Продажа → Отчеты по визитам → Конструктор отчётов по визитам

30. ⬜ QOLGAN | direct | ``anor/rep/mbi/mfa/purchase``
    Title: Конструктор по закупкам (финансы)
    User trace: finance proyektda ekan, trade proyektda chiqmaydi

31. ✅ YOZILGAN | direct | ``trade/tvt/visit_list``
    Title: Визиты
    User trace: Продажа → Визиты → Визиты

HEAD profil → ``Администрирование`` filial (22 ta)
-------------------------------------------------

32. ⬜ QOLGAN | direct | ``biruni/kauth/client_list``
    Title: Клиенты API/OAuth2 сервера
    User trace: Главное → Дополнительное → Клиенты API/OAuth2 сервера

33. ⬜ QOLGAN | direct | ``biruni/kauth/client+add``
    Title: Клиент API/OAuth2 (создание)
    User trace: client_list → Создать

34. ⬜ QOLGAN | via_list | ``biruni/kauth/client+edit``
    Title: Клиент API/OAuth2 (изменение)
    Parent: ``biruni/kauth/client_list``
    User trace: client_list → qator → Изменить

35. ⬜ QOLGAN | direct | ``biruni/kauth/security_settings``
    Title: Настройки безопасности
    User trace: Главное → Дополнительное → Настройки безопасности

36. ⬜ QOLGAN | direct | ``biruni/md/audit_setting``
    Title: Настройки истории изменений
    User trace: Главное → Дополнительное → Настройки истории изменений

37. ⬜ QOLGAN | direct | ``biruni/md/company_list``
    Title: Компании
    User trace: Главное → Дополнительное → Компании

38. ⬜ QOLGAN | direct | ``biruni/md/company_add``
    Title: Компания (создание)
    User trace: company_list → Создать

39. ⬜ QOLGAN | via_list | ``biruni/md/company_edit``
    Title: Компания (изменение)
    Parent: ``biruni/md/company_list``
    User trace: company_list → qator → Изменить

40. ⬜ QOLGAN | via_list | ``biruni/md/company_view``
    Title: Компания (просмотр)
    Parent: ``biruni/md/company_list``
    User trace: company_list → qator → Просмотр

41. ⬜ QOLGAN | direct | ``biruni/md/contact_info_setting``
    Title: Контактная информация
    User trace: Главное → Дополнительное → Контактная информация

42. ⬜ QOLGAN | direct | ``biruni/md/feedback_list``
    Title: Фидбеки
    User trace: Главное → Дополнительное → Фидбеки

43. ⬜ QOLGAN | direct | ``biruni/md/log_list``
    Title: Логи
    User trace: Главное → Дополнительное → Логи

44. ⬜ QOLGAN | direct | ``biruni/md/query_executor``
    Title: Запросы к базе данных
    User trace: Главное → Дополнительное → Запросы к базе данных

45. ⬜ QOLGAN | direct | ``biruni/md/request_limit_template_list``
    Title: Шаблоны лимитов (список)
    User trace: Главное → Дополнительное → Шаблоны лимитов

46. ⬜ QOLGAN | direct | ``biruni/md/request_limit_template+add``
    Title: Шаблоны лимитов (создание)
    User trace: request_limit_template_list → Создать

47. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template+edit``
    Title: Шаблоны лимитов (изменение)
    Parent: ``biruni/md/request_limit_template_list``
    User trace: request_limit_template_list → qator → Изменить

48. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template_view``
    Title: Шаблоны лимитов (просмотр)
    Parent: ``biruni/md/request_limit_template_list``
    User trace: request_limit_template_list → qator → Просмотр

49. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template_audit_details``
    Title: Подробности истории шаблона лимитов
    Parent: ``biruni/md/request_limit_template_list``
    User trace: Шаблоны лимитов → История изменений → detail

50. ⬜ QOLGAN | direct | ``biruni/ms/announcement_list``
    Title: Объявления
    User trace: Главное → Админ → Объявления

51. ⬜ QOLGAN | direct | ``biruni/ms/announcement+add``
    Title: Объявление (создание)
    User trace: announcement_list → Создать

52. ⬜ QOLGAN | via_list | ``biruni/ms/announcement+copy``
    Title: Объявление (копирование)
    Parent: ``biruni/ms/announcement_list``
    User trace: announcement_list → qator → Копировать

53. ⬜ QOLGAN | via_list | ``biruni/ms/announcement+edit``
    Title: Объявление (изменение)
    Parent: ``biruni/ms/announcement_list``
    User trace: announcement_list → qator → Изменить

HEAD profil → operatsion filial (1 ta)
--------------------------------------

54. ⬜ QOLGAN | direct | ``billing/blda/operational_dashboard``
    Title: Операционный дашборд
    User trace: Главное → Основное → Операционный дашборд
"""

import time

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError

from tests.smoke.flows.flow_authorization import authorization, company_url
from tests.smoke.test_forms.monitoring.monitor import FormMonitor
from tests.smoke.test_forms.monitoring.navigation import first_operational_filial, run_form_cases
from tests.smoke.test_forms.monitoring.suite_runner import OPERATIONAL_PLACEHOLDER, build_suite_inventory
from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


pytestmark = [
    pytest.mark.smoke_group(
        "Forms",
        independent=True,
        setup_independent=True,
    ),
    allure.epic("Smoke"),
    allure.feature("A2 Angular Forms"),
    allure.story("Migratsiya qilingan formalarni menyu orqali ochish"),
]

ADMIN_A2_FORMS = [
    {
        "navbar_tab": "Главное",
        "menu_column": "Дополнительное",
        "menu_item": "Клиенты OAuth2 сервера для компании",
        "title": "Клиенты OAuth2 сервера для компании",
        "path": "biruni/kauth/company_client_list",
        "ready": "app-company-client-list",
        "screenshot_mask": "company-client",
    },
]

OPERATIONAL_A2_FORMS = [
    {
        "navbar_tab": "Главное",
        "menu_column": "Дополнительное",
        "menu_item": "Настройки интеграции со сторонним ПО",
        "path": "trade/txs/external_settings",
    },
    {
        "navbar_tab": "Продажа",
        "menu_column": "Визиты",
        "menu_item": "Визиты",
        "path": "trade/tvt/visit_list",
    },
    {
        "navbar_tab": "Продажа",
        "menu_column": "Визиты",
        "menu_item": "Отслеживание пользователей",
        "path": "trade/tvt/user_locations",
    },
    {
        "navbar_tab": "Продажа",
        "menu_column": "Визиты",
        "menu_item": "Отслеживание мобильных представителей",
        "path": "trade/tph/user_tracking",
    },
    {
        "navbar_tab": "Продажа",
        "menu_column": "Отчеты по продажам",
        "menu_item": "Коммерческий дашборд",
        "path": "trade/tdeal/commercial_dashboard",
    },
    {
        "navbar_tab": "Продажа",
        "menu_column": "Отчеты по визитам",
        "menu_item": "Конструктор отчётов по визитам",
        "path": "trade/rep/mbi/tvt/visit",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Справочники",
        "menu_item": "Логистика",
        "path": "trade/tdeal/logistics_list",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по внутр. перемещениям",
        "path": "anor/rep/mbi/mkw/movement",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по запросам на закуп",
        "path": "anor/rep/mbi/mkw/purchase_request",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по закупкам",
        "path": "anor/rep/mbi/mkw/purchase",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по поступлениям",
        "path": "anor/rep/mbi/mkw/input",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по списанию",
        "path": "anor/rep/mbi/mkw/writeoff",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по запросам на межорг. перемещения",
        "path": "anor/rep/mbi/mfm/movement_request",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по межорг. перемещениям",
        "path": "anor/rep/mbi/mfm/movement",
    },
    {
        "navbar_tab": "Финансы",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчетов по финансам",
        "path": "anor/rep/mbi/mkcs/operation",
    },
    {
        "navbar_tab": "Финансы",
        "menu_column": "Отчеты",
        "menu_item": "Бухгалтерский баланс",
        "path": "anor/rep/mku/balance_sheet",
    },
    {
        "navbar_tab": "Финансы",
        "menu_column": "Отчеты",
        "menu_item": "Отчет о прибылях и убытках",
        "path": "anor/rep/mkr/pnl",
    },
    {
        "navbar_tab": "Торговый маркетинг",
        "menu_column": "Отчеты",
        "menu_item": "Конструктор отчётов по доле на полке",
        "path": "trade/rep/mbi/tmcg/shelf_share",
    },
    {
        "navbar_tab": "Оборудование",
        "menu_column": "Дополнительное",
        "menu_item": "Конструктор отчетов по заявкам на оборудование",
        "path": "anor/rep/mbi/mqpf/request",
    },
    {
        "navbar_tab": "Плагин",
        "menu_column": None,
        "menu_item": "Plugin Marketplace",
        "path": "biruni/plg/plugin_catalog",
    },
]

PAGE_LINK_A2_FORMS = [
    {
        "navbar_tab": "Справочники",
        "menu_column": "Маркетинг",
        "menu_item": "Акции",
        "page_links": ["Конструктор отчетов по акциям"],
        "path": "anor/rep/mbi/mcg/action",
    },
    {
        "navbar_tab": "Склад",
        "menu_column": "Документы",
        "menu_item": "Инвентаризации",
        "page_links": ["Инвентаризация КМ"],
        "path": "anor/mkw/marking_stocktaking/marking_stocktaking_list",
    },
]

# ----------------------------------------------------------------------------------------------------------------------


def run_a2_angular_forms(page, *, progress_test_id, terminal_reporter=None, checks=None, diagnostics=None):
    """A2Angular preconditionlari va cross-navbar formalarini mustaqil boshqaradi."""
    operational_forms = [*OPERATIONAL_A2_FORMS, *PAGE_LINK_A2_FORMS]
    form_buckets = (
        {"forms": ADMIN_A2_FORMS, "filial": "Администрирование", "section": "admin"},
        {"forms": operational_forms, "filial": OPERATIONAL_PLACEHOLDER, "section": "operational"},
    )
    planned_cases, skipped_cases = build_suite_inventory(form_buckets, shell="a2")
    monitor = FormMonitor(page, suite_name="A2Angular", planned_cases=planned_cases, skipped_cases=skipped_cases, terminal_reporter=terminal_reporter, progress_test_id=progress_test_id, checks=checks, diagnostics=diagnostics)
    try:
        planned = monitor.cases()
        operational_filial = None
        if planned:
            first_number = planned[0]["number"]
            operation = "Admin avtorizatsiyasi"
            started_at = time.monotonic()
            try:
                with allure.step(f"Suite precondition | {operation}"):
                    authorization(page, who="admin")
            except (AssertionError, PlaywrightError) as exc:
                monitor.record_precondition_failure(
                    operation,
                    exc,
                    affected_case_number=first_number,
                    started_at=started_at,
                )
                return

            operation = "Legacy shellni 'Администрирование' filialiga o'tkazish"
            started_at = time.monotonic()
            try:
                with allure.step(f"Suite precondition | {operation}"):
                    BasePage(page).switch_filial(name="Администрирование")
            except (AssertionError, PlaywrightError) as exc:
                monitor.record_precondition_failure(
                    operation,
                    exc,
                    affected_case_number=first_number,
                    started_at=started_at,
                )
                return

            operational_cases = monitor.cases(section="operational")
            if operational_cases:
                operation = "Operatsion filialni aniqlash"
                started_at = time.monotonic()
                try:
                    with allure.step(f"Suite precondition | {operation}"):
                        operational_filial = first_operational_filial(page)
                except (AssertionError, PlaywrightError) as exc:
                    monitor.record_precondition_failure(
                        operation,
                        exc,
                        affected_case_number=operational_cases[0]["number"],
                        started_at=started_at,
                    )
                    return
                monitor.update_filial(OPERATIONAL_PLACEHOLDER, operational_filial)

            operation = "A2 dashboard shellga kirish"
            started_at = time.monotonic()
            try:
                with allure.step(f"Suite precondition | {operation}"):
                    page.goto(
                        f"{company_url()}/a2/trade/intro/dashboard",
                        wait_until="domcontentloaded",
                        timeout=30_000,
                    )
                    AngularBasePage(page).wait_for_loader(timeout=30_000)
            except (AssertionError, PlaywrightError) as exc:
                monitor.record_precondition_failure(
                    operation,
                    exc,
                    affected_case_number=first_number,
                    started_at=started_at,
                )
                return

        all_cases = monitor.planned_cases + monitor.skipped_cases
        navbar_tabs = []
        for case in all_cases:
            navbar_tab = case["navbar_tab"]
            if navbar_tab not in navbar_tabs:
                navbar_tabs.append(navbar_tab)

        angular = AngularBasePage(page)
        current_filial = None
        for navbar_tab in navbar_tabs:
            with allure.step(f"Navbar tab | {navbar_tab}"):
                tab_cases = [
                    case for case in all_cases if case["navbar_tab"] == navbar_tab
                ]
                menu_columns = []
                for case in tab_cases:
                    menu_column = case.get("menu_column")
                    if menu_column not in menu_columns:
                        menu_columns.append(menu_column)

                for menu_column in menu_columns:
                    with allure.step(f"Menu column | {menu_column or '<ustunsiz>'}"):
                        sections = (
                            ("admin", "Администрирование"),
                            ("operational", operational_filial),
                        )
                        for section, target_filial in sections:
                            cases = [
                                case
                                for case in monitor.cases(section=section)
                                if case["navbar_tab"] == navbar_tab
                                and case.get("menu_column") == menu_column
                            ]
                            if not cases:
                                continue
                            if current_filial != target_filial:
                                operation = f"A2 shellni '{target_filial}' filialiga o'tkazish"
                                started_at = time.monotonic()
                                try:
                                    with allure.step(f"Suite precondition | {operation}"):
                                        angular.switch_filial(name=target_filial)
                                except (AssertionError, PlaywrightError) as exc:
                                    monitor.record_precondition_failure(
                                        operation,
                                        exc,
                                        affected_case_number=cases[0]["number"],
                                        started_at=started_at,
                                    )
                                    return
                                current_filial = target_filial
                            run_form_cases(page, cases, monitor=monitor)

                        skipped = [
                            case
                            for case in monitor.skipped_cases
                            if case["navbar_tab"] == navbar_tab
                            and case.get("menu_column") == menu_column
                        ]
                        if skipped:
                            with allure.step("Ataylab skip qilingan menu itemlar"):
                                for case in skipped:
                                    with allure.step(f"Menu item | {case['label']} | SKIPPED"):
                                        allure.attach(
                                            case["reason"],
                                            name="Skip sababi",
                                            attachment_type=allure.attachment_type.TEXT,
                                        )
    finally:
        with allure.step(f"{len(planned_cases)} ta A2 forma natijasini jamlash"):
            results = monitor.finish()
    return results


@allure.title("A2Angular")
def test_a2_angular_forms(page, pytestconfig, request):
    run_a2_angular_forms(page, progress_test_id=request.node.name, terminal_reporter=pytestconfig.pluginmanager.get_plugin("terminalreporter"))
