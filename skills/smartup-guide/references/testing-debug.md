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

Tags: debug, data-store, setup, screenshot, dependency, smoke

### Timeoutlar funksiya ichida saqlanadi
Tags: timeout, playwright, base-page, conftest, debug
- Loyiha qoidasi: alohida `utils/timeouts.py`, umumiy timeout klassi yoki markaziy timeout registri bo'lmaydi.
  <!-- kb-allow-missing: utils/timeouts.py -->
- Har bir helper o'z timeoutini funksiya signature'ida (`timeout=...`) yoki aynan shu amal yonidagi Playwright chaqiruvida saqlaydi. Qiymatni tushunish uchun boshqa faylga o'tish talab qilinmasin.
- `tests/smoke/conftest.py` Playwright context uchun `set_default_timeout(10_000)` va `set_default_navigation_timeout(20_000)` qiymatlarini fixture yaratiladigan joyning o'zida beradi.
- `BasePage` va `AngularBasePage` helperlari component, loader, transition, probe va typing delay qiymatlarini o'z funksiyalari ichida saqlaydi.
- Bir xil millisekund qiymati turli funksiyalarda takrorlansa ham markaziy constantga chiqarilmaydi; timeout shu funksiyaning xatti-harakatini o'qiyotganda ko'rinishi muhimroq.
- `delay=50` maksimal timeout emas; `b_input()` server-search typingida har bir belgi orasidagi real pauza.
- `BasePage.expect_page(url=...)` URL mosligini kutadi, lekin hozirgi implementatsiyada loader `check_unblocked` tekshiruvi faqat `heading` branchida ishlaydi; URL-only chaqiruv loader kutishi deb qabul qilinmaydi. Umumiy menu flowida loaderni `BasePage.navigate_to()`, standalone URL tekshiruvida esa alohida `BasePage.wait_for_loader()` kutadi. Forms monitoring oqimi bundan mustasno: unda URLdan keyingi yagona loader authority `check_loader`.
- `requests`/`urllib` HTTP timeoutlari sekundlarda va UI kutishlaridan boshqa mas'uliyatga ega; ular ham tegishli request funksiyasi yonida turadi.

### Integration report direct route `load` timeouti
Tags: report, navigation, playwright, timeout, load, open-report
Status: trace-confirmed
Verified: 2026-08-24
Source: `tests/smoke/test_groups/test_report_grup/report_helpers.py:15`; `test-results/traces/tests_smoke_test_groups_test_report_grup_test_06_integration_two.py__test_report_integration_two.zip`
- `open_report(..., timeout=...)`dagi timeout hozir faqat keyingi `expect_page()`ga uzatiladi; ichki `page.goto()` esa contextdagi `20_000 ms` navigation timeout bilan default `load` eventini kutadi.
- Trace'da `goto` timeout paytida target URL, `Интеграция с системой монолит` headingi va report radio control'lari allaqachon render bo'lgan. Shuning uchun bu failure forma ochilmagani yoki radio locator xatosi emas, readiness signal noto'g'ri tanlangan navigation-helper xatosidir.
- Testda ishlatish: Step 1 shu stack bilan yiqilsa keyingi settings/radio qadamlari bajarilmagan deb yoz; `open_report` timeoutini oshirishning o'zi `goto` timeoutini o'zgartirmaydi.

### Bitta pytest sessiyasida yagona Sync Playwright runtime
Tags: playwright, fixture, session-browser, asyncio, ci
- `sync_playwright()` bir threadda ichma-ich ochilmaydi. Session-scoped runtime faol
  paytda function-scoped fixture yana `sync_playwright()` ochsa Playwright
  `using Playwright Sync API inside the asyncio loop` xatosini beradi; bu testning
  async yozilganini yoki A2 UI xatosini anglatmaydi.
- `session_browser` pytest sessiyasi uchun yagona Sync Playwright runtime/browserni
  yaratadi. `session_context`, `group_session_page` va fresh `page` fixturelari
  shu browserdan alohida context/page yaratadi.
- Xato fixture setupda chiqsa test UI qadamlariga yetmagan bo'ladi; screenshot/trace
  locator diagnostikasi emas, fixture dependency va runtime lifecycle tekshiriladi.

