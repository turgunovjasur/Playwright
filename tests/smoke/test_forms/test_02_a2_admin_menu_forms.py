"""Admin A2 formalarni deklarativ reja va markaziy monitor orqali tekshirish.

Case ro'yxati bir xil ``FormCase`` modeliga aylantiriladi va ketma-ket loopda
real navbar → menu → page-link yo'li orqali ochiladi. Har forma title, URL,
readiness, loader, UI error va kontent holati bilan mustaqil tahlil qilinadi.
Allure, terminal progress va yakuniy JSON aynan shu monitor natijasidan quriladi.

A2 FORMALAR INVENTARI — kelajakdagi menu-track testlar uchun
==============================================================

Manba: ``test_a2_new_forms.py::A2_FORMS`` va ``new_forms.md``.
Jami: 53 | ✅ YOZILGAN: 21 | ⏸ VAQTINCHA SKIP: 1 | ⬜ QOLGAN: 31.

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

ADMIN profil → operatsion filial (24 ta)
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

18. ✅ YOZILGAN | direct | ``anor/rep/mbi/mcg/action``
    Title: Конструктор отчетов по акциям
    User trace: Справочники → Маркетинг → Акции → Конструктор отчетов по акциям

19. ✅ YOZILGAN | direct | ``anor/rep/mbi/mfm/movement``
    Title: Конструктор отчетов по межорг. перемещениям
    User trace: Склад → Отчеты → Конструктор отчетов по межорг. перемещениям

20. ✅ YOZILGAN | direct | ``anor/rep/mbi/mfm/movement_request``
    Title: Конструктор отчетов по запросам на межорг. перемещения
    User trace: Склад → Отчеты → Конструктор отчетов по запросам на межорг. перемещения

21. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/input``
    Title: Конструктор отчетов по поступлениям
    User trace: Склад → Отчеты → Конструктор отчетов по поступлениям

22. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/movement``
    Title: Конструктор отчетов по внутр. перемещениям
    User trace: Склад → Отчеты → Конструктор отчетов по внутр. перемещениям

23. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/purchase``
    Title: Конструктор отчетов по закупкам
    User trace: Склад → Отчеты → Конструктор отчетов по закупкам

24. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/purchase_request``
    Title: Конструктор отчетов по запросам на закуп
    User trace: Склад → Отчеты → Конструктор отчетов по запросам на закуп

25. ✅ YOZILGAN | direct | ``anor/rep/mbi/mkw/writeoff``
    Title: Конструктор отчетов по списанию
    User trace: Склад → Отчеты → Конструктор отчетов по списанию

26. ✅ YOZILGAN | direct | ``anor/rep/mbi/mqpf/request``
    Title: Конструктор отчетов по заявкам на оборудование
    User trace: Оборудование → Дополнительное → Конструктор отчетов по заявкам на оборудование

27. ✅ YOZILGAN | direct | ``trade/rep/mbi/tmcg/shelf_share``
    Title: Конструктор отчётов по доле на полке
    User trace: Торговый маркетинг → Отчеты → Конструктор отчётов по доле на полке

28. ✅ YOZILGAN | direct | ``trade/rep/mbi/tvt/visit``
    Title: Конструктор отчётов по визитам
    User trace: Продажа → Отчеты по визитам → Конструктор отчётов по визитам

29. ⬜ QOLGAN | direct | ``anor/rep/mbi/mfa/purchase``
    Title: Конструктор по закупкам (финансы)
    User trace: finance proyektda ekan, trade proyektda chiqmaydi

30. ✅ YOZILGAN | direct | ``trade/tvt/visit_list``
    Title: Визиты
    User trace: Продажа → Визиты → Визиты

HEAD profil → ``Администрирование`` filial (22 ta)
-------------------------------------------------

31. ⬜ QOLGAN | direct | ``biruni/kauth/client_list``
    Title: Клиенты API/OAuth2 сервера
    User trace: Главное → Дополнительное → Клиенты API/OAuth2 сервера

32. ⬜ QOLGAN | direct | ``biruni/kauth/client+add``
    Title: Клиент API/OAuth2 (создание)
    User trace: client_list → Создать

33. ⬜ QOLGAN | via_list | ``biruni/kauth/client+edit``
    Title: Клиент API/OAuth2 (изменение)
    Parent: ``biruni/kauth/client_list``
    User trace: client_list → qator → Изменить

34. ⬜ QOLGAN | direct | ``biruni/kauth/security_settings``
    Title: Настройки безопасности
    User trace: Главное → Дополнительное → Настройки безопасности

35. ⬜ QOLGAN | direct | ``biruni/md/audit_setting``
    Title: Настройки истории изменений
    User trace: Главное → Дополнительное → Настройки истории изменений

36. ⬜ QOLGAN | direct | ``biruni/md/company_list``
    Title: Компании
    User trace: Главное → Дополнительное → Компании

37. ⬜ QOLGAN | direct | ``biruni/md/company_add``
    Title: Компания (создание)
    User trace: company_list → Создать

38. ⬜ QOLGAN | via_list | ``biruni/md/company_edit``
    Title: Компания (изменение)
    Parent: ``biruni/md/company_list``
    User trace: company_list → qator → Изменить

39. ⬜ QOLGAN | via_list | ``biruni/md/company_view``
    Title: Компания (просмотр)
    Parent: ``biruni/md/company_list``
    User trace: company_list → qator → Просмотр

40. ⬜ QOLGAN | direct | ``biruni/md/contact_info_setting``
    Title: Контактная информация
    User trace: Главное → Дополнительное → Контактная информация

41. ⬜ QOLGAN | direct | ``biruni/md/feedback_list``
    Title: Фидбеки
    User trace: Главное → Дополнительное → Фидбеки

42. ⬜ QOLGAN | direct | ``biruni/md/log_list``
    Title: Логи
    User trace: Главное → Дополнительное → Логи

43. ⬜ QOLGAN | direct | ``biruni/md/query_executor``
    Title: Запросы к базе данных
    User trace: Главное → Дополнительное → Запросы к базе данных

44. ⬜ QOLGAN | direct | ``biruni/md/request_limit_template_list``
    Title: Шаблоны лимитов (список)
    User trace: Главное → Дополнительное → Шаблоны лимитов

45. ⬜ QOLGAN | direct | ``biruni/md/request_limit_template+add``
    Title: Шаблоны лимитов (создание)
    User trace: request_limit_template_list → Создать

46. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template+edit``
    Title: Шаблоны лимитов (изменение)
    Parent: ``biruni/md/request_limit_template_list``
    User trace: request_limit_template_list → qator → Изменить

47. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template_view``
    Title: Шаблоны лимитов (просмотр)
    Parent: ``biruni/md/request_limit_template_list``
    User trace: request_limit_template_list → qator → Просмотр

48. ⬜ QOLGAN | via_list | ``biruni/md/request_limit_template_audit_details``
    Title: Подробности истории шаблона лимитов
    Parent: ``biruni/md/request_limit_template_list``
    User trace: Шаблоны лимитов → История изменений → detail

49. ⬜ QOLGAN | direct | ``biruni/ms/announcement_list``
    Title: Объявления
    User trace: Главное → Админ → Объявления

50. ⬜ QOLGAN | direct | ``biruni/ms/announcement+add``
    Title: Объявление (создание)
    User trace: announcement_list → Создать

51. ⬜ QOLGAN | via_list | ``biruni/ms/announcement+copy``
    Title: Объявление (копирование)
    Parent: ``biruni/ms/announcement_list``
    User trace: announcement_list → qator → Копировать

52. ⬜ QOLGAN | via_list | ``biruni/ms/announcement+edit``
    Title: Объявление (изменение)
    Parent: ``biruni/ms/announcement_list``
    User trace: announcement_list → qator → Изменить

HEAD profil → operatsion filial (1 ta)
--------------------------------------

53. ⬜ QOLGAN | direct | ``billing/blda/operational_dashboard``
    Title: Операционный дашборд
    User trace: Главное → Основное → Операционный дашборд
"""

