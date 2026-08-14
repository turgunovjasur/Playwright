# Smoke Reporting va Allure

## Mundarija

- [Current architecture](#current-architecture)
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
- Allure results run boshida history, environment, categories va executor bilan
  tayyorlanadi.

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
  `FormMonitor` orqali ishlaydi. Asosiy Forms runner beshta navbar suite'ni
  shu tartibda non-parametrized pytest item sifatida collect qiladi;
  `A2Angular` runnerga kirmaydi. Navbar testlarida Allure ierarxiyasi
  `menu_column → menu_item`; cross-navbar `A2Angular` testida
  `navbar_tab → menu_column → menu_item`.
- Har top-level test o'z leaf modulida aynan bitta `FormMonitor` yaratadi va
  barcha menu guruhlar tugagach `finish()`ni bir marta chaqiradi. Forma xatosi
  monitor natijasiga yozilib keyingi forma davom etadi; intentional skip
  menu-item stepi va sabab bilan ko'rinadi, ammo failure hisoblanmaydi.
- Login, filial va shell preconditionlarini har leaf `run_*` funksiyasi o'z
  tartibida bevosita bajaradi. `FormMonitor` precondition callbackini
  ishlatmaydi; leaf xatoni `record_precondition_failure(...)` bilan qayd etadi,
  monitor esa `TEST_BLOCKED`/`NOT_CHECKED`, evidence va yakuniy hisobotni
  yaratadi.
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

## Failure artifacts

- Failed test uchun current URL, page title, redacted full-page screenshot va mavjud
  data-store Allure'ga attach qilinadi.
- Forms runnerda umumiy pytest failure screenshoti bilan birga har bir muammo
  aniqlangan paytdagi forma screenshoti ham alohida attach qilinadi. Yakuniy
  sahifa screenshoti `pytest-final-page-context — failed-form dalili emas` deb
  nomlanadi va oldingi forma xatosining dalili sifatida ishlatilmaydi.
- Pytest longrepr `test-results/logs/` ichiga yoziladi.
- Failure diagnostikasi add/edit formdagi asl save/error transitionini
  keyingi list/view timeoutidan oldin ko'rsatishi kerak.

## Local Allure lifecycle

- Direct pytest run `OPEN_REPORT=1` bo'lsa report generate/open qiladi;
  `SMARTUP_RUNNER=1` bo'lsa runner o'zi lifecycle'ni boshqaradi.
- `scripts/open_allure_report.py` state + lock + health-check bilan mavjud
  healthy serverni qayta ishlatadi.
- Stale state yangi server bilan almashtiriladi.
- Report tab heartbeat yuboradi; tab yopilgach lokal server grace perioddan
  keyin to'xtaydi.
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