### Code Fixture
Tags: code, data-store
- Session `code` setupda yaratiladi.
- Entity nomlari uchun ishlatiladi:
  - `natural_client-pw{code}`
  - `room-pw{code}`
  - `robot-pw{code}`
  - `product-pw{code}`
- Yakka testlarda `code` `test-results/data/data_store.json` dan olinadi.

### Admin-only runnerda ortiqcha `code` dependency
Tags: code, data-store, fixture, admin, forms
- `group_session_page` browser context/page lifecycle fixture'i bo'lib,
  `code`ni qabul qilmaydi.
- User login uchun `code` kerak bo'lsa uni `group_user_page`, test data uchun
  kerak bo'lsa tegishli test wrapper o'zi so'raydi.
- Admin-only Forms runner `group_session_page` orqali ishlaydi. Umumiy fixture
  `code`ga bog'lansa, `data_store.json` yo'q yakka run UI qadamlarigacha
  yetmasdan `pytest.exit` bilan to'xtaydi.

### Yakka testda user login code'i
Tags: authorization, user, code, data-store, debug
- `authorization` code generatsiya qilmaydi va `data_store.json`dan code o'qimaydi; yangi/eski code tanlovining yagona source'i `NEW_CODE` boshqaradigan `code` fixture.
- `who="user"` bilan login qiladigan runner va yakka testlarda doim `authorization(page, who="user", code=code)` ishlatilsin; `code` berilmasa authorization darhol aniq `AssertionError` beradi.

### NEW_CODE=1 bilan group-only login ishlamaydi
Tags: authorization, user, code, data-store, group, runner
Status: trace-confirmed
Verified: 2026-07-31
Source: `test-results/traces/test_0_group_runner.zip`;
`scripts/run_tests.py`; user correction
- Group-only target setupni ishlatmaydi. `.env`dagi `NEW_CODE=1` precedence
  sabab `code` fixture yangi random qiymat yaratsa, shu code uchun user va
  boshqa setup entitylar mavjud bo'lmaydi.
- Tasdiqlangan simptom: Group-0 fixture setupida login POST `400` va
  noto'g'ri login/parol javobi qaytdi; testcase bodygacha yetilmadi.
- Testda ishlatish: group-only rerun uchun `NEW_CODE=0` va joriy baseline;
  yangi code bilan Group-0 uchun setup va testni bir sessiyada bajaradigan
  `setup-group-0` targeti ishlatiladi. Runner `NEW_CODE=1 + group-only`
  kombinatsiyasini UI ochilishidan oldin bloklaydi.

### Debug Iteratsiyada Precondition Qayta Yaratilmaydi
Tags: debug, data-store, precondition
- Qoida: Test yozish/debug iteratsiyasi paytida precondition entity allaqachon yaratilgan va `data_store.json` ga saqlangan bo'lsa, uni qayta yaratish shart emas.
- Misol: contract code/name mavjud bo'lsa, order testdagi xatoni tekshirish uchun mavjud contractdan foydalan.
- Faqat real chain verification kerak bo'lsa yoki data yo'q bo'lsa precondition test qayta run qilinadi.

### Fresh Database Assumption
Tags: fresh-db, setup, group, data
- Qoida: Yangi testlar har doim yangi server/baza holatida ham ishlashi kerak; lokal debug rerunlari yaratgan mavjud dataga suyanib test yozma.
- Cleanup/cancel qadamlari faqat mavjud data bo'lsa ishlasin; data yo'q bo'lsa no-op bo'lib, test yangi record yaratib davom etsin.
- Testga kerakli entity setup runner yoki shu group ichida yaratilishi kerak; sahifada oldindan record bor deb hisoblama.
- Fresh DB default sozlamalari ham hisobga olinsin: testga kerak bo'lgan feature setting default o'chirilgan bo'lsa, test uni idempotent yoqib keyin asosiy flowga o'tsin.
- Order edit case yozish/debug paytida test yiqilib yarim holat qolsa, keyingi urinishdan oldin shu clientning active orderlarini `Отменен` qilib product bookingni tozala; aks holda edit logikasi eski data bilan buziladi.
- Kelajakda kamaytirib edit qilinadigan order preconditioni minimal quantity bilan yaratilmasin; masalan konsignatsiya edit testi uchun create bosqichida 5 dona yaratilib, editda 4 donaga tushiriladi.

