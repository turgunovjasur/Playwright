# A2 formalar — filial + real user track (BARCHASI ADMIN profil)

Yangi (a2) formalar eski AngularJS menyu ustiga qo'shilgan; eski menyudan bosilganda `{company_url}/a2/{path}`
ga to'liq sahifa ochiladi.

> **ASOSIY QOIDA:** Eski **angular menyu orqali ochiladigan a2 formalar — barchasi ADMIN formalar.**
> Ular uchun alohida "head" profil / alohida head test KERAK EMAS. Hammasi bitta admin test'da
> (`tests/smoke/test_forms/test_a2_angular_forms.py`) yig'iladi.

Bu fayl har formani **qaysi filial** (operatsion `filial-pw{code}` vs "Администрирование") va **real user qanday
yo'l bilan** ochishini guruhlab ko'rsatadi.

- **LIVE tasdiqlangan** — `test_a2_angular_forms.py`, 2026-07-27, red_test @ app3.greenwhite.uz/xtrade, 22/22 passed.
- **Hali live tasdiqlanmagan** formalar pastda alohida guruhда — treklar hujjat asosida, testга qo'shilganда tasdiqlanadi.

## Ochish patternlari (real user track)

- **LEAF** — menyu: `Tab` bosiladi → `«Leaf»` bosiladi (a2 ga to'liq sahifa). Flow: `navigate_to_a2(page, tab, path)`.
  Leaf selektor: `a.menu-link[href$="/a2/{path}"]`. Sub-kategoriya (`h3.menu-heading`) ni alohida ochish shart emas.
- **LIST-ACTION** — list (LEAF) ochilib: `«Создать»` bosiladi (+add), yoki qator bosilib chiqadigan `«Изменить»` bosiladi (+edit).
  Ochilish signali: main'da `«Сохранить»` tugmasi.
- **SIBLING** — eski (a2-emas) forma menyudan ochilib, uning subheader'idagi sub-link (`a[ng-click*="openSibling"]`)
  bosiladi → `/a2/{path}` ochiladi. Bu formalar **angular menyu modelida ko'rinmaydi** — eski formani OCHIB topiladi.

## Filial qoidasi

Eski menyu filialga bog'liq — har filialда boshqacha formalar. Login'дан keyingi default filial **"Администрирование"**.
Operatsion formalar `filial-pw{code}` (yoki har qanday operatsion filial) da, admin/справочник formalar "Администрирование" da.
Ochilgani signali: `document.title` "Smartup Online" (shell) dan forma nomiga o'zgaradi (dashboard/report ham async).

# =====================================================================================================================
# LIVE TASDIQLANGAN  (test_a2_admin_forms.py — 2026-07-08, red_test — 24/24)
# =====================================================================================================================

## operatsion filial (filial-pw{code}) — LEAF (19 ta)

| path | user track (Tab → Sub → Leaf) |
|---|---|
| trade/txs/external_settings | Главное → Дополнительное → «Настройки интеграции со сторонним ПО» |
| trade/tvt/visit_list | Продажа → Визиты → «Визиты» |
| trade/tvt/user_locations | Продажа → Визиты → «Отслеживание пользователей» |
| trade/tph/user_tracking | Продажа → Визиты → «Отслеживание мобильных представителей» |
| trade/tdeal/commercial_dashboard | Продажа → Отчеты по продажам → «Коммерческий дашборд» |
| trade/rep/mbi/tvt/visit | Продажа → Отчеты по визитам → «Конструктор отчётов по визитам» |
| trade/tdeal/logistics_list | Склад → Справочники → «Логистика» |
| anor/rep/mbi/mkw/movement | Склад → Отчеты → «Конструктор отчетов по внутр. перемещениям» |
| anor/rep/mbi/mkw/purchase_request | Склад → Отчеты → «Конструктор отчетов по запросам на закуп» |
| anor/rep/mbi/mkw/purchase | Склад → Отчеты → «Конструктор отчетов по закупкам» |
| anor/rep/mbi/mkw/input | Склад → Отчеты → «Конструктор отчетов по поступлениям» |
| anor/rep/mbi/mkw/writeoff | Склад → Отчеты → «Конструктор отчетов по списанию» |
| anor/rep/mbi/mfm/movement_request | Склад → Отчеты → «Конструктор отчетов по запросам на межорг. перемещения» |
| anor/rep/mbi/mfm/movement | Склад → Отчеты → «Конструктор отчетов по межорг. перемещениям» |
| anor/rep/mbi/mkcs/operation | Финансы → Отчеты → «Конструктор отчетов по финансам» |
| anor/rep/mkr/pnl | Финансы → Отчеты → «PnL» |
| trade/rep/mbi/tmcg/shelf_share | Торговый маркетинг → Отчеты → «Конструктор отчётов по доле на полке» |
| anor/rep/mbi/mqpf/request | Оборудование → Дополнительное → «Конструктор отчетов по заявкам на оборудование» |
| biruni/plg/plugin_catalog | Плагин → Документы → «Plugin Marketplace» |

## operatsion filial — SIBLING (2 ta)

| path | user track (Tab → «Eski forma» → sub-link) |
|---|---|
| anor/rep/mbi/mcg/action | Справочники → Маркетинг → «Акции» (eski `anor/mcg/action_list`) → sub-link «Конструктор отчетов по акциям» |
| anor/mkw/marking_stocktaking/marking_stocktaking_list | Склад → Документы → «Инвентаризации» (eski `anor/mkw/stocktaking/stocktaking_list`) → sub-link «Инвентаризация КМ» |

## Администрирование filial — LEAF + LIST-ACTION (3 ta)

| path | user track |
|---|---|
| biruni/kauth/company_client_list | Главное → Дополнительное → «Клиенты OAuth2 сервера для компании» (LEAF) |
| biruni/kauth/company_client+add | «Клиенты OAuth2 …» list → «Создать» |
| biruni/kauth/company_client+edit | «Клиенты OAuth2 …» list → qator bosiladi → «Изменить» |

# =====================================================================================================================
# HALI LIVE TASDIQLANMAGAN ADMIN FORMALAR  (hujjat asosida — testга qo'shilganда tasdiqlanadi)
# =====================================================================================================================

Bular ham ADMIN formalar (angular menyu orqali ochiladi). Ba'zilari faqat head KOMPANIYASIда ("нет доступа" boshqa
kompaniyada) mavjud bo'lishi mumkin — bu profil emas, kompaniya masalasi; forma baribir admin menyusidan ochiladi.

