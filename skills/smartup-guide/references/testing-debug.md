# Testing And Debug

## Qidiruv Kalitlari

Tags: debug, data-store, setup, screenshot, dependency, smoke, regression

### Markaziy Playwright timeout konfiguratsiyasi
Tags: timeout, playwright, base-page, conftest, debug
- Yagona source of truth: `utils/timeouts.py`.
- `PlaywrightTimeouts` faqat sof Playwright API defaultlarini, `BasePageTimeouts` esa loyiha yozgan `BasePage` helperlarining timeout va delay qiymatlarini millisekundda saqlaydi; asosiy ajratish chegarasi sof Playwright va loyiha helperlaridir.
- `TYPE_DELAY` maksimal timeout emas, lekin `BasePage.b_input()`ga tegishli bo'lgani uchun `BasePageTimeouts` ichida turadi va har bir belgi uchun real kutiladi.
- `utils/timeouts.py` ni faqat `tests/smoke/conftest.py` va `utils/base_page.py` import qiladi: `conftest.py` faqat `PlaywrightTimeouts`ni, `base_page.py` faqat `BasePageTimeouts`ni ishlatadi.
- Smoke flow/test/report helper/debug script timeoutlari, hatto qiymati boshqa test bilan bir xil bo'lsa ham, global deb hisoblanmaydi; ular o'z modulida lokal va actionga xos aniq nom bilan turadi. Masalan company create/save uchun `test_company.py` ichidagi `COMPANY_SAVE_TIMEOUT`.
- `PlaywrightTimeouts.NAVIGATION` faqat Playwright'ning to'liq document navigation operatsiyalariga (`page.goto()`, reload va hokazo) tegishli. `BasePageTimeouts.UI_TRANSITION` esa `BasePage` orqali Smartup ichidagi click/save/filial/sahifa holati almashishini kutadi. `BasePage.navigate_to()` nomiga qaramay `page.goto()` emas — u menyuni bosadigan UI helper.
- `BasePage.expect_page(url=...)` URL mosligini kutadi, lekin hozirgi implementatsiyada loader `check_unblocked` tekshiruvi faqat `heading` branchida ishlaydi; URL-only chaqiruv loader kutishi deb qabul qilinmaydi. Menyu flowida loaderni `BasePage.navigate_to()`, standalone URL tekshiruvida esa alohida `BasePage.wait_for_loader()` kutadi.
- `requests`/`urllib` HTTP timeoutlari sekundlarda va UI kutishlaridan boshqa mas'uliyatga ega, shu sabab `utils/timeouts.py` ga kiritilmaydi.
- Birinchi migratsiyada vaqtlar o'zgartirilmadi: refaktor faqat mavjud qiymatlarni markazlashtirdi. Tezlik optimizatsiyasi alohida, test natijalari bilan tasdiqlangan o'zgarish bo'lishi kerak.
- Loyiha qoidasi: timeout va interval klasslaridagi har bir qiymat yonida `Ishlatadi` bilan faqat tegishli `conftest`/`BasePage` funksiya-helperlari, `Ta'siri` bilan oshirish-kamaytirish oqibati hamda fixed interval yoki maksimal limit ekanini tushuntiruvchi inline izoh bo'lishi shart.

### Code Fixture
Tags: code, data-store
- Session `code` setupda yaratiladi.
- Entity nomlari uchun ishlatiladi:
  - `natural_client-pw{code}`
  - `room-pw{code}`
  - `robot-pw{code}`
  - `product-pw{code}`
- Yakka testlarda `code` `test-results/data/data_store.json` dan olinadi.