### Masked Input Replace
Tags: debug, input, date, amount, mask
- Smartup date/amount mask inputlarida invalid qiymatdan keyin oddiy `fill()` eski qiymatni almashtirmay ustiga qo'shib yuborishi mumkin.
- Test helper avval inputni focus qilib `ControlOrMeta+A` va `Backspace` bilan tozalasin, keyin yangi value yozib `Tab` bossin.

### Setup Va Group Model
Tags: setup, group, dependency
- `tests/smoke/test_setup/test_0_setup_runner.py` ichidagi mavjud testlar user setup testlari; runner setup testlari bilan bir papkada turadi.
- `scripts/run_tests.py all` setup, Group-0 va Report group runner fayllarini bitta pytest sessiyasida collect qiladigan full smoke entrypoint hisoblanadi.
- Setup testlari ketma-ket va bir-biriga bog'liq.
- Smoke runner bo'yicha har bir test vazifasi va entity naming xaritasi `references/smoke-runner.md` ichida saqlanadi.
- Group testlar user setup natijalariga bog'liq, lekin boshqa grouplarga bog'liq emas.
- Group ichidagi testlar bir-biriga bog'liq bo'lishi mumkin; shu groupda bitta test failed bo'lsa, shu groupning keyingi testlari skip qilinadi.
- Bir group failed bo'lishi boshqa grouplarga ta'sir qilmasin.
- Group testlar boshqa groupning `data_store` keylari, UI state yoki yaratilgan biznes recordlariga suyanmasin; faqat user_setup va o'z group prefixidagi data ishlatilsin.
- Yangi group runner qo'shilsa, full run uchun `scripts/run_tests.py` dagi `GROUP_RUNNER_PATHS` va `tests/smoke/conftest.py` default runner tanloviga ulanadi.
- Full run mexanizmida user_setup failed bo'lsa barcha group testlar skip qilinadi; user_setup passed bo'lsa group failed statuslari group marker/prefix bo'yicha alohida yuritiladi.
- Implementatsiya: `pytest.mark.user_setup` setup chain uchun, `pytest.mark.smoke_group("A")` kabi markerlar group chain uchun ishlatiladi.
- Grouplar orasida browser/page state leak bo'lmasligi uchun har group runner module-scoped `group_session_page` bilan alohida context/page oladi.
- User group ichidagi testlar `group_user_page` fixture bilan bitta module-scoped page ishlatadi; login group boshida bir marta qilinadi, group tugaganda fixture oynani yopadi.
- Group ichidagi testlar bir-biriga bog'liq bo'lmasa `pytest.mark.smoke_group("X", independent=True)` ishlatiladi — bitta test failed bo'lsa ham qolganlar skip qilinmaydi. Report group shu sababli `independent=True` bilan belgilangan.

### Company Mode Va Birinchi Authorization
Tags: setup, company, authorization, env, data-store, collection
- `.env`dagi `CREATE_COMPANY=1` bo'lsa `test_00_company` collectionda qoladi;
  `0` bo'lsa deselect qilinadi va Allure'da skipped test sifatida ko'rinmaydi.
- Create rejimida `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD` majburiy;
  `DISABLE_LICENSE_POLICY` faqat shu rejimda ishlaydi.
- Alohida Authorization pytest item yo'q. `test_01_legal_person` boshida
  `authorization(who="admin")` bajariladi va session `code` data storega yoziladi.
- Create rejimida admin suffix faqat `test_00_company` saqlagan
  `data_store.json.company_code`dan olinadi; existing rejimida oddiy
  `COMPANY_CODE` ishlatiladi, `COMPANY_CODE=0` esa saqlangan
  `data_store.json.company_code`ni qayta ishlatish sentinelidir. Admin
  credentiali har ikki holatda
  `admin@<current_company_code>` + `COMPANY_PASSWORD`.

### Report Group
Tags: report, group, integration, download
- Report testlar: `tests/smoke/test_groups/test_report_grup/` — CisLink, Integration Three, SalesWork, Optimum, Spot 2d, Integration Two.
- Alohida run: `python scripts/run_tests.py group-report --url ... --company-code ... --company-password ...`
- Report testlar `independent=True` — biri yiqilsa qolganlari davom etadi.
- Report testlar `code` fixture yoki `data_store.json.code`ga bog'liq emas;
  template va saqlanadigan download nomlari run-local UUID suffix oladi.
