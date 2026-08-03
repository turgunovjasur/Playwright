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
- `BasePage.expect_page(url=...)` URL mosligini kutadi, lekin hozirgi implementatsiyada loader `check_unblocked` tekshiruvi faqat `heading` branchida ishlaydi; URL-only chaqiruv loader kutishi deb qabul qilinmaydi. Menyu flowida loaderni `BasePage.navigate_to()`, standalone URL tekshiruvida esa alohida `BasePage.wait_for_loader()` kutadi.
- `requests`/`urllib` HTTP timeoutlari sekundlarda va UI kutishlaridan boshqa mas'uliyatga ega; ular ham tegishli request funksiyasi yonida turadi.

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
- Integration Two faqat "Администрирование" filialida ishlaydi — admin login, switch_filial yo'q.
- Integration Two Тип цены: user_setup `price_type_name_UZB` kaliti `data_store.json`ga saqlaydi; yo'q bo'lsa test `pytest.skip` qiladi.
- Download testlarida `generate_and_verify_download(page, trigger, expected_prefix, save_name)` helper ishlatiladi — fayl `test-results/downloads/` ga saqlanadi.
- Biruní alert (integration_two) generate'dan keyin chiqishi normal — fake URL bilan ishlanganda; `_close_alert_if_open` Escape bilan yopadi.

### Runner Va Debug Helper Qoidalari
Tags: runner, debug, modal, data-store
- Runnerlar hech qachon boshqa moduldagi pytest `test_*` funksiyani import qilib chaqirmaydi; umumiy bajariladigan body `run_*` funksiyalarda turadi, pytest entrypointlar esa thin wrapper bo'ladi.
- Global smoke/regression mode parametri olib tashlangan. `run_*` funksiyasiga
  ishlatilmaydigan `scope`/`mode` parametrini qo'shma; coverage farqi alohida
  testcase yoki runner targeti bilan ifodalansin.
- Group `run_*` funksiyalarida `login=True/login=False` mode parametri ishlatilmaydi. User group runnerlari login qilingan `group_user_page` uzatadi; fresh `page` bilan standalone pytest wrapper `run_*` chaqiruvidan oldin o'zi login qiladi. B-04 va Report kabi admin preconditionli caselar esa kerakli admin loginni `run_*` ichida parametrsiz bajaradi.
- `BasePage.confirm_biruni(expected_text=None)` `#biruniConfirm` uchun text, opacity `1`, scoped `да`, hidden kutishni bitta joyda bajaradi.
- `logger.fail(..., raise_error=True)` false-pass bo'lmasligi uchun kerakli joyda real `AssertionError` ko'taradi.
- `save_data/load_data` corrupt JSON holatini yashirmaydi; required precondition uchun `require_data` fixture ishlatiladi.
- CI/Telegram failure xabari faqat `TimeoutError` yoki locator call log bilan cheklanmasin; xabardan qaysi test, qaysi biznes step, sahifa/form holati, kutilgan action va tekshiriladigan keyingi joy aniq ko'rinishi kerak.
- Save transition xatolarida list/view timeoutini root cause deb ko'rsatma; avval add/edit formdagi `Сохранить` actionidan keyingi Biruni/UI error, actual heading va expected transition yozilsin.

### Forms runner terminal va Allure hisoboti
Tags: forms, report, terminal, allure, filial, menu, url, monitoring, screenshot
- `tests/smoke/test_forms/form_monitor.py` barcha Forms runnerlar uchun yagona
  holat va tahlil manbasi. `flow.py` navigatsiya va umumiy result formatini
  beradi; runner o'zicha alohida pass/fail hisoblamaydi.
- Runner boshlanishidan oldin rejalashtirilgan formalar monitor ro'yxatiga
  kiritiladi. Shuning uchun suite filial/login/shell bosqichida to'xtasa ham
  nechta forma rejalashtirilgani va qaysilari tekshirilmagani yo'qolmaydi.