## Администрирование filial — LEAF

| path | user track (hujjatdan) |
|---|---|
| biruni/kauth/client_list | Главное → Дополнительное → «Клиенты API/OAuth2 сервера» |
| biruni/kauth/security_settings | Главное → Дополнительное → «Настройки безопасности» |
| biruni/md/audit_setting | Главное → Дополнительное → «Настройки истории изменений» |
| biruni/md/company_list | Главное → Дополнительное → «Компании» |
| biruni/md/contact_info_setting | Главное → Дополнительное → «Контактная информация» |
| biruni/md/feedback_list | Главное → Дополнительное → «Фидбеки» |
| biruni/md/log_list | Главное → Дополнительное → «Логи» |
| biruni/md/query_executor | Главное → Дополнительное → «Запросы к базе данных» |
| biruni/md/request_limit_template_list | Главное → Дополнительное → «Шаблоны лимитов» |
| biruni/ms/announcement_list | Главное → Админ → «Объявления» |

## Администрирование filial — LIST-ACTION (yuqoridagi listlardan)

| path | user track (hujjatdan) |
|---|---|
| biruni/kauth/client+add | «Клиенты API/OAuth2 …» list → «Создать» |
| biruni/kauth/client+edit | «Клиенты API/OAuth2 …» list → qator → «Изменить» |
| biruni/md/company_add | «Компании» list → «Создать» |
| biruni/md/company_edit | «Компании» list → qator → «Изменить» |
| biruni/md/company_view | «Компании» list → qator → «Просмотр» |
| biruni/md/request_limit_template+add | «Шаблоны лимитов» list → «Создать» |
| biruni/md/request_limit_template+edit | «Шаблоны лимитов» list → qator → «Изменить» |
| biruni/md/request_limit_template_view | «Шаблоны лимитов» list → qator → «Просмотр» |
| biruni/md/request_limit_template_audit_details | «Шаблоны лимитов» → история → detali |
| biruni/ms/announcement+add | «Объявления» list → «Создать» |
| biruni/ms/announcement+copy | «Объявления» list → qator → «Копировать» |
| biruni/ms/announcement+edit | «Объявления» list → qator → «Изменить» |

## operatsion filial — LEAF

| path | user track (hujjatdan) |
|---|---|
| billing/blda/operational_dashboard | Главное → Основное → «Операционный дашборд» |

## Track hali aniqlanmagan (URL test qamraydi)

| path | holat |
|---|---|
| anor/rep/mbi/mfa/purchase | menyuda topilmadi (user track kutilmoqda) |
| biruni/ker/setting+add, +edit | ker/setting_list yo'q; Easy Report shablonidan ochilishi mumkin (tekshirilmagan) |
| biruni/ker/head_template_list+attach | «Доступные шаблоны» — real user track tekshirilmagan |
| biruni/md/company_audit_info_audit, +_details | kompaniya «История изменений» tugmasidan ochilishi mumkin (tekshirilmagan) |

# =====================================================================================================================
# ESLATMALAR
# =====================================================================================================================

- Barcha a2 formalar ADMIN — angular menyu orqali ochiladi. Alohida head test yo'q; hammasi `test_a2_angular_forms.py` da.
- Forma "menyuda yo'q" degan xulosani FAQAT angular menyu modelini skanlab chiqarma — SIBLING formalar (mcg/action,
  marking) menyu modelida ko'rinmaydi, lekin eski formaning subheader sub-link'i orqali ochiladi. Shubha bo'lsa eski/qardosh
  formani OCHIB, subheader `openSibling` sub-linklarини ham tekshir.
- Ochilgani signali: `document.title` shell nomidan forma nomiga o'zgaradi. `+edit` da title path bo'lib qolishi mumkin —
  main'da «Сохранить» borligi ochilgan demak. `heading`/`mainLen` ga tayanma (async formalarda false-negative).
- Batafsil arxitektura, selektorlar va test tafsiloti: `skills/smartup-guide/references/a2-migrated-forms.md`.