import allure
import pytest

from tests.smoke.flows.flow_authorization import authorization, company_url
from tests.smoke.test_forms.flow import (
    first_operational_filial,
    run_form_cases,
)
from tests.smoke.test_forms.form_monitor import FormMonitor, build_form_case_plan
from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


pytestmark = [
    pytest.mark.smoke_group(
        "A2 Admin Menu Forms",
        setup_independent=True,
    ),
    allure.epic("Smoke"),
    allure.feature("A2 New Forms"),
    allure.story("Aniq menyu qadamlari orqali ochilish"),
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


def _open_a2_dashboard_shell(page, angular):
    """Target formani bootstrap uchun ikki marta ochmasdan A2 shellga kiradi."""
    page.goto(
        f"{company_url()}/a2/trade/intro/dashboard",
        wait_until="domcontentloaded",
        timeout=30_000,
    )
    angular.wait_for_loader(timeout=30_000)


# ----------------------------------------------------------------------------------------------------------------------


def run_a2_admin_menu_forms(page, *, terminal_reporter=None):
    """21 ta active A2 formani markaziy monitor bilan kuzatib tekshiradi."""
    base = BasePage(page)
    angular = AngularBasePage(page)
    operational_placeholder = "<operatsion filial>"

    admin_cases = build_form_case_plan(
        ADMIN_A2_FORMS,
        start_number=1,
        filial="Администрирование",
        section="admin",
        shell="a2",
    )
    operational_cases = build_form_case_plan(
        OPERATIONAL_A2_FORMS,
        start_number=1 + len(admin_cases),
        filial=operational_placeholder,
        section="operational-menu",
        shell="a2",
    )
    page_link_cases = build_form_case_plan(
        PAGE_LINK_A2_FORMS,
        start_number=1 + len(admin_cases) + len(operational_cases),
        filial=operational_placeholder,
        section="operational-page-link",
        shell="a2",
    )
    planned_cases = admin_cases + operational_cases + page_link_cases
    admin_first = admin_cases[0]["number"] if admin_cases else None
    operational_first = operational_cases[0]["number"] if operational_cases else None
    monitor = FormMonitor(
        page,
        suite_name="Forms-02 — A2 admin",
        planned_cases=planned_cases,
        terminal_reporter=terminal_reporter,
        progress_test_id="test_forms_02_a2_admin",
    )

    monitor.precondition(
        "Admin avtorizatsiyasi",
        lambda: authorization(page, who="admin"),
        affected_case_number=admin_first,
    )
    if monitor.blocked:
        monitor.finish()

    monitor.precondition(
        "Legacy shellni 'Администрирование' filialiga o'tkazish",
        lambda: base.switch_filial(name="Администрирование"),
        affected_case_number=admin_first,
    )
    if monitor.blocked:
        monitor.finish()

    operational_filial = monitor.precondition(
        "Operatsion filialni aniqlash",
        lambda: first_operational_filial(page),
        affected_case_number=admin_first,
    )
    if monitor.blocked:
        monitor.finish()
    monitor.update_filial(operational_placeholder, operational_filial)
    admin_cases = monitor.cases(section="admin")
    operational_cases = monitor.cases(section="operational-menu")
    page_link_cases = monitor.cases(section="operational-page-link")

    with allure.step("1 - 'Администрирование' filialidagi OAuth2 list forma"):
        monitor.precondition(
            "A2 dashboard shellga kirish",
            lambda: _open_a2_dashboard_shell(page, angular),
            affected_case_number=admin_first,
        )
        if monitor.blocked:
            monitor.finish()

        monitor.precondition(
            "A2 filialini 'Администрирование' bilan sinxronlash",
            lambda: angular.switch_filial(name="Администрирование"),
            affected_case_number=admin_first,
        )
        if monitor.blocked:
            monitor.finish()

        run_form_cases(page, admin_cases, monitor=monitor)

    monitor.precondition(
        f"A2 shellni '{operational_filial}' filialiga o'tkazish",
        lambda: angular.switch_filial(name=operational_filial),
        affected_case_number=operational_first,
    )
    if monitor.blocked:
        monitor.finish()

    with allure.step(f"2 - '{operational_filial}' filialidagi menu formalar"):
        run_form_cases(page, operational_cases, monitor=monitor)

    with allure.step(
        "3 - Parent forma yuqorisidagi page link orqali ochiladigan formalar"
    ):
        run_form_cases(page, page_link_cases, monitor=monitor)

    with allure.step(f"4 - {len(planned_cases)} ta A2 forma natijalarini jamlash"):
        monitor.finish()


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("A2 admin formalar — aniq menyu qadamlari orqali ochilish smoke")
def test_a2_admin_menu_forms(page, pytestconfig):
    run_a2_admin_menu_forms(
        page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