- Forma holatlari: `PASSED` (ochildi), `OPENED_WITH_DEFECT` (URL va kontent
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
- Uzoq run paytida har tugagan forma terminal reporterga bitta `[FORM MONITOR]`
  progress qatori va Telegram consumer uchun `SMARTUP_PROGRESS form_result`
  eventi chiqaradi. Pass formalar uchun katta ko'p qatorli blok chiqarilmaydi;
  batafsil blok muammoli natija va yakuniy hisobotga qoladi.
- Forma `PASSED` bo'lishi uchun custom title/URL assertdan tashqari markaziy
  readiness tekshiruvi ham o'tishi shart: target URL, kontent, tugagan loader,
  UI error yo'qligi va title mosligi. `TypeError`, `KeyError` va boshqa kod
  kontrakti xatolari forma nuqsoni sifatida yashirilmaydi.
- `run_form_cases()` monitorsiz ishlamaydi; legacy parallel summary yo'li olib
  tashlangan. Avtorizatsiya har Forms suite ichida monitor preconditioni bo'lib,
  login xatosida ham planned coverage yo'qolmaydi.

### Legacy forma nomi document.title emas, visible headingdan olinadi
Tags: forms, legacy, title, heading, monitoring, false-positive
Status: live-ui-confirmed
Verified: 2026-08-03
Source: `SMARTUP_RUNNER=1 ./.venv/bin/pytest -q -s tests/smoke/test_forms/test_0_forms_runner.py`;
`tests/smoke/test_forms/form_monitor.py`
- Qayerda: legacy `#/` formalarining markaziy post-validation tekshiruvida.
- Qoida: A2 forma nomi `document.title`dan, legacy forma nomi esa ko'rinadigan
  headingdan olinadi. Masalan, menu item `Регионы` ochgan
  `anor/mr/region_list` formasining visible headingi `Страны`, browser
  `document.title`i esa boshqa qiymat bo'lishi mumkin.
- Testda ishlatish: legacy forma `BasePage.expect_page(heading=...)`dan
  o'tgach `document.title == expected heading` shartini qo'yma; monitor visible
  heading candidate'larini saqlasin. Aks holda sog'lom forma
  `TITLE_MISMATCH` false-positive bo'ladi.
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
  title `Заголовок` bo'lgani uchun `TITLE_MISMATCH` qayd etildi. Validatsiya
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

### PyCharmdagi Allure report cleanup
- PyCharm/direct pytest hookidagi `subprocess.Popen(["allure", "open", ...])` browser oynasi yopilganda Java serverini to'xtatmaydi; jarayonlar qolib ketmasligi uchun `scripts/open_allure_report.py`dagi heartbeatli serverdan foydalanish kerak.

### Xato Case Va Dublikat Kod
Tags: review, duplicate, testcase
- Test yozish, migratsiya yoki debug paytida xato testcase, noto'g'ri flow, ortiqcha murakkablik yoki dublikat kod ko'rinsa, foydalanuvchiga alohida xabar ber.
- Takrorlanadigan UI harakatlar flow/helperga chiqariladi.

### Ish Yakuni Knowledge Capture
Tags: summary, knowledge-capture, dossier
- Har bir Smartup/test vazifasi yakunida bajarilgan ish xulosasi mos skill reference fayllarga yoziladi.
- Agar ish aniq forma bilan bog'liq bo'lsa, avval `references/forms/<form-slug>.md` yangilanadi.
- Agar ish umumiy biznes qoida bo'lsa, `contracts.md` yoki `orders.md` yangilanadi.
- Agar ish locator/modal/grid/screenshot pattern bilan bog'liq bo'lsa, `ui-patterns.md` yangilanadi.
- Xulosa ichida quyilar tartibli bo'lsin: nima qilindi, qaysi fayllar/flowlar tegdi, qanday biznes/UI qoida o'rganildi, screenshot path, known issue yoki keyingi risk.
