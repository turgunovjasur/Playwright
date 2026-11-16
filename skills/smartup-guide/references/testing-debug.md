# Testing And Debug

## Mundarija

- [Playwright runtime](#bitta-pytest-sessiyasida-yagona-sync-playwright-runtime)
- [Code fixture](#code-fixture)
- [Setup va group model](#setup-va-group-model)
- [Company mode](#company-mode-va-birinchi-authorization)
- [Report group](#report-group)
- [Runner va debug helper qoidalari](#runner-va-debug-helper-qoidalari)
- [Screenshot debug workflow](#screenshot-debug-workflow)
- [Test results retention](#test-results-retention)

## Qidiruv Kalitlari

Qidiruv so‘zlari: debug, data-store, setup, screenshot, dependency, smoke

### Browser va page-object uchun UI timeout
Tags: timeout, playwright, base-page, conftest, debug
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/__init__.py`; `tests/shared/browser.py`; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- `browser_context` oddiy amal va navigatsiya uchun bir xil `UI_TIMEOUT_MS`
  qiymatini qo‘llaydi. Joriy default 60 000 ms. Legacy va A2 page-object
  metodlarida ham `timeout=UI_TIMEOUT_MS` ishlatiladi. Aniq amal uchun
  caller bergan timeoutni tegishli chaqiruvda tekshir.
- `delay=50` maksimal timeout emas; `b_input()` server-search typingida har bir belgi orasidagi real pauza.
- `expect_page(url=...)` URL mos kelgach, `check_unblocked=True` bo‘lsa heading berilmaganda ham tegishli shell loaderini kutadi. Forms monitoringidagi alohida gate uchun [check_loader](form-monitor/check-loader.md) kontraktini o‘qi.
- `requests`/`urllib` HTTP timeoutlari sekundlarda va UI kutishlaridan boshqa mas'uliyatga ega; ular ham tegishli request funksiyasi yonida turadi.

### Integration report navigatsiyasi
Tags: report, navigation, playwright, timeout, open-report
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/flow_report/report_helpers.py::open_report`; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- `open_report(base, route, heading=None, timeout=UI_TIMEOUT_MS)` report yo‘li,
  heading va timeoutni `base.open_route()`ga uzatadi. Yo‘lni page-object quradi. Legacy shellda authenticated
  session tokeni bo'lmasa aniq xato beradi.
- Legacy navigatsiya `commit`ni, A2 `domcontentloaded`ni kutadi. Har ikki
  implementation so‘ng `AutoBasePage.expect_page()`ga expected route,
  heading va timeoutni uzatadi.

### Bitta pytest sessiyasida yagona Sync Playwright runtime
Tags: playwright, fixture, session-browser, asyncio, ci
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/conftest.py::session_browser`; `tests/shared/browser.py::browser_context`
- Session-scoped `session_browser` bitta `sync_playwright()` kontekstida Chromium ochadi. Setup `session_context`ni, group va standalone fixturelar esa shu browser ichidagi alohida context/page’larni ishlatadi.
- Fixture setup paytidagi runtime xatosida `session_browser → context → page` dependency zanjirini tekshir. `browser_context` trace yozishni tugatib contextni yopadi, `session_browser` sessiya yakunida browser’ni yopadi.

### Code Fixture
Tags: code, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/conftest.py::code`; `utils/data_store.py::write_data_file`
- `code` session-scoped. Yakuniy collectionda `code`ga bog‘liq UI setup item tanlangan va `NEW_CODE=1` bo‘lsa, fixture yangi 6 xonali kod oladi. Oldingi data fayli mavjud bo‘lsa, uning baytlarini SHA-256 nomi bilan `baseline-backups/`ga saqlaydi. Yangi baseline `code`, `url`, `company_code`, `suite=ui_setup` bilan boshlanadi.
- Boshqa holatda fixture saqlangan baseline’ni o‘qiydi. `code`, `url`, `company_code` yetishmasa yoki server/kompaniya joriy konfiguratsiyaga mos kelmasa pytest usage error bilan tugaydi.
- [Setup zanjiri](smoke-runner.md#testlar-tartibi-va-vazifasi) shu koddan jismoniy shaxs, room, robot va mahsulot nomlarini yasaydi.

### Admin-only runnerda ortiqcha `code` dependency
Tags: code, data-store, fixture, admin, forms
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/conftest.py::group_session_page`; `tests/conftest.py::group_user_page`; `tests/smoke/test_forms/test_0_forms_runner.py::forms_session`
- `group_session_page` browser context/page lifecycle fixture'i bo'lib,
  `code`ni qabul qilmaydi.
- User login uchun `code` kerak bo'lsa uni `group_user_page`, test data uchun
  kerak bo'lsa tegishli test wrapper o'zi so'raydi.
- Admin-only Forms runner `group_session_page` orqali ishlaydi. Umumiy fixture
  orqali baseline yaratish yoki tekshirish boshlanmaydi.

### Yakka testda user login code'i
Tags: authorization, user, code, data-store, debug
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/shared/authorization.py::authorization`; `tests/shared/authorization.py::current_company_code`; `tests/conftest.py::group_user_page`
- `authorization(page, who="user", code=code)` foydalanuvchi loginini session kodi va joriy company suffixidan yig‘adi. Create rejimida `current_company_code()` suffixni data store’dan o‘qiydi. `code`ni helperga runner fixture yoki standalone wrapper uzatadi. Argumentning defaulti `None`, shu sabab helper chaqirishdan oldin fixture qiymatini uzatish caller zimmasida.

### Group-only baseline bilan login

Group-only run uchun server va company tekshiruvlari [Code Fixture](#code-fixture) bo‘limida. Wrapper `COMPANY_CODE=1` bilan group-only targetni startupda to‘xtatadi. [Runner shartlari](smoke-runner.md#runner-qoidasi)

### Debug Iteratsiyada Precondition Qayta Yaratilmaydi

Mavjud setup entity’ni qachon qayta ishlatish [debug-test](../../debug-test/SKILL.md)da belgilangan. Baseline qaysi server va kompaniyaga tegishli ekanini [Code Fixture](#code-fixture) orqali tekshir.

### Fresh Database Assumption
Tags: fresh-db, setup, group, data
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py::run_create_base_order`
- Group-0 birinchi case clientning settlement qatorini qidiradi. Qator mavjud bo‘lsa joriy summalarni saqlaydi. Bo‘sh gridda boshlang‘ich summalarni nol qilib, keyin o‘z orderini yaratadi.
- Test yaratishda feature precondition va cleanup egasi [group testcase mustaqilligi](../../write-test/references/project-rules.md#group-testcase-mustaqilligi) bilan belgilanadi.

### Masked Input Replace

Maydonni tozalash, qayta yozish va `press_tab` parametri [Masked Date/Amount Inputs](ui-patterns.md#masked-dateamount-inputs) bo‘limida.

### Setup Va Group Model
Tags: setup, group, dependency
Status: code-confirmed
Verified: 2026-11-16
Source: `scripts/run_tests.py::TARGETS`; `tests/smoke/conftest.py`; `tests/conftest.py::group_user_page`; `tests/smoke/test_forms/test_0_forms_runner.py`; `tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`; `tests/smoke/test_groups/test_visit_grup/test_0_visit_runner.py`; `tests/smoke/test_groups/test_report_grup/test_0_group_runner.py`
- `all` targeti bitta pytest jarayoniga Setup → Group-0 → Visit → Report → Forms runnerlarini uzatadi. [Setup zanjiri va entity nomlari](smoke-runner.md#testlar-tartibi-va-vazifasi)
- Oddiy `user_setup` xatosi keyingi setup itemlarni va setupga bog‘liq grouplarni skip qiladi. `SetupDependencyReadyError` bu cascade’ni boshlamaydi. `setup_independent=True` setup failure’dan keyin ham o‘z runneriga ruxsat beradi, `independent=True` esa shu group ichidagi failure cascade’ini o‘chiradi.
- Group-0 bitta module-scoped `group_user_page` bilan ishlaydi. Visit va Report `independent=True`, Forms esa ikkala mustaqillik markeri bilan belgilangan. Group page context’i modul tugaganda yopiladi.

### Company Mode Va Birinchi Authorization
Tags: setup, company, authorization, env, data-store, collection
Status: code-confirmed
Verified: 2026-11-16
Source: `scripts/smoke_environment.py::check_requiremants`; `tests/shared/config.py::configure_environment`; `tests/shared/authorization.py::current_company_code`; `tests/conftest.py::pytest_collection_modifyitems`; `tests/smoke/test_setup/test_01_legal_person.py::run_legal_person`
- `.env`dagi `COMPANY_CODE=1` bo'lsa `test_00_company` collectionda qoladi;
  haqiqiy mavjud company kodi berilsa deselect qilinadi va Allure'da skipped
  test sifatida ko'rinmaydi. `COMPANY_CODE=0` configuration error.
- Create rejimida `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD` majburiy;
  `DISABLE_LICENSE_POLICY` faqat shu rejimda ishlaydi.
- Alohida Authorization pytest item yo'q. `test_01_legal_person` boshida
  `authorization(who="admin")` bajariladi va session `code` data storega yoziladi.
- Create rejimida admin suffix faqat `test_00_company` saqlagan
  `data_store.json.company_code`dan olinadi; existing rejimida oddiy
  `COMPANY_CODE` ishlatiladi. Keyingi alohida run uchun yaratilgan haqiqiy
  company kodi va paroli existing konfiguratsiyaga beriladi. Admin login
  `admin@<current_company_code>`; `USER_PASSWORD` alohida environment qiymati.

### Report Group
Tags: report, group, integration, download
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/test_0_group_runner.py`; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py`; `tests/smoke/test_groups/test_report_grup/flow_report/report_helpers.py::generate_and_verify_download`; `scripts/run_tests.py::TARGETS`
- Report testlar: `tests/smoke/test_groups/test_report_grup/` — CisLink, Integration Three, SalesWork, Optimum, Spot 2d, Integration Two.
- Alohida run: `python scripts/run_tests.py group-report --url ... --company-code ... --company-password ...`
- Report testlar `independent=True` — biri yiqilsa qolganlari davom etadi.
- Report testlar `code` fixture yoki `data_store.json.code`ga bog'liq emas;
  template va saqlanadigan download nomlari run-local UUID suffix oladi.
- Integration Two testi admin loginidan keyin `Администрирование` filialini aniq tanlaydi.
- Integration Two `Тип цены` bo‘sh bo‘lsa birinchi optionni tanlaydi, mavjud qiymat bo‘lsa uni saqlaydi.
- Download testlarida `generate_and_verify_download(base, button_name, expected_prefix, save_name, expected_suffix=...)` helper ishlatiladi; fayl `test-results/downloads/`ga saqlanadi.
- Integration Two bo‘sh bo‘lmagan Monolith `User` va HTTP(S) URLni tekshiradi. `INTEGRATION_TWO_XML_URL` berilsa URL maydoniga shu qiymat yoziladi. Faqat `INTEGRATION_TWO_DEMO=1`da server proxy chaqiruvlariga lokal XML javobi beriladi. Download timeoutida helper URL, Biruni alert va screenshotni Allurega biriktirib xato beradi.

### Runner Va Debug Helper Qoidalari
Tags: runner, debug, modal, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`; `tests/smoke/test_groups/test_report_grup/test_0_group_runner.py`; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py::run_report_integration_two_check`
- Setup va Report runnerlari leaf’lardan `run_*` import qiladi. Group-0 wrapperi login qilingan `group_user_page`ni uzatadi. Integration Two kabi admin testi esa `authorization(who="admin")`ni o‘z flow’ida chaqiradi.
- Test/flow tuzilishi [write-test](../../write-test/SKILL.md)da, confirm modal kontrakti [Biruni Confirm](ui-patterns.md#biruni-confirm)da. Save’dan keyingi xatoda action, asl exception va dalillarni [debug-test](../../debug-test/SKILL.md) orqali tekshir.

### `load_data` strict data-store kontrakti
Tags: fixture, data-store, load-data, dependency
Status: code-confirmed
Verified: 2026-08-28
Source: `utils/data_store.py::load_data`
- `save_data` va `load_data` fixture emas; `utils.data_store`dan import qilinadi.
- Qoida: `load_data("key")` missing yoki bo'sh keyda aniq dependency xatosi
  ko'taradi; faqat optional key `allow_missing=True` bilan `None` qaytaradi.
- Testda ishlatish: setup baseline qiymatlari parametrsiz strict o'qiladi;
  birinchi run'da yaratiladigan `mobile_device_code` kabi optional qiymatlar
  `allow_missing=True` bilan olinadi.

### Forms runner terminal va Allure hisoboti
Tags: forms, report, terminal, allure, filial, menu, url, monitoring, screenshot
Status: code-confirmed
Verified: 2026-08-10
Source: `tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/checks/url.py`;
`tests/smoke/test_forms/monitoring/reporting.py`;
`tests/smoke/test_forms/monitoring/cases.py`;
`tests/smoke/test_forms/inventory/`;
`tests/smoke/test_forms/monitoring/suite_runner.py`

- `tests/smoke/test_forms/monitoring/suite_runner.py::run_legacy_form_monitoring`
  legacy navbar suite'lari uchun login qilingan page, filial/menu execution,
  skip va yakuniy reportni birlashtiradigan façade. `monitoring/monitor.py`
  esa per-form monitoring engine'i. `monitoring/checks/` package'i hard
  checklarni, `monitoring/diagnostics/` package'i alohida observation
  diagnostikalarni, `monitoring/cases.py` identity/case normalizatsiyasini,
  `monitoring/reporting.py` result/schema/human reportni,
  `monitoring/navigation.py` esa navigatsiya primitive'larini saqlaydi. Hozir
  diagnostika registry'sida faqat HTTP `4xx/5xx`
  `failed_requests` bor; FormMonitor package lifecycle'ini chaqiradi, listener
  logikasini o'zida saqlamaydi. Runner o'zicha alohida pass/fail yoki report
  qurmaydi.
- Façade filial executionidan oldin rejalashtirilgan formalarni monitor
  ro'yxatiga kiritadi. Shuning uchun suite filial bosqichida to'xtasa ham nechta
  forma rejalashtirilgani va qaysilari tekshirilmagani yo'qolmaydi. Admin login
  leafdagi oddiy birinchi qadam: u yiqilsa monitor hali boshlanmagan bo'ladi.
- Forma holatlari: `PASSED` (ochildi), `OBSERVED_ONLY` (navigatsiya bajarildi,
  lekin hard checklar test darajasida o'chirilgan), `OPENED_WITH_DEFECT` (URL va kontent
  ochildi, lekin title/kontent nuqsoni bor), `NOT_OPENED` (target forma
  ochilmadi), `TEST_BLOCKED` (test preconditionda to'xtadi), `NOT_CHECKED`
  (blokerdan keyin tekshiruv boshlanmadi).
- Har muammo uchun filial, to'liq yo'l, expected/actual URL, expected/actual
  title, test boshlangan-tugagani, target URLga yetilgani, validatsiya tugagani,
  validatsiyadan o'tgani, forma foydalanishga tayyorligi, xato bosqichi, qisqa
  QA sababi va texnik detail saqlanadi. Aynan xato paytidagi full-page
  screenshot Allure'da saqlanadi, lekin input va secret/password/token
  qiymatlari masklanadi.
- Allure forma step nomida `Filial | Forma | Tab | Menu`, ichki steplarda
  navigatsiya va tekshiruv ko'rinadi. Xato aynan forma yoki precondition stepini
  qizil qiladi; faqat yakuniy umumiy assertionga yashirilmaydi.
- Terminal summary, Allure text va `form-monitor.json` bitta result modelidan
  quriladi. Yakuniy hisob rejalashtirilgan, boshlangan, yakunlangan, ochilgan,
  nuqsonli, ochilmagan, bloklangan va tekshirilmagan sonlarni alohida ko'rsatadi.
- Uzoq run paytida har tugagan forma terminal reporterga filial, navbar tab,
  menu ustuni, tekshirilgan forma, expected/actual URL, status va sababni bergan
  bitta `[FORM MONITOR]` progress qatori chiqaradi. Yakuniy terminal/Allure
  summary ham ayni formatterdan foydalanadi. Telegram uchun
  `SMARTUP_PROGRESS form_result` eventi parent pytest itemning
  `request.node.name` identitysi bilan yuboriladi. Pass formalar uchun katta
  ko'p qatorli blok chiqarilmaydi; batafsil blok muammoli natijaga qoladi.
- Forma `PASSED` bo'lishi uchun custom title/URL assertdan tashqari markaziy
  readiness tekshiruvi ham o'tishi shart. Hard-check tartibi:
  `check_url → check_loader → check_application_error → check_content_ready → check_title`.
  JavaScript exception alohida hard check emas. `TypeError`, `KeyError` va
  boshqa kod kontrakti xatolari forma nuqsoni sifatida yashirilmaydi.
- Diagnostikada avval yiqilgan gate va uning `reason_code` qiymatini top.
  Keyingi `NOT_RUN` steplar uchun `blocked_by` maydonini tekshir.
  Har bir gate selektorlari, timeouti va kutiladigan natijasi o‘z kontraktida:
  [URL](form-monitor/check-url.md), [loader](form-monitor/check-loader.md),
  [application error](form-monitor/check-application-error.md),
  [content ready](form-monitor/check-content-ready.md), [title](form-monitor/check-title.md).
- URL gate yiqilganda avval menu failure screenshoti olinadi. Yoqilgan
  `try_direct_url` diagnostikasi keyin shellga mos expected URLni ochib ko'radi
  va ikkinchi screenshot, direct expected/actual URL hamda
  `direct_url_reached`ni saqlaydi. Direct probe muvaffaqiyati original forma
  natijasini passga aylantirmaydi. To'liq kontrakt:
  [form-monitor/check-url.md](form-monitor/check-url.md).
- `run_form_cases()` monitorsiz ishlamaydi; legacy parallel summary yo'li olib
  tashlangan. Legacy leaf admin authorization, inventory va façade monitoringni
  `run_legal_person` kabi raqamlangan ochiq qadamlarda bajaradi; login xatosi
  oddiy pytest/Allure step xatosi bo'lib, maxsus monitor blockeri yaratilmaydi.
- Navbar suite ownershipi faqat `navbar_tab`ga bog'liq; shu tab ichidagi legacy
  va A2 formalar bitta testga kiradi. Case identitysi `shell + navbar_tab`;
  `menu_column` pytest parametr emas, monitor ichidagi Allure guruhidir. Yangi forma
  `inventory/<navbar>.py` moduliga bitta dict qo'shish bilan qo'shiladi;
  leaf test o'z ro'yxatini `get_legacy_form_buckets(NAVBAR_TAB)` orqali oladi.
  A2Angular navbar runnerga kirmaydigan standalone migratsiya aggregati bo'lib,
  `navbar_tab + menu_column`ni ichki hisobot guruhida saqlaydi; A2 case'ning
  navbar suite va A2Angular'da takrorlanishi intentional.
- `label` optional va yo'q bo'lsa menu item/action/page-link/add-icon yo'lidan
  avtomatik quriladi. Bitta shell + navbar + menu column ichida filial + menu
  item + action + page-links + canonical path takrorlansa duplicate guard
  bloklaydi.
- FormMonitor konfiguratsiyasi test-level: `None` barcha signalni, `[]` hech
  birini, `list[str]` faqat tanlangan check/diagnostikani yoqadi. Per-form
  override yo'q. `checks=[]` muvaffaqiyatli navigatsiyani `OBSERVED_ONLY`
  qiladi va bu holat analyzerda failure emas.
- `form-monitor.json` schema v4: `config`, `identity`, `label`, nested
  `hard_checks`, nested `diagnostics`. Schema-v3 flat `checks` maydoni eski
  consumerlar uchun compatibility sifatida saqlanadi. Human report disabled
  yoki passed signallarni yoymaydi; failed check va counti bor diagnostikani
  user o'qiydigan qisqa qatorlarda beradi.
  URL gate konfiguratsiyasi `config.url_timeout_ms` va
  `config.try_direct_url`da, direct probe natijasi esa result va `hard_checks.url`
  ichida saqlanadi. Title timeouti `config.title_timeout_ms`da, source va
  expected/actual/candidate qiymatlar `hard_checks.title`da saqlanadi.

### Legacy forma nomi document.title emas, visible headingdan olinadi
Tags: forms, legacy, title, heading, monitoring, false-positive
Status: live-ui-confirmed
Verified: 2026-08-03
Source: `SMARTUP_RUNNER=1 ./.venv/bin/pytest -q -s tests/smoke/test_forms/test_0_forms_runner.py`;
`tests/smoke/test_forms/monitoring/monitor.py`
- Qayerda: legacy `#/` formalarining markaziy post-validation tekshiruvida.
- Qoida: A2 forma nomi `document.title`dan, legacy forma nomi esa ko'rinadigan
  headingdan olinadi. Masalan, menu item `Регионы` ochgan
  `anor/mr/region_list` formasining visible headingi `Страны`, browser
  `document.title`i esa boshqa qiymat bo'lishi mumkin.
- Testda ishlatish: legacy title hard check `document.title`ni emas, visible
  semantic heading candidate'larini whitespace-normalized exact taqqoslaydi.
  A2 title hard check esa `document.title`dan foydalanadi.
- Oddiy `print()` pass testda pytest capture ichida qoladi. Forms summary
  `terminalreporter` queue'iga yozilib, `tests/smoke/conftest.py`dagi
  `pytest_terminal_summary` hookida capture tugagach chiqariladi.

### Markaziy forma monitoringining real run verifikatsiyasi (2026-08-03)
Tags: forms, monitoring, allure, live-run, coverage, blocker
Status: live-ui-confirmed
Verified: 2026-08-03
Source: `test-results/logs/tests_smoke_test_forms_test_0_forms_runner.py__test_forms_01_spravochniki_20260803_142539.log`;
`test-results/logs/tests_smoke_test_forms_test_0_forms_runner.py__test_forms_02_a2_admin_20260803_142617.log`
- Forms-01: rejalashtirilgan 89 formaning 89 tasi boshlandi va target URLga
  yetdi; 88 tasi `PASSED`, 1 tasi `OPENED_WITH_DEFECT`. Forma 057
  `Конструктор отчетов по акциям` URL va kontent bo'yicha ochilgan, ammo visible
  title `Заголовок` bo'lgani uchun o'sha paytdagi
  `TITLE_MISMATCH` (joriy kontraktda `TITLE_NOT_REACHED`) qayd etildi. Validatsiya
  bajarilgan, lekin undan o'tmagan deb ko'rsatildi; xato-payt screenshoti aynan
  shu natijaga bog'landi.
- Forms-02: rejalashtirilgan 22 formadan birortasining test qadami boshlanmadi.
  A2 texnik dashboardda joriy project `SFA` bo'lsa-da helper eski `TRADE`
  project/filial triggerini qidirgani sabab birinchi case
  `TEST_BLOCKED/FILIAL_SWITCH_FAILED`, qolgan 21 case `NOT_CHECKED` bo'ldi.
  Bu 22 ta forma xatosi emas; bitta suite precondition bloklanganini anglatadi.
- Testda ishlatish: product defect, ochilmagan forma va suite blokerni bir xil
  `failed` deb ko'rsatma. `counts`, `metrics`, blocker detail va case screenshotini
  alohida chiqar; A2 project fallbackini `SFA`ga moslashtirish alohida fix scope
  bo'lib qoladi.

### Screenshot Debug Workflow

Oldingi forma holatini tekshirish uchun tegishli dossierning `Screenshot Paths` bo‘limini och. Doimiy screenshot, metadata va run output joylari [Screenshot Arxivi](ui-patterns.md#screenshot-arxivi)da. Yangi dalilni arxivlashga [learn](../../learn/SKILL.md) orqali write-back tasdig‘i kerak.

### Test Results Retention
Tags: test-results, data-store, traces, allure, cleanup
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/conftest.py::code`; `utils/logger.py::write_failure_log`; `tests/shared/browser.py::browser_context`; `scripts/report_lifecycle.py`; `scripts/result_retention.py::prune_results`
- UI baseline `test-results/data/data_store.json`da. Yangi setup eski baseline’ni saqlaydi, setupsiz consumer muhit mosligini tekshiradi.
- `test-results/allure-results/` va `test-results/allure-report/` hisobot fayllari. Browser fixture trace ZIP’ni kontekst yopilayotganda yozadi. `test-results/logs/`da test logger fayllari bilan birga xatoning pytest bosqichi va longrepr yozilgan failure loglar ham bo‘ladi.
- `prune_results` `runs/`dagi tegishli manifestli runlarni tozalaydi. Joriy runga qo‘shimcha ko‘pi bilan uchta eski run saqlanadi. Faol run, eng yangi eski run va retry/resume manbalari limitga sig‘masa funksiya o‘chirishdan oldin to‘xtaydi.

## Loyiha Xususiyatlari

### Codex Chrome MCP plagini
- Smartup UI'ni foydalanuvchining mavjud Chrome sessiyasida tekshirish uchun Plugins Directory'dagi `Chrome` (`Control Chrome with...`) plagini o'rnatiladi; `Codex Browser Recorder` faqat flowlarni MP4 yozadi va MCP browser boshqaruvini bermaydi.

### Diagnostika va kod o'zgartirish chegarasi
- Foydalanuvchi test xatosining sababini so'rasa, avval faqat diagnostika beriladi; test yoki production kod faqat foydalanuvchi tuzatishni aniq so'ragandan keyin o'zgartiriladi.

### Xato Case Va Dublikat Kod
Tags: review, duplicate, testcase
Status: user-reported
Verified: pending
Source: user
- Test yozish, migratsiya yoki debug paytida xato testcase, noto'g'ri flow, ortiqcha murakkablik yoki dublikat kod ko'rinsa, foydalanuvchiga alohida xabar ber.
- Takrorlanadigan UI harakatlar flow/helperga chiqariladi.
- Forms/test-infra refactorida fayllar bitta aniq mas'uliyat bo'yicha
  modullashsin, public importlar imkon qadar barqaror qolsin va drift xavfi bor
  dublikat result/report qurilishi yagona helperga yig'ilsin. Shu bilan birga
  oddiy deklarativ test inventorysi dataclass, universal dispatcher yoki katta
  generic framework bilan yashirilmasin: testning biznes qadamlari o'qishda
  to'g'ridan-to'g'ri ko'rinib tursin.

### Ish Yakuni Knowledge Capture

Yangi dalilni saqlashga ruxsat va canonical owner tanlash uchun [project-guide](../../project-guide/SKILL.md#governance) va [learn](../../learn/SKILL.md)ga qarang. Write-back faqat foydalanuvchi tasdiqlagan scope’da bajariladi.
