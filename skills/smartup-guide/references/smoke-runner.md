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

Qidiruv so‘zlari: smoke, setup, runner, dependency, data-store, license, balance, tmc, room, user

### 2026-07-20 Balance testlari setup papkasiga ko'chirildi
Tags: smoke, setup, runner, balance, init-balance, structure
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `tests/smoke/test_setup/test_23_init_balance.py`; `tests/smoke/test_setup/test_24_balance.py`
- `Init Balance` moduli joriy tartibda `tests/smoke/test_setup/test_23_init_balance.py`da.
- `Balance` moduli joriy tartibda `tests/smoke/test_setup/test_24_balance.py`da.
- `test_0_setup_runner.py` ikkala `run_*` funksiyani shu setup modullaridan import
  qiladi; UZS va USD productlar alohida 18/19-qadam bo'lgani uchun runnerda
  init balance `test_23_init_balance`, balance `test_24_balance` deb nomlangan.
- Ikkala modulning Allure feature qiymati `Setup`; joriy case soni runnerdagi
  `test_*` wrapperlar va collection guardlariga bog'liq. Eski 25/24 sonlarini
  joriy coverage deb ishlatma.

### Runner Qoidasi
Tags: smoke, setup, dependency, data-store
Status: code-confirmed
Verified: 2026-09-18
Source: `tests/conftest.py::code`; `scripts/run_tests.py`; `tests/smoke/test_setup/test_0_setup_runner.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`;
`tests/smoke/test_forms/test_04_finansy_forms.py`;
`tests/smoke/test_forms/test_05_spravochniki_forms.py`; `tests/smoke/conftest.py`;
`.github/workflows/daily-smoke.yml`; `.github/workflows/run-smartup-suite.yml`;
`telegram_bot/telegram_ci_bot.py`
- CI scheduling va dispatchning canonical owneri
  [telegram-ci.md](../../maintain-test-infra/references/telegram-ci.md#current-architecture).
  Workflowda cron yo'q; `suite=all` dispatchi `setup-smoke`, `group-report`
  va Smoke tugagach `forms` targetlarini bajaradi.
- `setup-forms` existing-company rejimida Setup case'lari va Forms runnerdagi
  `Главное`, `Продажа`, `Склад`, `Финансы`, `Справочники` inventorylarining har
  bir formasini alohida parametrized pytest item sifatida tanlaydi;
  `test_00_company` skip emas, collectiondan deselect qilinadi.
- CI ikkala serverda ham haqiqiy `COMPANY_CODE` va `DISABLE_LICENSE_POLICY=0`
  existing-company rejimida ishlaydi; serverga mos company credentiallari
  GitHub Secrets'dan olinadi.
- GitHub Actions manual dispatch `suite=all|smoke|report|forms` inputi orqali
  tanlangan targetni ishlatadi. Telegram bot menyusi Smoke va Forms bilan
  cheklangan. Bot GitHub'dagi scheduled yoki manual active runni ko'rsa yangi
  triggerni queue'ga qo'ymaydi va busy xabar bilan rad etadi.
- Full run `scripts/run_tests.py` orqali `test_0_setup_runner.py`, keyin Group-0,
  Visit, Report runnerlari va `test_forms/test_0_forms_runner.py`ni shu tartibda bitta
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
  Group-0, Visit va Report runner fayllarini collect qiladi; alohida
  `group-0`, `group-visit` va `group-report` targetlari saqlanadi.
- Setup tanlanmagan code-dependent item joriy server va kompaniyaga mos saqlangan baseline’ni talab qiladi. Yangi Group-0 baseline uchun `setup-group-0`da setup ham tanlanadi.
- `group-report` code-independent: u `code` fixture yoki
  `data_store.json.code`ni talab qilmaydi; yangi template va download nomlari
  run-local UUID suffix bilan ajratiladi.
- `COMPANY_CODE=1` bilan setup alohida pytest sessiyasida tugagach, group
  runnerni existing rejimda davom ettirish uchun `.env`da
  haqiqiy yaratilgan company kodi, uning `COMPANY_PASSWORD` qiymati,
  `DISABLE_LICENSE_POLICY=0` va `NEW_CODE=0` beriladi. `COMPANY_CODE=0`
  qo'llanmaydi; `NEW_CODE=0` esa `data_store.json.code`ni o'qiydi. Group yangi context ochib
  `user-pw{code}@{saved_company_code}` bilan login qiladi.
- `scripts/run_tests.py groups` wrapperi `COMPANY_CODE=1` group-only
  kombinatsiyasini startupda ataylab bloklaydi; yuqoridagi existing
  rejimi direct pytest/PyCharm va wrapperning ikkalasida ishlaydi.
- Har bir setup va group case runner faylida alohida `test_*` pytest item; outer `test_all_runner.py` va `run_*_group_chain` ishlatilmaydi.
- `tests/smoke/test_setup/test_0_setup_runner.py` ichidagi testlar bitta `session_page` bilan ketma-ket ishlaydi; UI state va login holati testlar orasida saqlanadi.
- Lokal `.env` mavjud bo'lsa `COMPANY_URL`, mode va credentiallar uchun yagona
  source shu fayl; `.env` yo'q muhitda tegishli CLI flaglar ishlaydi.
- Existing rejim: haqiqiy `COMPANY_CODE` va `COMPANY_PASSWORD` majburiy,
  `test_00_company` collectiondan deselect qilinadi.
- `COMPANY_CODE=1`: `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD` majburiy,
  `test_00_company` collectionda qoladi; company code test tomonidan
  `autotest{code}` ko'rinishida yaratiladi.
- `USER_PASSWORD` har ikki rejimda environmentdan olinadi va majburiy;
  head/company admin paroli bilan aralashtirilmaydi.
- `00 - Company` faqat `COMPANY_CODE=1` bo'lsa qo'shiladi. Mavjud companyda
  item skip qilinmaydi, deselect qilinadi va Allure'da ko'rinmaydi.

- Company testi run bo'lsa, `data_store.json`ga saqlangan `company_code`
  `test_01_legal_person` va keyingi loginlarda ishlatiladi. Existing rejimida
  haqiqiy `COMPANY_CODE=<company_code>` bevosita ishlatiladi; `0` yaroqsiz.
- Company testidagi security sozlamalari va serverdagi license aktivatsiyasi uchun [Company dossier](forms/company.md)ga qarang.
- `DISABLE_LICENSE_POLICY=1` faqat `COMPANY_CODE=1` bilan ishlaydi; boshqa
  kombinatsiya startup configuration error. Yoqilsa yangi companyda policy off
  qilinadi va `Buy License` / `Attach License` qadamlari o'tkazib yuboriladi.
- `--company-code 1` full runnerda user loginida yaratilgan `company_code` suffix sifatida olinadi. Group-0 loginidan avval setup tegishli userni yaratishi kerak.
- Har group runner module-scoped `group_session_page` bilan boshqa grouplardan alohida context/page oladi; user grouplari `group_user_page` orqali group boshida bir marta login qiladi.
- Barcha fixturelar bitta session-scoped Sync Playwright browser runtimeidan
  foydalanadi. `page` fresh context/page beradi, lekin ikkinchi
  `sync_playwright()` runtime ochmaydi; aks holda Setup session browseri faol
  turgan paytda keyingi standalone/A2 test fixture setupda yiqiladi.
- `code` fixture yangi yoki saqlangan baseline’ni yakuniy collection va `NEW_CODE` bo‘yicha tanlaydi. Backup va muhit mosligi [Code Fixture](testing-debug.md#code-fixture)da.
- `authorization`da `who` majburiy keyword-only parametr; har bir caller `who="admin"|"head"|"user"` rolini ochiq yozadi. Funksiya alohida code yaratmaydi yoki saqlangan code'ni o'qimaydi; user login uchun doim session `code` fixture qiymati `authorization(..., who="user", code=code)` orqali uzatiladi.
- Alohida `test_01_authorization` yo'q. `test_01_legal_person` admin login qiladi
  va `save_data("code", code)` orqali yangi code ni keyingi yakka/debug testlar uchun saqlaydi.

## Known Infrastructure Risks

### Global maxfail independent grouplarni erta to'xtatishi mumkin

Tags: pytest, maxfail, group, collection, independence
Status: code-confirmed
Verified: 2026-08-14
Source: `pytest.ini`; `tests/smoke/conftest.py`

- `pytest.ini` default `--maxfail=0` ishlatadi. User musbat `--maxfail=N`
  bersa, N ta failure'dan keyin pytest keyingi mustaqil runnerlarni ham
  bajarmasdan to'xtashi mumkin.
- Shu sabab run summaryda “keyingi group mustaqil” degan qoida u albatta
  ishladi degani emas; maxfail urilganini alohida ko'rsat.

### Telegram failure diagnostikasi
Tags: smoke, telegram, failure, playwright, locator, summary
Status: code-confirmed
Verified: 2026-11-16
Source: `telegram_bot/progress_details.py::_failed_entry_lines`; `scripts/analyze_test_result.py::_element_state`
- Smoke xatosida Telegram bloki test nomi, bosqich, xato turi, sabab va vaqtni mavjud qiymatlardan yig‘adi. Forms uchun forma nomi, foydalanuvchi bosgan yo‘l va filial ham ko‘rsatiladi.
- Playwright log tahlili ko‘rinmayotgan, o‘chirilgan, beqaror, click’i bloklangan, bir nechta moslik va topilmagan elementlarni farqlaydi. Masalan, `element is not visible` signali `hidden` bo‘ladi.

### Allure'da setup bosqichlarini alohida test sifatida ko'rsatish
Tags: smoke, setup, runner, allure, collection
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `tests/conftest.py::pytest_collection_modifyitems`; `tests/smoke/conftest.py`; `tests/smoke/test_forms/test_0_forms_runner.py`; `scripts/run_tests.py`
- Setup runnerdagi `test_00_company` dan `test_24_balance` gacha bo‘lgan wrapperlar alohida pytest item. Har biri session page bilan tegishli `run_*`ni chaqiradi. Ichki `allure.step` qadamlarini shu item ichida ko‘rish mumkin.
- Mavjud kompaniyada `test_00_company` collectiondan chiqariladi. Oddiy setup xatosida qolgan setup va unga bog‘liq grouplar skip bo‘ladi. `SetupDependencyReadyError` o‘sha itemni failed qiladi, ammo keyingi setupni bloklamaydi.
- Forms runner `setup_independent=True` bilan o‘z login va filial preconditionlarini bajaradi. `all` targeti runner fayllarini bitta pytest jarayoniga uzatadi. Bitta leafni tekshirish uchun uning node IDsi tanlanadi.
- Smoke targetlari va credential parametrlarini `scripts/run_tests.py`dagi `TARGETS` va `parse_args` belgilaydi. Shell wrapperi `./run_tests.sh`.

### Visit group runner
Tags: smoke, visit, mobile, runner, setup
Status: code-confirmed
Verified: 2026-08-28
Source: `scripts/run_tests.py`; `tests/smoke/smoke_config.py`; `tests/smoke/test_groups/test_visit_grup/test_0_visit_runner.py`
- `setup-visit` yangi setup baseline va Visit runnerni bitta pytest sessiyasida
  bajaradi; `.env NEW_CODE=1` uchun canonical Visit verification targeti shu.
- `group-visit` setupsiz faqat Visit runnerini tanlaydi. Group-only targetlar wrapper orqali mavjud company konfiguratsiyasi bilan ishga tushadi.
- Visit runnerdagi minimal va orderli visit caselari `independent=True`; bittasi
  failed bo'lsa ikkinchisi cascade-skip qilinmaydi.

### Smoke Credentiallari Majburiy
Tags: setup, runner, credential
Status: code-confirmed
Verified: 2026-11-16
Source: `scripts/smoke_environment.py::check_requiremants`; `tests/shared/config.py::configure_environment`; `tests/shared/authorization.py::authorization`; `tests/smoke/test_setup/test_00_company.py::run_company`
- Har ikki rejimga `COMPANY_URL`, `COMPANY_CODE` va `USER_PASSWORD` kerak. Mavjud companyda admin paroli `COMPANY_PASSWORD` orqali beriladi. `COMPANY_CODE=1` rejimida `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD` talab qilinadi. Konfiguratsiya yangi kompaniya admini uchun `COMPANY_PASSWORD` qiymatini `CREATED_COMPANY_PASSWORD`dan o‘rnatadi.
- Company server kodi `autotest{code}`. Admin login `admin@<company_code>` shaklida quriladi.

### Group-0 — Base Order
Tags: smoke, group-0, order, setup, runner
Status: live-ui-confirmed
Verified: 2026-07-31
Source: `tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py`;
`tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`; live UI
- `0-01` setup baseline room, robot, representative, client, product, price,
  payment type va balance bilan order add → list → view happy pathini
  tekshiradi.
- Leaf standalone va `test_0_group_runner.py` orqali alohida headless runlar
  muvaffaqiyatli o'tgan.

#### Joriy Group-0 case’lari orasida ma’lumot uzatish
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py::run_create_base_order`; `tests/smoke/test_groups/test_a_grup/test_02_archive_base_order.py`
- Create testi setup entity nomlarini `code`dan oladi. Settlement baseline va yangi order IDni `group_0_offset_baseline`, `group_0_order_id` bilan saqlaydi. Shu groupning Archive case’i ikkisini o‘qiydi.

### Entity Naming
Tags: smoke, entity, naming
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_0_setup_runner.py` import qiladigan leaf’lar. Har bir satr tegishli `run_*` manbasiga ega setup qadamiga havola beradi.

Tegishli setup qadami nomlash, saqlanadigan ID va kutilgan UI qiymatlarini birga beradi.

| Entity | Kod yoki login | Ko‘rinadigan nom |
|---|---|---|
| [Company](#00-company) | `autotest{code}` | `Autotest company {code}` |
| [Legal person](#01-legal-person) | `c_l_p_pw{code}` | Faker kompaniya nomi + `legal_person-pw{code}` |
| [Filial](#02-filial) | | `filial-pw{code}` |
| [Room](#03-room) | `c_rm_pw{code}` | `room-pw{code}` |
| [Robot](#04-robot) | `c_rb_pw{code}` | `robot-pw{code}` |
| [Natural person](#05-natural-person) | `c_n_p_pw{code}` | `natural_person-pw{code}` |
| [User](#06-user) | `user-pw{code}@<active_company_code>` | `natural_person-pw{code}` |
| [UZB price type](#13-price-type-uzb) | `c_p_t_uzb_pw{code}` | `Price Type UZB-pw{code}` |
| [Sector](#17-sector) | `c_s_pw{code}` | `sector-pw{code}` |
| [UZS product](#18-product-uzs) | `c_p_pw{code}` | `product-pw{code}` |
| [Client](#20-natural-person-for-client-1) | `c_n_c_pw{code}` | `natural_client-pw{code}` |

[Init Balance](#23-init-balance) hujjati UZS uchun `{code}`, USD uchun `1{code}` raqamini ishlatadi.

## Testlar Tartibi Va Vazifasi

### 00 Company
Tags: company, setup, head, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_00_company.py::run_company`; `tests/conftest.py::pytest_collection_modifyitems`; `tests/smoke/test_setup/flow_setup/flow_license.py`; `scripts/smoke_environment.py`
- Fayl: `tests/smoke/test_setup/test_00_company.py`.
- Ishga tushirish: faqat `COMPANY_CODE=1` bo'lganda suitega qo'shiladi.
- Guard: mavjud company kodi berilsa deselect qilinadi; Allure'da skipped bo'lib ko'rinmaydi.
- Login: majburiy `HEAD_ADMIN_EMAIL` / `HEAD_ADMIN_PASSWORD`.
- Navigation: `Главное` -> `Компании`.
- Nima qiladi: `Код сервера` sifatida `autotest{code}` kiritadi, visible required maydonlarni minimal to'ldiradi, Products card ichida `trade` va child productlarni yoqadi, saqlaydi va listda code bo'yicha tekshiradi.
- Company viewda bir vaqtdagi seanslar cheklovi o‘chiriladi. Kod server aktivatsiyasini tekshirmaydi.
- License policy: `COMPANY_CODE=1` va `DISABLE_LICENSE_POLICY=1` bo'lsa
  company viewdagi `Безопасность` tabda policy off qilinadi va setupdagi license
  xaridi/ulash qadamlari o'tkazib yuboriladi.
- Nima saqlaydi: `company_code`.

### 01 Legal Person
Tags: legal-person, setup, authorization, owner, director, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py::run_legal_person`; `tests/shared/authorization.py::dashboard`; `tests/shared/authorization.py::current_company_code`
- Fayl: `tests/smoke/test_setup/test_01_legal_person.py`.
- Birinchi qadam: admin sifatida login qilib `dashboard` URLini kutadi.
  Create rejimida suffix `test_00_company` saqlagan `company_code`, existing
  rejimida `COMPANY_CODE`; parol har ikki rejimda `COMPANY_PASSWORD`.
- Navigation: `Справочники` -> `Юридические лица`.
- `c_l_p_pw{code}` va Faker kompaniya nomiga `legal_person-pw{code}` qo‘shilgan to‘liq nom uchun maydonlar
  to'ldiriladi, saqlanadi va listda `Код`, `Название`, `Активный` tekshiriladi.
- Data store: session `code`, `legal_person_code` va `legal_person_name`.

### 02 Filial
Tags: filial, organization, legal-person
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_02_filial.py::run_filial`
- Fayl: `tests/smoke/test_setup/test_02_filial.py`.
- Navigation: `Главное` -> `Организации`.
- `filial-pw{code}` tashkilot yaratiladi, valyuta `Узбекский сум` va
  `c_l_p_pw{code}` yuridik shaxs bilan ulanadi.
- Ro'yxatda filial va legal person code tekshirilib, reload + loader kutiladi.
- Data store: view URLdagi `filial_id`, shuningdek `filial_name`, `filial_currency`, `filial_legal_person_code` va `filial_legal_person_name` saqlanadi.

### 03 Room
Tags: room, filial, work-zone
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_03_room.py::run_room`
- Fayl: `tests/smoke/test_setup/test_03_room.py`.
- Precondition: `base.switch_filial(name=f"filial-pw{code}")`.
- Navigation: `Справочники` -> `Рабочие зоны`.
- Nima yaratadi: `c_rm_pw{code}` / `room-pw{code}` ish zonasi.
- Tekshiruv: saqlagandan keyin `Рабочие зоны` ro'yxatida code va nom ko'rinadi.
- Data store: view URLdagi `room_id` saqlanadi.

### 04 Robot
Tags: robot, staff, room
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_04_robot.py::run_robot`
- Fayl: `tests/smoke/test_setup/test_04_robot.py`.
- Navigation: `Справочники` -> `Штат`.
- Nima yaratadi: `c_rb_pw{code}` / `robot-pw{code}` xodim.
- Bog'lanish: `Админ` tanlanadi va `room-pw{code}` ish zonasi ulanadi.
- Data store: view URLdagi `robot_id` saqlanadi.

### 05 Natural Person
Tags: natural-person, employee
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_05_natural_person.py::run_natural_person`; `tests/smoke/test_setup/flow_setup/flow_natural_person.py::create_natural_person`
- Fayl: `tests/smoke/test_setup/test_05_natural_person.py`.
- Standalone wrapper `filial-pw{code}` filialiga o‘tadi. Runnerda bu filialni Room qadami avval tanlaydi.
- Navigation: `Справочники` -> `Физические лица`.
- Nima yaratadi: xodim uchun `c_n_p_pw{code}` code va `natural_person-pw{code}` ko'rinadigan nomli jismoniy shaxs.
- Flow ism va kodni kiritib, aktiv holatni tekshiradi. List va viewda nom/status tekshiriladi.
- Data store: view URLdagi `person_id` `user_person_id` kaliti bilan saqlanadi;
  bu keyingi testda userga bog'lanadigan person IDsi.
- Arxitektura: reusable create/view oqimlari
  `tests/smoke/test_setup/flow_setup/flow_natural_person.py`da turadi.

### 06 User
Tags: user, robot, natural-person
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_06_user.py::run_user`
- Fayl: `tests/smoke/test_setup/test_06_user.py`.
- Navigation: `Главное` -> `Пользователи`.
- Nima yaratadi: `user-pw{code}@<active_company_code>` loginli user.
- Bog'lanish: `robot-pw{code}` va `natural_person-pw{code}` ulanadi; parol `USER_PASSWORD`dan olinadi.
- Tekshiruv: user ro'yxatida natural person va login ko'rinadi.
- Data store: user view URLdagi `user_id` saqlanadi; bu `user_person_id`dan
  alohida identifikator.

### 07 User Attach Form
Tags: user, permissions, forms
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_07_user_attach_form.py::run_user_attach_form`
- Fayl: `tests/smoke/test_setup/test_07_user_attach_form.py`.
- Nima qiladi: user view ichida `Формы` sahifasini ochib `Формы`, `Отчеты`, `Накладные`, `Внешние системы` tablaridagi mavjud elementlarni userga ulaydi.
- User view aniq login va shu natural person birga chiqqan qatordan ochiladi. Ro‘yxat qayta chizilib action yopilsa, o‘sha sahifada bir marta yana tanlaydi.
- `Накладные` uchun page size 500, qolgan uch tab uchun 1000. Har tabda helper `grid(checkbox="all")`, `Прикрепить`, confirm va `grid(state="empty")`ni ketma-ket bajaradi. Boshlang‘ich grid bo‘shligini tekshiradigan branch yo‘q.
- Tekshiruv: har bo'limda `Доступные` ro'yxati `нет данных` bo'lishi kerak.

### 08 Role
Tags: role, permissions
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_08_role.py::run_role`
- Fayl: `tests/smoke/test_setup/test_08_role.py`.
- Navigation: `Пользователи` sahifasidan `Роли`.
- `Админ` roli editida `ROLE_PERMISSIONS`dagi har bir permission labelini yoqadi. Yordamchi widgetlarni `hide_ui` orqali yashiradi. Saqlagach `UI_TIMEOUT_MS` bilan ro‘yxatga o‘tishni kutadi, editni qayta ochib permissionlarni tekshiradi.

### 09 Role Attach Form
Tags: role, forms, permissions
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_09_role_attach_form.py::run_role_attach_form`
- Fayl: `tests/smoke/test_setup/test_09_role_attach_form.py`.
- Nima qiladi: `Админ` rol viewidagi `Формы` bo'limida `Доступ ко всем формам` -> `Разрешить` qiladi.
- Confirm atrofida ruxsat beruvchi POST javobi kutiladi. Javob muvaffaqiyatli tugab loader yo‘qolgach, `Доступные` ro‘yxati bo‘shligi tekshiriladi.

### 10 Buy License
Tags: license, admin, balance
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_10_buy_license.py::run_buy_license`; `tests/smoke/test_setup/flow_setup/flow_license.py::skip_license_purchase_if_needed`
- Fayl: `tests/smoke/test_setup/test_10_buy_license.py`.
- Server sharti: `smartup.online`da license purchase ishlamagani uchun pytest
  skip; `app3.../xtrade`da unconditional skip yo'q.
- `--disable-license-policy` bo'lsa bu qadam real license flowga kirmaydi va Allure/logga skip sababini yozib davom etadi.
- Nima qiladi: login qilingan sessionda `Администрирование` filialiga o'tadi,
  `Главное → Лицензии` orqali license ro‘yxatini ochadi, balans
  musbatligini tekshiradi va `Smartup ERP` uchun kerakli license sotib oladi.
- To‘lovchi va shartnoma leafdagi konfiguratsiya qiymatlari bilan tanlanadi. Boshlanish sanasi dastlab bugun. Majburiy bazaviy license qatori ko‘rinsa oyning birinchi kuni va jadvaldagi 5 dona tekshiriladi. Qator ko‘rinmasa oddiy bazaviy qator uchun 1 dona kiritiladi. Bir chaqiruv bitta xaridni tasdiqlaydi.
- Standalone wrapper admin login qilib, shu flow’ni chaqiradi. Xariddan keyin `ERP users` qatoridagi `Активный` tekshiriladi.
- Xtrade A2’da xariddan oldingi va keyingi `ERP users` qatorlari `created_on` bo‘yicha solishtiriladi. Bitta yangi aktiv qatorda tegishli miqdor tekshirilgach, run kodi va `created_on` qiymati `ui_purchased_license`ga saqlanadi.
- Log: balans musbat bo'lsa `Balans musbat — Success`, sotib olinsa `Litsenziya olindi`.

### 11 Attach License
Tags: license, user
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_11_attach_license.py::run_attach_license`; `tests/smoke/test_setup/flow_setup/flow_license.py::skip_license_flow_if_needed`
- Fayl: `tests/smoke/test_setup/test_11_attach_license.py`.
- Attach uchun Online server guardi yo‘q. Xtrade A2 va boshqa route’larda license hujjatini tanlash turlicha.
- `--disable-license-policy` bo'lsa bu qadam real attach flowga kirmaydi va Allure/logga skip sababini yozib davom etadi.
- Xtrade A2’da `ui_purchased_license`dagi code joriy setup kodi bilan mos bo‘lishi va `created_on`ga aniq bitta qator to‘g‘ri kelishi shart. Test yangi license biriktirmalari bo‘shligini tekshiradi, userni biriktiradi va `Прикрепленные`da shu user va loginni tasdiqlaydi.
- Boshqa routeda `ERP users` hujjati tanlanadi. Unda avvaldan userlar bo‘lsa, ular ajratilgach `natural_person-pw{code}` biriktiriladi.

### 12 Change Password
Tags: user, password
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_12_change_password.py::run_change_password`
- Fayl: `tests/smoke/test_setup/test_12_change_password.py`.
- Nima qiladi: yangi `user-pw{code}@<active_company_code>` login bilan kiradi; majburiy password change alert chiqishini kutadi.
- Amaliyot: current/new/rewrite password maydonlariga `USER_PASSWORD` qiymati kiritilib `Подтвердить` va confirm `да` bosiladi.

### 13 Price Type UZB
Tags: price-type, room, nps
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_13_price_type_uzb.py::run_price_type_uzb`; `tests/smoke/test_setup/flow_setup/flow_nps_survey.py::fill_nps_survey`
- Fayl: `tests/smoke/test_setup/test_13_price_type_uzb.py`.
- Nima qiladi: NPS Survey modal chiqsa 10 ball bilan yuboradi; `Справочники` -> `Цены` sahifasida UZB price type yaratadi.
- Kodi `c_p_t_uzb_pw{code}`. `room-pw{code}` ish zonasi va `Узбекский сум` valyutasi ulanadi, `Цена продажи` tanlangani tekshiriladi.
- Tekshiruv: `Price Type UZB-pw{code}` searchdan keyin ro'yxatda ko'rinadi.
- Data store: `price_type_name_UZB` bilan birga view URLdagi
  `price_type_id_uzb` saqlanadi.

### 14 Price Type USA
Tags: price-type, room, usd
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_14_price_type_usa.py`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_14_price_type_usa.py`.
- Nima qiladi: `Справочники` -> `Цены` sahifasida USA price type yaratadi.
- Bog'lanish: `room-pw{code}` ish zonasi va `Доллар США` valyutasi tanlanadi.
- Tekshiruv: `Price Type USA-pw{code}` searchdan keyin ro'yxatda ko'rinadi.
- Data store: `price_type_name_USA` bilan birga view URLdagi
  `price_type_id_usa` saqlanadi.

### 15 Currency
Tags: currency, usd, rate
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_setup/test_15_currency.py`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_15_currency.py`.
- Nima qiladi: USD view formasida Markaziy bank kursini yangilaydi va bugungi manual kursni saqlaydi.
- Tekshiruv: bugungi sana va saqlangan kurs `Курсы` gridida ko'rinadi.
- Data store: USD view URLdagi `currency_id` saqlanadi.

### 16 Payment Type
Tags: payment-type, room-attachment
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_16_payment_type.py::run_payment_type`
- Fayl: `tests/smoke/test_setup/test_16_payment_type.py`.
- Nima qiladi: `Цены` -> `Типы оплат` ichida `Прикрепление` orqali barcha 4 payment typeni tizimga ulaydi.
- Data store: grid settingdagi `ИД` ustuni orqali `Наличные деньги` IDsi olinib
  `payment_type_id` kaliti bilan saqlanadi.
- Tekshiruv: `Наличные деньги`, `Перечисление`, `Терминал`, `Чековая книжка` ro'yxatda ko'rinadi.

### 17 Sector
Tags: tmc, sector, room
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_17_sector.py::run_sector`
- Fayl: `tests/smoke/test_setup/test_17_sector.py`.
- Nima yaratadi: `Наборы ТМЦ` ichida `c_s_pw{code}` / `sector-pw{code}` TMC to'plami.
- Bog'lanish: `room-pw{code}` tanlanadi.

### 18 Product UZS
Tags: tmc, product, price
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_18_product.py::run_product`; `tests/smoke/test_setup/flow_setup/flow_product.py::create_product_with_price`; `tests/smoke/test_setup/test_0_setup_runner.py::test_18_product_uzs`
- Fayl: `tests/smoke/test_setup/test_18_product.py`.
- Nima yaratadi: `ТМЦ` ichida `c_p_pw{code}` / `product-pw{code}` mahsuloti.
- Bog'lanish: measure `шт`, product type `Товар`, sahifada `sector-pw{code}` ko'rinishi precondition sifatida tekshiriladi.
- Qo'shimcha: `run_product` `Price Type UZB-pw{code}` bo'yicha `7000` narx
  yozadi va view URLdagi IDni `product_id` kaliti bilan saqlaydi.

### 19 Product USD
Tags: tmc, product, price, usd
Status: code-confirmed
Verified: 2026-08-27
Source: `tests/smoke/test_setup/test_19_product_usa.py`;
`tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_19_product_usa.py`.
- Nima yaratadi: `ТМЦ` ichida `c_p_usa_pw{code}` / `product-usa-pw{code}`
  mahsuloti.
- Qo'shimcha: `run_product_usa` `Price Type USA-pw{code}` bo'yicha `1` narx
  yozadi; bu case product ID saqlamaydi.

### 20 Natural Person For Client 1
Tags: natural-person, client
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_20_natural_person_for_client_1.py::run_natural_person_for_client_1`; `tests/smoke/test_setup/flow_setup/flow_natural_person.py::create_natural_person`
- Fayl: `tests/smoke/test_setup/test_20_natural_person_for_client_1.py`.
- Nima yaratadi: `c_n_c_pw{code}` code va `natural_client-pw{code}` ko'rinadigan nomli jismoniy shaxs, `Клиент` belgisi yoqiladi.
- Tekshiruv: avval `Физические лица` list va `Просмотр` viewda nom/status
  tekshiriladi, keyin `Клиенты` ro'yxatida ko'rinadi.
- Data store: client view URLdagi `person_id` qiymati `client_person_id`
  kaliti bilan saqlanadi.

### 21 Room Attachment
Tags: room, payment-type, warehouse, cashbox, client
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_21_room_attachment.py::run_room_attachment`
- Fayl: `tests/smoke/test_setup/test_21_room_attachment.py`.
- Nima qiladi: yangi user sifatida kirib `room-pw{code}` ish zonasi `Прикрепление` sahifasiga kiradi.
- Bog'lanishlar: 4 payment type, 1 warehouse, 1 cashbox va `natural_client-pw{code}` client ish zonasiga ulanadi.
- Tekshiruv: `Прикрепленные` tablarida 4 to‘lov turi, asosiy ombor, asosiy kassa va client tekshiriladi. `Акция` narx turi avvaldan biriktirilmagan bo‘lsa, katalogdan olinib roomga ulanadi.
- Data store: bu case ID saqlamaydi; warehouse ID keyingi alohida case'da olinadi.

### 22 Warehouse
Tags: warehouse, view, id, data-store
Status: code-confirmed
Verified: 2026-08-27
Source: `tests/smoke/test_setup/test_22_warehouse.py`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Fayl: `tests/smoke/test_setup/test_22_warehouse.py`.
- Nima qiladi: `Склад` -> `Склады` ro'yxatidan `Основной склад` view formasini
  ochib nom/statusni tekshiradi.
- Data store: view URLdagi `warehouse_id` musbat integer sifatida tekshirilib
  `warehouse_id` kaliti bilan saqlanadi.
- Bu Room Attachment ichidagi qo'shimcha qadam emas, alohida pytest case.

### 23 Init Balance
Tags: inventory, init-balance, product
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_23_init_balance.py::run_init_balance`
- Fayl: `tests/smoke/test_setup/test_23_init_balance.py`.
- Nima qiladi: standalone wrapper `authorization(page, who="user", code=code)`
  bilan kiradi; yagona `run_init_balance` `Склад` ->
  `Ввод начальных остатков ТМЦ` sahifasida ikkita boshlang'ich qoldiq hujjati yaratadi.
- Har hujjatda test `Склад` maydonini `clear=True` bilan tozalab, `Основной склад`ni qayta tanlaydi.
- Hujjatlar: `{code}` / `c_p_pw{code}` / `100` / `5000` UZS va
  `1{code}` / `c_p_usa_pw{code}` / `100` / `1` USD.
- Tekshiruv: UZS hujjati o'tkazilgandan keyin `Проводки` popupida `100` va `500 000` borligi tekshiriladi.

### 24 Balance
Tags: inventory, balance, product
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_24_balance.py::run_balance`
- Fayl: `tests/smoke/test_setup/test_24_balance.py`.
- Navigation: `Склад` -> `Остатки ТМЦ`.
- Tekshiruv: qoldiq sahifasida `c_p_pw{code}` va `c_p_usa_pw{code}` ko'rinadi.

### Price Type USA va Currency alohida setup case
Tags: smoke, setup, price-type, currency, collection
Status: code-confirmed
Verified: 2026-08-03
Source: user; `tests/smoke/test_setup/test_0_setup_runner.py`
- Qoida: `run_price_type_usa(...)` va `run_currency(...)` UZB price type wrapperi ichida yashirilmaydi; ular o'z Allure title'i va pytest wrapperiga ega mustaqil setup case sifatida collect qilinadi.
