# Smoke Runner Setup Chain

## Mundarija

- [Qidiruv kalitlari](#qidiruv-kalitlari)
- [Runner qoidasi](#runner-qoidasi)
- [Known infrastructure risks](#known-infrastructure-risks)
- [Telegram failure diagnostikasi](#telegram-failure-diagnostikasi)
- [Smoke credentiallari](#smoke-credentiallari-majburiy)
- [Entity naming](#entity-naming)
- [Testlar tartibi va vazifasi](#testlar-tartibi-va-vazifasi)

## Qidiruv Kalitlari

Tags: smoke, setup, runner, dependency, data-store, license, balance, tmc, room, user

### 2026-07-20 Balance testlari setup papkasiga ko'chirildi
Tags: smoke, setup, runner, balance, init-balance, structure
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `tests/smoke/test_setup/test_21_init_balance.py`; `tests/smoke/test_setup/test_22_balance.py`
- `Init Balance` moduli joriy tartibda `tests/smoke/test_setup/test_21_init_balance.py`da.
- `Balance` moduli joriy tartibda `tests/smoke/test_setup/test_22_balance.py`da.
- `test_0_setup_runner.py` ikkala `run_*` funksiyani shu setup modullaridan import qiladi; hozirgi zanjirda ular `test_21_init_balance` va `test_22_balance`.
- Ikkala modulning Allure feature qiymati `Setup`; hozirgi setup runner create rejimida 23, existing rejimida 22 test collect qiladi.

### Runner Qoidasi
Tags: smoke, setup, dependency, data-store
Status: code-confirmed
Verified: 2026-08-14
Source: `scripts/run_tests.py`; `tests/smoke/test_setup/test_0_setup_runner.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`;
`tests/smoke/test_forms/test_04_finansy_forms.py`;
`tests/smoke/test_forms/test_05_spravochniki_forms.py`; `tests/smoke/conftest.py`;
`.github/workflows/daily-smoke.yml`; `.github/workflows/run-smartup-suite.yml`;
`scripts/telegram_ci_bot.py`
- GitHub Actions cron har soatda ikkita alohida job ishlatadi: avval
  `setup-group-0` targetli Online Smoke, keyin Smoke natijasidan qat'i nazar
  `forms` targetli Online Forms. Har job alohida Telegram progress/final xabar,
  Allure report va result artifact yaratadi; Report group CI dispatchga
  kiritilmaydi.
- `setup-forms` existing-company rejimida 22 ta Setup case va Forms runnerdagi
  `Главное`, `Продажа`, `Склад`, `Финансы`, `Справочники` inventorylarining har
  bir formasini alohida parametrized pytest item sifatida tanlaydi;
  `test_00_company` skip emas, collectiondan deselect qilinadi.
- Telegram bot faqat manual trigger qiladi. `/run`dan keyin `Smoke` yoki
  `Forms`, keyin `Online` (`smartup.online`) yoki `Xtrade`
  (`app3.greenwhite.uz/xtrade`) tanlanadi; botning alohida auto-runi yo'q.
- CI ikkala serverda ham `CREATE_COMPANY=0` va `DISABLE_LICENSE_POLICY=0`
  existing-company rejimida ishlaydi; serverga mos company credentiallari
  GitHub Secrets'dan olinadi.
- Manual dispatch `suite=smoke|forms` inputi orqali faqat tanlangan targetni
  ishlatadi. Bot GitHub'dagi scheduled yoki manual active runni ko'rsa yangi
  triggerni queue'ga qo'ymaydi va busy xabar bilan rad etadi.
- Full run `scripts/run_tests.py` orqali `test_0_setup_runner.py`, keyin Group-0,
  Report runnerlari va `test_forms/test_0_forms_runner.py`ni shu tartibda bitta
  pytest sessiyasida collect qiladi.
- `setup-forms` setupdan keyin Forms runnerni, `forms` esa setupni
  ishlatmasdan faqat Forms runnerni collect qiladi. Forms runner Smartup navbar
  tartibidagi beshta inventorydan har bir active forma va intentional skipni
  alohida pytest/Allure item sifatida collect qiladi. Allure ierarxiyasi
  `Forms — navbar → menu_column → forma`; item metadata'sida navbar, filial,
  expected URL va shell ham ko'rsatiladi. Runnerga kirmaydigan,
  alohida ishga tushiriladigan cross-navbar `A2Angular` esa
  `navbar_tab → menu_column → menu_item` ichki Allure ierarxiyasidan
  foydalanadi.
- Har bir keyingi oddiy navbar o'z leaf inventari/`run_*` funksiyasini saqlaydi
  va canonical runnerning `NAVBAR_SUITES` ro'yxatiga qo'shiladi; runner uning
  formalarini markaziy inventorydan parametr qiladi.
- `setup-group-0` target setup va Group-0 runnerni bitta pytest sessiyasida
  yangi code bilan collect qiladi. `groups` target setupni ishlatmasdan faqat
  Group-0 va Report runner fayllarini collect qiladi; alohida `group-0` va
  `group-report` targetlari saqlanadi.
- Group-only code targetlarida `.env NEW_CODE=1` taqiqlanadi: yangi random code
  uchun setup user/entitylar yaratilmagan bo'ladi. Joriy baseline'ni qayta
  ishlatishda `.env NEW_CODE=0`, yangi Group-0 verificationida esa
  `setup-group-0` ishlatiladi.
- `CREATE_COMPANY=1` bilan setup alohida pytest sessiyasida tugagach, group
  runnerni existing rejimda davom ettirish uchun `.env`da
  `CREATE_COMPANY=0`, `DISABLE_LICENSE_POLICY=0`, `COMPANY_CODE=0` va
  `NEW_CODE=0` beriladi. `COMPANY_CODE=0` sentinel qiymati
  `data_store.json.company_code`ni, `NEW_CODE=0` esa alohida
  `data_store.json.code`ni o'qiydi. Group yangi browser ochib
  `user-pw{code}@{saved_company_code}` bilan login qiladi.
- `scripts/run_tests.py groups` wrapperi `CREATE_COMPANY=1` group-only
  kombinatsiyasini startupda ataylab bloklaydi; yuqoridagi existing/sentinel
  rejimi direct pytest/PyCharm va wrapperning ikkalasida ishlaydi.
- Har bir setup va group case runner faylida alohida `test_*` pytest item; outer `test_all_runner.py` va `run_*_group_chain` ishlatilmaydi.
- `tests/smoke/test_setup/test_0_setup_runner.py` ichidagi testlar bitta `session_page` bilan ketma-ket ishlaydi; UI state va login holati testlar orasida saqlanadi.
- Lokal `.env` mavjud bo'lsa `COMPANY_URL`, mode va credentiallar uchun yagona
  source shu fayl; `.env` yo'q muhitda tegishli CLI flaglar ishlaydi.
- `CREATE_COMPANY=0`: `COMPANY_CODE` va `COMPANY_PASSWORD` majburiy,
  `test_00_company` collectiondan deselect qilinadi.
- `CREATE_COMPANY=1`: `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD` majburiy,
  `test_00_company` collectionda qoladi; company code test tomonidan
  `autotest{code}` ko'rinishida yaratiladi.
- Test user paroli kod ichida hardcode; head/company admin paroli bilan aralashtirilmaydi.
- `00 - Company` suitega URLga qarab emas, `CREATE_COMPANY` orqali qo'shiladi.
  Flag o'chiq bo'lsa item skip qilinmaydi, deselect qilinadi va Allure'da ko'rinmaydi.

- Company testi run bo'lsa, `data_store.json`ga saqlangan `company_code`
  `test_01_legal_person` va keyingi loginlarda ishlatiladi. Existing rejimida
  oddiy `COMPANY_CODE=<code>` bevosita ishlatiladi; `COMPANY_CODE=0` bo'lsa
  saqlangan `data_store.json.company_code` olinadi.
- License policy yoqiq qolsa, yangi company license flowdan oldin head viewdagi
  `Активация для лицензии` bajarilishi shart; faqat
  `Политика лицензирования` yoqiq bo'lishi yetarli emas. Aks holda
  `Buy License` `license_list` URLiga o'tadi, ammo
  `Ошибка | Компания не активирована` bilan to'xtaydi.
- `DISABLE_LICENSE_POLICY=1` faqat `CREATE_COMPANY=1` bilan ishlaydi; boshqa
  kombinatsiya startup configuration error. Yoqilsa yangi companyda policy off
  qilinadi va `Buy License` / `Attach License` qadamlari o'tkazib yuboriladi.
- `--create-company` full runnerda user grouplari ham yaratilgan `company_code`ni ishlatadi; setup zanjirida user/role/password/license kabi user login precondition qadamlari o'chirilgan bo'lsa `user-pw{code}@<company_code>` yaratilmaydi va group login `login.html`da qolib ketadi.
- Har bir group boshida user bir marta login qiladi; group ichidagi test/flowlar shu oynada davom etadi va group tugaganda yoki failed/skip bo'lganda fixture oynani yopadi.
- Har group runner module-scoped `group_session_page` bilan boshqa grouplardan alohida context/page oladi; user grouplari `group_user_page` orqali group boshida bir marta login qiladi.
- Barcha fixturelar bitta session-scoped Sync Playwright browser runtimeidan
  foydalanadi. `page` fresh context/page beradi, lekin ikkinchi
  `sync_playwright()` runtime ochmaydi; aks holda Setup session browseri faol
  turgan paytda keyingi standalone/A2 test fixture setupda yiqiladi.
- `code` fixture faqat `NEW_CODE` bilan boshqariladi: `NEW_CODE=1` (yoki `.env` yo'q muhitda `--new-code`) yangi random 6 xonali qiymat beradi; `NEW_CODE=0` mavjud `test-results/data/data_store.json` dagi code ni o'qiydi. Alohida `REUSE_CODE`/`--reuse-code` yo'q.
- `authorization`da `who` majburiy keyword-only parametr; har bir caller `who="admin"|"head"|"user"` rolini ochiq yozadi. Funksiya alohida code yaratmaydi yoki saqlangan code'ni o'qimaydi; user login uchun doim session `code` fixture qiymati `authorization(..., who="user", code=code)` orqali uzatiladi.
- Alohida `test_01_authorization` yo'q. `test_01_legal_person` admin login qiladi
  va `save_data("code", code)` orqali yangi code ni keyingi yakka/debug testlar uchun saqlaydi.
- Smoke runner `data_store.json` ni tozalab qayta yaratmaydi; faqat `code` yozadi. Shu sabab group testlardan qolgan eski `contract_*` yoki `order_id` qiymatlarini smoke setupning hozirgi code qiymati bilan bir xil deb qabul qilmaslik kerak.

## Known Infrastructure Risks

### Global maxfail independent grouplarni erta to'xtatishi mumkin

Tags: pytest, maxfail, group, collection, independence
Status: code-confirmed
Verified: 2026-08-14
Source: `pytest.ini`; `tests/smoke/conftest.py`

- `pytest.ini` global `--maxfail=3` ishlatadi. Uchta failure yig'ilsa pytest
  keyingi, o'zaro mustaqil group/runnerlarni ham collect qilingan bo'lsa-da
  bajarmasdan to'xtashi mumkin.
- Shu sabab run summaryda “keyingi group mustaqil” degan qoida u albatta
  ishladi degani emas; maxfail urilganini alohida ko'rsat.

### Telegram failure diagnostikasi
Tags: smoke, telegram, failure, playwright, locator, summary
- Final failure bloki `Test → Qadam → Muammo → Texnik → Kod → Ta'sir → Yechim` tartibida chiqadi; bir xil ma'nodagi `Runner`, `Test` va `Step` qatorlari takrorlanmaydi.
- Playwright call log holati deterministik ajratiladi: `locator resolved to` bilan birga `element is not visible` chiqsa element topilgan, lekin yashirin; bu holat "element topilmadi" deb yozilmasin.
- `hidden`, `disabled`, `unstable`, pointer-event bilan `blocked` va haqiqiy `not_found` holatlari alohida sabab hamda keyingi amaliy harakatga ega.
- 2026-07-24 CI runida Room setup `BasePage.switch_filial()` ichidagi `.pt-3.px-2` elementini topgan, ammo u yashirin bo'lgani uchun click 10 sekundda timeout bergan; summary aynan shu faktni ko'rsatgan. Root cause dekorativ strelkani target qilish bo'lgan. Helper ko'rinadigan `.dropdown-locations-custom:visible` trigger va uning ochilgan `.dropdown-menu` optioniga o'tkazildi.

### Allure'da setup bosqichlarini alohida test sifatida ko'rsatish
Tags: smoke, setup, runner, allure, collection
- `allure.step` faqat bitta pytest test ichidagi nested step yaratadi; Allure'da alohida test case chiqishi uchun har setup/group bosqichi pytest tomonidan alohida `test_*` item sifatida collect qilinishi shart.
- Amaldagi model: `test_0_setup_runner.py` ichida optional `test_00_company`,
  `test_01_legal_person` ... `test_22_balance` wrapperlari `session_page` bilan
  collect qilinadi. Moduldagi `pytest.mark.user_setup` barcha wrapperlarga tatbiq qilinadi.
- Mavjud `pytest_runtest_makereport`/`pytest_runtest_setup` mexanizmi alohida
  setup itemlar bilan mos: bir setup item fail bo'lsa `_USER_SETUP_FAILED=True`
  va keyingi setup itemlar hamda setupga bog'liq grouplar skip qilinadi. Forms
  runner `smoke_group(..., setup_independent=True)` bo'lgani uchun setup failed
  bo'lsa ham o'z admin login va filial preconditionlari bilan ishlaydi; filial
  topilmasa markaziy monitor `TEST_BLOCKED` xatosini chiqaradi. Allure har bir
  itemni `passed`/`failed`/`skipped` sifatida alohida ko'rsatadi.
- Full run bitta outer `test_01_user_setup_runner -> run_setup_chain(...)` ni yuritmasligi kerak; pytest targetlari setup runner fayli va group runner fayllarini birga collect qilishi kerak. Aks holda setup Allure'da yana bitta test bo'lib qoladi yoki ikki marta bajariladi.

- Setup zanjiri buzilsa keyingi testlar ham precondition yo'qligi sabab yiqilishi mumkin; yakka testdan oldin to'liq runner yoki mos precondition ma'lumotlari kerak.
- Directory/default collection duplicate business flow yurmasligi uchun faqat mos runner fayllarini qoldiradi; leaf testni debug qilish uchun uning fayl yo'li pytestga aniq beriladi.
- Cross-platform asosiy run: `python scripts/run_tests.py --url {server_url} --company-code {code} --company-password {password}` yoki `python scripts/run_tests.py --url {server_url} --create-company --head-email {email} --head-password {password}`; Mac/Linux wrapper: `./run_tests.sh ...`.
- Runner targetlari: `all`, `setup`, `setup-group-0`, `setup-report`,
  `setup-a2-admin`, `setup-forms`, `company`, `groups`, `group-0`,
  `group-report`, `forms`; foydalanuvchi odatda
  bo'laklarga bo'lib run qilmaydi, normal lokal run `all`; CI Smoke targeti
  `setup-group-0`, CI Forms targeti `forms`.

### Smoke Credentiallari Majburiy
Tags: setup, runner, credential
- Qoida: existing rejimda `COMPANY_CODE/COMPANY_PASSWORD`; create rejimida
  `HEAD_ADMIN_EMAIL/HEAD_ADMIN_PASSWORD` majburiy. Yangi company code
  `autotest{code}`, keyingi admin login `admin@autotest{code}`, admin password
  esa test belgilagan `COMPANY_PASSWORD`.

### Group-0 — Base Order
Tags: smoke, group-0, order, setup, runner
Status: live-ui-confirmed
Verified: 2026-07-31
Source: `tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py`;
`tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`; live UI
- `0-01` setup baseline room, robot, representative, client, product, price,
  payment type va balance bilan order add → list → view happy pathini
  tekshiradi.
- Test faqat `code` orqali setup entity nomlarini hosil qiladi; sibling group
  `load_data/save_data` dependency'si yo'q.
- Leaf standalone va `test_0_group_runner.py` orqali alohida headless runlar
  muvaffaqiyatli o'tgan.

### Entity Naming
Tags: smoke, entity, naming
- Company server code: `autotest{code}`; login suffix sifatida `@autotest{code}` ishlatiladi.
- Legal person: `c_l_p_pw{code}` / Faker company name + `legal_person-pw{code}` suffix.
- Employee natural person code: `c_n_p_pw{code}`; ko'rinadigan nom: `natural_person-pw{code}`.
- Client natural person code: `c_n_c_pw{code}`; ko'rinadigan nom: `natural_client-pw{code}`.
- Filial/organization: `filial-pw{code}`; yuridik shaxs `c_l_p_pw{code}` ga ulanadi.
- Room/work zone: `c_rm_pw{code}` / `room-pw{code}`.
- Robot/staff: `c_rb_pw{code}` / `robot-pw{code}`.
- User: `user-pw{code}@<active_company_code>`; active company code company testi yaratgan `company_code`, bo'lmasa `--company-code`; password kod ichidagi test user default qiymati.
- Price type: `c_p_t_pw{code}` / `Price Type UZB-pw{code}`.
- Sector/TMC set: `c_s_pw{code}` / `sector-pw{code}`.
- Product/TMC: `c_p_pw{code}` / `product-pw{code}`; price `7000`.
- Init balance document number: `{code}`; quantity `100`, price `5000`, expected posting sum `500 000`.

## Testlar Tartibi Va Vazifasi

### 00 Company
Tags: company, setup, head, data-store
- Fayl: `tests/smoke/test_setup/test_00_company.py`.
- Ishga tushirish: faqat `CREATE_COMPANY=1` bo'lganda suitega qo'shiladi.
- Guard: `CREATE_COMPANY=0` bo'lsa deselect qilinadi; Allure'da skipped bo'lib ko'rinmaydi.
- Login: majburiy `HEAD_ADMIN_EMAIL` / `HEAD_ADMIN_PASSWORD`.
- Navigation: `Главное` -> `Компании`.
- Nima qiladi: `Код сервера` sifatida `autotest{code}` kiritadi, visible required maydonlarni minimal to'ldiradi, Products card ichida `trade` va child productlarni yoqadi, saqlaydi va listda code bo'yicha tekshiradi.
- License activation: `DISABLE_LICENSE_POLICY=0` bo'lsa yangi company uchun
  license sotib olishdan oldin `Активация для лицензии` majburiy. Bu bajarilmasa
  `test_10_buy_license`da `Ошибка | Компания не активирована` chiqadi.
- License policy: `CREATE_COMPANY=1` va `DISABLE_LICENSE_POLICY=1` bo'lsa
  company viewdagi `Безопасность` tabda policy off qilinadi va setupdagi license
  xaridi/ulash qadamlari o'tkazib yuboriladi.
- Nima saqlaydi: `company_code`.

### 01 Legal Person
Tags: legal-person, setup, authorization, owner, director, data-store
- Fayl: `tests/smoke/test_setup/test_01_legal_person.py`.
- Birinchi qadam: admin sifatida login qilib `Trade` dashboard headingini kutadi.
  Create rejimida suffix `test_00_company` saqlagan `company_code`, existing
  rejimida `COMPANY_CODE`; parol har ikki rejimda `COMPANY_PASSWORD`.
- Navigation: `Справочники` -> `Юридические лица`.
- `c_l_p_pw{code}` va `legal_person-pw{code}` uchun asosiy maydonlar
  to'ldiriladi, saqlanadi va listda `Код`, `Название`, `Активный` tekshiriladi.
- Data store: session `code`, `legal_person_code` va `legal_person_name`.

### 02 Filial
Tags: filial, organization, legal-person
- Fayl: `tests/smoke/test_setup/test_02_filial.py`.
- Navigation: `Главное` -> `Организации`.
- `filial-pw{code}` tashkilot yaratiladi, valyuta `Узбекский сум` va
  `c_l_p_pw{code}` yuridik shaxs bilan ulanadi.
- Ro'yxatda filial va legal person code tekshirilib, reload + loader kutiladi.
- Data store: `filial_name`, `filial_code`, `filial_currency`, `filial_legal_person_code`, va agar mavjud bo'lsa `filial_legal_person_name` saqlanadi.

### 03 Room
Tags: room, filial, work-zone
- Fayl: `tests/smoke/test_setup/test_03_room.py`.
- Precondition: `switch_filial(page, name=f"filial-pw{code}")`.
- Navigation: `Справочники` -> `Рабочие зоны`.
- Nima yaratadi: `c_rm_pw{code}` / `room-pw{code}` ish zonasi.
- Tekshiruv: saqlagandan keyin `Рабочие зоны` ro'yxatida code va nom ko'rinadi.

### 04 Robot
Tags: robot, staff, room
- Fayl: `tests/smoke/test_setup/test_04_robot.py`.
- Navigation: `Справочники` -> `Штат`.
- Nima yaratadi: `c_rb_pw{code}` / `robot-pw{code}` xodim.
- Bog'lanish: `Админ` tanlanadi va `room-pw{code}` ish zonasi ulanadi.

### 05 Natural Person
Tags: natural-person, employee
- Fayl: `tests/smoke/test_setup/test_05_natural_person.py`.
- Precondition: `filial-pw{code}` filialiga o'tadi.
- Navigation: `Справочники` -> `Физические лица`.
- Nima yaratadi: xodim uchun `c_n_p_pw{code}` code va `natural_person-pw{code}` ko'rinadigan nomli jismoniy shaxs.
- Majburiy `d.first_name`, `d.code` va `Активный` minimal path; list va viewda
  nom/status tekshiriladi.
- Arxitektura: reusable create/view oqimlari
  `tests/smoke/flows/flow_natural_person.py`da turadi.

### 06 User
Tags: user, robot, natural-person
- Fayl: `tests/smoke/test_setup/test_06_user.py`.
- Navigation: `Главное` -> `Пользователи`.
- Nima yaratadi: `user-pw{code}@<active_company_code>` loginli user.
- Bog'lanish: `robot-pw{code}` va `natural_person-pw{code}` ulanadi; password kod ichidagi test user default qiymati.
- Tekshiruv: user ro'yxatida natural person va login ko'rinadi.

### 07 User Attach Form
Tags: user, permissions, forms
- Fayl: `tests/smoke/test_setup/test_07_user_attach_form.py`.
- Nima qiladi: user view ichida `Формы` sahifasini ochib `Формы`, `Отчеты`, `Накладные`, `Внешние системы` tablaridagi mavjud elementlarni userga ulaydi.
- Muhim pattern: har bir tabda page size `1000` qilinadi, `BasePage.click_first_visible_checkbox()` orqali real checkbox/select all bosiladi, `#biruniConfirm` orqali tasdiqlanadi.
- Qayta run: bo'limda `нет данных` bo'lsa attach qadam no-op bo'lib o'tadi; bu qadam mavjud companyda permissionlarni qayta qo'llash uchun idempotent bo'lishi kerak.
- Tekshiruv: har bo'limda `Доступные` ro'yxati `нет данных` bo'lishi kerak.

### 08 Role
Tags: role, permissions
- Fayl: `tests/smoke/test_setup/test_08_role.py`.
- Navigation: `Пользователи` sahifasidan `Роли`.
- Nima qiladi: `Админ` rolini edit qilib, `.switch span` ichidagi barcha `нет` switchlarni yoqadi.
- Muhim pattern: onboarding launcher JS orqali yashiriladi; saqlashdan keyin loader 600s gacha kutiladi.

### 09 Role Attach Form
Tags: role, forms, permissions
- Fayl: `tests/smoke/test_setup/test_09_role_attach_form.py`.
- Nima qiladi: `Админ` rol viewidagi `Формы` bo'limida `Доступ ко всем формам` -> `Разрешить` qiladi.
- Tekshiruv: `Доступные` ro'yxati `нет данных` bo'ladi.

### 10 Buy License
Tags: license, admin, balance
- Fayl: `tests/smoke/test_setup/test_10_buy_license.py`.
- Server sharti: `smartup.online`da license purchase ishlamagani uchun pytest
  skip; `app3.../xtrade`da unconditional skip yo'q.
- `--disable-license-policy` bo'lsa bu qadam real license flowga kirmaydi va Allure/logga skip sababini yozib davom etadi.
- Nima qiladi: login qilingan sessionda `Администрирование` filialiga o'tadi,
  legacy `Главное -> Лицензии` yo'li bilan A2 license formani ochadi, balans
  musbatligini tekshiradi va `Smartup ERP` uchun kerakli license sotib oladi.
- Oyning boshida yoki shu oy uchun birinchi xaridda `Smartup ERP: Базовый пользователь (Обязательный)` alohida row chiqadi; bu rowda quantity `5` disabled/auto-filled bo'ladi, avval shu majburiy license olinadi, keyin oddiy `Smartup ERP: Базовый пользователь` rowdan 1 ta license olinadi. Shu oy keyingi runlarda majburiy row chiqmasligi mumkin.
- Standalone `test_buy_license` blank `page` bilan boshlanishi mumkin; faol sessiya headeri ko'rinsa logout qilinadi, aks holda logout skip qilinib admin login qilinadi.
- Kerakli ma'lumotlar: payer `AUTOTEST GWS`, contract `Договор № bn от 01.01.2025`, begin date today.
- Debug note: payer/contract `b-input` bo'sh bo'lsa `.edit` clear icon `ng-hide` bo'ladi; optionlar ko'rinib turgan bo'lsa ham yashirin `.edit`ni bosish `Locator.click TimeoutError` beradi. `clear=True` helperlari `.edit` faqat visible bo'lsa bosishi kerak.
- Log: balans musbat bo'lsa `Balans musbat — Success`, sotib olinsa `Litsenziya olindi`.

### 11 Attach License
Tags: license, user
- Fayl: `tests/smoke/test_setup/test_11_attach_license.py`.
- `smartup.online`da server sabab skip qilinmaydi va flow ishlashda davom
  etadi; `app3.../xtrade`da ham ishlaydi.
- `--disable-license-policy` bo'lsa bu qadam real attach flowga kirmaydi va Allure/logga skip sababini yozib davom etadi.
- Precondition: `ERP users` license hujjati mavjud bo'lishi kerak. Xtrade'da
  uni oldingi Buy item yaratishi mumkin; Smartup.online'da Buy skip bo'lgani
  uchun Attach serverdagi mavjud hujjatdan foydalanadi.
- Nima qiladi: A2 `Лицензии и документы` ichida `ERP users` license ochiladi,
  mavjud attached users bo'lsa ajratiladi, `natural_person-pw{code}` userga
  ulanadi.

### 12 Change Password
Tags: user, password
- Fayl: `tests/smoke/test_setup/test_12_change_password.py`.
- Nima qiladi: yangi `user-pw{code}@<active_company_code>` login bilan kiradi; majburiy password change alert chiqishini kutadi.
- Amaliyot: current/new/rewrite password maydonlariga kod ichidagi test user default paroli kiritilib `Подтвердить` va confirm `да` bosiladi.

### 13 Price Type UZB
Tags: price-type, room, nps
- Fayl: `tests/smoke/test_setup/test_13_price_type_uzb.py`.
- Nima qiladi: NPS Survey modal chiqsa 10 ball bilan yuboradi; `Справочники` -> `Цены` sahifasida UZB price type yaratadi.
- Bog'lanish: `room-pw{code}` ish zonasi ulanadi; `Цена продажи` ko'rinishi tekshiriladi.
- Tekshiruv: `Price Type UZB-pw{code}` searchdan keyin ro'yxatda ko'rinadi.

### 14 Price Type USA
Tags: price-type, room, usd
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_14_price_type_usa.py`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_14_price_type_usa.py`.
- Nima qiladi: `Справочники` -> `Цены` sahifasida USA price type yaratadi.
- Bog'lanish: `room-pw{code}` ish zonasi va `Доллар США` valyutasi tanlanadi.
- Tekshiruv: `Price Type USA-pw{code}` searchdan keyin ro'yxatda ko'rinadi.

### 15 Currency
Tags: currency, usd, rate
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_15_currency.py`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_15_currency.py`.
- Nima qiladi: USD view formasida Markaziy bank kursini yangilaydi va bugungi manual kursni saqlaydi.
- Tekshiruv: bugungi sana va saqlangan kurs `Курсы` gridida ko'rinadi.

### 16 Payment Type
Tags: payment-type, room-attachment
- Fayl: `tests/smoke/test_setup/test_16_payment_type.py`.
- Nima qiladi: `Цены` -> `Типы оплат` ichida `Прикрепление` orqali barcha 4 payment typeni tizimga ulaydi.
- Tekshiruv: `Наличные деньги`, `Перечисление`, `Терминал`, `Чековая книжка` ro'yxatda ko'rinadi.

### 17 Sector
Tags: tmc, sector, room
- Fayl: `tests/smoke/test_setup/test_17_sector.py`.
- Nima yaratadi: `Наборы ТМЦ` ichida `c_s_pw{code}` / `sector-pw{code}` TMC to'plami.
- Bog'lanish: `room-pw{code}` tanlanadi.

### 18 Product
Tags: tmc, product, price
- Fayl: `tests/smoke/test_setup/test_18_product.py`.
- Nima yaratadi: `ТМЦ` ichida `c_p_pw{code}` / `product-pw{code}` va
  `c_p_usa_pw{code}` / `product-usa-pw{code}` mahsulotlari.
- Bog'lanish: measure `шт`, product type `Товар`, sahifada `sector-pw{code}` ko'rinishi precondition sifatida tekshiriladi.
- Qo'shimcha: yagona `run_product` UZS productga `Price Type UZB-pw{code}`
  bo'yicha `7000`, USD productga `Price Type USA-pw{code}` bo'yicha `1` narx
  yozib saqlaydi.

### 19 Natural Person For Client 1
Tags: natural-person, client
- Fayl: `tests/smoke/test_setup/test_19_natural_person_for_client_1.py`.
- Nima yaratadi: `c_n_c_pw{code}` code va `natural_client-pw{code}` ko'rinadigan nomli jismoniy shaxs, `Клиент` belgisi yoqiladi.
- Tekshiruv: avval `Физические лица` list va `Просмотр` viewda nom/status
  tekshiriladi, keyin `Клиенты` ro'yxatida ko'rinadi.

### 20 Room Attachment
Tags: room, payment-type, warehouse, cashbox, client
- Fayl: `tests/smoke/test_setup/test_20_room_attachment.py`.
- Nima qiladi: yangi user sifatida kirib `room-pw{code}` ish zonasi `Прикрепление` sahifasiga kiradi.
- Bog'lanishlar: 4 payment type, 1 warehouse, 1 cashbox va `natural_client-pw{code}` client ish zonasiga ulanadi.
- Tekshiruv: payment/warehouse/cashbox available listlari `нет данных`; client attached listida `natural_client-pw{code}` ko'rinadi.

### 21 Init Balance
Tags: inventory, init-balance, product
- Fayl: `tests/smoke/test_setup/test_21_init_balance.py`.
- Nima qiladi: standalone wrapper `authorization(page, who="user", code=code)`
  bilan kiradi; yagona `run_init_balance` `Склад` ->
  `Ввод начальных остатков ТМЦ` sahifasida ikkita boshlang'ich qoldiq hujjati yaratadi.
- Formda `Склад` display text auto-fill ko'rinsa ham `warehouse_id` backendga set bo'lmasligi mumkin; test `d.warehouse_name` b-inputida `Основной склад`ni real dropdown orqali qayta tanlaydi.
- Hujjatlar: `{code}` / `c_p_pw{code}` / `100` / `5000` UZS va
  `1{code}` / `c_p_usa_pw{code}` / `100` / `1` USD.
- Tekshiruv: hujjat o'tkazilgandan keyin `Проводки` popupida `100` va `500 000` borligi tekshiriladi.

### 22 Balance
Tags: inventory, balance, product
- Fayl: `tests/smoke/test_setup/test_22_balance.py`.
- Navigation: `Склад` -> `Остатки ТМЦ`.
- Tekshiruv: qoldiq sahifasida `c_p_pw{code}` va `c_p_usa_pw{code}` ko'rinadi.

### Price Type USA va Currency alohida setup case
Tags: smoke, setup, price-type, currency, collection
Status: code-confirmed
Verified: 2026-08-03
Source: user; `tests/smoke/test_setup/test_0_setup_runner.py`
- Qoida: `run_price_type_usa(...)` va `run_currency(...)` UZB price type wrapperi ichida yashirilmaydi; ular o'z Allure title'i va pytest wrapperiga ega mustaqil setup case sifatida collect qilinadi.
