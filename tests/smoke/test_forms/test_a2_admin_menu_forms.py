"""Admin formalarni real navbar → menu column → menu item yo'li orqali tekshirish.

Bu fayl formalarni loop orqali aylantirmaydi. Legacy dashboarddan birinchi A2
formaga ``BasePage``, A2 shell ichidagi keyingi formalarga ``AngularBasePage``
orqali o'tiladi. Menu ichidan ochilgan parent forma yuqorisidagi linklar
``page_links`` orqali ketma-ket bosiladi. Har bir navigatsiyadan keyin title va
URL test ichidagi alohida ``AngularBasePage.expect_page`` bilan tekshiriladi.
Allure'da filial parent step, uning ichida har bir forma raqamlangan step bo'ladi.
Forma stepida filial, tab, menu va forma; ichki steplarda navigatsiya yo'li,
kutilgan URL va haqiqiy URL ko'rinadi. Terminal yakunida ham shu maydonlar bilan
22 qatorli summary chiqariladi.

A2 FORMALAR INVENTARI — kelajakdagi menu-track testlar uchun
==============================================================

Manba: ``test_a2_new_forms.py::A2_FORMS`` va ``new_forms.md``.
Jami: 53 | ✅ YOZILGAN: 22 | ⬜ QOLGAN: 31.

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

10. ✅ YOZILGAN | direct | ``anor/mkw/marking_stocktaking/marking_stocktaking_list``
    Title: Инвентаризация КМ
    User trace: Склад → Документы → Инвентаризации → Инвентаризация КМ

11. ✅ YOZILGAN | direct | ``anor/rep/mkr/pnl``
    Title: PnL
    User trace: Финансы → Отчеты → PnL

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
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.flow import (
    build_form_result,
    finish_form_results,
    first_operational_filial,
    form_navigation_track,
    form_step_title,
    format_form_result,
    print_form_result,
)
from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


pytestmark = [
    pytest.mark.smoke_group("A2 Admin Menu Forms"),
    allure.epic("Smoke"),
    allure.feature("A2 New Forms"),
    allure.story("Aniq menyu qadamlari orqali ochilish"),
]

FORM_TIMEOUT = 10_000

# ----------------------------------------------------------------------------------------------------------------------


def _check_form(
    page,
    *,
    number,
    filial,
    navbar_tab,
    menu_column,
    menu_item,
    page_links=None,
    report=True,
):
    """Joriy legacy/A2 shell menyusidan click qiladi; sahifani tekshirmaydi."""
    links = [] if page_links is None else list(page_links)
    title = links[-1] if links else menu_item
    track = form_navigation_track(
        navbar_tab=navbar_tab,
        menu_column=menu_column,
        menu_item=menu_item,
        page_links=links,
    )
    step_name = (
        form_step_title(
            number=number,
            filial=filial,
            navbar_tab=navbar_tab,
            menu_column=menu_column,
            title=title,
        )
        if report
        else f"A2 shellga kirish | Yo'l: {track}"
    )

    with allure.step(step_name):
        with allure.step(f"Navigatsiya | Yo'l: {track}"):
            if "/a2/" in page.url:
                AngularBasePage(page).navigate_to(
                    tab=navbar_tab,
                    name=menu_item,
                    timeout=FORM_TIMEOUT,
                )
                for page_link in links:
                    link = page.get_by_role(
                        "link",
                        name=page_link,
                        exact=True,
                    ).filter(visible=True).first
                    expect(link).to_be_visible(timeout=FORM_TIMEOUT)
                    link.click()
            else:
                BasePage(page).navigate_to_form(
                    navbar_tab=navbar_tab,
                    menu_column=menu_column,
                    menu_item=menu_item,
                    page_links=links or None,
                    timeout=FORM_TIMEOUT,
                )

    return {
        "number": number,
        "filial": filial,
        "navbar_tab": navbar_tab,
        "menu_column": menu_column,
        "menu_item": menu_item,
        "page_links": links,
    }


# ----------------------------------------------------------------------------------------------------------------------


def _expect_form_page(angular, *, report, results, title, url, ready=None):
    """A2 formani tekshiradi va terminal/Allure uchun tushunarli natija yozadi."""
    try:
        with allure.step(
            f'Tekshiruv | Forma: "{title}" | Kutilgan URL: "{url}"'
        ):
            angular.expect_page(
                title=title,
                url=url,
                ready=ready,
            )
    except (AssertionError, PlaywrightTimeoutError) as exc:
        result = build_form_result(
            **report,
            title=title,
            expected_path=url,
            actual_url=angular.page.url,
            ok=False,
            detail=" ".join(str(exc).split()),
        )
        results.append(result)
        allure.attach(
            format_form_result(result),
            name=f"{report['number']:03d} | {title} | xato tafsilotlari",
            attachment_type=allure.attachment_type.TEXT,
        )
        try:
            allure.attach(
                angular.page.screenshot(full_page=True),
                name=f"{report['number']:03d}-{title}-failure",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        print_form_result(result)
        raise
    else:
        result = build_form_result(
            **report,
            title=title,
            expected_path=url,
            actual_url=angular.page.url,
            ok=True,
        )
        results.append(result)
        with allure.step(f"Natija: OCHILDI | Haqiqiy URL: {angular.page.url}"):
            pass
        print_form_result(result)
        return result


# ----------------------------------------------------------------------------------------------------------------------


def run_a2_admin_menu_forms(page, *, terminal_reporter=None):
    """Testcase: admin formalarni real va ma'noli UI qadamlari orqali ochish.

    1. Legacy va A2 shellni ``Администрирование`` filialiga sinxronlash.
    2. OAuth2 list formani tekshirish va shu formadan operatsion filialga o'tish.
    3. Operatsion filialdagi formalarni ortga qaytmasdan ketma-ket tekshirish.
    4. Parent forma yuqorisidagi page link orqali ochiladigan formalarni tekshirish.
    5. Filial, tab, menu, forma va URLlar bilan terminal/Allure summary chiqarish.

    OAuth2 add/edit formalar hozircha bu testga kiritilmagan:
    ular alohida qo'lda tekshirilib, aniq sabab tasdiqlangach qo'shiladi.
    """
    base = BasePage(page)
    angular = AngularBasePage(page)
    results = []

    with allure.step("1 - 'Администрирование' filialidagi OAuth2 list forma"):
        base.switch_filial(name="Администрирование")
        operational_filial = first_operational_filial(page)

        with allure.step("01 — Клиенты OAuth2 сервера для компании"):
            _check_form(
                page,
                number=1,
                filial="Администрирование",
                navbar_tab="Главное",
                menu_column="Дополнительное",
                menu_item="Клиенты OAuth2 сервера для компании",
                report=False,
            )
            with allure.step(
                "A2 filial: 'Администрирование' bilan sinxronlash va formani qayta ochish"
            ):
                angular.switch_filial(name="Администрирование")
                report = _check_form(
                    page,
                    number=1,
                    filial="Администрирование",
                    navbar_tab="Главное",
                    menu_column="Дополнительное",
                    menu_item="Клиенты OAuth2 сервера для компании",
                )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Клиенты OAuth2 сервера для компании",
                url="biruni/kauth/company_client_list",
                ready="app-company-client-list",
            )

    with allure.step(f"2 - '{operational_filial}' filialidagi menu formalar"):
        angular.switch_filial(name=operational_filial)

        with allure.step("02 — Настройки интеграции со сторонним ПО"):
            report = _check_form(
                page,
                number=2,
                filial=operational_filial,
                navbar_tab="Главное",
                menu_column="Дополнительное",
                menu_item="Настройки интеграции со сторонним ПО",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Настройки интеграции со сторонним ПО",
                url="trade/txs/external_settings",
            )

        with allure.step("03 — Визиты"):
            report = _check_form(
                page,
                number=3,
                filial=operational_filial,
                navbar_tab="Продажа",
                menu_column="Визиты",
                menu_item="Визиты",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Визиты",
                url="trade/tvt/visit_list",
            )

        with allure.step("04 — Отслеживание пользователей"):
            report = _check_form(
                page,
                number=4,
                filial=operational_filial,
                navbar_tab="Продажа",
                menu_column="Визиты",
                menu_item="Отслеживание пользователей",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Отслеживание пользователей",
                url="trade/tvt/user_locations",
            )

        with allure.step("05 — Отслеживание мобильных представителей"):
            report = _check_form(
                page,
                number=5,
                filial=operational_filial,
                navbar_tab="Продажа",
                menu_column="Визиты",
                menu_item="Отслеживание мобильных представителей",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Отслеживание мобильных представителей",
                url="trade/tph/user_tracking",
            )

        with allure.step("06 — Коммерческий дашборд"):
            report = _check_form(
                page,
                number=6,
                filial=operational_filial,
                navbar_tab="Продажа",
                menu_column="Отчеты по продажам",
                menu_item="Коммерческий дашборд",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Коммерческий дашборд",
                url="trade/tdeal/commercial_dashboard",
            )

        with allure.step("07 — Конструктор отчётов по визитам"):
            report = _check_form(
                page,
                number=7,
                filial=operational_filial,
                navbar_tab="Продажа",
                menu_column="Отчеты по визитам",
                menu_item="Конструктор отчётов по визитам",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчётов по визитам",
                url="trade/rep/mbi/tvt/visit",
            )

        with allure.step("08 — Логистика"):
            report = _check_form(
                page,
                number=8,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Справочники",
                menu_item="Логистика",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Логистика",
                url="trade/tdeal/logistics_list",
            )

        with allure.step("09 — Конструктор отчетов по внутр. перемещениям"):
            report = _check_form(
                page,
                number=9,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по внутр. перемещениям",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по внутр. перемещениям",
                url="anor/rep/mbi/mkw/movement",
            )

        with allure.step("10 — Конструктор отчетов по запросам на закуп"):
            report = _check_form(
                page,
                number=10,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по запросам на закуп",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по запросам на закуп",
                url="anor/rep/mbi/mkw/purchase_request",
            )

        with allure.step("11 — Конструктор отчетов по закупкам"):
            report = _check_form(
                page,
                number=11,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по закупкам",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по закупкам",
                url="anor/rep/mbi/mkw/purchase",
            )

        with allure.step("12 — Конструктор отчетов по поступлениям"):
            report = _check_form(
                page,
                number=12,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по поступлениям",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по поступлениям",
                url="anor/rep/mbi/mkw/input",
            )

        with allure.step("13 — Конструктор отчетов по списанию"):
            report = _check_form(
                page,
                number=13,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по списанию",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по списанию",
                url="anor/rep/mbi/mkw/writeoff",
            )

        with allure.step("14 — Конструктор отчетов по запросам на межорг. перемещения"):
            report = _check_form(
                page,
                number=14,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по запросам на межорг. перемещения",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по запросам на межорг. перемещения",
                url="anor/rep/mbi/mfm/movement_request",
            )

        with allure.step("15 — Конструктор отчетов по межорг. перемещениям"):
            report = _check_form(
                page,
                number=15,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по межорг. перемещениям",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по межорг. перемещениям",
                url="anor/rep/mbi/mfm/movement",
            )

        with allure.step("16 — Конструктор отчетов по финансам"):
            report = _check_form(
                page,
                number=16,
                filial=operational_filial,
                navbar_tab="Финансы",
                menu_column="Отчеты",
                menu_item="Конструктор отчетов по финансам",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по финансам",
                url="anor/rep/mbi/mkcs/operation",
            )

        with allure.step("17 — PnL"):
            report = _check_form(
                page,
                number=17,
                filial=operational_filial,
                navbar_tab="Финансы",
                menu_column="Отчеты",
                menu_item="PnL",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="PnL",
                url="anor/rep/mkr/pnl",
            )

        with allure.step("18 — Конструктор отчётов по доле на полке"):
            report = _check_form(
                page,
                number=18,
                filial=operational_filial,
                navbar_tab="Торговый маркетинг",
                menu_column="Отчеты",
                menu_item="Конструктор отчётов по доле на полке",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчётов по доле на полке",
                url="trade/rep/mbi/tmcg/shelf_share",
            )

        with allure.step("19 — Конструктор отчетов по заявкам на оборудование"):
            report = _check_form(
                page,
                number=19,
                filial=operational_filial,
                navbar_tab="Оборудование",
                menu_column="Дополнительное",
                menu_item="Конструктор отчетов по заявкам на оборудование",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по заявкам на оборудование",
                url="anor/rep/mbi/mqpf/request",
            )

        with allure.step("20 — Plugin Marketplace"):
            report = _check_form(
                page,
                number=20,
                filial=operational_filial,
                navbar_tab="Плагин",
                menu_column=None,
                menu_item="Plugin Marketplace",
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Plugin Marketplace",
                url="biruni/plg/plugin_catalog",
            )

    with allure.step("3 - Parent forma yuqorisidagi page link orqali ochiladigan formalar"):
        with allure.step("21 — Конструктор отчетов по акциям"):
            report = _check_form(
                page,
                number=21,
                filial=operational_filial,
                navbar_tab="Справочники",
                menu_column="Маркетинг",
                menu_item="Акции",
                page_links=["Конструктор отчетов по акциям"],
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Конструктор отчетов по акциям",
                url="anor/rep/mbi/mcg/action",
            )

        with allure.step("22 — Инвентаризация КМ"):
            report = _check_form(
                page,
                number=22,
                filial=operational_filial,
                navbar_tab="Склад",
                menu_column="Документы",
                menu_item="Инвентаризации",
                page_links=["Инвентаризация КМ"],
            )
            _expect_form_page(
                angular,
                report=report,
                results=results,
                title="Инвентаризация КМ",
                url="anor/mkw/marking_stocktaking/marking_stocktaking_list",
            )

    with allure.step("4 - 22 ta A2 forma natijalarini jamlash"):
        finish_form_results(results, terminal_reporter=terminal_reporter)


# ----------------------------------------------------------------------------------------------------------------------


@allure.title("A2 admin formalar — aniq menyu qadamlari orqali ochilish smoke")
def test_a2_admin_menu_forms(page, pytestconfig):
    authorization(page, who="admin")
    run_a2_admin_menu_forms(
        page,
        terminal_reporter=pytestconfig.pluginmanager.get_plugin(
            "terminalreporter"
        ),
    )
