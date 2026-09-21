# A2 (migratsiya qilingan yangi) formalar

## Mundarija

- [Arxitektura](#arxitektura)
- [Yangi Angular component kontrakti](#yangi-angular-component-kontrakti-companyda-live-tasdiqlangan-2026-07-23)
- [Menyu filialga bog'liqligi](#menyu-filialга-bogliq-eng-muhim-kuzatuv-2026-07-07)
- [Real-user navigatsiya](#real-user-navigatsiya-menyu-orqali--2-etap-testlar-uchun)
- [Forma yo'llari va backlog](#forma-yollari-va-backlog)
- [Filial switcher DOM](#filial-switcher-dom)
- [Test](#test)
- [Tarixiy diagnostika](#tarixiy-diagnostika)

Tags: a2, migrated-forms, filial, menu, navigation, error, url

Smartup yangi formalari (yangi Angular/modern app) eski AngularJS Biruni app ustiga qo'shilgan.
Ular URL'da **`a2`** prefiksi bilan ajraladi; filial va navigatsiya yo'llari
[Forma yo'llari va backlog](#forma-yollari-va-backlog) bo'limida saqlanadi.

## Arxitektura

- **Page-object chegarasi:** legacy AngularJS/Biruni formalar
  `utils/base_pages/base_page.py::BasePage` bilan, yangi A2 Angular formalar
  `utils/base_pages/angular_base_page.py::AngularBasePage` bilan yoziladi. Legacy class
  mavjud eski formalar tugamaguncha aktual saqlanadi; ikki DOM selectorlari bitta
  helperga fallback qilib aralashtirilmaydi.
- **Alohida app.** Eski menyudan a2 forma bosilganda `{base}/a2/{path}` ga **to'liq sahifa** navigatsiya bo'ladi
  (SPA hash-route emas). `base` = `os.environ["COMPANY_URL"].rstrip("/")`:
  - smartup.online: `https://smartup.online/a2/{path}`
  - app3: `https://app3.greenwhite.uz/xtrade/a2/{path}`
  - `{path}` = forma route'i, masalan `biruni/md/company_list`, `anor/rep/mbi/mkw/purchase`.
- **Sog'lom forma signali:** `document.title` forma nomiga aylanadi (masalan "Компании", "Логистика").
  Content async yuklanadi — dashboard/list/catalog formalar title resolve bo'lgach ham 1-1.5s kontent yuklaydi.
- **Dashboard readiness:** nested `[aria-busy=true]` sahifa to'liq render
  bo'lgandan keyin ham qolishi mumkin; u post-validationda o'zicha blocking
  loader emas. Blocking signal — visible `.smt-skeleton` yoki
  `.block-ui-overlay`. Monitor busy countni diagnostika sifatida saqlaydi.
- **Muammo signallari** (title "Smartup Online" da qoladi):
  - `Страница не найдена` — 404 (forma yo'q).
  - `Нет доступа к форме {name}` / `Не удалось загрузить` / `Что-то пошло не так` — ruxsat yo'q yoki load error.
  - `+edit`/`_view`/`_details` yakka URL bilan ochilmaydi — id (record) kerak; title shell'da qoladi.
- 2026-08-05 real Chrome auditida joriy `SFA Администрирование` rolida direct
  `Визиты` va `Коммерческий дашборд` route'lari expected URLga o'tib, taxminan
  500 ms ichida `[role=alert]` orqali `Нет доступа к форме ...` ko'rsatdi.
  Shuning uchun form monitorning 1200 ms visible-error oynasi kerak; URL/title
  tekshiruvi yakka o'zi dostup muammosini sog'lom deb o'tkazishi mumkin.

## Yangi Angular component kontrakti (Company'da live tasdiqlangan, 2026-07-23)

- Forma maydoni: `smt-control`; oddiy input: `smt-input` ichidagi native
  `input`/`textarea`; select: `smt-data-select` → `smt-select-trigger`.
- Select optionlari `.cdk-overlay-container` ichidagi `smt-select-dropdown li`
  sifatida portal qilinadi. Ular legacy `b-input .hint-item` yoki
  `.ui-select-choices-row-inner` emas. Option clickdan keyin dropdown ochiq
  qolishi mumkin; tashqi sahifa nuqtasini bosib overlay yopiladi va backdrop
  yo'qolgani kutiladi.
- List: `smt-data-table`/`smt-table`; data qatori `.smt-data-row`; ustunlar
  `[data-smt-col-key="..."]`; search native `input[type="search"]`.
- List yuklanayotgan paytda `.smt-skeleton` qatorlari ko'rinadi;
  `.block-ui-overlay` bo'lmasligi mumkin. URL/title yangilanishi component mount
  bo'lishidan oldin sodir bo'lishi mumkin, shu sabab stabil component yoki
  skeleton yo'qolishi alohida kutiladi.
- A2 ichki menyusi CDK overlay'da `[role="menu"]` va `[role="menuitem"]`
  bilan ishlaydi. A2 filial selectorida
  `data-testid="shell-project-filial--project-list"` /
  `data-testid="shell-project-filial--filial-list"` va `[role="option"]` bor.
  Legacy `.pt-3.px-2` va `a.menu-link...` selektorlari faqat eski shell'dan A2
  formaga kirish bosqichida ishlaydi; A2 ichida qayta ishlatilmaydi.
- A2 save errorlari `role=dialog`/CDK overlay'da chiqishi mumkin. Save helperi
  target page readiness va error dialogni bir vaqtda kutadi; error chiqsa uzoq URL
  timeoutini kutmasdan dialog matni bilan fail qiladi.

## Menyu FILIALга bog'liq (eng muhim kuzatuv, 2026-07-07)

- Eski chap menyu `session.si.filial.menus` ga bog'langan — **har filialда boshqacha formalar** ko'rinadi.
  Login'дан keyingi default filial odatda **"Администрирование"**.
- Barcha filiallarning to'liq menyu daraxti login'да oldindan yuklanadi:
  `angular scope -> a.session.si.projects[0].filials[].menus[].menus[].forms[]`.
  Har `form`: `{form (path), name, add_form, is_migrated: 'Y'/'N', url, add_form_url}`.
  **`is_migrated === 'Y'` ⇒ a2 forma.** (Bu modelni `page.evaluate` bilan read-only o'qish mumkin — diagnostika uchun.)
- **ASOSIY QOIDA: eski angular menyu orqali ochiladigan a2 formalar — BARCHASI ADMIN formalar.** Alohida "head"
  profil / alohida head test KERAK EMAS; hammasi bitta admin testda
  (`test_a2_angular_forms.py`) yig'iladi.
- **Forma joyi (filial + aniq user track)** shu reference'ning
  [Forma yo'llari va backlog](#forma-yollari-va-backlog) bo'limida saqlanadi.
  Ochish usullari: LEAF / LIST-ACTION / SIBLING. Qisqacha (2026-07-08 live tasdiqlangan):
  - "Администрирование" da: `kauth/company_client_list` (+undan `+add`/`+edit` list-action).
  - Operatsion filialda LEAF: Визиты/Логистика, dashboardlar, `anor/rep/mkr/pnl` («Отчет о прибылях и убытках»),
    barcha `anor|trade/rep/mbi/*` report designerlar, `plg/plugin_catalog`, `external_settings`.
  - Operatsion, SIBLING (menyu modelida YO'Q, eski forma ichidan): `mcg/action` (Акции→…), `marking_stocktaking_list`
    (Инвентаризации→Инвентаризация КМ).
- **Hali live tasdiqlanmagan admin formalar** (`md/*`, `ms/announcement_list`, `kauth/client_list`,
  `kauth/security_settings`, `billing/operational_dashboard` va ularning list-action ko'rinishlari) — bular ham ADMIN
  formalar; hujjatdagi user tracklar quyidagi backlogda, testga qo'shilganda tasdiqlanadi.
  Ba'zilari faqat head KOMPANIYASIда bor bo'lishi mumkin (boshqa kompaniyada "нет доступа") — bu profil emas, kompaniya
  masalasi; forma baribir admin menyusidan ochiladi.
  - Track hali aniqlanmagan (URL only): `mfa/purchase`, `ker/setting`, `ker/head_template_list+attach`, `company_audit_info_audit`.
- **`_list`/`+add`/`+edit` bitta formaning ko'rinishlari:** `_list` va `+add` ochiladi (URL `..._list` -> `...+add`);
  `+edit`/`+copy`/`_view`/`_audit_details` yakka URL bilan ochilmaydi — record `id` kerak.
- **`+edit`/`+view`/`+copy` ni tekshirish (2026-07-07 MCP tasdiqlangan):** mos `_list` ni ochib, grid'ning BIRINCHI
  qatorini **double-click** qilinadi -> forma o'sha record id'si bilan ochiladi. Hosil bo'lgan URL patterni:
  `{base}/a2/{path}?-project_code=trade&-filial_id={filial_id}&{id_param}={id}` (`{path}` dagi `+` URLda `%2B`).
  Misol: `company_client+edit` <- `company_client_list` grid double-click -> `client_id`=grid "Client ID" ustuni.
  `{id_param}` formaga qarab farq qiladi (client_id, company_id, setting_id...). Ochilganda `document.title`
  path bo'lib qoladi (`/biruni/.../+edit`), lekin `main` da forma maydonlari (Сохранить, Название*...) bo'ladi = ochilgan.

## Real-user navigatsiya (menyu orqali — 2-etap testlar uchun)

- Eski menyu tuzilishi: **Tab** (`a.menu-link.menu-toggle`, matn = "Главное"/"Продажа"/...) → **Sub kategoriya**
  (`h3.menu-heading` matn) → **leaf** (`a.menu-link`, `href` ichida `/a2/{path}`).
- Menyu **CLICK** bilan ochiladi (hover emas): `ng-click="a.setMenuPosition($event)"`. Tab bosilganда flyout
  ochiladi/yopiladi (toggle) — holat desync bo'lmasligi uchun leaf ko'rinishini `expect(...).to_be_visible()` bilan kut.
- Leaf'ni **ends-with** selektor bilan tanla: `a.menu-link[href$="/a2/{path}"]` (`href*=` `purchase` ni `purchase_request`
  bilan ham tutadi — noto'g'ri).
- Leaf bosilganда a2 ga to'liq sahifa navigatsiya. Keyingi formaga o'tish uchun `page.go_back()` — eski dashboard
  menyusi bilan tiklanadi (2026-07-08 MCP tasdiqlangan: go_back'dan keyin tablar/leaflar qayta ishlaydi).
- Explicit menu-track testning yangi oqimida `page.go_back()` ishlatilmaydi:
  forma ochilgach joriy sahifadagi navbar orqali keyingi forma ochiladi.
- Visit consumerlari uchun helper:
  `tests/smoke/test_groups/test_visit_grup/flow_visit/flow_navigate.py::navigate_to_a2(page, tab, path, *, name)`.
  U `AutoBasePage.navigate_to(tab=..., name=...)` bilan navigatsiya qiladi,
  route va shell title'dan chiqishni kutadi. Bu A2Angular runner helperi emas.
  Legacy flyoutda `h3.menu-heading` alohida ochilmaydi.
- **Ochilgani signali:** `expect(page).not_to_have_title("Smartup Online")` — dashboardlar ham (async) title'ni
  forma nomiga o'zgartiradi. `heading`/`mainLen` ga tayanma (dashboardlarda async, false-negative).
- **Menyu leaflari filial menusidan keladi** — barcha a2 leafni bitta o'qishда olish uchun angular session
  modelini (read-only) ishlat: `a.session.si.projects[0].filials[].menus[].menus[].forms[]`, `is_migrated==='Y'`
  bo'lganlari. Har `form`: `{form(path), name, is_migrated}`. Bu real menyu leaflarining AVTORITET manbai
  (URL'да ochiladigan, lekin menyuда YO'Q formalardan farqli).

## Forma yo'llari va backlog

### Kodda mavjud navigatsiya yo'llari
Tags: a2, inventory, filial, navigation
Status: code-confirmed
Verified: 2026-09-18
Source: `tests/smoke/test_forms/test_a2_angular_forms.py` (`ADMIN_A2_FORMS`, `OPERATIONAL_A2_FORMS`, `PAGE_LINK_A2_FORMS`)

Bu jadval koddagi yo'llarni ko'rsatadi; yangi live tekshiruv natijasi emas.
LEAF — navbar → menyu ustuni → forma. SIBLING — eski parent forma → page-link;
bu route angular menyu modelida alohida leaf sifatida ko'rinmasligi mumkin.
LIST-ACTION — list ichidagi yaratish yoki qator actioni; u menyu leafi emas.

Operatsion filial (`filial-pw{code}` yoki boshqa operatsion filial), LEAF:

| Path | Navbar → ustun → forma |
|---|---|
| `trade/txs/external_settings` | Главное → Дополнительное → Настройки интеграции со сторонним ПО |
| `trade/tvt/visit_list` | Продажа → Визиты → Визиты |
| `trade/tvt/user_locations` | Продажа → Визиты → Отслеживание пользователей |
| `trade/tph/user_tracking` | Продажа → Визиты → Отслеживание мобильных представителей |
| `trade/tdeal/commercial_dashboard` | Продажа → Отчеты по продажам → Коммерческий дашборд |
| `trade/rep/mbi/tvt/visit` | Продажа → Отчеты по визитам → Конструктор отчётов по визитам |
| `trade/tdeal/logistics_list` | Склад → Справочники → Логистика |
| `anor/rep/mbi/mkw/movement` | Склад → Отчеты → Конструктор отчетов по внутр. перемещениям |
| `anor/rep/mbi/mkw/purchase_request` | Склад → Отчеты → Конструктор отчетов по запросам на закуп |
| `anor/rep/mbi/mkw/purchase` | Склад → Отчеты → Конструктор отчетов по закупкам |
| `anor/rep/mbi/mkw/input` | Склад → Отчеты → Конструктор отчетов по поступлениям |
| `anor/rep/mbi/mkw/writeoff` | Склад → Отчеты → Конструктор отчетов по списанию |
| `anor/rep/mbi/mfm/movement_request` | Склад → Отчеты → Конструктор отчетов по запросам на межорг. перемещения |
| `anor/rep/mbi/mfm/movement` | Склад → Отчеты → Конструктор отчетов по межорг. перемещениям |
| `anor/rep/mbi/mkcs/operation` | Финансы → Отчеты → Конструктор отчетов по финансам |
| `anor/rep/mkr/pnl` | Финансы → Отчеты → Отчет о прибылях и убытках |
| `anor/rep/mku/balance_sheet` | Финансы → Отчеты → Бухгалтерский баланс |
| `trade/rep/mbi/tmcg/shelf_share` | Торговый маркетинг → Отчеты → Конструктор отчётов по доле на полке |
| `anor/rep/mbi/mqpf/request` | Оборудование → Дополнительное → Конструктор отчетов по заявкам на оборудование |
| `biruni/plg/plugin_catalog` | Плагин → Plugin Marketplace (ustunsiz) |

Operatsion filial, SIBLING:

| Path | Parent forma → page-link |
|---|---|
| `anor/rep/mbi/mcg/action` | Справочники → Маркетинг → Акции (`anor/mcg/action_list`) → Конструктор отчетов по акциям |
| `anor/mkw/marking_stocktaking/marking_stocktaking_list` | Склад → Документы → Инвентаризации (`anor/mkw/stocktaking/stocktaking_list`) → Инвентаризация КМ |

Marking yo'li inventarda bor, ammo aktiv coverage emas; dostup va vaqtinchalik
skip holati [forma dossierida](forms/marking-stocktaking-list.md) saqlanadi.

`Администрирование` filiali, LEAF:
`biruni/kauth/company_client_list` — Главное → Дополнительное → Клиенты OAuth2 сервера для компании.
Undan `company_client+add` (Создать) va `company_client+edit` (qator → Изменить)
LIST-ACTION bilan ochilishi avval kuzatilgan; joriy test inventarida ikkalasi
`QOLGAN`. Eski live kuzatuv joriy test coverage'i degani emas.

### Hali menu-track bilan qamralmagan inventar
Tags: a2, backlog, navigation
Status: code-confirmed
Verified: 2026-09-18
Source: `tests/smoke/test_forms/test_a2_angular_forms.py` module docstringi

Status faqat quyidagi yozuvlar test backlogida mavjudligini tasdiqlaydi.
Hujjatdan olingan menyu yo'llari live tasdiqlanmagan; implementatsiyadan oldin
tegishli kompaniya, project va filialda tekshiriladi. Ularni current UI fakti
yoki test o'tganligi dalili sifatida ishlatma.

`Администрирование` filialiga tegishli deb ko'rsatilgan LEAF nomzodlari:

| Path | Hujjatdagi user track |
|---|---|
| `biruni/kauth/client_list` | Главное → Дополнительное → Клиенты API/OAuth2 сервера |
| `biruni/kauth/security_settings` | Главное → Дополнительное → Настройки безопасности |
| `biruni/md/audit_setting` | Главное → Дополнительное → Настройки истории изменений |
| `biruni/md/company_list` | Главное → Дополнительное → Компании |
| `biruni/md/contact_info_setting` | Главное → Дополнительное → Контактная информация |
| `biruni/md/feedback_list` | Главное → Дополнительное → Фидбеки |
| `biruni/md/log_list` | Главное → Дополнительное → Логи |
| `biruni/md/query_executor` | Главное → Дополнительное → Запросы к базе данных |
| `biruni/md/request_limit_template_list` | Главное → Дополнительное → Шаблоны лимитов |
| `biruni/ms/announcement_list` | Главное → Админ → Объявления |

Shu listlardan ochiladigan LIST-ACTION nomzodlari:

| Path | Hujjatdagi list → action |
|---|---|
| `biruni/kauth/client+add` | Клиенты API/OAuth2 сервера → Создать |
| `biruni/kauth/client+edit` | Клиенты API/OAuth2 сервера → qator → Изменить |
| `biruni/md/company_add` | Компании → Создать |
| `biruni/md/company_edit` | Компании → qator → Изменить |
| `biruni/md/company_view` | Компании → qator → Просмотр |
| `biruni/md/request_limit_template+add` | Шаблоны лимитов → Создать |
| `biruni/md/request_limit_template+edit` | Шаблоны лимитов → qator → Изменить |
| `biruni/md/request_limit_template_view` | Шаблоны лимитов → qator → Просмотр |
| `biruni/md/request_limit_template_audit_details` | Шаблоны лимитов → История изменений → detail |
| `biruni/ms/announcement+add` | Объявления → Создать |
| `biruni/ms/announcement+copy` | Объявления → qator → Копировать |
| `biruni/ms/announcement+edit` | Объявления → qator → Изменить |

Operatsion filial LEAF nomzodi: `billing/blda/operational_dashboard` —
Главное → Основное → Операционный дашборд.

To'liq menu-track hali yo'q: `anor/rep/mbi/mfa/purchase`,
`biruni/ker/setting+add`, `biruni/ker/setting+edit`,
`biruni/ker/head_template_list+attach`, `biruni/md/company_audit_info_audit`,
`biruni/md/company_audit_info_audit_details`. Eski URL diagnostikasi ularning
menyudagi yo'lini tasdiqlamaydi; tarixiy kontekst [history.md](history.md)da.

## Filial switcher DOM

- Ochish: `.dropdown-locations-custom:visible`. Ichki `.pt-3.px-2` faqat dekorativ
  strelka bo'lib, 1920x1080 CI viewportida ham hidden nusxaga tushishi mumkin;
  uni click target sifatida ishlatma.
- Optionlar: `.filial-list a.ng-binding` (matn = filial nomi), `href=""` (bo'sh) — shuning uchun **role=link**,
  ya'ni ochilgan locations containerining `.dropdown-menu` qismida
  `get_by_role("link", name=filial, exact=True)` ishlaydi (`BasePage.switch_filial`
  shu asosda).
  `.project-list a.ng-binding` — bu proyektlar (Trade/Финансы), filiallar emas.
- `BasePage(page).switch_filial(name)` filialga o'tadi va dashboard qayta yuklanadi.
- `test_a2_angular_forms.py` code/data_store'ga bog'lanmaydi: operatsion filial sifatida angular session modelidagi
  "Администрирование" bo'lmagan birinchi filial tanlanadi va `switch_filial(page, name=<shu filial>)` qilinadi.
- URL diagnostika testlarida operatsion filial nomini aniqlash: avval `filial-pw{code}` ({code} data_store.json dan),
  topilmasa har qanday `filial-pw*`, topilmasa "Администрирование" bo'lmagan birinchi filial.
- **head profilida `filial-pw*` YO'Q** (ular oddiy kompaniyalarda autotest yaratadi) -> 3-qadam ishlaydi va
  "Администрирование" bo'lmagan BIRINCHI filial olinadi (head'da odatda "Test org to delete"). Bu TASODIFIY tanlov,
  lekin operatsion formalar (masalan operational_dashboard) istalgan operatsion filialda ochilaveradi, shuning uchun
  shunday qoldirilgan (2026-07-07 user qarori). Aniq/barqaror filial kerak bo'lsa keyin o'zgartiriladi.

## Test

Tags: a2, forms-runner, menu-track, navigation, code
Status: code-confirmed
Verified: 2026-09-18
Source: `tests/smoke/test_forms/test_a2_angular_forms.py`; `tests/smoke/test_forms/monitoring/navigation.py`; `tests/smoke/test_forms/monitoring/suite_runner.py`

- Entrypoint `test_a2_angular_forms.py::test_a2_angular_forms`, Allure title
  `A2Angular`. Bu alohida cross-navbar test; oddiy Forms runneriga kirmaydi.
- Module docstringidagi 54 formalik inventar backlog/provenance; faol coverage
  `ADMIN_A2_FORMS`, `OPERATIONAL_A2_FORMS`, `PAGE_LINK_A2_FORMS` va skip
  registrydan tuzilgan `FormCase` rejasiga qarab aniqlanadi.
- Precondition: admin login → legacy `Администрирование` filialiga o'tish →
  birinchi operatsion filialni aniqlash → `COMPANY_URL` ostidagi texnik
  `/a2/trade/intro/dashboard` shellini ochish. Biznes formalari real menu va
  page-link orqali `run_form_cases()` bilan tekshiriladi.
- `FormMonitor` URL, loader, application error, content va title checklarini
  boshqaradi. `expect_page(title=...)` chaqiruvi yo'q; title check kontrakti
  [check-title.md](form-monitor/check-title.md)da. Lokal `_check_form` yoki
  Visitning `navigate_to_a2` flowi bu runnerning entrypointi emas.
- Allure guruhlari `navbar_tab → menu_column → menu_item`; filial, expected
  URL va actual URL monitoring kontekstida saqlanadi. `menu_column=None`
  ustunsiz menyu uchun, `page_links` parent formadan keyingi linklar uchun.
- Precondition xatosi monitor orqali qayd etiladi; yakuniy `finish()` barcha
  yig'ilgan natijalarni report qiladi. Marking skip holati
  [dossierda](forms/marking-stocktaking-list.md), company client add/edit esa
  [backlogda](#forma-yollari-va-backlog).
- Test `code` fixturega bog'liq emas; fresh `page` contexti session-scoped
  browser runtimeini qayta ishlatadi. Setup bilan bir sessiyada ikkinchi
  `sync_playwright()` yaratilmaydi.
- 2026-07 dagi 20/22/24 formalik run hisoblari joriy coverage emas;
  [history.md](history.md#skills-auditida-ajratilgan-eski-kontraktlar)da tarixiy dalil sifatida saqlanadi.

### Legacy dropdown linklarini filial deb qabul qilish regressiyasi (2026-07-27)
Tags: a2, filial, project, menu, ci, locator, regression
- GitHub Actions run `30264090893` failure screenshot/trace'ida A2 selector ikki
  alohida ro'yxat ekanligi tasdiqlandi: chapdagi `TRADE`/`Финансы` —
  `shell-project-filial--project-list` loyihalari, o'ngdagi
  `Администрирование`/`filial-pw{code}` — haqiqiy
  `shell-project-filial--filial-list` tashkilot/filiallari.
- `tests/smoke/test_forms/monitoring/navigation.py::first_operational_filial()` legacy
  `.dropdown-menu` ichidagi barcha `role=link` elementlarni olgani sabab birinchi
  `Администрирование` bo'lmagan matn sifatida `Trade` loyiha nomini qaytargan.
- Keyingi `AngularBasePage.switch_filial(name="Trade")` haqiqiy filial
  ro'yxatidan `Trade` optionini qidirib 30 soniyada `element(s) not found` bilan
  yiqilgan. Bu setup yaratgan filial, server yoki A2 formaning ochilish xatosi
  emas; operatsion filialni topish bosqichidagi project/filial klassifikatsiya
  xatosi.
- Tuzatish: `_first_operational_filial()` optionlarni umumiy `.dropdown-menu`
  ichidan emas, faqat `.filial-list` ichidan oladi; so'ng
  `Администрирование`ni chiqarib, qolgan birinchi haqiqiy filialni qaytaradi.
- Tuzatishdan keyingi standalone headless run: barcha 22 forma ochildi,
  `1 passed in 122.26s`.

### A2 project nomi TRADE'dan SFA'ga o'zgardi (2026-08-03)
Tags: a2, project, filial-switch, locator, sfa, trade
Status: live-ui-confirmed
Verified: 2026-08-03
Source: user; `test-results/allure-results/0e25c8ce-df57-4b59-8cae-60045db94448-attachment.png`;
`utils/base_pages/angular_base_page.py`
- Qayerda: `smartup.online` A2 headeridagi project/filial triggerida.
- Qoida: serverdagi avvalgi `TRADE` project nomi `SFA`ga o'zgargan. 2026-07-27
  dalillaridagi `TRADE` nomi tarixiy holat, joriy triggerda `SFA` ko'rinadi.
- Testda ishlatish: A2 filial switchining `TRADE` matniga fallbacki joriy server
  uchun eskirgan. Joriy project sifatida `SFA` ishlatiladi yoki locator project
  nomiga bog'lanmaydigan qilib yoziladi.

## Tarixiy diagnostika

Eski URL-only diagnostika va run natijalari
[history.md](history.md#skills-auditida-ajratilgan-eski-kontraktlar)ga ko'chirilgan.
Ular joriy serverdagi dostup yoki barcha formalar sog'lomligini tasdiqlamaydi.
