# Smartup Knowledge History

Bu fayl faqat superseded qoidalar, eski implementatsiya kontraktlari va tarixiy
verification natijalari uchun. Agent joriy test yoki locator yozishda bu
fayldagi ma'lumotni current truth sifatida ishlatmasin.

## Mundarija

- [Entry formati](#entry-formati)
- [Superseded runner scope](#superseded-runner-scope)
- [Removed Forms Monitor checklari](#removed-forms-monitor-checklari)
- [Superseded Forms Monitor title modeli](#superseded-forms-monitor-title-modeli)
- [Removed runner va test entrypointlari](#removed-runner-va-test-entrypointlari)
- [Removed legacy Scenario 1 catalog](#removed-legacy-scenario-1-catalog)
- [Removed session recovery helper](#removed-session-recovery-helper)
- [Removed BasePage helperlari](#removed-basepage-helperlari)
- [Superseded locator qoidalari](#superseded-locator-qoidalari)
- [Eski server xatti-harakati](#eski-server-xatti-harakati)
- [Superseded Allure server lifecycle](#superseded-allure-server-lifecycle)

## Entry formati

```markdown
### <mavzu>
Status: superseded
Observed: YYYY-MM-DD
Superseded: YYYY-MM-DD
Source: <fayl, trace yoki live UI>
Replaced by: <joriy reference heading yoki kod path>
- Old behavior: <eski qoida>
```

## Superseded Allure server lifecycle

### Global Allure open subprocessi
Status: superseded
Observed: 2026-07
Superseded: 2026-08-24
Source: eski PyCharm/direct pytest reporting hooki
Replaced by: `skills/maintain-test-infra/references/reporting.md#local-allure-lifecycle`
- Old behavior: global Allure CLI Java serveri `allure open` subprocessi orqali
  ochilar va browser yopilgach server processi qolib ketishi mumkin edi.
- Current behavior: project-local Allure Report 3 HTML yaratadi;
  `scripts/open_allure_report.py` heartbeat va grace period bilan lokal static
  server lifecycle'ini boshqaradi.

## Superseded runner scope

### Global smoke/regression scope
Status: superseded
Observed: 2026-05
Superseded: 2026-07
Source: historical smoke skill/reference entries
Replaced by: `scripts/run_tests.py` target modeli va
`skills/smartup-guide/references/smoke-runner.md`
- Old behavior: runner `--regression` yoki `--scope=regression` orqali global
  mode uzatgan.
- Current behavior: global scope konfiguratsiyasi yo'q; suite faqat amaldagi
  smoke targetlari bilan ishlaydi.

### Forms-03 rejasidagi `+add` creation formalari
Status: superseded
Observed: 2026-08-04
Superseded: 2026-08-04
Source: user; `tests/smoke/test_forms/test_02_prodaja_menu_forms.py`
Replaced by:
`skills/smartup-guide/references/legacy-form-navigation.md#продажа-page-link-va-add-inventari-2026-08-04-live`
- Old behavior: Forms-03 rejasiga uchta `+add` ikonka-link case
  (`Заказ (создание)`, `Возврат (создание)`, `Лид (создание)`) kirgan va jami
  41 navigation tekshirilgan; `Возврат (создание)` uchun `allowed_warnings`
  berilgan edi.
- Current behavior: foydalanuvchi qaroriga ko'ra `+add` tekshiruvi olib
  tashlandi; Forms-03 faqat 26 direct + 12 page-link = 38 navigation tekshiradi.

### Leaf-owned legacy forma inventorylari
Status: superseded
Observed: 2026-08-07
Superseded: 2026-08-10
Source: user; eski `tests/smoke/test_forms/test_01_spravochniki_menu_forms.py` va
`tests/smoke/test_forms/test_02_prodaja_menu_forms.py` strukturasi
Replaced by: `tests/smoke/test_forms/inventory/` va
`skills/write-test/references/project-rules.md` → `Form-opening smoke suite arxitekturasi`
- Old behavior: har oddiy legacy leaf test barcha literal forma definitionlarini
  o'z faylida saqlar, shu sabab execution va katta ro'yxatlar aralashib ketardi.
- Current behavior: legacy forma definitionlari navbar modullariga bo'lingan
  markaziy inventory package'ida turadi; leaf faqat o'z `NAVBAR_TAB`i bilan
  query qiladi. A2Angular migratsiya testi alohida cross-navbar inventory bo'lib
  qoladi.

### Leaf-owned legacy Forms orchestrationi
Status: superseded
Observed: 2026-08-07
Superseded: 2026-08-10
Source: user; eski `run_spravochniki_forms` va `run_prodaja_forms` strukturasi
Replaced by: `tests/smoke/test_forms/monitoring/suite_runner.py::run_legacy_form_monitoring`
va `skills/write-test/references/project-rules.md` → `Form-opening smoke suite arxitekturasi`
- Old behavior: har legacy leaf login/filial negative handling, menu/section
  loopi, skip attach va `monitor.finish()`ni o'zida takrorlardi.
- Current behavior: leaf `run_legal_person` kabi admin login, inventory va
  monitoringni raqamlangan uchta ochiq qadamda bajaradi; umumiy filial/menu,
  skip va monitor lifecycle'i bitta façade'da turadi. A2Angular o'zgarmagan.

## Removed Legacy Scenario 1 Catalog

### Eski `tests/ui` 84-case katalogi

Status: superseded
Observed: 2026-02
Superseded: 2026-08-14
Source: removed `docs/developer_testcases_scenario1.md`; eski `tests/ui/`
Replaced by: joriy `tests/smoke/test_setup/`, `tests/smoke/test_groups/` va
`skills/write-test/references/order-test-coverage.md`

- Old behavior: yo'q qilingan `tests/ui/` va `test_ui_runner.py` asosida 84 ta
  setup, order, purchase, supplier, warehouse va integration scenario katalogi
  saqlangan edi.
- Current behavior: u katalog current automation coverage yoki current UI truth
  emas. Amaldagi setup/group runnerlar actual coverage source of truth'i;
  Order regression backlogi alohida canonical coverage reference'da turadi.

## Removed Forms Monitor checklari

### JavaScript exception hard-checki
Status: superseded
Observed: 2026-08-05
Superseded: 2026-08-06
Source: synthetic legacy/A2 browser probes; 147-form baseline; user decision
Replaced by: `skills/smartup-guide/references/ui-patterns.md` →
`User-reported: kuzatilgan Smartup xatolari BiruniAlert ichida ko'rsatiladi`
- Old behavior: legacy shell'da Playwright `pageerror`, A2 shell'da esa
  capture-fazali init-script window JS exceptionlarni yig'ar va topilgan signal
  formani `OPENED_WITH_DEFECT / JS_ERROR` qilardi.
- Old evidence: sun'iy `throw` detector ishlashini ko'rsatgan, ammo 147-forma
  baseline runida tabiiy JS exception topilmagan.
- Current behavior: FormMonitor'da `javascript` hard check, `JS_ERROR`,
  `pageerror` listeneri va window JS exception capture'i yo'q. Ko'rinadigan
  Smartup application xatolari `APPLICATION_ERROR` orqali tekshiriladi.

## Removed Forms Monitor observation diagnostikalari

### Busy, resource, promise va title-metadata diagnostikalari
Status: superseded
Observed: 2026-08-05
Superseded: 2026-08-10
Source: user decision; `tests/smoke/test_forms/form_diagnostics/`;
`tests/smoke/test_forms/form_monitor.py`
Replaced by: `skills/maintain-test-infra/references/reporting.md` →
`Forms central monitoring`
- Old behavior: FormMonitor `[aria-busy=true]`, `img/script/link` resource load
  errorlari, `unhandledrejection` va title metadata'ni observation-only
  diagnostika sifatida yig'ar edi.
- Current behavior: faqat HTTP `4xx/5xx` `failed_requests` diagnostikasi qolgan.
  U `form_diagnostics/failed_requests.py` modulida, extensible registry va
  lifecycle esa `form_diagnostics/core.py`da turadi.

## Superseded Forms Monitor title modeli

### Snapshot title check va Legacy silent pass
Status: superseded
Observed: 2026-08-03
Superseded: 2026-08-06
Source: `tests/smoke/test_forms/form_checks/core.py` va eski
`tests/smoke/test_forms/flow.py`; user-approved title contract
Replaced by: `skills/smartup-guide/references/form-monitor/check-title.md`
- Old behavior: `settle_form_open()` title transitionini kutar, keyin pure
  snapshot check alohida pass/fail chiqarardi. Legacy heading topilmasa title
  taqqoslanmasdan pass bo'lishi mumkin edi; boshqa title `TITLE_MISMATCH`
  sifatida yozilardi.
- Current behavior: mustaqil `check_title()` kutish va exact taqqoslashning
  yagona authoritysi. Missing/partial title yagona `TITLE_NOT_REACHED` reasoni
  bilan failure; `settle_form_open()` va silent unverified-pass yo'li yo'q.

## Removed runner va test entrypointlari

### Outer `test_all_runner.py`
Status: superseded
Observed: 2026-05
Superseded: 2026-07-21
Source: historical smoke run va A-group trace yozuvlari
Replaced by: `scripts/run_tests.py`, `tests/smoke/test_setup/test_setup_runner.py`
va `tests/smoke/test_groups/**/test_*_group_runner.py`
- Old behavior: setup va grouplar `tests/smoke/test_all_runner.py` outer chaini
  orqali bitta yoki bir nechta wrapper test sifatida ishga tushirilgan.
- Old evidence: 2026-05-25 run 21 passed bo'lgan; 2026-07-20 A-group locator
  tuzatishi outer runner orqali tekshirilgan.
- Current behavior: har setup/group case alohida pytest item; `scripts/run_tests.py`
  kerakli runner fayllarini bevosita collect qiladi.

### Bitta `test_license.py` moduli
Status: superseded
Observed: 2026-06
Superseded: 2026-07
Source: historical setup structure
Replaced by: `tests/smoke/test_setup/test_buy_license.py` va
`tests/smoke/test_setup/test_attach_license.py`
- Old behavior: license sotib olish va userga ulash bitta
  `tests/smoke/test_setup/test_license.py` modulida saqlangan.

### A2 URL-only diagnostika harnessi
Status: superseded
Observed: 2026-07-07
Superseded: 2026-07-27
Source: historical `tests/smoke/test_life_cycle/test_a2_new_forms.py`
Replaced by: `tests/smoke/test_forms/test_a2_admin_menu_forms.py` va
`tests/smoke/test_forms/test_forms_runner.py`
- Old behavior: 53 ta A2 route `direct`, `via_list` va `skip` modelida URL
  orqali admin/head profillarda diagnostika qilingan.
- Current behavior: faqat real menu/page-link yo'li yozilgan formalar current
  coverage hisoblanadi; 53 formalik inventar joriy test docstringida backlog
  konteksti sifatida saqlanadi.

### 2026-07 runner migratsiya verifikatsiyalari
Status: superseded
Observed: 2026-07-14..2026-07-21
Superseded: 2026-07-30
Source: historical setup va group run natijalari
Replaced by: `skills/smartup-guide/references/smoke-runner.md` current runner
qoidalari
- Old evidence: compact entity codelari bilan setup 02–19 o'tgan, Init Balance
  warehouse preconditionida to'xtagan.
- Old evidence: setup wrapperlari va A/B/C/Report caselari alohida Allure
  testlarga migratsiya qilinganda vaqtinchalik collection sonlari qayd etilgan.
- Current behavior: collection tarkibi `scripts/run_tests.py` targetlari va
  joriy runner fayllaridan olinadi; eski collection sonini hard-code qilma.

## Removed session recovery helper

### `install_session_keepalive()` avtomatik overlay recovery
Status: superseded
Observed: 2026-06-12
Superseded: 2026-07-02
Source: git commits `21bdc3c`, `f94b377`
Replaced by:
`skills/smartup-guide/references/forms/login.md#joriy-kodda-sessiya-qulf-recovery-handleri-yoq`
- Old behavior: har `login()`dan keyin `page.add_locator_handler(...)`
  o'rnatilib, timeout-warningda `Продолжить`, lock holatida esa parolni
  Angular modelga commit qilib `Войти` bosilar va overlay yopilishi kutilar edi.
- Current behavior: helper va uning `login()` caller'i `f94b377` refaktorida
  olib tashlangan; CI head `0670b8f`da avtomatik session-lock recovery yo'q.

## Superseded Filial Form Kontrakti

### Filial formasini A2 deb noto'g'ri tasniflash
Status: superseded
Observed: 2026-08-13
Superseded: 2026-08-13
Source: user; eski `skills/smartup-guide/references/forms/filial.md`
Replaced by: `skills/smartup-guide/references/forms/filial.md`
- Superseded xulosa: Filial list/add/view `smt-*` komponentli A2 forma deb
  tasniflanib, test `AngularBasePage`ga migratsiya qilingan.
- Current behavior: Filial test legacy Biruni `BasePage`ga qaytarildi va
  relevant setup run bilan tasdiqlandi.

## Superseded License Form Kontrakti

### License formasini A2 deb noto'g'ri tasniflash
Status: superseded
Observed: 2026-08-13
Superseded: 2026-08-13
Source: user; `test-results/allure-results/d9911418-1c48-4e7f-ab31-e5b6ec17f96a-result.json`
Replaced by: `skills/smartup-guide/references/forms/license.md`
- Superseded xulosa: license forma `/a2/...` route va `smt-*` komponentli deb
  tasniflanib, Buy/Attach `AngularBasePage`ga migratsiya qilingan.
- Current behavior: real route `/#/!<session>/biruni/kl/license_list`; forma
  legacy Biruni/AngularJS `b-*` komponentlarida va Buy/Attach `BasePage` bilan
  ishlaydi. Faqat serverga bog'liq skip policy yangi holatda saqlanadi.

## Superseded setup/group/Forms test naming qoidalari

### Setup/group/Forms runner va leaf fayllarini eski usulda nomlash
Status: superseded
Observed: 2026-07-31
Superseded: 2026-07-31
Source: user
Replaced by: `skills/write-test/references/project-rules.md` → `Setup, group va Forms runner/leaf fayllarini tartib bilan nomlash`
- Old behavior: setup runner `test_setup_runner.py`, setup leaf fayllari raqamsiz edi.
- Old behavior: group leaf fayllari raqamsiz, tartib faqat runner wrapper va Allure title ichida yozilar edi.
- Old behavior: runner fayli group nomini takrorlab `test_<group>_group_runner.py` ko'rinishida bo'lishi mumkin edi.
- Old behavior: Forms runner `test_forms_runner.py`, Forms leaf modullari raqamsiz edi.
- Current behavior: setup runner `test_0_setup_runner.py`, group runner `test_0_group_runner.py`, Forms runner `test_0_forms_runner.py`; barcha leaf fayllar runner wrapper raqamiga mos prefix oladi.

## Removed BasePage helperlari

### Birlashtirilgan `save_and_expect_heading()` transition helperi
Status: superseded
Observed: 2026-07-01
Superseded: 2026-07-31
Source: user; `utils/base_page.py`; legacy test call-site'lari
Replaced by: `skills/smartup-guide/references/ui-patterns.md` →
`Legacy Save Transition Ochiq Yoziladi`
- Old behavior: legacy save, optional Biruni confirm, loader va target heading
  bitta ko'p parametrli `BasePage.save_and_expect_heading()` ichida
  birlashtirilgan edi.
- Current behavior: test action va assertionni ochiq yozadi:
  `base.click(name="Сохранить", exact=...)`, kerak bo'lsa
  `base.confirm_biruni(...)`, keyin `base.expect_page(heading=..., url=...)`.

## Superseded locator qoidalari

### Change Password uchun raw `#id.fill()` majburiy degan qoida
Status: superseded
Observed: 2026-07
Superseded: 2026-07-30
Source: `tests/smoke/test_setup/test_change_password.py`; local
`scripts/run_tests.py setup --headless` (`20 passed, 1 deselected`)
Replaced by: `skills/smartup-guide/references/forms/user.md`
- Old behavior: validation overlay `BasePage.input()` clickini to'sishi
  mumkinligi sabab raw `#current_password`/`#new_password`/
  `#rewritten_password.fill()` majburiy deb yozilgan edi.
- Current behavior: `BasePage.input(label=...)`, jumladan `Новый пароль`
  uchun `press_tab=True`, fresh user bilan to'liq Setup runida muvaffaqiyatli
  o'tdi.

### `Возврат (создание)` alertini application error deb hisoblash
Status: superseded
Observed: 2026-08-04
Superseded: 2026-08-04
Source: live UI; user correction
Replaced by:
`skills/smartup-guide/references/legacy-form-navigation.md#возврат-создание-administrator-draft-ogohlantirishi`
- Old behavior: `Возврат (создание)` ochilganda ko'ringan administrator draft
  cheklovi alerti Forms-03 uchun haqiqiy `APPLICATION_ERROR` deb qabul qilingan.
- Current behavior: foydalanuvchi bu xabar application error emas, balki admin
  faqat `Черновик` statusida saqlashi mumkinligini bildiradigan kutilgan biznes
  ogohlantirishi ekanini aniqlashtirdi.

## Eski server xatti-harakati

### PnL menyusining eski nomi va legacy route holati
Status: superseded
Observed: 2026-07-24
Superseded: 2026-08-04
Source: `app3.greenwhite.uz/xtrade` live UI; `smartup.online` live UI
Replaced by: `skills/smartup-guide/references/forms/pnl.md#quick-lookup`
- Old behavior: operatsion filialdagi `Финансы → Отчеты` yo'lida exact
  `PnL` menu itemi kuzatilgan va u
  `anor/rep/mkr/profit_and_loss` legacy route'ini bergan; test esa
  `menu_item="PnL"` bilan `/a2/anor/rep/mkr/pnl`ni kutgan.
- Current behavior: A2 `anor/rep/mkr/pnl` leaf matni
  `Отчет о прибылях и убытках`; exact `PnL` menuitem joriy UI'da yo'q.
  `Прибыль и убыток (PnL)` esa alohida legacy route bo'lib qolgan.

### Xtrade OnlyOffice ulanmagan davr
Status: superseded
Observed: 2026-06-12
Superseded: 2026-06-16
Source: CI run 27402337118
Replaced by: `skills/smartup-guide/references/orders.md` Custom Invoice Report
Template qoidasi
- Old behavior: xtrade'da custom invoice report endpointi OnlyOffice viewer
  o'rniga `.xlsx` attachment qaytargan; popup `url=':'`da qolgan.
- Current behavior: xtrade va smartup.online ikkalasida report OnlyOffice
  spreadsheet iframe ichida ochiladi.

## Superseded FormMonitor URL va shell qoidalari

### Forms-02 A2 precondition bloklanishi
Status: superseded
Observed: 2026-08-03
Superseded: 2026-08-11
Source: `test-results/logs/tests_smoke_test_forms_test_0_forms_runner.py__test_forms_02_a2_admin_20260803_142617.log`
Replaced by: `skills/smartup-guide/references/a2-migrated-forms.md`;
`skills/smartup-guide/references/forms/company-client.md`
- Old behavior: texnik `/a2/trade/intro/dashboard`da project `SFA` ko'rinsa
  ham eski helper `TRADE` triggerini kutib, A2 filial syncini bloklagan;
  birinchi case `TEST_BLOCKED`, qolgan 21 case `NOT_CHECKED` bo'lgan.
- Current behavior: A2Angular standalone test, joriy `SFA` filial selector
  kontrakti va company-client sync oqimi current reference'larda saqlanadi.

### Canonical path exact tengligi va inventory shell authoritysi
Status: superseded
Observed: 2026-08-06
Superseded: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/url.py`;
`tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/suite_runner.py`
Replaced by: `skills/smartup-guide/references/form-monitor/check-url.md`;
`skills/smartup-guide/references/form-monitor/check-title.md`
- Old behavior: URL check canonical pathni inventory pathga exact tenglashtirar,
  keyingi title check esa suite/inventory bergan shellga tayanar edi.
- Current behavior: inventory path actual URL ichida mavjud bo'lishi yetarli;
  destination shell actual URLdan bir marta aniqlanib loader,
  application-error, content-ready va title checklarga parametr sifatida
  uzatiladi.

### Record-dependent Forms caselarini target bo'yicha ajratish
Status: superseded
Observed: 2026-08-18
Superseded: 2026-08-18
Source: user; user correction
Replaced by:
`skills/write-test/references/project-rules.md#user-reported-form-crud-coverage-smoke-testlarda-kengaytiriladi`
- Old behavior: `_edit` va `_view` alohida pytest case bo'lib, har biri `_add`
  orqali o'z recordini yaratishi kerak deb talqin qilingan edi.
- Current behavior: form-specific smoke testcase o'zi yaratgan record bilan
  `list -> add/save -> view -> edit/save -> final view` lifecycle'ini boshidan
  oxirigacha bajaradi.

### Alohida universal CRUD Forms subsystemi
Status: superseded
Observed: 2026-08-18
Superseded: 2026-08-18
Source: user; user correction
Replaced by:
`skills/write-test/references/project-rules.md#user-reported-form-crud-coverage-smoke-testlarda-kengaytiriladi`
- Old behavior: yangi `test_crud_forms` mexanizmi bitta form familyning `list`,
  `add`, `view` va `edit` holatlarini FormMonitor orqali boshqarishi kerak deb
  rejalashtirilgan edi.
- Current behavior: alohida universal CRUD framework yaratilmaydi; kerakli CRUD
  qadamlar mavjud yoki yangi form-specific business smoke testlarga qo'shiladi.

## Superseded integration report qoidalari

### CisLink global skip va legacy settings modal
Status: superseded
Observed: 2026-06-12
Superseded: 2026-08-20
Source: `smartup.online` live Chromium UI
Replaced by: `skills/smartup-guide/references/forms/cislink.md`
- Old behavior: Smartup Online CisLink formasida `Настройки` inline paneli bor,
  Xtrade'da esa template-based forma bo'lgani uchun deploymentlar farqi sabab
  Report-01 global skip qilinishi kerak deb yozilgan edi.
- Current behavior: `smartup.online` ham template-based main formaga migratsiya
  qilingan; `Настройки` yo'q, `Шаблоны` orqali alohida template list/create
  formasi ochiladi va global skip olib tashlangan.

### Optimum `Все филиалы` va sticky loader gap
Status: superseded
Observed: 2026-07-23
Superseded: 2026-08-20
Source: `smartup.online` live Chromium UI
Replaced by: `skills/smartup-guide/references/forms/integration-reports.md#optimum-optimum`
- Old behavior: main formada `Все филиалы` default checked va birinchi generate
  ortidan sticky overlay ikkinchi generate'ni bloklaydi deb qabul qilingan.
- Current behavior: joriy main formada `Все филиалы` controli yo'q; test real
  period, settings va bitta ZIP export kontraktini tekshiradi.

### Integration Two to'rtta XML download flowi
Status: superseded
Observed: 2026-07-23
Superseded: 2026-08-20
Source: `smartup.online` live Chromium UI
Replaced by: `skills/smartup-guide/references/forms/integration-reports.md#integration-two--monolith-integration_two`
- Old behavior: `URL=https` saqlab to'rtta exchange mode uchun XML download
  kutilgan; balance va internal movement modelari qamrab olinmagan.
- Current behavior: test fake URL yozmaydi; configured HTTP(S) Monolith
  endpointini precondition sifatida tekshiradi va barcha oltita mode uchun
  non-empty XML downloadni talab qiladi.

### CisLinkni faqat side-effectsiz forma kontrakti sifatida tekshirish
Status: superseded
Observed: 2026-08-20
Superseded: 2026-08-20
Source: user correction; live Chromium UI
Replaced by: `skills/smartup-guide/references/forms/cislink.md#end-to-end-test-flowi`
- Old behavior: template yo'q filialda Report-01 create formasini ochib,
  hech narsa saqlamasdan yopar va generate/download qilmas edi.
- Current behavior: test code'ga tegishli template yaratadi yoki tanlaydi,
  report sanasini beradi va CisLink ZIP downloadni majburiy tekshiradi.

### `b_input(select_first=True)` qidiruv natijasini tanlashi
Status: superseded
Observed: 2026-08-20
Superseded: 2026-08-20
Source: user correction; `utils/base_page.py`; `utils/angular_base_page.py`
Replaced by: `skills/smartup-guide/references/ui-patterns.md#select_first-va-search_text-kontrakti`
- Old behavior: `select_first=True` bilan `search_text` birga berilib, qidiruvdan
  keyingi birinchi visible option tanlanar edi.
- Current behavior: `select_first=True` qidiruvsiz birinchi optionni tanlaydi;
  non-empty `search_text`ning o'zi qidirib, qaytgan birinchi optionni tanlaydi.

### Template-based reportda mavjud template'ni qayta ishlatish
Status: superseded
Observed: 2026-08-20
Superseded: 2026-08-20
Source: user correction; `tests/smoke/test_groups/test_report_grup/test_01_cislink.py`; `test_03_saleswork.py`; `test_05_spot.py`
Replaced by: `skills/smartup-guide/references/forms/cislink.md#end-to-end-test-flowi`; `skills/smartup-guide/references/forms/integration-reports.md#saleswork-saleswork`; `skills/smartup-guide/references/forms/integration-reports.md#spot2d-spot`
- Old behavior: CisLink, SalesWork va Spot2D testlari code'ga tegishli template
  mavjud bo'lsa uni qayta ishlatar, faqat topilmasa yangi template yaratar edi.
- Current behavior: uchala template-based report har bir run uchun UUID suffixli
  yangi template yaratadi, aynan shu template tanlanganini tekshiradi va shu
  bilan reportni download qiladi.
