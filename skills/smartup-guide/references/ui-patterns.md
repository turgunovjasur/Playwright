# UI Patterns

## Mundarija

- [Locator tanlash](#locator-tanlash)
- [Page-object tanlash](#page-object-tanlash)
- [Heading va sahifa tekshirish](#heading--sahifa-tekshirish--expect_page-helper)
- [Form field discovery](#form-field-discovery)
- [b-input](#b-input)
- [UI select](#ui-select)
- [Masked inputs](#masked-dateamount-inputs)
- [Biruni confirm va error](#biruni-confirm)
- [Legacy va A2 modal helper ownershipi](#legacy-va-a2-modal-helper-ownershipi)
- [Status dialog return semantikasi](#status-dialog-return-semantikasi)
- [Alert kutish va o'lik timeout](#alert-kutish--is_visibletimeout-olik-parametr)
- [Blocking loader va aria-busy](#blocking-loader-va-aria-busy-2026-08-05)
- [A2 sahifada `pageerror` chiqmaydi](#a2-sahifada-pageerror-chiqmaydi-2026-08-05)
- [List va grid setting](#list-va-grid-setting)
- [Screenshot arxivi](#screenshot-arxivi)
- [Umumiy forma helperlari](#umumiy-forma-helperlari-dry)

## Qidiruv Kalitlari

Qidiruv so‘zlari: locator, b-input, grid, modal, biruni, screenshot, list

### Page-object tanlash
Tags: page-object, auto-base-page, legacy, a2, dispatch
Status: code-confirmed
Verified: 2026-09-18
Source: `utils/base_pages/auto_base_page.py`; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- `AutoBasePage` har bir public metod chaqiruvida joriy URL pathida `/a2/`
  bo'lsa `AngularBasePage`, aks holda `BasePage`ni tanlaydi. Explicit
  page-objectlar ham shell turi oldindan ma'lum joylarda ishlatiladi.
- DOM selectorlari tegishli concrete classda qoladi; xatoda ikkinchi classni
  sinash yoki legacy/A2 selectorlarini union qilish yo'q.
- Sahifa ochadigan actiondan keyin `base.expect_page(url=..., heading=...)`
  ishlatiladi. `AutoBasePage.expect_page` avval destination URLni kutadi,
  so'ng target sahifa helperini tanlaydi. `title=` uning parametri emas.
- Explicit CSS, `ng_model` va `root` locatorlari avtomatik tarjima qilinmaydi;
  ular target sahifaning DOMiga mos bo'lishi kerak.

### Locator Tanlash
Tags: locator, angular
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/auto_base_page.py`; `utils/base_pages/base_page.py::BasePage.input`; `tests/smoke/test_setup/test_02_filial.py::run_filial`
- Migratsiyaga mos consumer `AutoBasePage`dan foydalanadi. Label bilan topiladigan maydonda `base.input(label="Код", value=...)` yoki `base.b_input(label=..., value=...)` ishlatiladi. Legacy `input` bitta qidiruv usulini oladi: `label`, `ng_model`, `placeholder` yoki `locator`.
- Avval mavjud semantic helper va form dossierini tekshir. Bevosita DOM talab qiladigan selector target shell’ga bog‘liq. [Page-object tanlash](#page-object-tanlash) va [test yozish qoidalari](../../write-test/SKILL.md)

### MCP uchun locator manbalari
Tags: mcp, playwright, locator, snapshot, workflow
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.switch_filial`; `utils/base_pages/base_page.py::BasePage.navigate_to_form`; `utils/base_pages/angular_base_page.py`; `tests/shared/authorization.py::login`
- Filial switcheri va menu uchun locator manbalari `BasePage.switch_filial`, `BasePage.navigate_to_form` va ularning A2 implementatsiyalarida. Login maydonlari uchun `tests/shared/authorization.py`da accessible label va placeholder variantlari bor.
- MCP tekshiruvida kerakli shell va komponentni shu koddan topish mumkin. Qo‘shimcha UI dalili kerak bo‘lsa, tegishli menu, modal yoki grid holatini tekshir.

### Legacy shell filial switcher
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.switch_filial`

- Helper ko‘rinadigan `.header-logo.custom-dropdown` ichidagi `.dropdown-locations-custom` triggerini bosadi. Option shu containerning ochiq `.dropdown-menu` qismidan exact link nomi bilan tanlanadi. Loader tugagach, trigger ichidagi `.project-filial p` tanlangan filialni ko‘rsatishi tekshiriladi.

### Birinchi operatsion filialni tanlash
Tags: filial, navigation, legacy, a2, report
Status: code-confirmed
Verified: 2026-08-20
Source: user; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`; `utils/helper_utils.py`
- Qoida: `BasePage.switch_filial(first_filial=True)` va
  `AngularBasePage.switch_filial(first_filial=True)` filial ro'yxatidagi
  `Администрирование` bo'lmagan birinchi ko'rinadigan filialni tanlaydi. Bu
  rejimda `name` berilmaydi; aniq filial kerak bo'lsa avvalgidek
  `switch_filial(name=...)` ishlatiladi.

### Heading / Sahifa Tekshirish — `expect_page` helper
Tags: locator, heading, get_by_role, navigation, url
Status: trace-confirmed
Verified: 2026-08-20
Source: `test-results/traces/tests_smoke_test_groups_test_report_grup_test_0_group_runner.zip`; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- **DOM fakti** (2026-06-29 live tekshirilgan): sahifa sarlavhasi yagona `<h6 class="text-dark font-weight-bolder ...">` (Angular `ng-binding`). `<h1>` mavjud, lekin **bo'sh** — sarlavha uchun `h1` ISHLATMA, `get_by_role("heading")` ishlat.
- Report trace'da heading `innerText`i ko'rinadigan nom bilan bir xil bo'lsa ham raw `textContent` boshida va oxirida newline/whitespace saqlashi tasdiqlangan. Playwright'da `filter(has_text=regex)` ham, `get_by_role(name=regex)` ham anchored regexning tashqi whitespace'ini avtomatik olib tashlamaydi. Exact dynamic heading uchun regex `^\s*...\s*$` ko'rinishida yoziladi; shared `expect_page` string contracti o'zgartirilmaydi.
- Oddiy list/create sahifada `role=heading` aniq **1 ta**. Sahifa o'zgarsa shu elementning matni **almashadi** (yangi heading element qo'shilmaydi). `navigate_to` transition o'rtasida heading matni qisqa vaqt **bo'sh `''`** bo'ladi — shuning uchun tekshiruv doim **auto-retry qiluvchi `expect(...)`** bilan bo'lsin, bir martalik `inner_text()` emas.
- **Ko'p heading muammosi:** wizard yoki ko'p bo'limli formalarda bir vaqtda bir nechta ko'rinadigan heading bo'ladi (masalan Акция create: `Акция (создание)`, `Главное`, `Условия`). Bunda `expect(page.get_by_role("heading")).to_contain_text(X)` — kerakli matn ulardan birida bo'lsa ham — **FAIL bo'ladi** (2026-06-29 sintetik isbotlangan: locator 2+ elementga to'g'ri kelsa, scalar `to_contain_text` to'g'ri matnda ham yiqiladi). Ya'ni to'g'ri sahifada turib ham false-negative beradi.
- **Afzal yechim — `base.expect_page(heading=None, url=None, timeout=...)`** (`base.navigate_to(...)` dan keyin chaqiriladi; `navigate_to` o'zi faqat navigatsiya qiladi, tekshirmaydi):
  - `base.expect_page(heading="Цены")` — `heading` str (substring) yoki `re.compile(...)` bo'lishi mumkin (masalan `re.compile(r"Комп|Comp")`). Ichida `get_by_role("heading").filter(has_text=heading).first` + `to_be_visible()` ishlatiladi: ortiqcha heading bo'lsa mosini tanlaydi, `.first` strict-mode'dan saqlaydi va retry qiladi. Exact anchored regex raw DOM whitespace'ini ham qamrashi uchun `re.compile(r"^\s*Spot2D\(\d+\)\s*$")` kabi yoziladi; registrga befarq qidiruv kerak bo'lsa `re.IGNORECASE` ochiq beriladi.
  - `root` faqat to'liq sahifa uchun emas: modal headingini `base.expect_page(heading="Добавить курс", root=page.get_by_role("dialog"))` kabi scoped tekshirish mumkin.
  - `base.expect_page(url="price_type_list")` — `url` bo'lagi (substring) yoki regex. **URL slug eng ishonchli signal**: locale'ga bog'liq emas, har sahifada unikal.
  - `base.expect_page(heading="...", url="...")` — ikkalasi birga, eng kuchli tekshiruv.
- Barqaror URL slug'lar: `price_type_list`, `payment_type_list`, `filial_list`, `inventory_list` (ТМЦ), `action_list` (Акции), `order_list`, `anor/mkf/contract_list`, `template_list`.
- Eski `expect(page.get_by_role("heading", name="X")).to_be_visible()` ham ishlaydi (substring; `exact=True` ISHLATMA — list heading'larda ko'pincha oldida icon/probel bo'ladi), lekin yangi/refactor kodda `expect_page` afzal: bitta markaziy nuqta, xato xabari hozirgi heading + url ni ko'rsatadi.

### View qiymatini label bilan olish
Tags: locator, order-view, label, xpath
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/flow_order_list.py::flow_order_list`; `tests/smoke/test_life_cycle/flow_order/flow_order_view.py`; `utils/base_pages/base_page.py::BasePage.form_view`; `utils/helper_utils.py::label_pattern`
- `flow_order_list(..., view=True)` tanlangan qator ichidan `Просмотр` yoki `Просмотреть` tugmasini qidiradi.
- `flow_order_view` qiymatlarni `form_view(label=..., return_value=True)` orqali o‘qiydi. Legacy helper aniq label matniga mos `label` yonidagi `.form-view`, tarjima `t` yonidagi qiymat yoki ketma-ket `span` juftligini qidiradi.
- Formatlangan summada `remove_spaces=True` satr qiymatini solishtirish va qaytarishda whitespace’ni olib tashlaydi. Default `False`. Masalan, `7 000` va `7000`ni solishtirishda flag ochiq beriladi.

### Form Field Discovery
Tags: form, discovery, checkbox, switch, radio
Status: live-ui-confirmed
Verified: 2026-11-16
Source: `skills/smartup-guide/references/forms/screenshots/filial/filial__add-fields.json`; `skills/smartup-guide/references/forms/screenshots/filial/filial__add-fields-after-switches.json`; `skills/smartup-guide/references/forms/screenshots/filial/filial__add-switches-after-switches.json`; `utils/helper_utils.py::label_pattern`; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- Filial add arxivida `НДС` switchi `d.vat_enabled` modeliga ulangan. Yoqilgan holatda inputlar ro‘yxatiga `d.vat_percent` qo‘shilgan va guruh matnida `Ставка НДС (%)*` ko‘rinadi. Shu sabab bu formani tekshirganda default va switch yoqilgan holat alohida olinadi.
- Checkbox/radio uchun field turi, label, model, tanlangan va bloklangan holatlarni alohida tekshir. Label matnida qo‘shtirnoq bo‘lsa, ikkala page-object ishlatadigan `label_pattern` uning yonidagi ixtiyoriy backslashni ham taniydi.

### b-input

#### `select_first` va `search_text` kontrakti
Tags: b-input, locator
Status: code-confirmed
Verified: 2026-11-16
Source: user; `utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- `select_first=True` qidiruv maydoniga hech narsa yozmasdan ochilgan optionlar ichidan birinchi ko'rinadiganini tanlaydi; `search_text` birga berilgan bo'lsa ham qidiruv qilmaydi.
- `search_text=query` berilganda ikkala implementation ham ko‘rinadigan optionlar orasidan query matniga mosini qidiradi. Default `exact=True`, substring uchun `exact=False`. `option_contains` berilsa qo‘shimcha matnlar bilan bitta mos option qolishi tekshiriladi.
- Faqat `value=option_text` berilsa option matn bo'yicha tanlanadi. `value=option_text, search_text=""` esa qidiruvga yozmasdan ochiq ro'yxatdan aynan shu optionni tanlaydi.

- Qoida: `b-input` uchun public API bitta bo'lsin: `BasePage.b_input(...)`.
- Ishlatish:
  - `BasePage.b_input(label, value=option_text)` — tanlash
  - `BasePage.b_input(label, value=option_text, search_text="")` — dropdown clickda kerakli variant allaqachon ko'rinsa, searchga yozmasdan tanlash (masalan Product `Ед. изм.` → `шт`)
  - `BasePage.b_input(label, search_text=query, server_search=True)` yoki `AngularBasePage.b_input(...)` — qaytgan optionlardan query’ga mosini tanlash
  - `BasePage.b_input(label, select_first=True)` — qidiruvsiz birinchi ko'rinadigan optionni tanlash
  - `BasePage.b_input(ng_model="d.x", value=option_text)` — label ishonchsiz/yo'q bo'lsa fallback
  - `BasePage.b_input(label, expect_value=expected_value)` — value assert
  - `BasePage.b_input(label, return_value=True)` — joriy value olish
- Eslatma: ba'zi input value'lar sahifa textiga kirmaydi; input value assert qilish kerak.

#### Mavjud tanlov bilan `select_first`
Status: trace-confirmed
Verified: 2026-08-24
Source: user correction; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py`; `test-results/traces/tests_smoke_test_groups_test_report_grup_test_06_integration_two.py__test_report_integration_two.zip`
- `b-input`da oldindan tanlangan qiymat turgan bo'lsa, qidiruvsiz boshqa birinchi optionni tanlash uchun `clear=True, select_first=True` birga beriladi; `clear=True` mavjud tanlovni olib tashlab dropdown optionlarini ochadi.

### b-input Server-Search (report group)
Tags: b-input, server-search, hint, clear
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.b_input`; `utils/base_pages/angular_base_page.py::AngularBasePage.b_input`
- Legacy `b_input()` qidiruv maydonini komponent ichidagi `input[placeholder]` bilan topadi. `clear=True` holatida ko‘rinadigan `.edit` bo‘lsa bosadi, so‘ng inputni tozalab bo‘sh qiymatni tasdiqlaydi.
- `server_search=True` so‘rovni `press_sequentially` orqali, default 50 ms belgi oralig‘i bilan yozadi. Oddiy qidiruv `fill` ishlatadi. Ko‘rinadigan `.hint-item` optionlari ichidan query/value va ixtiyoriy qo‘shimcha matnlar bo‘yicha qidiriladi. Helper bosishdan avval mos option ko‘rinishini kutadi.
- A2 implementation ochilgan komponentning `li:visible` optionlarini oladi. Remote `smt-data-select` uchun tegishli lookup so‘rovi va loader tugashini kutadi.

### UI Select
Tags: ui-select, locator, dropdown
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.ui_select`
- Qoida: Angular UI Select uchun public API `BasePage.ui_select(...)`; uni `BasePage.b_input(...)` bilan boshqarma, chunki DOM va option strukturasi boshqa.
- Ishlatish:
  - `BasePage.ui_select(label="Статус", value="Черновик")` — option tanlash
  - `BasePage.ui_select(label="Статус", expect_value="Черновик")` — tanlangan qiymatni tekshirish
  - `BasePage.ui_select(label="Статус", return_value=True)` — joriy qiymatni olish
  - `BasePage.ui_select(ng_model="d.status", value="Черновик")` — label ishonchsiz bo'lsa fallback
- DOM: wrapper `.ui-select-container`, toggle `.ui-select-toggle`, tanlangan matn `.ui-select-match-text`, ochiq option `.ui-select-choices-row-inner:visible`.
- Search yoqilgan variantlarda `search_text=...` beriladi; helper faqat visible `.ui-select-search`ni to'ldiradi.
- `root` faqat qidiruv hududini cheklaydi, komponent turini almashtirmaydi.

### Multi-select b-input API
Tags: b-input, multiselect, helper, selected-chip
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.multiselect`; `tests/smoke/test_setup/flow_setup/flow_product.py::create_product_with_price`
- `BasePage.multiselect` parametrlari `BasePage.b_input` uslubida: `label`/`name` fieldni topadi, `value` tanlaydi, `expect_value` faqat selected chipni tekshiradi, `return_value=True` tanlangan chip matnlarini list qilib qaytaradi, `clear=True` barcha chiplarni tozalaydi.
- Testda auto-selected qiymatni tekshirish uchun locatorni olib alohida `base.text(..., root=field)` yozilmaydi; `base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)` ishlatiladi.
- `value` va `expect_value` bitta string yoki bir nechta qiymat uchun list/tuple qabul qiladi. `label` va `name` birga berilmaydi.

### Masked Date/Amount Inputs
Tags: input, mask, date, amount
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.input`; `utils/base_pages/angular_base_page.py::AngularBasePage.input`; `utils/base_pages/base_page.py::BasePage.date_picker`; `utils/date_utils.py::resolve_date`
- Legacy `input` va A2 `input` qiymat berilganda maydonni bosadi. `clear=True`da `ControlOrMeta+A` va `Backspace` orqali tozalab, `fill` qiladi. `press_tab=True` bo‘lsa oxirida `Tab` bosadi.
- Legacy `date_picker(..., auto_fill=True)` inputdagi sanani tekshiradi. Oddiy rejim kerakli kunni kalendardan tanlaydi, boshqa oy uchun ko‘rsatilgan `data-day` qiymatlarini `resolve_date` bilan o‘qiydi.
- `base.date(...)` bugun, kecha, ertaga, oy boshi/oxiri, `days` siljishi va `date_format`ni qabul qiladi. Nisbiy sanalar Asia/Tashkent bo‘yicha hisoblanadi.

### Biruni Confirm
Tags: biruni, confirm, modal
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.confirm_biruni`; `tests/smoke/test_life_cycle/flow_order/flow_order_list.py::flow_order_list`
- Legacy `confirm_biruni(expected_text=None, button_name="да")` ko‘rinadigan modal candidate’lardan kerakli tugmasi borini tanlaydi. Matn berilgan bo‘lsa uni va modalning opacity qiymati `1`ga yetganini tekshiradi. Tugmani shu modal ichida bosib, modal yashirilishini kutadi.
- `flow_order_list` status o‘zgartirishda `Изменить статус на {status}?` matnini kutadi. A2/CDK dialoglari uchun [modal helper ownershipi](#legacy-va-a2-modal-helper-ownershipi)ga qarang.

### Legacy va A2 modal helper ownershipi
Tags: modal, biruni, a2, cdk, locator, page-object
Status: live-ui-confirmed
Verified: 2026-08-25
Source: live UI `*/trade/rep/integration/integration_two`;
`utils/base_pages/base_page.py`; `utils/base_pages/angular_base_page.py`
- Legacy Biruni modal primitive'lari `BasePage`, A2/CDK modal primitive'lari
  `AngularBasePage` ichida alohida qoladi; ikki DOM kontrakti bitta generic
  utils helperga yoki bitta selector ro'yxatiga aralashtirilmaydi.
- Ikkala page-object bir xil public API'ni saqlaydi: majburiy confirm uchun
  `confirm_biruni(...)`, error dialogni tekshirib yopish uchun
  `close_biruni_alert(*expected_text)`.
- Legacy ona locator faqat ko'rinadigan `#biruniConfirm`,
  `#biruniAlertExtended` va `#biruniAlert` candidate'larini bir marta yig'adi;
  public metod modal turini button/error matni bilan filterlaydi.
- A2 ona locator `[role='dialog']:visible`. Jonli CDK error modali bir vaqtda
  tashqi `.cdk-overlay-pane` va ichki `[role='dialog']`ga mos tushadi; ikkisini
  union qilish bitta vizual modalni ikki candidate sifatida qaytaradi. Action
  scope sifatida ichki dialog ishlatiladi.
- Close tugmasi faqat visible semantic `Закрыть`/`Close`/`×` candidate'laridan
  tanlanadi. Legacy oddiy alertdagi `button.close` DOMda mavjud bo'lsa ham
  nol o'lchamli hidden nusxa bo'lishi mumkin.

### Status Dialog Return Semantikasi

Tags: modal, status, helper, return-value, known-issue
Status: code-confirmed
Verified: 2026-08-14
Source: `tests/smoke/test_life_cycle/flow_order/flow_status_dialog.py::dialog_status`

- Docstring “modal topilsa `True`, topilmasa `False`” deydi, ammo joriy kod
  modalni topib yopganda `False`, topilmaganda `True` qaytaradi.
- Joriy caller return qiymatini ishlatmaydi. Yangi consumer docstringka tayanib
  branch qilmasin; semantika tuzatilmaguncha helperni side-effect-only deb ol.

### Biruni Error
Tags: biruni, error, modal
Status: live-ui-confirmed
Verified: 2026-08-06
Source: user; live UI `*/anor/mr/product/inventory+add`;
`tests/smoke/test_forms/monitoring/checks/application_error.py`;
`tests/smoke/test_forms/monitoring/monitor.py`
- Legacy formadagi odatiy blocking backend/business xato modali
  `#biruniAlert.modal.fade.show[role="dialog"]`. Ko'rinadigan strukturasi:
  `Ошибка` headingi, `.text-danger` xato matni, `button.close` va textli
  `Закрыть` tugmasi. Jonli misol: mavjud `<product_code>` bilan TMC saqlashda
  duplicate-code xatosi shu modalda chiqdi.
- Extended varianti `#biruniAlertExtended[role="dialog"]`; oddiy va extended
  modal DOMda bir vaqtda mavjud bo'lishi mumkin, lekin faqat `.show`/`:visible`
  holati xato signali hisoblanadi. Ko'rinadigan oddiy yoki extended alertni
  tekshirib yopish uchun `BasePage.close_biruni_alert(*expected_text)`
  ishlatiladi; helper visible `button.close` bo'lmasa `Закрыть`/`Close` textli
  buttonni bosadi va modal yashirilishini kutadi.
- Barcha forma xatolari aynan shu modal ko'rinishida chiqmaydi. Legacy formani
  saqlash/tranzaksiya backend xatolari ko'pincha Biruni modalida; forma
  ochilishidagi vaqtinchalik xabar `[role="alert"]`, inline validatsiya
  `.alert-danger`, A2 xatolari esa boshqa error komponentida ko'rinishi mumkin.
- Forms monitor `check_application_error` orqali faqat
  `#biruniAlertExtended:visible`, `#biruniAlert:visible`,
  `.alert-danger:visible` va
  `[role="dialog"]:visible [data-testid*="error" i]` hard signallarini
  tekshiradi. Generic `[role="alert"]:visible` warning yoki axborot ham bo'lishi
  mumkinligi uchun hard signal emas. Aniq signal target sahifada ko'rinsa
  natija `OPENED_WITH_DEFECT / APPLICATION_ERROR` bo'ladi. Faqat formani
  ochadigan smoke test save-time modalni o'zi hosil qilmaydi; modal formani
  ochishda paydo bo'lsa yoki case tegishli actionni bajarsa aniqlanadi.
- Modal yopilmasa menu/list clicklari intercept bo'lishi mumkin. Save/transition
  debugda kutilgan list/view ochilmasa joriy heading va URL bilan birga ikkala
  Biruni alertning visible matnini tekshir.

#### User-reported: kuzatilgan Smartup xatolari BiruniAlert ichida ko'rsatiladi
Tags: biruni, error, javascript, forms-monitor, test-policy
Status: user-reported
Verified: 2026-08-06
Source: user; `tests/smoke/test_forms/monitoring/checks/core.py`;
`tests/smoke/test_forms/monitoring/monitor.py`
- Qayerda: Smartup formalarida foydalanuvchi ko'rgan funksional/application
  xatolari.
- Kuzatuv: foydalanuvchi hozirgacha barcha turdagi real Smartup xatolarini
  BiruniAlert modali ichida ko'rgan; modal tashqarisidagi tabiiy JS exception
  holatini kuzatmagan. 2026-08-05 dagi 147-forma baseline runida ham tabiiy JS
  exception `0` bo'lgan.
- Chegara: sun'iy `throw` probe'i JS detector ishlashini isbotlaydi, ammo
  Smartup mahsulotida bunday tabiiy xato mavjudligini yoki Forms smoke uchun
  `javascript` hard check zarurligini isbotlamaydi. Bu kuzatuv tasdiqlanmasdan
  universal UI haqiqati deb olinmaydi.
- 2026-08-06 user qarori va joriy kod contracti: FormMonitor'da `javascript`
  hard check, `JS_ERROR`, Playwright `pageerror` listeneri va window JS
  exception capture'i yo'q. Application xatosi ko'rinadigan UI/Biruni
  signallari orqali `APPLICATION_ERROR` sifatida tekshiriladi. FormMonitor
  resource error va unhandled promise rejectionni ham yig'maydi.

### Alert Kutish — `is_visible(timeout=...)` O'lik Parametr
Tags: locator, alert, timeout, is_visible, wait_for, forms-monitor
Status: code-confirmed
Verified: 2026-08-06
Source: Playwright API docstring; real Chromium tekshiruvi;
`tests/smoke/test_forms/monitoring/checks/application_error.py`;
`tests/smoke/test_forms/monitoring/monitor.py`
- Qoida: `locator.is_visible(timeout=...)` — **o'lik parametr**. O'rnatilgan
  Playwright dokumentatsiyasi: *"Deprecated: This option is ignored.
  `locator.is_visible()` does not wait."* Ya'ni `is_visible` doim lahzalik
  surat, `timeout=` yozilsa kod yolg'on tushuntiradi. Kutish kerak bo'lsa
  `locator.wait_for(state="visible", timeout=...)` ishlatiladi.
- Nega muhim: forma ochilgandan keyin server validatsiya xatosi kechikib
  kelishi mumkin. Lahzalik surat uni ko'rmaydi va forma **yolg'on PASSED**
  bo'ladi — hisobotda hech qanday iz qolmaydi, ya'ni bu muammoni hisobotdan
  topib bo'lmaydi.
- **O'lchangan kechikish (2026-08-05, `Заказы`/`Возвраты` `+add`, 6 o'lchov):**
  min **24 ms**, o'rtacha **227 ms**, maksimum **849 ms**. Taymer navigatsiya
  tugagan zahoti boshlandi. Bu o'lchov eski `capture_form_state` alert
  kutishidan olingan; joriy kodda kutish mustaqil `check_application_error`
  gate'ida bajariladi. Maksimum **birinchi (cold) navigatsiyada** chiqdi;
  keyingi takrorlarda 20–30 ms.
- 2026-08-05 o‘lchovida 700 ms kutish cold-startdagi 849 ms xatoni
  o‘tkazib yuborgan bo‘lardi. Amaldagi default
  [application error kontraktida](form-monitor/check-application-error.md).
- Bir nechta alert selektorini kutish kerak bo'lsa, ularni **vergul bilan bitta
  locatorga birlashtir**:
  `page.locator(", ".join(HARD_ERROR_SELECTORS)).first.wait_for(state="visible", timeout=...)`.
  Alert chiqsa darhol qaytadi, chiqmasa bir marta timeout to'laydi. Har
  selektorni alohida kutish 6 × timeout ga tushadi.
- Real Chromium'da tekshirildi: `:visible` pseudo-klassi vergulli listda
  ishlaydi — `display:none` element sanalmaydi, ko'rinadigani topiladi.
- Narxi: sog'lom sahifaga bir marta to'liq timeout. `1_200 ms` bilan
  Forms-03 (38 forma) 146.78 s → 184.10 s, ya'ni **+0.98 s har formaga**.
- Joriy check faqat `PlaywrightTimeoutError`ni "error topilmadi" deb qabul
  qiladi. Yaroqsiz selector yoki boshqa Playwright contract xatosi jim
  yutilmaydi. Selector ro'yxati o'zgarsa real brauzerda tekshir.
- Forms monitoringda blocking loader alohida browser-aware gate sifatida
  kutiladi; undan keyin application-error gate ishlaydi. `capture_form_state`
  alertni qayta kutmaydi. `aria-busy` blocking signal emas va FormMonitor uni
  diagnostika sifatida yig'maydi. Blocking signalni quyidagi qoida bo'yicha
  ajrat.

### Blocking loader va `aria-busy` (2026-08-05)
Tags: loader, aria-busy, a2, dashboard, forms-monitor, false-fail
Status: live-ui-confirmed
Verified: 2026-08-06
Source: 2026-08-05dagi tarixiy Forms-03 Allure artifact; real Chrome audit — A2 dashboard va Plugin Marketplace;
`tests/smoke/test_forms/monitoring/checks/loader.py`; `tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/navigation.py`; `utils/base_pages/angular_base_page.py`
- `check_loader` URL gate'dan darhol keyin ko'rinadigan
  `.block-ui-overlay` yoki `.smt-skeleton` yo'qolishini default `60_000 ms`
  kutadi. Ular timeout oxirida qolib ketsa forma
  `OPENED_WITH_DEFECT / LOADER_NOT_FINISHED`; keyingi hard checklar `NOT_RUN`.
- `[aria-busy=true]` o'zicha blocking loader emas. Dashboard ichidagi nested
  widget to'liq sahifa render bo'lgandan keyin ham busy qolishi mumkin.
  o'sha tarixiy Forms-03 `Коммерческий дашборд` artifactida expected URL/title/content va
  screenshot sog'lom bo'lsa ham aynan shu signal eski monitorni yolg'on
  `NOT_OPENED` qilgan.
- FormMonitor `[aria-busy=true]`ni yig'maydi. Forms oqimidagi navigation
  helperlari loaderni oldindan kutmaydi; yagona pass/fail authority
  `check_loader`. Boshqa setup/group testlarida umumiy
  `AngularBasePage.wait_for_loader()` o'zgarishsiz ishlaydi.
- Expected pathga yetgan blocking loader `NOT_OPENED` emas: sahifa ochilgan,
  lekin nuqsonli. `NOT_OPENED` noto'g'ri/missing route yoki yetib bo'lmagan
  content uchun saqlanadi.

### A2 sahifada `pageerror` chiqmaydi (2026-08-05)
Tags: a2, angular, pageerror, js-error, forms-monitor, listener
Status: trace-confirmed
Verified: 2026-08-05
Source: real Chromium probe — legacy va A2 formalarida 4 kanal;
`tests/smoke/test_forms/monitoring/monitor.py`
- Qoida: **A2 (`/a2/...`) sahifalarida `page.on("pageerror")` ishlamaydi.**
  Ilova global `error` eventida `preventDefault()` chaqiradi, shuning uchun
  Chrome xatoni "handled" deb hisoblaydi va Playwright'ga uncaught exception
  sifatida yubormaydi. Legacy sahifalarda esa kanal normal ishlaydi.
- O'lchov (bir xil forma, ikki xil kelish yo'li bilan):

  | Sahifa / yo'l | `error` eventi `preventDefault` | `setTimeout` | `queueMicrotask` | `rAF` | inline `script` |
  |---|---|---|---|---|---|
  | Legacy forma (`#/!<code>/...`) | ❌ yo'q | ✅ | ✅ | ✅ | ✅ |
  | A2 forma — to'liq sahifa yuklanishi | ❌ yo'q | ✅ | ✅ | ❌ | ❌ |
  | A2 forma — **SPA route** o'zgarishi | ✅ **bor** | ❌ | ❌ | ❌ | ❌ |

- Ya'ni A2 ga **birinchi** kirishda (legacy shell'dan to'liq yuklanish) ba'zi
  kanallar hali ishlaydi, lekin ilova ishga tushib SPA navigatsiyaga o'tgach
  hammasi jim bo'ladi. Forms suite A2 formalarini aynan SPA route bilan
  ochadi — demak ular uchun kanal **ko'r**.
- Tarixiy amaliy natija: Playwright `pageerror` signali **119 legacy formada**
  ishlagan (sun'iy injektsiya bilan tasdiqlangan), **28 A2 formada** esa
  ko'r bo'lgan. Capture yechimidan oldin A2 da "0 JS xato" sog'lom degani emas edi.
- **Tarixiy detector (2026-08-05 da qilindi va isbotlandi):** `page.add_init_script` bilan
  app bundle'dan **oldin** capture-fazada
  `window.addEventListener("error", ..., true)` o'rnatiladi va xatolar `window`
  massividan `page.evaluate` orqali o'qiladi. Init script har document'da
  birinchi ishlagani uchun `preventDefault` unga ta'sir qilmaydi.
  Real A2 SPA route'da sun'iy injektsiya bilan tekshirildi:

  | Texnika | `page.on("pageerror")` | Capture-faza listeneri |
  |---|---|---|
  | `setTimeout` | ❌ jim | ✅ ushlaydi |
  | `queueMicrotask` | ❌ jim | ✅ ushlaydi |
  | `requestAnimationFrame` | ❌ jim | ✅ ushlaydi |

  Ushbu detector joriy FormMonitor'dan 2026-08-06 user qarori bilan olib
  tashlangan; tarixiy contract `history.md`da saqlanadi.
- Joriy monitor `pageerror`, window JS exception, resource load error va
  `unhandledrejection`ni yig'maydi. Eski capture diagnostikasi
  `history.md`da tarixiy kontrakt sifatida saqlanadi.

### List va Grid Setting
Tags: list, grid, search, column
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage.grid_setting`; `utils/base_pages/angular_base_page.py::AngularBasePage.grid_setting`; `tests/smoke/test_setup/test_16_payment_type.py::run_payment_type`; `tests/smoke/test_groups/test_visit_grup/test_01_mobile_visit.py`; `tests/smoke/test_setup/test_01_legal_person.py::run_legal_person`
- `grid_setting(menu_name=..., field_name=..., search_name=...)` ustunni yoqadi va saqlangach uning indeksini qaytaradi. `search_name` berilsa qidiruv sozlamasida ham shu nomdagi fieldni yoqadi.
- Payment Type’da `ИД` ikkala parametrga beriladi. Visit listda test `field_name="ИД"` bilan cheklanadi. Katta listda Legal Person kabi testlar gridni tekshirishdan oldin `grid_controller(search=...)` orqali yaratilgan entity kodini qidiradi.

### A2 grid setting alohida DOM kontrakti

Tags: a2, grid, setting, column, search, angular-base-page
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `https://kernel.greenwhite.uz/anor/mkr/price_type_list`;
`utils/base_pages/angular_base_page.py`

- A2 `smt-data-table` actions menyusi `smtvalue="menu"` buttoni orqali ochiladi;
  actionlar CDK overlaydagi `menuitem` elementlar.
- Table fieldlar `Настройки таблицы` dialogidagi `Активные поля` va
  `Неактивные поля`da boshqariladi; inactive field button bosilganda active
  listga o'tadi, `Сохранить` dialogni yopadi.
- Search fieldlar table dialogida emas, alohida `Настройки поиска` dialogida
  checkbox orqali yoqiladi va `Подтвердить` bilan saqlanadi.
- Search fieldlar tarkibi formaga bog'liq: Visit listda `ИД` table fieldi bor,
  ammo search settingda `ИД` yo'q.
- `AngularBasePage.grid_setting()` shu A2 kontraktni ishlatadi; legacy
  `BasePage.grid_setting()` esa Biruni grid-setting route kontraktini saqlaydi.

### Umumiy CRUD Sahifa Tuzilishi
Tags: list, add, edit, view, grid, loader
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py::run_legal_person`; `tests/smoke/test_setup/test_04_robot.py::run_robot`; `utils/base_pages/auto_base_page.py`
- Legal Person va Robot testlarida list → `Создать` → maydonlarni to‘ldirish → `Сохранить` → listdagi qator → `Просмотреть` → view qiymatlarini tekshirish → `Закрыть` oqimi ishlatiladi. Har sahifa almashganda test kutilgan heading va route’ni `expect_page`ga beradi.
- Migratsiyaga mos testlar shu amallarni `AutoBasePage` orqali bajaradi. List qatorlari va loader signallarini tanlangan legacy/A2 implementation aniqlaydi.

### Screenshot Arxivi
Tags: screenshot, debug, url
Status: code-confirmed
Verified: 2026-11-16
Source: `skills/smartup-guide/scripts/validate_knowledge_base.py::check_screenshots`; `tests/shared/reporting.py::attach_failure_artifacts`
- Forma screenshotlari dossierga bog‘langan `references/forms/screenshots/<form-slug>/` arxivida turadi. Validator rasmlarning dossier/indexda tilga olinganini, sidecar JSON mavjudligini, JSON sintaksisini va session yoki entity qiymatlarining belgilangan patternlarini tekshiradi.
- Run paytidagi failure screenshoti pytest/Allure hisobotiga biriktiriladi. Keyingi locator yoki debug uchun doimiy dalil kerak bo‘lsa, mavjud arxivni tekshir. Tasdiqlangan yangi capture uchun nomlash, session qiymatlarini parametrga almashtirish va write-back tartibi [Smartup Guide](../SKILL.md#form-dossier-qoidasi) va [learn](../../learn/SKILL.md)da.
- Yangi tasvir uchun `<form-slug>__<state>__<viewport>__<stable-id>.png` va bir xil stemli JSON ishlatiladi. Manbasi ma’lum bo‘lsa parametrik route, form/state, viewport, sana, browser va dinamik/mask hududlarini metadata’da ko‘rsat. Eski arxivda mavjud format va ma’lumotlar turlicha.
- Arxivni yangilash tasdiqlanganida faqat yangi yoki vizual o‘zgargan form/state/viewport tasvirini saqla. Metadata va snapshot matnidagi session qiymatlarini placeholder bilan almashtir. Eski tasvir o‘rniga yangisini saqlashdan avval dossier havolasi va tarixiy qiymatini tekshir.

### Umumiy Forma Helper'lari (DRY)
Tags: locator, form, helper, setup
Status: code-confirmed
Verified: 2026-11-16
Source: `utils/base_pages/base_page.py::BasePage._field_locator_by_label`; `utils/base_pages/base_page.py::BasePage.input`; `utils/base_pages/base_page.py::BasePage.checkbox`; `utils/base_pages/base_page.py::BasePage.radio`; `utils/base_pages/base_page.py::BasePage.grid`; `utils/base_pages/auto_base_page.py`; `tests/smoke/test_setup/test_21_room_attachment.py::run_room_attachment`
- Legacy helperlar `BasePage`da, A2 helperlar `AngularBasePage`da. Migratsiyaga mos testda `AutoBasePage` har bir amalda shell’ga mos implementationni tanlaydi. Navigatsiya, filial, click, modal va form field uchun mavjud primitive ishlatiladi. [Page-object tanlash](#page-object-tanlash)
- Legacy `input` locatorni `label`, `ng_model`, `placeholder` yoki berilgan `locator`dan oladi. `value` yozadi, `expect_value` bilan tekshiradi, `return_value=True` satr qaytaradi. `press_tab`, `index` va `root` bilan toraytirish mumkin. Display qiymat uchun [form_view](#view-qiymatini-label-bilan-olish) ishlatiladi.
- Label resolver checkbox/radio uchun avval `ancestor-or-self::label`dagi mos inputni, u bo‘lmasa labeldan keyingi inputni tekshiradi. Boshqa fieldda eng yaqin tegishli form/column containerdagi target yoki labeldan keyingi fieldni qidiradi. Oddiy input strategiyasi yashirin, checkbox/radio va `focusser-*` inputlarni chetlab o‘tadi. Grid sarlavhasi orqali qidiruvda headerga mos ustun aniqlanadi.
- Forma switch/checkbox uchun `checkbox(..., checked=...)` holatni o‘rnatadi yoki `expect_checked` orqali tekshiradi. Radio uchun `radio(label, click=True)` tanlaydi, `expect_checked` holatni tekshiradi. Legacy `_toggle_checkbox` yashirin native inputda ko‘rinadigan label/wrapper yoki grid checkbox koordinatasi orqali toggle qila oladi.
- Legacy `grid(checkbox="row")` mos qator checkboxini, `grid(checkbox="all")` ko‘rinadigan gridning `input[bcheckall]` elementini belgilaydi. Header select-all bo‘lmasa helper birinchi checkboxni oladi. `root` berilmasa birinchi ko‘rinadigan `b-grid` ishlatiladi.
- `grid(state="empty")` ko‘rinadigan griddagi `нет данных`ni kutadi. `grid(text, *contains)` mos qatorni va uning matnlarini tekshiradi. `remove_spaces=True` default bo‘lib, formatlangan sonlarni whitespace’ga bog‘lamasdan solishtiradi.
- `return_bool=True` row yoki bo‘sh holatni bir marta o‘qiydi. U bilan `contains`, click va checkbox amallari birga ishlatilmaydi. `state="empty"` ham row/click/checkbox bilan birga berilmaydi. Room Attachment testida tab almashgach `wait_for_loader()` tugashi kutiladi, shundan keyin grid holati tekshiriladi.

### BasePage Semantic Click Helper
Tags: locator, helper, button, tab
Status: code-confirmed
Verified: 2026-07-31
Source: user; `utils/base_pages/base_page.py::BasePage.click`
- Qayerda: legacy AngularJS/Biruni sahifalaridagi semantic role/name bilan topiladigan elementlar.
- Qoida: raw `page.get_by_role(role, name=...).click()` o'rniga
  `base.click(name=name, role=role)` ishlatiladi. Ko'p uchraydigan tugmalar
  uchun `role="button"` default. Playwright `get_by_role` xulqini saqlash uchun
  `exact=False` ham default va testda qayta yozilmaydi; faqat exact match kerak
  bo'lsa `exact=True` beriladi. Kerak bo'lsa `role`, `index`, `root` va
  `timeout` aniq beriladi.
- Testda ishlatish: masalan, `base.click(name="Формы", role="tab")` va
  `base.click(name="Доступные")`.

### Legacy Save Transition Ochiq Yoziladi
Tags: save, transition, helper, loader
Status: code-confirmed
Verified: 2026-07-31
Source: user; `utils/base_pages/base_page.py`; `tests/smoke/test_setup/test_13_price_type_uzb.py`
- Qayerda: legacy AngularJS/Biruni add/edit formadan list yoki viewga saqlab
  o'tish.
- Qoida: birlashtirilgan save+heading helperi ishlatilmaydi. Test
  `base.click(name="Сохранить")` (exact kerak bo'lsa `exact=True`), confirm majburiy bo'lsa
  `base.confirm_biruni(...)`, so'ng `base.expect_page(heading=..., url=...)`
  amallarini ochiq yozadi.
- Testda ishlatish: `expect_page(heading=...)` target heading bilan birga
  visible loader overlay yo'qolishini ham kutadi; shu page transitionda
  alohida `base.wait_for_loader()` takrorlanmaydi.

### Order wizard yakunida saqlash
Tags: order, locator, error
Status: trace-confirmed
Verified: 2026-11-16
Source: `outputs/online-regression-20261018/canonical-traces/tests_smoke_test_groups_test_a_grup_test_0_group_runner.zip` (`trace.trace`, `after@call@12560`, `after@call@12812`); `tests/smoke/test_life_cycle/flow_order/flow_order_add.py::flow_order_final_page`; `utils/base_pages/base_page.py::BasePage.click`
- Arxivlangan Group-0 trace’da `#anor279-button-next_step` oldingi qadamda `Далее`, oxirgi qadamda `Сохранить` bo‘lgan. Oxirgi button ichida `fa-save` ikonka bor. Snapshot accessibility tree’dagi yakuniy nomni o‘lchamagan.
- `flow_order_final_page(save=True)` oxirgi qadamda `base.click(name="Сохранить")`dan foydalanadi. Click helperida button default role va `exact=False`. Keyin `Сохранить?` confirmi hamda `Заказы` headingi va `order_list` route’i tekshiriladi.

## Loyiha Xususiyatlari

### Legacy Navbar → Forma Navigatsiyasi

- Umumiy primitive `BasePage.navigate_to_form(...)`: `navbar_tab → menu_column
  → menu_item → page_links`.
- Bu primitive faqat navigatsiya qiladi. Forma ochilganini tasdiqlash chaqiruvchi
  testda alohida bajariladi; URL/title tekshiruvi `navigate_to_form()` ichiga
  yashirilmaydi.
- `BasePage.navigate_to_form()` legacy shelldagi menu/page-link navigatsiyasi
  uchun; target legacy yoki A2 bo'lishi mumkin. Joriy sahifa A2 bo'lsa keyingi menu navigatsiya
  `AngularBasePage.navigate_to(tab=..., name=...)`, filial almashtirish
  `AngularBasePage.switch_filial(...)`, forma tasdig'i esa
  `AngularBasePage.expect_page(heading=..., url=...)` bilan bajariladi.
  Forms monitor esa URL/title checklarini o'zi boshqaradi.
- A2 listlarda ko'rinadigan forma nomi semantik `role=heading` bo'lmasligi
  mumkin. `company_client_list`da `BasePage.expect_page(heading=...)` false
  failure bergan, holbuki URL, `document.title` va `smt-data-table` to'g'ri
  yuklangan. A2 uchun legacy heading assertion ishlatilmaydi.
- Kichik flyoutda ustun heading bo'lmasa `menu_column=None` beriladi va
  `menu_item` bevosita ochilgan flyout ichidan qidiriladi; `Плагин → Plugin
  Marketplace` 2026-07-27 live tasdiqlangan misol.
- Menu matni real DOM bilan aynan yozilsin: `е` va `ё` farqi locator uchun
  muhim. Shelf-share leaf matni `Конструктор отчётов по доле на полке`.
- Mega-menu ustun headingi substring bilan emas, exact matn bilan topilsin.
  `Продажа` tabida `has_text="Продажа"` bir vaqtda `Продажа` va
  `Отчеты по продажам` headinglarini match qiladi; natijada ustun UI'da
  ko'rinib turgan bo'lsa ham yagona element assertioni yiqiladi.
  - Status: trace-confirmed
  - Verified: 2026-08-04
  - Source:
    `test-results/logs/tests_smoke_test_forms_test_0_forms_runner.py__test_forms_03_prodaja_20260804_151214.log`;
    Allure `010-Заказы-NOT_OPENED-URL_MISMATCH-evidence` screenshoti;
    `utils/base_pages/base_page.py`
- Parent forma ichidagi bir yoki bir nechta yuqori linklar `page_links`ga
  bosilish tartibida beriladi.
- Foydalanuvchi bergan visual namunalar:
  `forms/screenshots/menu-navigation/menu-navigation__navbar-and-column__1036x448.png`
  va `forms/screenshots/menu-navigation/menu-navigation__page-link__361x131.png`.