### Yakka testda user login code'i
Tags: authorization, user, code, data-store, debug
- `authorization` code generatsiya qilmaydi va `data_store.json`dan code o'qimaydi; yangi/eski code tanlovining yagona source'i `NEW_CODE` boshqaradigan `code` fixture.
- `who="user"` bilan login qiladigan runner va yakka testlarda doim `authorization(page, who="user", code=code)` ishlatilsin; `code` berilmasa authorization darhol aniq `AssertionError` beradi.

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
- `tests/smoke/test_setup/test_setup_runner.py` ichidagi mavjud testlar user setup testlari; runner setup testlari bilan bir papkada turadi.
- `tests/smoke/test_all_runner.py` barcha runnerlarni jamlaydi va full smoke entrypoint hisoblanadi.
- Setup testlari ketma-ket va bir-biriga bog'liq.
- Smoke runner bo'yicha har bir test vazifasi va entity naming xaritasi `references/smoke-runner.md` ichida saqlanadi.
- Group testlar user setup natijalariga bog'liq, lekin boshqa grouplarga bog'liq emas.
- Group ichidagi testlar bir-biriga bog'liq bo'lishi mumkin; shu groupda bitta test failed bo'lsa, shu groupning keyingi testlari skip qilinadi.
- Bir group failed bo'lishi boshqa grouplarga ta'sir qilmasin: A failed bo'lsa B/C/D... group testlari run bo'lishi kerak.
- Group testlar boshqa groupning `data_store` keylari, UI state yoki yaratilgan biznes recordlariga suyanmasin; faqat user_setup va o'z group prefixidagi data ishlatilsin.
- Yangi C/D/F/... group runner qo'shilsa, full run uchun `tests/smoke/test_all_runner.py`ga ham ulanadi.
- Full run mexanizmida user_setup failed bo'lsa barcha group testlar skip qilinadi; user_setup passed bo'lsa group failed statuslari group marker/prefix bo'yicha alohida yuritiladi.
- Implementatsiya: `pytest.mark.user_setup` setup chain uchun, `pytest.mark.smoke_group("A")` kabi markerlar group chain uchun ishlatiladi.
- Grouplar orasida browser/page state leak bo'lmasligi uchun full runner group wrapperlari `session_page` emas, `group_page` fixture ishlatadi; har group alohida context/page oladi.
- Alohida group runner faylida group ichidagi testlar `group_user_page` fixture bilan bitta module-scoped page ishlatadi; login group boshida bir marta qilinadi, group tugaganda yoki failed bo'lganda fixture oynani yopadi.
- A-group testlari `tests/smoke/test_groups/test_A_grup/` ichida.
- Group ichidagi testlar bir-biriga bog'liq bo'lmasa `pytest.mark.smoke_group("X", independent=True)` ishlatiladi — bitta test failed bo'lsa ham qolganlar skip qilinmaydi. Report group shu sababli `independent=True` bilan belgilangan.

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
- `run_*` va `run_*_chain` funksiyalari global test mode parametrini qabul qilishi kerak; runner mode qiymatini pastga uzatadi, leaf test esa default smoke yoki explicit regression bilan ishlaydi.
- Group `run_*` funksiyalari standalone debug uchun `login=True` defaultga ega bo'ladi; group chain/runner wrapperlari esa bir martalik login qilganidan keyin ularni `login=False` bilan chaqiradi.
- `BasePage.confirm_biruni(expected_text=None)` `#biruniConfirm` uchun text, opacity `1`, scoped `да`, hidden kutishni bitta joyda bajaradi.
- `logger.fail(..., raise_error=True)` false-pass bo'lmasligi uchun kerakli joyda real `AssertionError` ko'taradi.
- `save_data/load_data` corrupt JSON holatini yashirmaydi; required precondition uchun `require_data` fixture ishlatiladi.
- CI/Telegram failure xabari faqat `TimeoutError` yoki locator call log bilan cheklanmasin; xabardan qaysi test, qaysi biznes step, sahifa/form holati, kutilgan action va tekshiriladigan keyingi joy aniq ko'rinishi kerak.
- Save transition xatolarida list/view timeoutini root cause deb ko'rsatma; avval add/edit formdagi `Сохранить` actionidan keyingi Biruni/UI error, actual heading va expected transition yozilsin.

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
