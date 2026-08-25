# Smoke Reporting va Allure

## Mundarija

- [Current architecture](#current-architecture)
- [User-facing execution phase contract](#user-facing-execution-phase-contract)
- [Forms central monitoring](#forms-central-monitoring)
- [Failure artifacts](#failure-artifacts)
- [Local Allure lifecycle](#local-allure-lifecycle)
- [Verification](#verification)

## Current architecture

Status: code-confirmed
Verified: 2026-07-30
Source: `tests/smoke/smoke_reporting.py`, `scripts/open_allure_report.py`

- Progress metadata marker, runner path, pytest item va Allure title'dan yig'iladi.
- `started` va final event har test uchun faqat bir marta chiqariladi.
- Forms ichki `form_result` eventi ham parent pytest itemning ayni
  `request.node.name` identitysidan foydalanadi; main runner va standalone
  wrapper o'z nomini `run_*` funksiyasiga uzatadi.
- Allure results run boshida environment va executor metadata bilan
  tayyorlanadi; category authoritysi rootdagi `allurerc.mjs`dir.
- Lokal pytest sessionlari oldingi `allure-results` fayllarini default
  saqlaydi; shu sabab setup, group va Forms kabi ketma-ket targetlar bitta
  joriy report daraxtida jamlanadi. `--clean-results` yoki
  `CLEAN_ALLURE_RESULTS=1` explicit berilgandagina raw natijalar tozalanadi.
  Allure 3 history alohida `test-results/allure-history/history.jsonl`da
  saqlanadi va raw reset unga tegmaydi. CI har jobni `--clean-results` bilan
  izolyatsiyalaydi.
- Direct pytest run ham session oxirida deterministic analyzerni ishlatadi;
  `OPEN_REPORT` faqat tayyor reportni generate/open qilishni boshqaradi.

## User-facing execution phase contract

### Allure phase ownershipi
Status: code-confirmed
Verified: 2026-08-24
Source: `tests/smoke/conftest.py`; installed `allure-pytest==2.15.3`

- Pytest fixture `yield`igacha bajarilgan `allure.step`lar `Execution -> Set up`,
  test funksiyasi ichidagilar `Test body`, `yield`dan keyingi fixture ishlari
  `Tear down` ostida ko'rinadi. Test body ichida yaratilgan stepni nomi orqali
  `Set up`ga ko'chirib bo'lmaydi; precondition haqiqatan fixture setupida
  bajarilishi kerak.
- Session/module-scoped fixture setupi faqat resursni birinchi yaratgan consumer
  testda ko'rinadi. Har test uchun bir xil setup konteksti kerak bo'lsa,
  function-scoped reporting fixture mavjud resurs holatini qayd etadi; browser,
  context yoki loginni faqat report uchun qayta yaratmaydi.
- `.env` yuklash, pytest configuration va collection test item lifecycle'idan
  oldin bajariladi. Ular per-test `Set up` execution step emas; kerakli qismi
  keyin secretlardan tozalangan setup metadata sifatida attach qilinadi.

### AI'siz user-facing diagnostika
Status: user-reported
Verified: 2026-08-24
Source: user; `test_report_integration_two` Allure failure muhokamasi

- Allure'dagi asosiy failure xulosasi AI'ga bog'lanmaydi. User raw stacktrace'ni
  tahlil qilmasdan `nima tayyorlandi`, `qaysi action bajarildi`, `nima
  kutilgan`, `amalda nima bo'ldi`, `qayerda to'xtadi` va `qaysi keyingi
  qadamlar bajarilmadi`ni ko'ra olishi kerak.
- `Set up` userga faqat qaror uchun kerakli, sanitizatsiya qilingan kontekstni
  beradi: run mode, test-data source/mavjudligi, browser/context scope,
  action/navigation timeoutlari, diagnostika yoqilganligi va authorization
  role/natijasi. Password, API key, token, session hash va credential qiymati
  ko'rsatilmaydi.
- `Test body` raqamlangan biznes qadamlarini ko'rsatadi. Failure xulosasi kamida
  `Bosqich`, `Kutilgan`, `Haqiqiy`, `Sabab klassi` va `Keyingi qadamlar`
  maydonlariga ega bo'ladi. Exception stack qo'shimcha texnik detail bo'lib
  qoladi, user-facing asosiy sabab o'rnini bosmaydi.
- `Tear down` artifact va cleanup natijasini ko'rsatadi: failure screenshot,
  trace/log saqlanishi va page/context yopilishi. Cleanup xatosi test bodydagi
  original root cause'ni yashirmaydi.

Tavsiya etilgan ko'rinish:

```text
Execution
├── Set up
│   ├── 01 | Test data — source=data_store, mavjud=ha
│   ├── 02 | Browser — Chromium, context=fresh
│   ├── 03 | Timeout — action=10000 ms, navigation=20000 ms
│   └── 04 | Authorization — role=admin, status=PASSED
├── Test body
│   └── 01 | Integration Two reportini ochish — FAILED
│       ├── Kutilgan: target URL va heading tayyor
│       ├── Haqiqiy: URL/heading tayyor, `load` 20000 msda tugamadi
│       ├── Sabab klassi: TEST_HELPER_NAVIGATION_WAIT_ERROR
│       └── Keyingi qadamlar: 02-09 NOT RUN
└── Tear down
    ├── Failure screenshot — SAVED
    ├── Trace/log — SAVED
    └── Page/context — CLOSED
```

## Forms central monitoring

Status: code-confirmed
Verified: 2026-08-10
Source: `tests/smoke/test_forms/monitoring/monitor.py`,
`tests/smoke/test_forms/monitoring/checks/url.py`,
`tests/smoke/test_forms/monitoring/checks/loader.py`,
`tests/smoke/test_forms/monitoring/checks/application_error.py`,
`tests/smoke/test_forms/monitoring/checks/content_ready.py`,
`tests/smoke/test_forms/monitoring/checks/title.py`,
`tests/smoke/test_forms/monitoring/navigation.py`,
`tests/smoke/test_forms/monitoring/reporting.py`,
`tests/smoke/test_forms/monitoring/checks/core.py`,
`tests/smoke/test_forms/monitoring/diagnostics/core.py`,
`tests/smoke/test_forms/monitoring/diagnostics/failed_requests.py`,
`tests/smoke/test_forms/inventory/skipped_forms.py`,
`tests/smoke/screenshot_masking.py`

- Forms-01 (`Главное`), Forms-02 (`Продажа`), Forms-03 (`Склад`), Forms-04
  (`Финансы`), Forms-05 (`Справочники`) va standalone `A2Angular` bir xil
  `FormMonitor` orqali ishlaydi. Asosiy Forms runner beshta navbar inventorydagi
  har bir formani alohida parametrized pytest/Allure item sifatida collect
  qiladi; `A2Angular` runnerga kirmaydi. Navbar testlarida Allure ierarxiyasi
  `Forms — navbar → menu_column → forma`; cross-navbar `A2Angular` testida
  `navbar_tab → menu_column → menu_item`.

### Forma kesimidagi canonical runner

Status: code-confirmed
Verified: 2026-08-14
Source: `tests/smoke/test_forms/test_0_forms_runner.py`,
`tests/smoke/test_forms/monitoring/recovery.py`,
`tests/smoke/test_forms/inventory/`

- `test_0_forms_runner.py` asosiy smoke/CI runner bo'lib, markaziy inventorydagi
  har bir active forma va intentional skipni bittadan parametrized pytest/Allure
  itemga aylantiradi. Forma definitionlari runnerda takrorlanmaydi; inventory
  yagona ma'lumot manbasi bo'lib qoladi. Allure total soni navbarlar sonini emas,
  jami active + intentional-skip formalar sonini ko'rsatadi.
- Canonical runner har formani `monitoring/recovery.py`dagi fail-closed policy
  orqali bajaradi. Joriy `session_unauthorized` qoidasi shu test davomida yozilgan HTTP
  `401` diagnostikasi yoki joriy `login.html` redirectini ko'rsagina admin
  authorizationni yangilaydi, filial state'ni tozalaydi va ayni formani bir
  marta qayta bajaradi. Maksimum ikki urinish bor; ikkinchi xato yoki registryga
  mos kelmagan har qanday birinchi xato original exception bilan `FAILED`
  bo'lib qoladi. Yangi recoverable holat umumiy exception retry orqali emas,
  alohida matcher/action qoidasi sifatida registryga qo'shiladi.
- Har parametrized active forma itemi aynan bitta `FormMonitor` yaratadi va
  joriy forma tugagach `finish()`ni bir marta chaqiradi. Forma xatosi shu pytest
  itemini failed qiladi, keyingi forma esa alohida item sifatida davom etadi;
  intentional skip pytest mark va sabab bilan ko'rinadi.
- Admin login module-scoped `forms_session` fixture'da bir marta bajariladi;
  kerakli filial har item oldidan session state asosida almashtiriladi. Filial
  preconditioni yiqilsa monitor `record_precondition_failure(...)` orqali
  `TEST_BLOCKED` evidence va yakuniy hisobotni yaratadi.
- Har forma faqat quyidagi holatlardan birini oladi:
  `PASSED`, `OBSERVED_ONLY`, `OPENED_WITH_DEFECT`, `NOT_OPENED`,
  `TEST_BLOCKED`, `NOT_CHECKED`. `checks=[]` bilan navigatsiya bajarilib hard
  check ishlamasa `OBSERVED_ONLY`; analyzer uni failure deb hisoblamaydi.
- `OPENED_WITH_DEFECT` target forma/URL ochilgan, lekin title, blocking loader,
  UI application error yoki kontent tekshiruvida nuqson borligini bildiradi. `NOT_OPENED` target URL/kontentga
  yetilmaganini bildiradi. Login, filial yoki shell tayyorlovi yiqilsa joriy
  forma `TEST_BLOCKED`, boshlanmagan qolgan formalar `NOT_CHECKED` bo'ladi.
- Har xatoda monitor actual URL/title, URL mosligi, kontent tayyorligi, blocking loader,
  ko'rinadigan UI error, xato bosqichi va qisqa QA sababini yig'adi. Bundan
  tashqari `test_started`, `test_completed`, `page_reached`,
  `validation_completed`, `validation_passed` va `usable` alohida saqlanadi.
  Nuqson topilgan forma uchun validatsiya bajarilgan, ammo undan o'tmagan deb
  ko'rsatiladi; suite bloklangan sahifa esa forma ochildi deb noto'g'ri
  hisoblanmaydi.
- URL birinchi hard gate: `url_timeout` ichida exact canonical target ochilmasa
  `EXPECTED_URL_NOT_REACHED` yoziladi va boshqa hard check/diagnostikalar
  `NOT_RUN` bo'ladi. Menu failure screenshoti direct urinishdan oldin olinadi;
  optional shell-aware direct probe ikkinchi screenshot va structured xulosani
  saqlaydi, ammo original failure'ni passga aylantirmaydi.
- Loader URLdan keyingi ikkinchi hard gate: ko'rinadigan `.block-ui-overlay`
  yoki `.smt-skeleton` default `60_000 ms` ichida yo'qolmasa
  `OPENED_WITH_DEFECT / LOADER_NOT_FINISHED` yoziladi. `application_error`,
  `content_ready` va `title` `NOT_RUN`, `blocked_by=loader` bo'ladi; evidence
  olingach suite keyingi formaga davom etadi. Forms navigatsiyasi loaderni
  oldindan kutmaydi — kutish va timeout klassifikatsiyasi `check_loader`
  ichida.
- Application error URL va loaderdan keyingi uchinchi browser-aware hard gate:
  aniq Biruni, inline yoki A2 error signali default `1_200 ms` ichida
  ko'rinsa `OPENED_WITH_DEFECT / APPLICATION_ERROR` yoziladi.
  `content_ready` va `title` `NOT_RUN`, `blocked_by=application_error` bo'ladi.
  Generic `[role="alert"]` hard signal emas va `allowed_warnings` exceptioni
  yo'q. Failure screenshoti Biruni modalini yopishga urinishdan oldin olinadi;
  cleanup faqat Biruni modaliga tegadi va original failure'ni o'zgartirmaydi.
- Content ready to'rtinchi browser-aware hard gate: explicit `ready` selector
  bo'lsa o'shani, aks holda legacy `b-page/.subheader` yoki A2 `main` kontentini
  default `15_000 ms` ichida kutadi. Timeoutda
  `NOT_OPENED / CONTENT_NOT_READY`; `title` `NOT_RUN`,
  `blocked_by=content_ready`. `capture_form_state()` content readinessni qayta
  kutmaydi yoki baholamaydi.
- Title beshinchi va oxirgi browser-aware hard gate: legacy formada visible
  semantic headingni, A2 formada `document.title`ni default `15_000 ms` ichida
  whitespace-normalized exact kutadi. Partial match va missing Legacy heading
  failure: `OPENED_WITH_DEFECT / TITLE_NOT_REACHED`. Title kutishning yagona
  authoritysi `check_title`; eski `settle_form_open()` va silent unverified-pass
  hisoboti yo'q.
- Xato paytidagi full-page screenshot aynan shu forma Allure stepiga
  biriktiriladi. Default mask faqat password/secret/token elementlarini
  yashiradi; oddiy search/filter inputlari ochiq qoladi.
- Kengroq forma masklari `screenshot_masking.py`dagi opt-in profillarda turadi.
  Profil case inventarida explicit ko'rsatiladi va faqat profilga mos URL
  ochilganida ishlaydi. Hozir `company-client` profili OAuth inputlari va list
  qatorlarini to'liq yopadi.
- `run_form_cases()` uchun `FormMonitor` majburiy. Eski parallel
  `finish_form_results()`/`results` hisoboti yo'q; barcha yangi forma rejalari
  yagona `build_form_case_plan()` orqali normalizatsiya qilinadi.
- `SKIPPED_FORMS` registry'sidagi canonical pathlar active `planned_cases`ga
  kirmaydi, ammo `build_form_case_inventory()` ularni reason bilan alohida
  qaytaradi. Terminal/Allure va schema v4 JSON total inventory, active count va
  intentional skip count/listni ko'rsatadi.
- Har forma tugashi bilan terminal reporter orqali bitta to'liq kontekstli
  `[FORM MONITOR]` qatori chiqariladi: filial, navbar tab, menu ustuni,
  tekshirilgan forma, kutilgan URL, haqiqiy URL, status va sabab. Uzoq Forms
  run vaqtida joriy progress va oxirgi forma holati ko'rinib turadi. Yakuniy
  terminal/Allure summarydagi har bir boshlangan forma qatori ham shu yagona
  formatterdan foydalanadi. Shu natija `SMARTUP_PROGRESS form_result` eventiga
  ham aylanadi va Telegram progress consumeri uni joriy forma sifatida o'qiydi.
  Failure uchun ko'p qatorli diagnostika alohida saqlanadi.
- Yakuniy terminal text, Allure text va `form-monitor.json` bir xil natijalar
  ro'yxatidan quriladi; shu sabab hisoblar va forma tafsilotlari bir-biridan
  farq qilmasligi kerak.
- Har top-level Forms testida bitta summary va bitta `form-monitor.json`
  attachmenti bo'ladi. `scripts/analyze_test_result.py` shu yagona payloadni
  suite coverage/count/failure xulosasiga aylantiradi.
- Analyzer `test_forms_<raqam>_<slug>` nomini generic taniydi va yangi navbar
  labelini monitorning `Forms-XX — <Navbar>` suite nomidan oladi. Shu sabab
  yangi `Склад`/`Финансы` suite qo'shilganda analyzerga alohida hardcoded key
  qo'shish talab qilinmaydi; `A2Angular` uchun eski `a2_admin` compatibility
  key saqlanadi.
- A2 uchun forma nomi manbasi browser `document.title`; legacy uchun visible
  page heading. JSONdagi `hard_checks.title.title_source` qaysi signal
  ishlatilganini, `document_title` va `title_candidates` esa failure
  diagnostikasini saqlaydi.
- Browser-aware `check_loader` ko'rinadigan `.block-ui-overlay` yoki
  `.smt-skeleton` yo'qolishini kutadi. `[aria-busy=true]` blocking loader emas
  va FormMonitor uni diagnostika sifatida yig'maydi.
- FormMonitor JavaScript exceptionni hard check yoki alohida `pageerror`
  listener orqali kuzatmaydi. Smartup application xatolari ko'rinadigan UI
  error/Biruni signallari orqali `APPLICATION_ERROR` sifatida tekshiriladi.
- `monitoring/diagnostics/` package'i `monitoring/checks/`ga parallel extension
  boundary: har diagnostika alohida modul va `core.py` registry entry oladi.
  Hozir faqat `failed_requests` registered; FormMonitor package'ning
  `reset/evaluate/close` lifecycle'ini chaqiradi va HTTP listener logikasini
  o'zida saqlamaydi.
- HTTP `4xx/5xx` response diagnostikasi observation-only. Query stringsiz raw
  namunalari va haqiqiy count `form-monitor.json`da saqlanadi; human report
  `/page/tour/` va optional A2 i18n request shovqinini agregatsiya qiladi.
  `busy`, resource error, unhandled promise rejection va `title_metadata`
  diagnostikalari yig'ilmaydi.
- `build_form_case_inventory()` active planned va registry-skipped formalarni
  alohida normalizatsiya qiladi. `form-monitor.json` schema v4 `inventory`,
  `skipped`, `config.enabled_checks` va `config.enabled_diagnostics`ni beradi;
  intentional skip `NOT_CHECKED` emas. Har resultda `identity`, auto/explicit
  `label`, schema-v4 `hard_checks` va `diagnostics` bor. Eski consumerlar uchun
  schema-v3 flat `checks` compatibility maydoni saqlanadi.
- Schema v4 configida `url_timeout_ms`, `loader_timeout_ms`,
  `application_error_timeout_ms`, `content_ready_timeout_ms`,
  `title_timeout_ms` va
  `try_direct_url`; URL failure resultida
  direct expected/actual URL,
  `direct_url_reached` va xulosa mavjud. Direct probe yoqilganida menu va
  direct holatlar uchun ikki evidence yozuvi saqlanadi. Loader failure
  resultida `visible_loaders`, `loader_count` va timeout saqlanadi.
  Application-error resultida `matched_error_selector`, `error_text`, timeout
  va `modal_cleanup_attempted/succeeded/error` maydonlari saqlanadi.
  Content-ready resultida `ready_source`, `expected_ready`,
  `matched_ready_selector`, `content_observation` va timeout saqlanadi.
  Title resultida `title_source`, `expected_title`, `actual_title`,
  `title_candidates` va timeout saqlanadi.
- Konfiguratsiya faqat test/FormMonitor darajasida: `None` barcha registered
  signallar, `[]` hech biri, `list[str]` faqat tanlangan nomlar. Disabled signal
  pass sifatida ko'rsatilmaydi; nested resultda `enabled: false` bo'lib qoladi.
- Terminal/Allure human report enabled/total coverage, failed hard checklar va
  counti bor HTTP diagnostikasini ko'rsatadi. Disabled yoki counti `0` signal
  alohida uzun qatorga yoyilmaydi; to'liq signal inventari JSONda qoladi.
- Har bir forma uchun ko'p qatorli human report bitta umumiy skeletdan
  foydalanadi: header, forma, filial, to'liq navigatsiya yo'li va kutilgan URL.
  Failure bo'lsa xato bosqichi, reason-code va bitta aniq sabab ko'rsatiladi;
  menu/title/label, status va generic/technical sabablar dublikat qilinmaydi.
  Bo'sh action, page-link, direct-probe yoki diagnostika maydonlari chiqarilmaydi.
- Human report hard checkni faqat uning `execution_status` qiymati
  `PASSED` yoki `FAILED` bo'lsa bajarilgan deb ko'rsatadi. Navigatsiya,
  precondition yoki not-started bosqichida olingan compatibility snapshot
  checklari failure sifatida talqin qilinmaydi: barcha enabled hard checklar
  aniq sabab bilan `Bajarilmadi` bo'ladi. Validation gate xatosida undan oldingi
  checklar `✅/❌`, `NOT_RUN` checklar esa bloklovchi gate bilan ko'rsatiladi.
- Diagnostika reason-code bo'yicha shartli: navigation uchun joriy sahifa,
  URL uchun actual URL/timeout va faqat bajarilgan direct probe, loader uchun
  visible loaderlar, application error uchun UI xato signali, content-ready
  uchun kontent kuzatuvi, title uchun expected/actual title ko'rsatiladi.
  Screenshot va davomiylik human reportda qoladi; to'liq schema-v4 metadata va
  compatibility maydonlari `form-monitor.json`da saqlanadi.

## Failure artifacts

- Failed test uchun `00 - Failure Summary`, `01 - Browser State`, redacted
  full-page screenshot, tayyor Playwright trace, session-tokeni yashirilgan
  current URL, page title va mavjud data-store Allure'ga attach qilinadi.
- `Browser State` current URL/title, visible headinglar, visible Biruni/UI
  alertlar va blocking loader countini strukturali JSON sifatida beradi.
- Deterministic analyzer failed Allure step, exception, browser state va trace
  reference'ni birlashtirib aynan failed testcase ichiga human-readable
  Markdown va JSON summary qo'shadi. Alohida System Summary'ni ochish failure
  sababini tushunish uchun majburiy emas.
- Function-scoped test trace'i testga, module/session-scoped trace esa shu
  contextni qamragan failed testlarga biriktiriladi; bir xil katta trace
  Allure results ichiga faqat bir marta ko'chiriladi.
- Failure kategoriyalari `allurerc.mjs`da o'zaro takrorlanmaydigan
  synchronization, navigation, locator/UI state, download, verification,
  environment/precondition, unclassified va ignored guruhlarga ajratiladi.
- Forms runnerda umumiy pytest failure screenshoti bilan birga har bir muammo
  aniqlangan paytdagi forma screenshoti ham alohida attach qilinadi. Yakuniy
  sahifa screenshoti `pytest-final-page-context — failed-form dalili emas` deb
  nomlanadi va oldingi forma xatosining dalili sifatida ishlatilmaydi.
- Pytest longrepr `test-results/logs/` ichiga yoziladi.
- Failure diagnostikasi add/edit formdagi asl save/error transitionini
  keyingi list/view timeoutidan oldin ko'rsatishi kerak.

### Integration report navigatsiyasi

Status: code-confirmed
Verified: 2026-08-24
Source: `tests/smoke/test_groups/test_report_grup/report_helpers.py`

- Hash-route integration reporti `page.goto(..., wait_until="commit")` bilan
  ochiladi; global browser `load` eventi biznes readiness signali emas.
- Route commitdan keyin real readiness `BasePage.expect_page()` orqali target
  URL, heading va Smartup loader holati bilan tekshiriladi.
- `open_report(..., timeout=...)` timeouti navigation commitga ham,
  `expect_page()`ga ham uzatiladi.

## Local Allure lifecycle

### Allure 3 startup heartbeat tartibi
Status: live-ui-confirmed
Verified: 2026-08-24
Source: Chrome `http://127.0.0.1:<port>`; `test-results/logs/allure-report-server.log`;
`scripts/open_allure_report.py`

- Allure 3 app bundle'i birinchi heartbeatdan oldin yuklansa, 12 soniyalik
  watchdog serverni yopib, qisman ochilgan report widgetlarida
  `Failed to fetch` chiqarishi mumkin.
- Heartbeat standart report HTMLida `<head>` boshiga, app bundle'dan oldin
  inject qilinadi; `</head>` bo'lmagan nonstandard HTML uchun body/append
  fallback saqlanadi.
- Tuzatilgan server real Chrome'da 15 soniyadan keyin ham healthy qoldi,
  reportda `Failed to fetch` yo'q va 11 ta result ko'rindi.

### Ketma-ket lokal run natijalarini jamlash talabi
Status: code-confirmed
Verified: 2026-08-24
Source: user; `scripts/run_tests.py`; `tests/smoke/smoke_reporting.py`;
`.github/workflows/run-smartup-suite.yml`

- Setup, Group-0 va boshqa lokal targetlar alohida-alohida ketma-ket run
  qilinganda oldingi target natijalari keyingi Allure report daraxtida saqlanib,
  yangi target natijalari bilan birga ko'rinishi kerak.
- JSONL history bu talabning o'rnini bosmaydi: history trend va status
  transitionlar uchun, joriy report daraxti esa ketma-ket targetlarning
  jamlangan raw resultlarini ko'rsatishi kerak.
- Yangi toza report boshlash alohida explicit reset bo'lishi kerak; oddiy
  target runi oldingi boshqa target natijalarini avtomatik o'chirmaydi.
- Bir xil `historyId`li test qayta run qilinsa Allure 3 eng yangi natijani
  primary status sifatida ko'rsatadi, oldingi natijani esa retry sifatida
  saqlaydi; bir xil test ikkita primary leaf bo'lib ko'rinmaydi.

- Status: code-confirmed
- Verified: 2026-08-24
- Source: `allurerc.mjs`, `scripts/allure_report_cli.py`,
  `scripts/run_tests.py`, `tests/smoke/smoke_reporting.py`,
  `scripts/open_allure_report.py`, `.github/workflows/run-smartup-suite.yml`
- Allure Report 3 CLI `package-lock.json`da `3.14.3`ga pin qilingan va faqat
  `node_modules/.bin/allure[.cmd]` orqali resolve qilinadi; global CLI yoki Java
  fallback yo'q.
- Direct pytest run `OPEN_REPORT=1` bo'lsa shared helper bilan Awesome report
  generate/open qiladi; `SMARTUP_RUNNER=1` bo'lsa runner lifecycle'ni
  boshqaradi. CI `DEFER_ALLURE_REPORT=1` bilan runner generationini o'tkazib,
  `if: always()` workflow stepida shu helperni bir marta chaqiradi.
- Allure 3 config primary daraxtni `epic → feature → story`, report nomini
  `Smartup Smoke Tests`, tilni `en` va multi-file outputni explicit belgilaydi.
- Har executable smoke test title va hierarchy label manbasiga ega. Group
  runner wrapper title'lari standalone leaf title'lari bilan bir xil;
  parametrized Forms itemlari feature/story marklarini `pytest.param`ga qo'yadi,
  shuning uchun test body boshlanmasdan skip bo'lsa ham hierarchy saqlanadi.
- System va AI summary resultlari hierarchy uchun faqat `epic`, `feature`,
  `story` label'lariga tayanadi; `titlePath` compatibility maydoni yozilmaydi.
- History default `test-results/allure-history/history.jsonl`, append yoqilgan
  va 50 entry bilan cheklangan. CI cache `server_key + target` prefixi bilan
  izolyatsiyalanadi; har run unique cache key saqlaydi.
- Eski Allure 2 `allure-report/history → allure-results/history` copy qilinmaydi
  va avtomatik convert qilinmaydi; yangi JSONL history migratsiyadan keyingi
  birinchi generationdan boshlanadi.
- `scripts/open_allure_report.py` state + lock + health-check bilan mavjud
  healthy serverni qayta ishlatadi.
- Stale state yangi server bilan almashtiriladi.
- Report tab heartbeat yuboradi; `</body>` bo'lmagan HTMLda script oxiriga
  fail-safe append qilinadi. Allure 3'ning katta app bundle'i birinchi signalni
  kechiktirmasligi uchun standart HTMLda heartbeat `<head>` boshiga, barcha app
  scriptlaridan oldin inject qilinadi. Tab yopilgach lokal server grace
  perioddan keyin to'xtaydi.
- Helper process parent stdout/stderr va session lifecycle'iga bog'lanib
  qolmasligi kerak.

## Verification

- Default holatda reporting kodini syntax parse, linter, read-only artifact
  inspection va `git diff --check` bilan tekshir; unit test fayllarini yaratma
  yoki o'zgartirma.
- `tests/unit/test_telegram_reporting.py` faqat user aynan unit test yozish yoki
  o'zgartirishni so'rasa tahrirlanadi; `pytest` esa user aynan `run qil` deganda
  ishga tushiriladi. Bu reference'dagi command/tavsiya o'zicha authority emas.
- Report server uchun production browser/processni o'zboshimchalik bilan ochma;
  lokal generated report yoki state/health-check ham user execution so'ragan
  scope ichida bo'lsin.