- Integration Two faqat `Администрирование` filialida ishlaydi; test admin loginidan keyin shu filialga aniq o'tadi.
- Integration Two `Тип цены`ni qidiruv qiymatisiz `select_first=True` bilan
  birinchi mavjud optiondan tanlaydi.
- Download testlarida `generate_and_verify_download(base, button_name, expected_prefix, save_name, expected_suffix=...)` helper ishlatiladi; fayl `test-results/downloads/`ga saqlanadi.
- Integration Two fake URL yozmaydi: configured Monolith `User` va valid HTTP(S) URL majburiy precondition. Generate download bermasa helper URL, Biruni alert va screenshotni Allurega biriktirib fail qiladi.

### Runner Va Debug Helper Qoidalari
Tags: runner, debug, modal, data-store
- Runnerlar hech qachon boshqa moduldagi pytest `test_*` funksiyani import qilib chaqirmaydi; umumiy bajariladigan body `run_*` funksiyalarda turadi, pytest entrypointlar esa thin wrapper bo'ladi.
- Global smoke/regression mode parametri olib tashlangan. `run_*` funksiyasiga
  ishlatilmaydigan `scope`/`mode` parametrini qo'shma; coverage farqi alohida
  testcase yoki runner targeti bilan ifodalansin.
- Group `run_*` funksiyalarida `login=True/login=False` mode parametri ishlatilmaydi. User group runnerlari login qilingan `group_user_page` uzatadi; fresh `page` bilan standalone pytest wrapper `run_*` chaqiruvidan oldin o'zi login qiladi. B-04 va Report kabi admin preconditionli caselar esa kerakli admin loginni `run_*` ichida parametrsiz bajaradi.
- `BasePage.confirm_biruni(expected_text=None)` `#biruniConfirm` uchun text, opacity `1`, scoped `да`, hidden kutishni bitta joyda bajaradi.
- `logger.fail(..., raise_error=True)` false-pass bo'lmasligi uchun kerakli joyda real `AssertionError` ko'taradi.
- CI/Telegram failure xabari faqat `TimeoutError` yoki locator call log bilan cheklanmasin; xabardan qaysi test, qaysi biznes step, sahifa/form holati, kutilgan action va tekshiriladigan keyingi joy aniq ko'rinishi kerak.
- Save transition xatolarida list/view timeoutini root cause deb ko'rsatma; avval add/edit formdagi `Сохранить` actionidan keyingi Biruni/UI error, actual heading va expected transition yozilsin.

### `load_data` strict data-store kontrakti
Tags: fixture, data-store, load-data, dependency
Status: code-confirmed
Verified: 2026-08-28
Source: `tests/smoke/conftest.py:248`
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
- Menu navigatsiyasidan keyin `check_url` birinchi hard gate bo'lib, o'zining
  `url_timeout` vaqti ichida exact canonical `expected_path`ni kutadi. URL
  ochilmasa yagona reason `EXPECTED_URL_NOT_REACHED`; `previous_url`,
  `URL_MISMATCH` va `URL_TIMEOUT` klassifikatsiyasi ishlatilmaydi. Qolgan hard
  checklar va diagnostikalar `NOT_RUN` bo'ladi.
- URL gate o'tgach `check_loader` ko'rinadigan `.block-ui-overlay` va
  `.smt-skeleton` yo'qolishini o'zining default `60_000 ms` timeouti ichida
  kutadi. Timeoutda `OPENED_WITH_DEFECT / LOADER_NOT_FINISHED`; undan keyingi
  `application_error`, `content_ready` va `title` `NOT_RUN`,
  `blocked_by=loader` bo'ladi. Forms navigation helperlari bu loader kutishini
  takrorlamaydi. To'liq kontrakt:
  [form-monitor/check-loader.md](form-monitor/check-loader.md).
- URL va loader o'tgach `check_application_error` aniq
  `#biruniAlertExtended:visible`, `#biruniAlert:visible`,
  `.alert-danger:visible` yoki
  `[role="dialog"]:visible [data-testid*="error" i]` signalini default
  `1_200 ms` kuzatadi. Error ko'rinmasa timeout muvaffaqiyat; ko'rinsa
  `OPENED_WITH_DEFECT / APPLICATION_ERROR`, undan keyingi `content_ready` va
  `title` esa `NOT_RUN`, `blocked_by=application_error`. Generic
  `[role="alert"]` hard signal emas. Screenshot Biruni cleanupidan oldin
  olinadi; `capture_form_state()` application errorni kutmaydi. To'liq
  kontrakt: [form-monitor/check-application-error.md](form-monitor/check-application-error.md).
