# Orders

## Mundarija

- [Order navigation](#order-navigation)
- [Mavjud order flowlar](#mavjud-order-flowlar)
- [Order settlement scenario coverage](#order-settlement-scenario-coverage)
- [Order flow chegarasi](#order-flow-chegarasi--target-architecture)
- [Minimal setup entitylar](#minimal-order-setup-entitylar)
- [Contract limit](#contract-limit-order-case)
- [Payment type](#contract--payment-type-order-case)
- [Consignment](#consignment-order-case)
- [Order list reports](#order-list-накладные-reports)
- [Custom report template](#custom-invoice-report-template)

## Qidiruv Kalitlari

Qidiruv kalitlari: order, order-add, order-list, order-view, product, payment-type, contract-limit

### Order Navigation
Tags: order, navigation
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/flow_order_list.py::flow_order_list`; `tests/smoke/test_life_cycle/flow_order/flow_order_add.py::flow_order_main_page`; `tests/smoke/test_life_cycle/flow_order/order_regression.py::open_saved_order`
- Qayerda: `Продажа > Заказы`.
- URLlar:
  - list: `*/order_list`
  - add: `*/order+add`
  - view: `*/order_view`
- Testda ishlatish: list heading `Заказы`, add content `Заказ (создание)`, view content `Заказ / Просмотр`.

### Mavjud Order Flowlar
Tags: order, flow
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/flow_order_list.py`; `tests/smoke/test_life_cycle/flow_order/flow_order_add.py`; `tests/smoke/test_life_cycle/flow_order/flow_order_view.py`
- Qayerda: `tests/smoke/test_life_cycle/flow_order/`.
- Flowlar:
  - `flow_order_list(page, add=True/find_row/view/edit/status)`
  - `flow_order_main_page(...)`
  - `flow_order_product_page(...)`
  - `flow_order_final_page(...)`
  - `flow_order_view(page, get_value=...)`
- Hozirgi inventory yuqoridagi funksiyalar mavjudligini bildiradi; har bir
  mavjud flow yangi test uchun avtomatik tavsiya degani emas.

### Order Settlement Scenario Coverage
Tags: order, settlement, coverage, test-plan
Status: user-reported
Verified: 2026-07-31
Source: user
- Qayerda: order yopish, client payment va o'zaro hisob-kitob test rejalari.
- Qoida: bajarilgan, qisman bajarilgan va yozilmagan ssenariylarning joriy
  registri [order-settlement-scenarios.md](order-settlement-scenarios.md)da
  yuritiladi.
- Testda ishlatish: yangi order/settlement testi yozishdan oldin scenario ID
  tanla, live run natijasidan keyin coverage statusi va test pathini yangila.

### Order flow chegarasi — target architecture
Tags: order, flow, group, base-page, refactor
Status: user-reported
Verified: pending
Source: user; historical Group A implementation removed 2026-07-31
- Qayerda: yangi va refactor qilinadigan order group testlari.
- Qoida: `flow_order_list` order testlari uchun tasdiqlangan umumiy gateway,
  chunki create/view/edit/status oqimlari order listdan o'tadi. Main/product/
  final biznes qadamlar testcase ichida `BasePage` bilan ochiq yoziladi.
- Qoida: `flow_order_prepare_with_contract` kabi product, payment, status va
  savegacha butun scenario tayyorlaydigan orchestrator flow target pattern
  emas; u leaf testga qaytariladigan refactor kandidati.
- Qoida: boshqa order flow faqat ko'p mustaqil testda aynan bir xil majburiy
  choreography qayta-qayta paydo bo'lsa qoladi. Flow testcase-specific
  assertion, data yoki `save_data/load_data`ni yashirmaydi.
- Testda ishlatish: page state/input/grid/view/save uchun mavjud `BasePage`
  funksiyalaridan foydalan; raw Playwright faqat BasePage qamramagan maxsus
  interactionda minimal scope bilan qoladi.

### Minimal Order Setup Entitylar
Tags: order, setup
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_18_product.py`; `tests/smoke/test_setup/test_19_product_usa.py`; `tests/smoke/test_setup/test_23_init_balance.py`; `tests/smoke/test_life_cycle/test_order.py::run_order_basic`
- Client: `natural_client-pw{code}`
- Room: `room-pw{code}`
- Robot: `robot-pw{code}`
- Products:
  - `product-pw{code}` — `Price Type UZB-pw{code}`, 7000 UZS
  - `product-usa-pw{code}` — `Price Type USA-pw{code}`, 1 USD
- Stock: Setup 23-qadam har ikkala productga 100 donadan boshlang'ich qoldiq
  o‘tkazishni ko‘zlaydi.
- Lifecycle smoke case tanlaydigan to‘lov turi: `Наличные деньги`
- Shu case tanlaydigan status: `Черновик`

### Order currency va price type mosligi
Tags: order, currency, price-type, mobile, validation
Status: trace-confirmed
Verified: 2026-08-28
Source: `test-results/logs/tests_smoke_test_groups_test_visit_grup_test_02_mobile_visit_with_order.py__test_mobile_visit_with_order_20260828_091633.log`; successful dedicated leaf run
- Qoida: order `currency_id` qiymati item `price_type_id` valyutasi bilan mos
  bo'lishi shart. USD `currency_id` bilan UZS price type yuborilsa server
  `A02-16-011` (`Валюты заказа и тип цены разные`) bilan rad etadi.
- Testda ishlatish: `product-pw{code}` + `price_type_id_uzb` kombinatsiyasida
  `currency_id_uzb` ishlatiladi.

### Contract Limit Order Case
Eski Group A’dagi limit summalari va validatsiya matni [contract reference](contracts.md#contract-sum-limit) orqali topiladi.

### Contract + Payment Type Order Case
To‘lov turining auto-fill va manual almashtirish case’i [contract reference](contracts.md#contract--payment-type)da.

### Order Edit Save As New
Tags: order, edit, status
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/regression/legacy/orders/cases/test_01_create_edit_order.py::run_create_edit_order`

- ORD-01 o‘z draft orderini yaratadi, saqlangan ID orqali editni ochadi,
  miqdor, TTN va izohni almashtiradi. Qayta ochishda shu ID, uch dona va
  300 USD tekshiriladi. `Новый` bilan saqlash boshqa, eski A-group case’i edi:
  [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Consignment Order Case
Konsignatsiya kartasi va uning fieldlari [order-add dossierida](forms/order-add.md). Oldingi B-group 30 kunlik limitni qanday tekshirgani — [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Order list view tugmasi
Tags: order, order-list, view, locator
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/flow_order_list.py::flow_order_list`
- Helper tanlangan row ichida `Просмотр` yoki `Просмотреть` nomli tugmani kutadi.
- Testda ishlatish: amount cellni qo'lda bosib global tugma qidirmang. `flow_order_list(page, find_row=<unique client>, view=True)` ishlating; flow ikkala matn variantini qabul qiladi va tugmani tanlangan row ichida qidiradi.

### Consignment Edit And Split Case
B-group tarixiy case’i ikki sana bo‘yicha ajratilgan summalarni tekshirgan. Fixture, chegara va view assertionlari — [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Product Chiqmasa
Tags: order, product, balance, booking, setup
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/regression/test_orders/business_cases/stock/test_cancel_reserve.py::run_cancel_reserve`; `tests/smoke/test_setup/test_23_init_balance.py::run_init_balance`

- Diagnostikada shu mahsulot va ombor uchun mavjud hamda bronlangan miqdorni
  tekshir. Stock regression case yangi order miqdorini baseline bilan
  solishtiradi va aynan o‘zi yaratgan order bekor qilingach zaxirani qayta o‘qiydi.
- Setup oqimida UZS va USD mahsulotlariga kirim beruvchi testcase — `test_23_init_balance`.
  Mahsulot ko‘rinmayotganining aniq sababini qoldiq va order dalili bilan ajrat.

### Order ID
Tags: order, view, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/order_regression.py::open_saved_order`; `tests/regression/legacy/orders/cases/test_01_create_edit_order.py`
- Qayerda: order view.
- Locator: `ИД заказа` label textidan yaqin view value olinadi; yangi testlarda raw XPath yozilmaydi.
- Data: group testcase IDni o'z create→view→edit oqimi ichida ishlatadi; sibling
  testcase consumeri uchun `data_store.json`ga uzatmaydi.

### Order viewda buyurtma sanasi vaqtni ko'rsatmaydi
Tags: order, add, view, date
Status: trace-confirmed
Verified: 2026-07-31
Source: `test-results/traces/tests_smoke_test_groups_test_0_grup_test_create_base_order.py__test_create_base_order.zip`
- Qayerda: order add final summary va saqlangandan keyingi `order_view`.
- Qoida: add/final formadagi `Дата заказа` `DD.MM.YYYY HH:mm`, order viewdagi
  shu label esa faqat `DD.MM.YYYY` ko'rinishida chiqadi.
- Testda ishlatish: add/finalda to'liq `deal_time`ni, viewda esa uning sana
  qismini tekshir; viewdan vaqtni talab qilma.

### Order List Накладные Reports
Tags: order, invoice, report, locator
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/regression/legacy/orders/cases/test_17_invoice_consistency.py::run_invoice_consistency`

- ORD-17 o‘zi yaratgan orderning saqlangan miqdor va summasini o‘qiydi,
  `Накладная № 4 (2012)` HTML reportini ochadi va mahsulot hamda yakuniy
  summani solishtiradi. Eski B-group’dagi popup/download variantlari —
  [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Custom Invoice Report Template
Tags: order, invoice, report-template, admin
Status: live-ui-confirmed
Verified: 2026-07-21
Source: live UI on `smartup.online` and `app3.greenwhite.uz/xtrade`; historical Group B implementation removed 2026-07-31
- Navigation: `Главное -> Шаблоны накладных`; URL pattern `anor/mr/template_list`.
- Mavjud admin login bilan `Шаблоны накладных` sahifasida `Накладная (заказ)` uchun `Test_invoice_report-{code}` nomli custom invoice report template yaratiladi.
- Precondition: `data/test_invoice_report.xlsx` repo ichida mavjud bo'lishi kerak; shu Excel fayl template sifatida upload qilinadi.
- Role: template `Админ` rolega attach qilinadi; attachdan oldin shu role uchun detach/no-op qadam bajarilishi mumkin.
- Davomiy tekshiruv: role oynasi yopilgandan keyin admin profildan chiqiladi, `user-pw{code}@<company>` bilan login qilinadi; `Продажа > Заказы` / `order_list`da testcase yaratgan draft order row bosilganda yangi `Счёт-фактуры` buttoni chiqadi. Shu button bosilganda `Test_invoice_report-{code}` optioni ko'rinishi tekshiriladi.
- **е/ё (MUHIM locator nuancei, 2026-06-21):** Order-row buttoni `Счёт-фактуры` deb **`ё`** (U+0451) bilan yoziladi, B-03 report nomlari (`Счет-фактура с НДС`) esa oddiy `е` bilan. `re.IGNORECASE` `е`/`ё` ni tenglashtirmaydi — button regex `r"Сч[её]т-?фактуры"` bo'lishi shart. `r"Счет-?фактуры"` (faqat `е`) button ko'rinib turib ham topa olmay 120s timeout beradi.
- **MUHIM (download emas, viewer):** `Счет-фактуры` custom xlsx template optioni bosilganda **fayl download BO'LMAYDI**. Yangi popup ochilib report endpoint `b/anor/rep/mdeal/order_report:run?...&invoice_view_kind=O&...` ga ketadi (`invoice_view_kind=O` = "Open in **O**nlyOffice"). Bu endpoint `Content-Type: text/html` (SPA shell) qaytaradi, `Content-Disposition: attachment` yo'q; so'ng popup ichiga `office.smartup.online/web-apps/apps/spreadsheeteditor/main/index.html` (OnlyOffice 8.0.x Spreadsheet Editor) iframe yuklanib, xlsx report **brauzerda ko'rsatiladi**.
- Testda tekshirish: `page.context.expect_page()` bilan popup ushlanadi, so'ng `report_page.frames` ichidan URL'i `office.smartup.online` + `spreadsheeteditor` bo'lgan iframe kutiladi. `expect_download` ISHLATILMAYDI — u headless CI da 180s timeout bilan `AssertionError: ... download boshlanmadi` beradi (eski xato). Solishtirish: bu report viewer'da ochiladi, `Экспортировать заказ` esa haqiqiy `attachment` download (B-03, `expect_download` mos).
- CI vs Mac: OnlyOffice editor headless CI da ham yuklanadi (api.js, app.js, Editor.bin), shuning uchun frame-darajadagi tekshiruv ikkala muhitda ham o'tadi; canvas piksellariga bog'lanish shart emas (headless render quirklari).
- **SERVER FARQI HAL QILINDI (2026-06-16):** xtrade'ga OnlyOffice document server o'rnatildi, endi **`app3.greenwhite.uz/xtrade`** ham **`smartup.online`** kabi OnlyOffice editor viewer'da ochadi (download emas). Ikkala serverda B-04 bir xil ishlaydi: `_open_custom_report_in_editor_and_assert` to'liq ishlatiladi, vaqtinchalik host-skip (`XTRADE_ONLYOFFICE_SKIP_HOST`, `if XTRADE_ONLYOFFICE_SKIP_HOST in page.url`) olib tashlandi.
