# A2 (migratsiya qilingan yangi) formalar

## Mundarija

- [Arxitektura](#arxitektura)
- [Yangi Angular component kontrakti](#yangi-angular-component-kontrakti-companyda-live-tasdiqlangan-2026-07-23)
- [Menyu filialga bog'liqligi](#menyu-филиалга-bogliq-eng-muhim-kuzatuv-2026-07-07)
- [Real-user navigatsiya](#real-user-navigatsiya-menyu-orqali--2-etap-testlar-uchun)
- [Filial switcher DOM](#filial-switcher-dom)
- [Test](#test)
- [Diagnostika natijasi](#diagnostika-natijasi-2026-07-07-app3greenwhiteuzxtrade--2-passed-0-muammo)

Tags: a2, migrated-forms, filial, menu, navigation, error, url, new_forms

Smartup yangi formalari (yangi Angular/modern app) eski AngularJS Biruni app ustiga qo'shilgan. Ular
`new_forms.md` (repo root) da ro'yxatlangan va URL'да **`a2`** prefiksi bilan ajraladi.

## Arxitektura

- **Page-object chegarasi:** legacy AngularJS/Biruni formalar
  `utils/base_page.py::BasePage` bilan, yangi A2 Angular formalar
  `utils/angular_base_page.py::AngularBasePage` bilan yoziladi. Legacy class
  mavjud eski formalar tugamaguncha aktual saqlanadi; ikki DOM selectorlari bitta
  helperga fallback qilib aralashtirilmaydi.
- **Alohida app.** Eski menyudan a2 forma bosilganda `{base}/a2/{path}` ga **to'liq sahifa** navigatsiya bo'ladi
  (SPA hash-route emas). `base` = `company_url()`:
  - smartup.online: `https://smartup.online/a2/{path}`
  - app3: `https://app3.greenwhite.uz/xtrade/a2/{path}`
  - `{path}` = `new_forms.md` dagi yo'l, masalan `biruni/md/company_list`, `anor/rep/mbi/mkw/purchase`.
- **Sog'lom forma signali:** `document.title` forma nomiga aylanadi (masalan "Компании", "Логистика").
  Content async yuklanadi — dashboard/list/catalog formalar title resolve bo'lgach ham 1-1.5s kontent yuklaydi.
- **Muammo signallari** (title "Smartup Online" da qoladi):
  - `Страница не найдена` — 404 (forma yo'q).
  - `Нет доступа к форме {name}` / `Не удалось загрузить` / `Что-то пошло не так` — ruxsat yo'q yoki load error.
  - `+edit`/`_view`/`_details` yakka URL bilan ochilmaydi — id (record) kerak; title shell'da qoladi.

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
  (`test_02_a2_admin_menu_forms.py`) yig'iladi.
- **Forma joyi (filial + aniq user track) — AVTORITET manba: `new_forms.md` (repo root).** U formalarni
  operatsion/Администрирование filial bo'yicha guruhlab, har biriga real user track (LEAF / LIST-ACTION / SIBLING)
  beradi. Qisqacha (2026-07-08 live tasdiqlangan):
  - "Администрирование" da: `kauth/company_client_list` (+undan `+add`/`+edit` list-action).
  - Operatsion filialda LEAF: Визиты/Логистика, dashboardlar, `anor/rep/mkr/pnl` («PnL»),
    barcha `anor|trade/rep/mbi/*` report designerlar, `plg/plugin_catalog`, `external_settings`.
  - Operatsion, SIBLING (menyu modelida YO'Q, eski forma ichidan): `mcg/action` (Акции→…), `marking_stocktaking_list`
    (Инвентаризации→Инвентаризация КМ).
- **Hali live tasdiqlanmagan admin formalar** (`md/*`, `ms/announcement_list`, `kauth/client_list`,
  `kauth/security_settings`, `billing/operational_dashboard` va ularning list-action ko'rinishlari) — bular ham ADMIN
  formalar, angular menyudan ochiladi; user track hujjat asosida `new_forms.md` da, testga qo'shilганда tasdiqlanadi.
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
- **Flow helper:** `navigate_to_a2(page, tab, path)` (flows/flow_navigate.py) — tab bosadi, leaf ko'rinishini kutadi,
  bosadi, URL `/a2/{path}` ga o'tguncha va `document.title` "Smartup Online" (shell) dan forma nomiga aylanguncha kutadi.
  Sub-kategoriya (`h3.menu-heading`) ni ochish SHART EMAS — tab bosilganda flyout barcha leaflarni ko'rsatadi.
- **Ochilgani signali:** `expect(page).not_to_have_title("Smartup Online")` — dashboardlar ham (async) title'ni
  forma nomiga o'zgartiradi. `heading`/`mainLen` ga tayanma (dashboardlarda async, false-negative).
- **Menyu leaflari filial menusidan keladi** — barcha a2 leafni bitta o'qishда olish uchun angular session
  modelini (read-only) ishlat: `a.session.si.projects[0].filials[].menus[].menus[].forms[]`, `is_migrated==='Y'`
  bo'lganlari. Har `form`: `{form(path), name, is_migrated}`. Bu real menyu leaflarining AVTORITET manbai
  (URL'да ochiladigan, lekin menyuда YO'Q formalardan farqli).

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
- `test_02_a2_admin_menu_forms.py` code/data_store'ga bog'lanmaydi: operatsion filial sifatida angular session modelidagi
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
Verified: 2026-07-30
Source: `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py`; `tests/smoke/test_forms/test_0_forms_runner.py`

- Joriy entrypoint `test_0_forms_runner.py::test_forms_02_a2_admin`;
  u `run_a2_admin_menu_forms(...)`ni mavjud admin sessiyasida chaqiradi.
- Har bir qamralgan A2 forma real navbar → menu column → menu item yoki
  page-link yo'li orqali ochiladi; title va URL alohida tekshiriladi.
- 53 formalik inventar joriy test docstringida backlog/provenance sifatida
  saqlangan; current coverage faqat `✅ YOZILGAN` menu-tracklar bilan
  belgilanadi. Oldingi URL-only harness konteksti
  [history.md](history.md)da turadi.

- **Joriy menu-track runner (`test_02_a2_admin_menu_forms.py`) — real menyu orqali:**
  Har a2 formani ESKI menyudan `navigate_to_a2(page, tab, path)` bilan ochadi (real user yo'li), xatoda to'xtamaydi,
  filial bo'yicha guruhlangan hisobot beradi. **Barcha angular-menyu a2 formalar ADMIN** — alohida head test YO'Q;
  hali live tasdiqlanmagan admin formalar (`md/*`, `announcement`, `client_list`, `security_settings`,
  `operational_dashboard`, ...) shu SHU faylga qo'shib boriladi.
  - Har bir qamralgan forma yozuvida `new_forms.md` bilan bir xil to'liq user
    track saqlanadi. Track Allure step nomi bo'ladi va yakuniy `HISOBOT`da har
    forma ostida `Track:` qatori sifatida chiqadi. `LEAF`, `SIBLING`,
    `company_client+add` va `company_client+edit` tracklari majburiy.
  - **Menyudan ochiladigan admin formalar (red_test, 2026-07-08 live tasdiqlangan):**
    - birinchi "Администрирование" bo'lmagan operatsion filialda 19 ta: `external_settings`, `visit_list`, `user_locations`, `user_tracking`,
      `commercial_dashboard`, `rep/mbi/tvt/visit`, `logistics_list`, `mkw/{movement,purchase_request,purchase,input,writeoff}`,
      `mfm/{movement,movement_request}`, `mkcs/operation`, `anor/rep/mkr/pnl` (leaf matni "PnL", Финансы),
      `tmcg/shelf_share`, `mqpf/request`, `plugin_catalog`.
    - "Администрирование" filialida: `biruni/kauth/company_client_list` + undan `+add` (list → «Создать») va
      `+edit` (qator bosilsa «Изменить» tugmasi chiqadi → ochiladi). Ochilish signali: main'da «Сохранить» tugmasi.
      `+add`/`+edit` menyu leafi EMAS — list ichidan tugma bilan ochiladi (dblclick shart emas, bir marta qator bosiladi).
  - **"Sibling" orqali ochiladigan a2 (menyu leafi EMAS, eski forma ICHIDAN — MUHIM):** ba'zi a2 konstruktorlar
    alohida menyu leafiga ega emas va **angular menyu modelida ham ko'rinmaydi** — eski forma menyudan ochilib, uning
    subheader'idagi sub-link (`a[ng-click*="openSibling"]`) bosiladi → `/a2/{path}` ga o'tadi. Shuning uchun forma
    "menyuda yo'q" degan xulosani FAQAT menyu modelini skanlab chiqarma — eski/qardosh formani OCHIB, subheader
    sub-linklarini ham tekshir. Tasdiqlangan (2026-07-08):
    - `anor/rep/mbi/mcg/action` = Справочники → «Акции» (eski `anor/mcg/action_list`) → sub-link «Конструктор отчетов по акциям».
    - `anor/mkw/marking_stocktaking/marking_stocktaking_list` = Склад → Документы → «Инвентаризации» (eski
      `anor/mkw/stocktaking/stocktaking_list`) → sub-link «Инвентаризация КМ».
    Action konstruktori testda `PAGE_LINK_A2_FORMS` orqali ochiladi. Marking
    stocktaking formasining joriy coverage holati
    [form dossierida](forms/marking-stocktaking-list.md) saqlanadi.
  - **new_forms.md da bor, red_test menyusida hali topilmadi** (URL test qamraydi):
    `anor/rep/mbi/mfa/purchase` (user bermagan — keyin). Boshqa company/serverda bo'lishi mumkin.
  - Hali URL-only (real user yo'li aniqlanmagan): `ker/setting+add/+edit`, `ker/head_template_list+attach`,
    `company_audit_info_audit(+details)` — kompaniya «История изменений» tugmasidan ochilishi mumkin (tekshirilmagan).
  - **Standalone run:** `test_02_a2_admin_menu_forms.py` uchun `code` fixture kerak emas; `.env` faqat login/server
    credentiallariga (`COMPANY_URL`, `COMPANY_CODE`, `COMPANY_PASSWORD`) ta'sir qiladi.
  - Setup bilan bir sessiyada collect qilinganda test fresh `page` contextida
    ishlaydi, ammo u Setupning faol `session_browser` runtimeini qayta ishlatadi;
    alohida `sync_playwright()` ochilmaydi.

### Explicit menu-track test (2026-07-27)

- `test_02_a2_admin_menu_forms.py` module docstringi kelajak backlogi sifatida
  `A2_FORMS`dagi barcha 53 formani profile → filial bo'yicha saqlaydi. Har
  yozuvda status (`✅ YOZILGAN`/`⬜ QOLGAN`), mode, path, title, parent (kerak
  bo'lsa) va mavjud user trace bor. Yangi menu-track qo'shilganda shu yozuvning
  statusi va yuqoridagi jami hisoblari ham yangilansin.
- `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py` aktiv route
  definitionlarini yagona `FormCase` rejasiga aylantirib, markaziy monitor
  orqali ketma-ket loopda bajaradi. Plan qurish va title fallback boshqa
  runnerlarda takrorlanmaydi.
- Parametrlar real UI ma'nosida: `navbar_tab` — yuqori navbar,
  `menu_column` — mega-menu ustuni, `menu_item` — ustundagi forma,
  `page_links` — parent forma ochilgach bosiladigan yuqori linklar.
- Lokal `_check_form(...)` faqat click navigatsiyasini bajaradi. Legacy
  dashboarddan birinchi forma `BasePage.navigate_to_form(...)` bilan ochiladi;
  undan keyingi A2 menu qadamlari `AngularBasePage.navigate_to(...)` bilan
  bajariladi. Har bir A2 formadan keyin title va URL alohida
  `AngularBasePage.expect_page(title=..., url=...)` bilan tekshiriladi.
- Allure ierarxiyasi: filial parent step → raqamlangan forma step → `Yo'l: ...`
  navigatsiya stepi + kutilgan title va URL qiymatlari aniq yozilgan tekshiruv
  stepi. Generic `Tekshiruv: title va URL` ishlatilmaydi; reportda nima
  tekshirilgani stepni ochmasdan ko'rinishi kerak. Navigatsiya yoki
  `expect_page()` yiqilsa aynan tegishli forma qizil ko'rinadi.
- A2 filial switchi ham A2 sahifada
  `AngularBasePage.switch_filial(name=operational_filial)` bilan qilinadi;
  legacy `BasePage.switch_filial()` A2 shell selectorlariga mos emas.
- 2026-07-27 live natija: **20/20 passed**. Keyin PnL foydalanuvchi
  tasdiqlagan exact `menu_item="PnL"` bilan qayta qo'shildi, ammo foydalanuvchi
  ko'rsatmasiga ko'ra bu o'zgarishdan keyin test run qilinmadi.
- Keyin `biruni/kauth/company_client_list` ham foydalanuvchi tasdiqlagan real
  track bilan qayta qo'shildi; bu o'zgarishdan keyin ham test run qilinmadi.
- Kelishilgan execution tartibi:
  1. login'dan keyin `dashboard()` heading va URLni tasdiqlaydi;
  2. `switch_filial(name="Администрирование")`;
  3. ochilgan filial ro'yxatidan birinchi `Администрирование` bo'lmagan nom
     `operational_filial`ga saqlanadi;
  4. texnik A2 dashboard shell ochilib, A2 filial konteksti
     `Администрирование` bilan sinxronlanadi;
  5. real A2 menu track orqali `company_client_list` bir marta ochilib,
     markaziy URL/title/readiness tekshiruvi bilan tasdiqlanadi;
  6. ortga qaytmasdan shu sahifadan
     `switch_filial(name=operational_filial)` qilinadi;
  7. operatsion filialdagi direct menu formalar, keyin `page_links` orqali
     ochiladigan formalar ketma-ket tekshiriladi.
- Joriy refaktorda 22 forma bor: 1 ta admin list, 19 ta operatsion direct va
  2 ta `page_links` formasi. 2026-07-27 live run:
  **22/22 passed, 123.45s**.
- Forms runner bitta page'da legacy `#/` → A2 → legacy `#/` → A2 o'tishlarini
  bajarganda legacy va A2 shell filial kontekstlari ajralib qolishi mumkin.
  `BasePage.switch_filial("Администрирование")` A2 shellning oldingi
  operatsion filialini almashtirmaydi. Admin-only A2 route ochilgach
  `AngularBasePage.switch_filial("Администрирование")` qilinadi; bu switch
  `/a2/trade/intro/dashboard`ga redirect qilgani uchun target forma A2
  menyusidan qayta ochilib, shundan keyin title/readiness tekshiriladi.
  2026-07-29 target Forms-02 headless run: **22/22 passed, 137.19s**.
- Strukturali reporting verifikatsiyasi: Forms-02 target headless run
  **22/22 passed, 136.83s**. Terminal summary har qatorda filial, tab, menu,
  forma va full URLni chiqardi; generatsiya qilingan Allure JSONda har forma
  uchun kontekstli step, kutilgan URL va haqiqiy URL steplari `passed`.
- Reporting-only o'zgarishda forma UI/state o'zgarmagani uchun yangi screenshot
  olinmadi; mavjud A2 forma screenshotlari aktual.
- Live title farqlari: PnL formasi title'i aynan `PnL`; shelf-share title'i
  aynan `Конструктор отчётов по доле на полке`; mkw/mfm report konstruktorlari
  `Конструктор отчетов по ...` ko'rinishida.
- Hozircha keyinga qoldirilgan 2 forma:
  `biruni/kauth/company_client+add`, `biruni/kauth/company_client+edit`.
- Real menu farqlari:
  - shelf-share: `Торговый маркетинг → Отчеты → Конструктор отчётов по доле на полке`;
  - Plugin Marketplace ustunsiz kichik flyout: `Плагин → Plugin Marketplace`,
    shuning uchun `menu_column=None`;
  - action va marking stocktaking konstruktorlari `page_links` orqali parent
    formadan ochiladi.

### Legacy dropdown linklarini filial deb qabul qilish regressiyasi (2026-07-27)
Tags: a2, filial, project, menu, ci, locator, regression
- GitHub Actions run `30264090893` failure screenshot/trace'ida A2 selector ikki
  alohida ro'yxat ekanligi tasdiqlandi: chapdagi `TRADE`/`Финансы` —
  `shell-project-filial--project-list` loyihalari, o'ngdagi
  `Администрирование`/`filial-pw{code}` — haqiqiy
  `shell-project-filial--filial-list` tashkilot/filiallari.
- `test_02_a2_admin_menu_forms.py::_first_operational_filial()` legacy
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
`utils/angular_base_page.py`
- Qayerda: `smartup.online` A2 headeridagi project/filial triggerida.
- Qoida: serverdagi avvalgi `TRADE` project nomi `SFA`ga o'zgargan. 2026-07-27
  dalillaridagi `TRADE` nomi tarixiy holat, joriy triggerda `SFA` ko'rinadi.
- Testda ishlatish: A2 filial switchining `TRADE` matniga fallbacki joriy server
  uchun eskirgan. Joriy project sifatida `SFA` ishlatiladi yoki locator project
  nomiga bog'lanmaydigan qilib yoziladi.

## Diagnostika natijasi (2026-07-07, app3.greenwhite.uz/xtrade — 2 passed, 0 muammo)

- **ADMIN profil (admin@red_test):** 30/30 muvaffaqiyatli (28 direct OCHILDI + 1 via_list edit OCHILDI + 1 skip[ker/setting+edit]).
- **HEAD profil (admin@head):** 23/23 muvaffaqiyatli (14 direct OCHILDI + 8 via_list edit OCHILDI, jumladan
  Компании, Логи, Настройки безопасности, Объявления, Операционный дашборд + ularning +edit/+view formalari).
- **Hech bir a2 forma buzuq emas.** +edit/+view/+copy/_details formalar mos `_list` birinchi qatoridan
  (double-click) ochiladi — hammasi OCHILDI.
- **TUZATISH (2026-07-08 user qoidasi):** "head-only" deb belgilangan formalar aslida ham ADMIN formalar — angular
  menyu orqali ochiladi. Yuqoridagi URL-diagnostikada admin@head da ochilishi shundan: forma faqat head KOMPANIYASIда
  mavjud bo'lgan (profil emas, kompaniya masalasi). Menyu-based testда bularning hammasi admin sifatida qamraladi.
- "Ochilgan" signali — `document.title` forma nomiga (yoki `+edit` da path'ga) aylanishi + `main` da kontent.
  `mainLen` ni yakka ochilish mezoni sifatida ishlatma — async/datasiz formalarda false-negative beradi.