- Application-error gate o'tgach `check_content_ready` explicit `ready`
  selectorni, u bo'lmasa legacy `b-page/.subheader` yoki A2 `main` kontentini
  o'zining default `15_000 ms` timeouti ichida kutadi. Timeoutda
  `NOT_OPENED / CONTENT_NOT_READY`; `title` `NOT_RUN`,
  `blocked_by=content_ready`. `capture_form_state()` kontentni kutmaydi.
  To'liq kontrakt:
  [form-monitor/check-content-ready.md](form-monitor/check-content-ready.md).
- Content-ready gate o'tgach `check_title` legacy formada visible semantic
  headingni, A2 formada `document.title`ni o'zining default `15_000 ms`
  timeouti ichida whitespace-normalized exact kutadi. Partial match yoki
  missing Legacy heading `OPENED_WITH_DEFECT / TITLE_NOT_REACHED`; timeout va
  mismatch alohida reasonlarga ajratilmaydi. `check_title` kutishning yagona
  authoritysi, `capture_form_state()` esa faqat diagnostik snapshot oladi.
  To'liq kontrakt: [form-monitor/check-title.md](form-monitor/check-title.md).
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
Tags: screenshot, debug
- Yangi Smartup formaga kirilganda yoki URL/form state o'zgarganda screenshot saqla.
- Forma bo'yicha doimiy bilim screenshotlari skill ichida saqlanadi: `references/forms/screenshots/<form-slug>/`.
- `test-results/screens/smartup/` ishlatilmasin; debug/form screenshot ham skill arxiviga yoziladi.
- Form dossieridagi screenshot pathlar `test-results`ga emas, skill ichidagi arxiv pathlariga ko'rsatsin; `test-results` run output bo'lgani uchun tozalanishi mumkin.
- Naming: `<form-slug>__<state>__<viewport>__<stable-id>.png`.
- Har screenshot uchun shu form slug arxiv papkasi ichida metadata `.json` saqla.
- Screenshotlar kelajakdagi release visual regression uchun baseline/current taqqoslashga tayyor bo'lishi kerak.
- Muammo bo'lsa avval mavjud screenshotni tekshir; yo'q bo'lsa formani ochib screenshot ol, keyin locator/test flow yoz.

### Test Results Retention
Tags: test-results, data-store, traces, allure, cleanup
- `test-results/data/data_store.json` `NEW_CODE=0` rejimidagi yakka testlar va runnerlar uchun kerakli runtime state; keyingi chain/test shu run datalariga tayanayotgan bo'lsa saqlanadi.
- `test-results/allure-results/` va `test-results/allure-report/` hisobot output; test ishlashi uchun doimiy shart emas, yangi run/reportda qayta yaratiladi.
- `test-results/traces/*.zip` debug output; xato tahlili tugaganidan keyin kerak emas, yangi runlarda qayta yoziladi yoki yangi zip yaratiladi.
- `test-results/logs/*.log` faqat failed test longrepr loglari; 0 byte yoki tahlil qilingan eski loglar kerak emas.
- `test-results/allure-results/` pytest/Allure failure attachment outputi; foydali form screenshotlar doim skill arxivida bo'lishi kerak.

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
Tags: summary, knowledge-capture, dossier
- Har bir Smartup/test vazifasi yakunida bajarilgan ish xulosasi mos skill reference fayllarga yoziladi.
- Agar ish aniq forma bilan bog'liq bo'lsa, avval `references/forms/<form-slug>.md` yangilanadi.
- Agar ish umumiy biznes qoida bo'lsa, `contracts.md` yoki `orders.md` yangilanadi.
- Agar ish locator/modal/grid/screenshot pattern bilan bog'liq bo'lsa, `ui-patterns.md` yangilanadi.
- Xulosa ichida quyilar tartibli bo'lsin: nima qilindi, qaysi fayllar/flowlar tegdi, qanday biznes/UI qoida o'rganildi, screenshot path, known issue yoki keyingi risk.
