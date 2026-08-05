# UI Patterns

## Mundarija

- [Locator tanlash](#locator-tanlash)
- [Heading va sahifa tekshirish](#heading--sahifa-tekshirish--expect_page-helper)
- [Form field discovery](#form-field-discovery)
- [b-input](#b-input)
- [UI select](#ui-select)
- [Masked inputs](#masked-dateamount-inputs)
- [Biruni confirm va error](#biruni-confirm)
- [Alert kutish va o'lik timeout](#alert-kutish--is_visibletimeout-olik-parametr)
- [A2 sahifada `pageerror` chiqmaydi](#a2-sahifada-pageerror-chiqmaydi-2026-08-05)
- [List va grid setting](#list-va-grid-setting)
- [Screenshot arxivi](#screenshot-arxivi)
- [Umumiy forma helperlari](#umumiy-forma-helperlari-dry)

## Qidiruv Kalitlari

Tags: locator, b-input, grid, modal, biruni, screenshot, list

### Locator Tanlash
Tags: locator, angular
- Qoida: Angular `ng-model` locatorlardan iloji boricha qoch.
- Qoida: Yangi testlarda raw CSS/XPath/`ng-model` locator yozma; avval `page.get_by_role(...)`, `page.get_by_text(...)` yoki label/textga tayangan helper ishlat.
- Kontekst: hozircha Angular migratsiyaga o'tgan UI faqat `company` formasi; qolgan formalar eski Biruni/AngularJS tuzilmasida va ularda mavjud `ng-model`/`b-input` helperlari ishlatiladi.
- Afzal locatorlar:
  - `BasePage.input(label="Код", value=...)` (universal: `label=`/`ng_model=`/`placeholder=`/`locator=`)
  - `BasePage.b_input(label, value=...)`
  - label/text asosidagi local yoki umumiy helper
  - `page.get_by_role(...)`
- Sabab: UI Angular migratsiya/yangilanishlarida semantik locatorlar barqarorroq.

### MCP bilan Smartup'ni Haydash — locator manbasi, snapshot iqtisodi
Tags: mcp, playwright, locator, snapshot, workflow
- Qoida: MCP (`mcp__playwright__*`) bilan Smartup'ni jonli haydashda har qadamda `browser_snapshot` OLMA. Avval locatorni shu guide'dan va helper/flow fayllaridan ol: `BasePage.switch_filial()` (`.dropdown-locations-custom:visible`), `flow_navigate.py` (`a.menu-link.menu-toggle`, `a.menu-link.menu-link-title`), `flow_authorization.py`, `forms/<slug>.md` dossierlari, hamda yuqoridagi afzal helper/role locatorlar. Ular bilan to'g'ridan-to'g'ri CSS/role selector orqali `browser_click`/`browser_type` qil.

### Legacy shell filial switcher

- Filial menyusini ichki dekorativ strelka `.pt-3.px-2` orqali ochma. 2026-07-24 CI
  trace'da bu locator elementni topgan, lekin u hidden bo'lgan.
- Ko'rinadigan trigger: `.dropdown-locations-custom:visible`. Barqaror helper
  `BasePage.switch_filial()` avval `.header-logo.custom-dropdown:visible` locations
  containerini topadi, triggerni bosadi va optionni faqat shu container ichidagi
  ko'rinadigan `.dropdown-menu` orqali tanlaydi.
- Tanlash tugagach aynan trigger ichidagi `.project-filial p` filial nomi bilan
  yangilangani tekshiriladi.
- `browser_snapshot` faqat: (a) locator hujjatlanmagan/noma'lum bo'lsa (yangi forma), (b) kutilmagan holatni aniqlash uchun. Olsang ham `target`/`depth` bilan cheklab ol, butun sahifani emas.
- Grid/natija tekshirish uchun butun snapshot o'rniga `browser_evaluate` bilan aniq elementni target qilib olish yengilroq (masalan `b-grid .tbl-row` matnlarini `innerText` orqali). 2026-07-02 da user grid login ustunini shu yo'l bilan tekshirdim.
- Sabab: har `browser_snapshot` yuzlab qator YAML qaytaradi va kontekstni behuda to'ldiradi; locator allaqachon guide/flow'da bo'lsa snapshot ortiqcha.

### Heading / Sahifa Tekshirish — `expect_page` helper
Tags: locator, heading, get_by_role, navigation, url
- **DOM fakti** (2026-06-29 live tekshirilgan): sahifa sarlavhasi yagona `<h6 class="text-dark font-weight-bolder ...">` (Angular `ng-binding`). `<h1>` mavjud, lekin **bo'sh** — sarlavha uchun `h1` ISHLATMA, `get_by_role("heading")` ishlat.
- Oddiy list/create sahifada `role=heading` aniq **1 ta**. Sahifa o'zgarsa shu elementning matni **almashadi** (yangi heading element qo'shilmaydi). `navigate_to` transition o'rtasida heading matni qisqa vaqt **bo'sh `''`** bo'ladi — shuning uchun tekshiruv doim **auto-retry qiluvchi `expect(...)`** bilan bo'lsin, bir martalik `inner_text()` emas.
- **Ko'p heading muammosi:** wizard yoki ko'p bo'limli formalarda bir vaqtda bir nechta ko'rinadigan heading bo'ladi (masalan Акция create: `Акция (создание)`, `Главное`, `Условия`). Bunda `expect(page.get_by_role("heading")).to_contain_text(X)` — kerakli matn ulardan birida bo'lsa ham — **FAIL bo'ladi** (2026-06-29 sintetik isbotlangan: locator 2+ elementga to'g'ri kelsa, scalar `to_contain_text` to'g'ri matnda ham yiqiladi). Ya'ni to'g'ri sahifada turib ham false-negative beradi.
- **Afzal yechim — `base.expect_page(heading=None, url=None, timeout=...)`** (`base.navigate_to(...)` dan keyin chaqiriladi; `navigate_to` o'zi faqat navigatsiya qiladi, tekshirmaydi):
  - `base.expect_page(heading="Цены")` — `heading` str (substring, registrga befarq) yoki `re.compile(...)` bo'lishi mumkin (masalan `re.compile(r"Комп|Comp")`). Ichida `get_by_role("heading").filter(has_text=...).first` + `to_be_visible()` ishlatiladi: ortiqcha heading bo'lsa ham mosini tanlaydi, `.first` strict-mode'dan saqlaydi, retry qiladi.
  - `root` faqat to'liq sahifa uchun emas: modal headingini `base.expect_page(heading="Добавить курс", root=page.get_by_role("dialog"))` kabi scoped tekshirish mumkin.
  - `base.expect_page(url="price_type_list")` — `url` bo'lagi (substring) yoki regex. **URL slug eng ishonchli signal**: locale'ga bog'liq emas, har sahifada unikal.
  - `base.expect_page(heading="...", url="...")` — ikkalasi birga, eng kuchli tekshiruv.
- Barqaror URL slug'lar: `price_type_list`, `payment_type_list`, `filial_list`, `inventory_list` (ТМЦ), `action_list` (Акции), `order_list`, `anor/mkf/contract_list`, `template_list`.
- Eski `expect(page.get_by_role("heading", name="X")).to_be_visible()` ham ishlaydi (substring; `exact=True` ISHLATMA — list heading'larda ko'pincha oldida icon/probel bo'ladi), lekin yangi/refactor kodda `expect_page` afzal: bitta markaziy nuqta, xato xabari hozirgi heading + url ni ko'rsatadi.

### View (Просмотр) label→value olish — exact match
Tags: locator, order-view, label, xpath
- Order list row action tugmasi hozir `Просмотр`, eski deploymentlarda `Просмотреть`; `flow_order_list(..., view=True)` ikkala variantni regex bilan qabul qiladi va tugmani row ichida scope qiladi.
- `BasePage.form_view(...)` ikkala eski Smartup view DOMini qo'llaydi: `label + .form-view` va order viewdagi exact `<t>` labelning `../../span` qiymati. `flow_order_view` ham shu helperdan foydalanadi.
- Formatlangan amountlarda `form_view(label=..., expect_value="7000", remove_spaces=True)` ishlatiladi: UI'dagi `7 000` kabi barcha whitespace assertda e'tiborsiz qilinadi; `return_value=True` bilan ham whitespace'siz qiymat qaytadi. Default `remove_spaces=False`, shuning uchun ism/status kabi qiymatlarda probellar tekshirilishda davom etadi.
- `contains(text(),"{key}")` ISHLATMA: ilova label'larga yangi uzun matn qo'shsa (masalan `Статус` yoniga `Статус заказов, которые более 90 (дней)` tooltip/label qo'shilgan — 2026-06-21), `contains` ikkala `<t>` ga mos kelib strict mode violation beradi. Aniq (`normalize-space()=`) moslik shart.

### Form Field Discovery
Tags: form, discovery, checkbox, switch, radio
- Yangi add/edit forma o'rganilganda faqat `input[type=text]`, `textarea`, `select` va `b-input`larni yig'ish yetarli emas.
- Smartup switchlar ko'pincha styled checkbox sifatida chiqadi; `input[type="checkbox"]`, `input[type="radio"]`, ularning label/group texti, `ng-model`, `checked`, `disabled`, `visible` holati alohida yig'ilsin.
- Switch yoqilgandan keyin yangi required maydon paydo bo'lishi mumkin; masalan filial add’da `НДС` (`d.vat_enabled`) yoqilganda `Ставка НДС (%)` (`d.vat_percent`) majburiy input bo'ladi.
- Formani "full" qilishdan oldin field discovery kamida ikki holatni tekshirsin: default state va switch/checkbox yoqilgandan keyingi state.

### b-input
Tags: b-input, locator
- Qoida: `b-input` uchun public API bitta bo'lsin: `BasePage.b_input(...)`.
- Ishlatish:
  - `BasePage.b_input(label, value=option_text)` — tanlash
  - `BasePage.b_input(label, value=option_text, search_text="")` — dropdown clickda kerakli variant allaqachon ko'rinsa, searchga yozmasdan tanlash (masalan Product `Ед. изм.` → `шт`)
  - `BasePage.b_input(ng_model="d.x", value=option_text)` — label ishonchsiz/yo'q bo'lsa fallback
  - `BasePage.b_input(label, expect_value=expected_value)` — value assert
  - `BasePage.b_input(label, return_value=True)` — joriy value olish
- Eslatma: ba'zi input value'lar sahifa textiga kirmaydi; input value assert qilish kerak.

### b-input Server-Search (report group)
Tags: b-input, server-search, hint, clear
- Ba'zi `b-input`lar client-side emas, server-side qidiradi (masalan `price_types`).
- Placeholder `"Поиск..."` (nuqta bilan) yoki `"Поиск"` bo'lishi mumkin — locator sifatida `b_input.locator("input[placeholder]").first` ishlatiladi.
- Allaqachon tanlangan qiymat bo'lsa: X tugmasi `.edit` (Angular `ng-hide`) — `is_visible()` tekshirish kerak, `count() > 0` emas.
- Agar `.edit` ko'rinsa — avval clear qil, keyin yoz; ko'rinmasa — to'g'ri click qil.
- Server-search uchun `press_sequentially(search_text, delay=50)` ishlatiladi (debounce trigger); client-search uchun oddiy `fill()` yetarli.
- Dropdown locator faqat visible optionni oladi: `b_input.locator(".hint-item:visible").filter(has_text=option).first`. Hidden stale optionni `.first` qilib kutish mumkin emas — server/client refreshdan keyingi visible row DOMda boshqa element bo'lishi mumkin.
- Asinxron dropdown natijasidan keyin `option.count()` bilan darhol fallback tanlanmasin. `expect(option).to_be_visible(timeout=...)` visible `.hint-item` DOMga kelguncha auto-retry qilsin. Aks holda qidiruv javobi hali kelmagan paytda exact-text fallback tanlanadi; option qatorida ombor/narx turi kabi qo'shimcha matnlar bo'lsa, backend natija qaytargan bo'lsa ham false-negative timeout yuz beradi (2026-07-22 order product trace bilan tasdiqlangan).
- Radio button ustida label span tursa `label:has(input[value="..."])` orqali click qilinadi (force=True ishlamaydi — Angular ng-model update bo'lmaydi).
- Shared helper: `report_helpers.select_b_input_option(page, b_input_name, option, search_text=None)`.

### UI Select
Tags: ui-select, locator, dropdown
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
- `BasePage.multiselect` parametrlari `BasePage.b_input` uslubida: `label`/`name` fieldni topadi, `value` tanlaydi, `expect_value` faqat selected chipni tekshiradi, `return_value=True` tanlangan chip matnlarini list qilib qaytaradi, `clear=True` barcha chiplarni tozalaydi.
- Testda auto-selected qiymatni tekshirish uchun locatorni olib alohida `base.text(..., root=field)` yozilmaydi; `base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)` ishlatiladi.
- `value` va `expect_value` bitta string yoki bir nechta qiymat uchun list/tuple qabul qiladi. `label` va `name` birga berilmaydi.

### Masked Date/Amount Inputs
Tags: input, mask, date, amount
- Qoida: date/amount mask inputlarda qiymatni almashtirishdan oldin focus + `ControlOrMeta+A` + `Backspace` qiling; faqat `fill(new_value)` ba'zan eski invalid qiymatga append qiladi.
- Testda ishlatish: label/text helperlar inputni label orqali topsin, keyin clear-and-fill patternini bajarsin va `Tab` bilan mask formatini yakunlasin.
- `BasePage.date_picker(..., auto_fill=True)` date inputda hisoblangan target sana avvaldan turganini tekshiradi va kalendarni ochmaydi; default `False` real datepicker kunini tanlaydi.
- `date_picker()` boshqa oyga o'tishda calendar `data-day` qiymatlarini markaziy `resolve_date()` bilan parse qiladi; `BasePage` ichida import qilinmagan `datetime.strptime()` ishlatilmaydi. Bu branch target kun joriy calendar viewda bo'lmagandagina bajariladi.
- Dinamik sana matni uchun `BasePage.date(...)` ishlatiladi: today/yesterday/tomorrow, first_day/month_start, last_day/month_end, `days=±N`, common input formatlar va `date_format` output formatini qo'llaydi. Hisob Asia/Tashkent sanasiga tayangan; `conftest.py`ga date fixture qo'shilmaydi.

### Biruni Confirm
Tags: biruni, confirm, modal
- Preferred: majburiy confirm uchun `BasePage.confirm_biruni(expected_text=...)`, faqat ayrim holatda chiqadigan confirm uchun `BasePage.confirm_biruni_if_visible(expected_text=...)` ishlatiladi. Optional helper modal ko'rinmasa `False`, tasdiqlasa `True` qaytaradi.
- Pattern:
  - `confirm = page.get_by_role("dialog").filter(has=page.get_by_role("button", name="да"))`
  - `expect(confirm).to_be_visible()`
  - `confirm.get_by_role("button", name="да").click()`
  - `confirm.wait_for(state="hidden")`
- Qoida: `да` button har doim confirm modal ichida scope qilinadi.
- Order status o'zgartirish confirm matni: `Изменить статус на {status}?` (masalan `Изменить статус на Отменен?`). Ilgari `Изменить на {status}?` edi — 2026-06-21 da ilova matni o'zgargan, `confirm_biruni` `to_contain_text` mosligi buzilgan (modal ochiq qolib ketgan ko'rinadi). `flow_order_list` shu yangi matnga moslangan.

### Biruni Error
Tags: biruni, error, modal
Status: live-ui-confirmed
Verified: 2026-08-04
Source: user; live UI `*/anor/mr/product/inventory+add`;
`tests/smoke/test_forms/form_monitor.py`
- Legacy formadagi odatiy blocking backend/business xato modali
  `#biruniAlert.modal.fade.show[role="dialog"]`. Ko'rinadigan strukturasi:
  `Ошибка` headingi, `.text-danger` xato matni, `button.close` va textli
  `Закрыть` tugmasi. Jonli misol: mavjud `<product_code>` bilan TMC saqlashda
  duplicate-code xatosi shu modalda chiqdi.
- Extended varianti `#biruniAlertExtended[role="dialog"]`; oddiy va extended
  modal DOMda bir vaqtda mavjud bo'lishi mumkin, lekin faqat `.show`/`:visible`
  holati xato signali hisoblanadi. Extended alertni tekshirib yopish uchun
  `BasePage.close_biruni_alert(*expected_text)` ishlatiladi; unda ba'zan
  `Закрыть` textli button yo'q.
- Barcha forma xatolari aynan shu modal ko'rinishida chiqmaydi. Legacy formani
  saqlash/tranzaksiya backend xatolari ko'pincha Biruni modalida; forma
  ochilishidagi vaqtinchalik xabar `[role="alert"]`, inline validatsiya
  `.alert-danger`, A2 xatolari esa boshqa error komponentida ko'rinishi mumkin.
- Forms monitor `#biruniAlertExtended:visible`, `#biruniAlert:visible`,
  `[role="alert"]:visible` va `.alert-danger:visible` signallarini tekshiradi;
  ulardan biri target sahifada ko'rinsa natija `OPENED_WITH_DEFECT /`
  `APPLICATION_ERROR` bo'ladi. Faqat formani ochadigan smoke test save-time
  modalni o'zi hosil qilmaydi; modal formani ochishda paydo bo'lsa yoki case
  tegishli actionni bajarsa aniqlanadi.
- Modal yopilmasa menu/list clicklari intercept bo'lishi mumkin. Save/transition
  debugda kutilgan list/view ochilmasa joriy heading va URL bilan birga ikkala
  Biruni alertning visible matnini tekshir.

### Alert Kutish — `is_visible(timeout=...)` O'lik Parametr
Tags: locator, alert, timeout, is_visible, wait_for, forms-monitor
Status: code-confirmed
Verified: 2026-08-05
Source: Playwright API docstring; real Chromium tekshiruvi;
`tests/smoke/test_forms/form_monitor.py`
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
  tugagan zahoti boshlandi, `capture_form_state` esa alert kutishiga qadar yana
  URL/title/content o'qiydi — ya'ni monitorning haqiqiy zaxirasi shundan
  kattaroq. Maksimum **birinchi (cold) navigatsiyada** chiqdi; keyingi
  takrorlarda 20–30 ms.
- Shu sabab `ALERT_WAIT_MS = 1200` **o'zgartirilmadi**. 700 ms ga tushirish
  taklifi bor edi (avvalgi "300–500 ms" raqami kuzatuvdan, o'lchovdan emas
  edi) — o'lchov uni **rad etdi**: cold-start 849 ms o'tkazib yuborilardi va
  natija yolg'on PASSED bo'lardi. Local 849 ms, CI sekinroq, 1200 ms zaxirasi
  ~1.4×.
- Bir nechta alert selektorini kutish kerak bo'lsa, ularni **vergul bilan bitta
  locatorga birlashtir**:
  `page.locator(", ".join(ALERT_SELECTORS)).first.wait_for(state="visible", timeout=...)`.
  Alert chiqsa darhol qaytadi, chiqmasa bir marta timeout to'laydi. Har
  selektorni alohida kutish 6 × timeout ga tushadi.
- Real Chromium'da tekshirildi: `:visible` pseudo-klassi vergulli listda
  ishlaydi — `display:none` element sanalmaydi, ko'rinadigani topiladi.
- Narxi: sog'lom sahifaga bir marta to'liq timeout. `ALERT_WAIT_MS = 1200` bilan
  Forms-03 (38 forma) 146.78 s → 184.10 s, ya'ni **+0.98 s har formaga**.
- Diqqat: yaroqsiz selektor `PlaywrightError` beradi va u jim yutiladi —
  natija "alert yo'q" bilan **bir xil** ko'rinadi. Selektor ro'yxati o'zgarsa
  real brauzerda tekshir.
- Loader (`.block-ui-overlay`, `.smt-skeleton`, `[aria-busy='true']`) uchun
  lahzalik surat **to'g'ri** — u yerda kutish noto'g'ri bo'lardi.

### A2 sahifada `pageerror` chiqmaydi (2026-08-05)
Tags: a2, angular, pageerror, js-error, forms-monitor, listener
Status: trace-confirmed
Verified: 2026-08-05
Source: real Chromium probe — legacy va A2 formalarida 4 kanal;
`tests/smoke/test_forms/form_monitor.py`
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
- Amaliy natija: `FormMonitor` ning `JS_ERROR` tekshiruvi **119 legacy formada**
  ishlaydi (sun'iy injektsiya bilan tasdiqlangan), **28 A2 formada** esa
  hech narsa ko'rmaydi. A2 da "0 JS xato" — sog'lom degani **emas**.
- **Yechim (2026-08-05 da qilindi va isbotlandi):** `page.add_init_script` bilan
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

  Kod: `tests/smoke/test_forms/form_monitor.py` — `CAPTURE_JS_ERROR_SCRIPT`.

### Capture-faza `error` listeneri resurs xatosini ham beradi (2026-08-05)
Tags: a2, pageerror, js-error, init-script, resource-error, forms-monitor
Status: trace-confirmed
Verified: 2026-08-05
Source: real Chromium run — Forms-02, 21 A2 forma;
`tests/smoke/test_forms/form_monitor.py`
- Qoida: `window.addEventListener("error", ..., true)` **faqat JS exception
  emas**, `img`/`script`/`link` yuklanmaganda chiqadigan resurs xatosini ham
  beradi. `page.on("pageerror")` bunday eventni **hech qachon** bermaydi,
  shuning uchun capture kanaliga o'tishda bu yangi, kutilmagan signal turi.
- Ajratish: resurs xatosida `event.target !== window` va `event.target.tagName`
  mavjud; JS exceptionda `event.target === window` va `event.message` bor.
- Nega muhim: ajratmasdan qattiqlashtirilsa **buzuq rasm formani qizil qiladi**.
  Real misol — `Plugin Marketplace` (`biruni/plg/plugin_catalog`) sahifasida
  `IMG .../api/b/biruni/m:load_image_v2` yuklanmaydi. Ustiga bu signal network
  kanalidagi `404 m:load_image_v2` bilan **aynan bir xil hodisa**, ya'ni
  ikki marta hisoblanardi.
- Diqqat: `String(event.message || event)` yozish resurs xatosida
  **`[object Event]`** beradi — diagnostik qiymati nol. Foydali yorliq:
  `event.message` + `event.filename:event.lineno`, resurs uchun esa
  `target.tagName` + `target.src/href`.
- Diqqat: `typeof window.onerror` bu yerda **yo'l ko'rsatmaydi** — ikkala shell'da
  ham `null` (`typeof null === "object"`, ya'ni "object" javobi handler bor
  degani emas). `window.Zone` ham `undefined` — zone.js sabab emas.
- Diqqat: sun'iy JS xato injektsiyasi bilan test qilganda `setTimeout` ichida
  `throw` legacy'da ishonchli, A2 da esa **hech narsa isbotlamaydi** — jim
  natija "xato yo'q" va "kanal ko'r" uchun bir xil ko'rinadi.

### List va Grid Setting
Tags: list, grid, search, column
- Qoida: Smartup list formalarida kerakli ustun yoki search field ko'rinmasa, grid setting orqali ustun va shu ustun bo'yicha searchni yoqish mumkin.
- Bu pattern barcha listlarda umumiy.
- Testda ishlatish: qo'shilgan elementni listda topish uchun kerakli ustun/search yo'q bo'lsa, avval grid settingdan yoq.
- Qoida: Listda qatorlar ko'p bo'lsa grid faqat birinchi sahifadagi qatorlarni render qiladi; yaratilgan entity 50 tadan keyin bo'lsa `b-grid` bo'yicha to'g'ridan-to'g'ri `to_contain_text` fail qiladi. List assertdan oldin global `Поиск`ga unique code/name yozib `Enter` bos.

### Umumiy CRUD Sahifa Tuzilishi
Tags: list, add, edit, view, grid, loader
- Qoida: Smartup sahifalarining ko'pi bir xil CRUD patternida: list tepasida search/filter/list-exchange/setting controls, pastida `b-grid` rowlari; row tanlanganda `Создать`/`Просмотр`/`Изменить` kabi action buttonlar ishlaydi.
- Qoida: add va edit formalar odatda bir xil forma tuzilishiga ega; qo'shilgan element listdan topilib view formadan tekshiriladi.
- Qoida: tizimdagi blocking loader/spinner umumiy va sahifa/forma o'tishlarida kech yuklanishi mumkin; list/add/view/edit action helperlari loader yo'qolishini markaziy kutishi kerak.
- Testda ishlatish: yangi testlarda list search, grid row select, action button click, save transition, view assert va close kabi qadamlar lokal takror yozilmasin — umumiy list/form/view helper yoki flow orqali yuritilsin.

### Screenshot Arxivi
Tags: screenshot, debug, url
- Screenshotlar kelajakdagi visual regression/baseline taqqoslashga tayyor formatda saqlansin.
- Saqlash joylari:
  - `skills/smartup-guide/references/forms/screenshots/<form-slug>/` — forma bo'yicha doimiy screenshot va metadata arxivi.
  - `test-results/allure-results/` — faqat pytest/Allure failure attachment outputi; forma bilim arxivi sifatida ishlatilmaydi.
  - `test-results/screens/smartup/` — ishlatilmasin, chunki run output tozalanishi mumkin va skill bilim manbasi emas.
- Naming: `<form-slug>__<state>__<viewport>__<stable-id>.png`.
  - Misol: `contract-view__default__desktop-1440x783__current.png`
  - URL asosida saqlash kerak bo'lsa: `<form-slug>__url-<sanitized-url-hash>__<viewport>.png`
- Metadata: har screenshot bilan bir xil arxiv papkasida `.json` saqlansin:
  - URL
  - form slug
  - state
  - viewport
  - parametrik entity patterni (`product-pw{code}` kabi), real session qiymati emas
  - created_at
  - browser
  - dynamic areas yoki mask kerak bo'lishi mumkin bo'lgan joylar
- Qoida: yangi formaga kirilganda yoki URL/form state sezilarli o'zgarganda
  skill arxividagi screenshotni yangila; bir xil form/state/viewport uchun
  vizual farqsiz dublikat yaratma.
- Retention: joriy locator/debug uchun kerakli current screenshot va muhim
  historical evidence saqlanadi. Eski artefaktni o'chirishdan oldin dossier
  linklari va tarixiy qiymatini tekshir; avtomatik bulk delete qilma.
- Debug tartibi: muammo chiqqanda avval mavjud screenshotlardan qaraladi; kerakli screen yo'q bo'lsa UI ochilib yangi screenshot olinadi.
- Release visual check qo'shilganda current screenshot baseline bilan solishtiriladi; shuning uchun screenshotlar random modal/loader/dropdown ochiq holda emas, barqaror UI state’da olinishi kerak.

### Umumiy Forma Helper'lari (DRY)
Tags: locator, form, helper, setup
- Qayerda: `utils/base_page.py`.
- Kontekst: `company` formasi Angular `smt-control` strukturada; boshqa setup/report/biznes formalar eski Biruni/AngularJS holida. Umumiy UI primitive'lar `BasePage` ichida turadi.
- Joylashuv: navigatsiya/page state va label/ng-model asosidagi universal helperlar (`navigate_to`, `expect_page`, `switch_filial`, `input`, `b_input`, `ui_select`, `checkbox`, `radio`, `text`, `form_view`, `close_biruni_alert`) `utils/base_page.py` ichida tursin; ular biznes flow emas, umumiy UI primitive.
- Chegara: faqat bitta testga kerak bo'lgan biznes/helper logika `BasePage` ga chiqmaydi; o'sha test faylida `_...` local helper bo'lib qoladi.
- Qoida: `navigate_to`, `expect_page`, `switch_filial` uchun alohida wrapper import qilinmaydi; avval `base = BasePage(page)` qilinadi, keyin `base.navigate_to(...)`, `base.expect_page(...)`, `base.switch_filial(...)` ishlatiladi. `flow_navigate.py` faqat maxsus `navigate_to_a2` kabi alohida flowlar uchun qoladi.
- Qoida: ng-model asosidagi forma amallari uchun yangi helper yozilmasin — text input/textarea uchun `base.input(ng_model="d.x", value=...)`, b-input uchun `base.b_input(ng_model="d.x", value=...)` (label ishonchsiz bo'lganda), checkbox/switch uchun `base.checkbox(...)`, sahifa/view matn tekshiruvi uchun `base.text(...)` ishlatiladi. `text` default `root="b-page"` ishlatadi; kerak bo'lsa `root` sifatida selector yoki modal locator (`.modal.show`) beriladi — alohida `_modal_*` variant kerak emas.
- Qoida: **oddiy text input bilan ishlashda yagona universal funksiya — `BasePage.input(...)`** (`checkbox()` kabi pattern). Topish strategiyalari (faqat bittasi): `label="Код"` (asosiy), `ng_model="d.code"` (label ishonchsiz bo'lsa, masalan label DOMda inputdan keyin kelsa), `placeholder="Поиск"`, `locator` (positional, tayyor selector). Amal: `value=...` (clear+fill), `expect_value=...` (assert; value berilsa default expect_value=value), `return_value=True` (string), `press_tab=True`, `index=`, `root=`. `first`/`nth` locatorlar test ichida qolmasin.
- Qoida: view sahifasidagi `label + .form-view` yoki order viewdagi exact `<t>` labelga bog'langan `../../span` qiymati readonly input emas; bunday qiymat `BasePage.form_view(label=..., expect_value=..., return_value=..., index=..., root=...)` bilan tekshiriladi. `BasePage.input(...)` faqat real `input`/`textarea` uchun qoladi.
- Qoida: label konteyner qidirishda avval eng yaqin `col`/`col-*` konteyneri olinadi, keyin `input-group`, `form-group`, `form-row`, `row`. Sabab: eski formalarda bir `form-group` ichida ikkita field turishi mumkin (`Код` + `Порядковый номер`, `Название` + `Код акции`, `Дата начала` + `Срок действия`); `form-group`ni birinchi olish noto'g'ri birinchi inputni tanlaydi.
- Qoida: labeldan field topishda keng card/col ichidagi birinchi inputni olish yetarli emas; label elementidan keyingi birinchi mos field (`input`/`textarea`/`b-input`/checkbox) target qilinsin. Room add formasida `Название` keng konteyner orqali `Код` inputini qayta to'ldirib yuborgani 2026-06-26 da tasdiqlangan.
- Qoida: `id="focusser-*"` inputlar real fill qilinadigan field emas, ular toggle/radio/focus uchun ichki elementlar. `input` bunday inputlarni chetlab o'tsin.
- Qoida: **forma checkbox/switch — `BasePage.checkbox(...)`; grid checkbox — `BasePage.grid(checkbox="row"/"all")`** (rollar 2026-07-10 da ajratildi). `checkbox()` endi faqat page/forma checkbox+switch bilan ishlaydi. Topish strategiyalari (faqat bittasi): `label="НДС"` (asosiy), `ng_model="d.vat_enabled"`, `locator` (positional). Amal: `checked=True/False` (idempotent set+assert), `expect_checked=` (faqat assert), `return_value=True` (bool), `index=`, `root=` (modal locator). Grid'ga oid eski `check_all`/`first_visible`/`grid_name` parametrlari **`checkbox()` dan olib tashlandi** — grid checkbox endi `grid(checkbox=...)` orqali. Fizik click ikkovi uchun umumiy private `_toggle_checkbox(cb, checked)` da (opacity:0 cascade). Eski `set_checkbox`, `set_checkall`, `click_first_visible_checkbox`, `switch_by_label` va `flow_form.set_checkbox` ham olib tashlangan (2026-06-29).
- Qoida: **forma radio — `BasePage.radio(label, expect_checked=True/False)`**. U nested `<label class="radio"><input type="radio">...` strukturadan radio inputni label orqali topib, tanlangan holatini tekshiradi; raw `get_by_label(...).to_be_checked()` testda yozilmaydi.
- DOM fakti (2026-06-29 `filial+add` da jonli): Smartup form switch tuzilishi `<label class="switch"> <input type=checkbox opacity:0 ng-model=...> <span>holat matni</span></label>`. `<input>` ko'rinmas (raw click overlay tomonidan ushlanishi mumkin) — shuning uchun `checkbox()` click'ni DOIM ko'rinadigan `label`/grid-cell/wrapper ustiga cascade qiladi (funksiya ichida). Modalda `label.checkbox`. `ng-true-value`/`ng-false-value` string ('Y'/'N', 'A'/'P') bo'lsa ham `is_checked()` to'g'ri bool qaytaradi. Switch ichidagi `<span>` matni holatga qarab o'zgaradi — switch'ni **field label** orqali topish kerak, span matni orqali emas.
- **Switch-label wrapper resolution bug + fix (MCP, 2026-07-02):**
  counterparty toggle'lari `<label class="checkbox"><input type=checkbox
  ng-model=d.is_client><t>Клиент</t></label>` ko'rinishida. Eski
  `ancestor::label[1]` self'ni hisobga olmagani uchun helper keyingi checkboxga
  siljigan va bir xil noto'g'ri elementdagi assertion bugni yashirgan.
  **Tuzatish:** `(ancestor-or-self::label[1]//input[@type='checkbox'])[1]`;
  wrapping label bo'lmasa `following::` fallback saqlanadi.
- Qoida: **grid checkbox — `base.grid(checkbox="row"/"all")`** (2026-07-10). `"row"` → matn bo'yicha topilgan qator checkbox'i; `"all"` → ko'rinadigan grid tepasidagi select-all (`input[bcheckall]`, fallback birinchi checkbox), bu holda `text` kerak emas. Migratsiya: `checkbox(check_all=True)` → `grid(checkbox="all")`; ma'lum grid uchun `grid(checkbox="all", root='b-grid[name="..."]')`; `checkbox(first_visible=True)` ham `grid(checkbox="all")` (grid'ning 1-checkbox'i doim select-all).
- Qoida: **bo'sh grid assertioni — `base.grid(state="empty", root='b-grid[name="..."]')`**. Helper ko'rinadigan grid ichidagi aniq `"нет данных"` matnini auto-retry bilan kutadi va grid locatorini qaytaradi. Branch kerak bo'lsa `return_bool=True` qo'shiladi: bo'sh grid uchun `True`, ma'lumotli grid uchun `False`.
- `grid(..., return_bool=True)` bir martalik holatni o'qiydi; assertion rejimi targetni auto-retry qiladi, lekin ikkalasi ham tab/filter transitionining boshlangan-tugaganini isbotlamaydi. Gridni almashtiruvchi actiondan keyin avval `base.wait_for_loader()`, keyin grid helper chaqirilsin; aks holda oldingi grid state yangi state bilan bir xil bo'lsa tekshiruv muddatidan oldin o'tishi mumkin.
- Qoida: **grid qatori assertioni — `base.grid("row text", root='b-grid[name="..."]')`**. Helper target `.tbl-row`ni auto-retry bilan kutadi va row locatorini qaytaradi. Conditional Available/Attached flow uchun `base.grid("row text", return_bool=True, root=...)` ishlatiladi; qator ko'rinsa `True`, topilmasa `False` qaytaradi.
- `state="empty"` text/`contains`/click/checkbox bilan, `return_bool=True` esa `contains`/click/checkbox bilan birga berilmaydi; noto'g'ri kombinatsiya `ValueError` beradi.
- `BasePage.grid()` default `remove_spaces=True`: row qidirish va `contains` assertlari oddiy/non-breaking whitespace'ni e'tiborsiz qoldiradi (`"10000"` UI'dagi `"10 000"`ga mos keladi). Whitespace aynan tekshirilishi kerak bo'lsa `remove_spaces=False` beriladi.
- DOM fakti (2026-07-10 MCP `red_test` user attach form jonli): **(1)** attach/tabli sahifada **8 ta `b-grid`, faqat 1 tasi ko'rinadi** — DOM'dagi birinchisi (`user_audits`) yashirin; shuning uchun `grid(checkbox="all")` `.filter(visible=True).first` ishlatadi (oddiy `b-grid.first` noto'g'ri yashirin grid'ni oladi). **(2)** Grid'ning birinchi checkbox'i = `input[bcheckall]` (select-all), `.tbl-header-cell.tbl-checkbox-cell` ichida; row checkbox `.tbl-checkbox-cell` ichida — ikkovi ham `opacity:0`. **(3)** Header katak baland (87px) va checkbox uning **tepasida** turadi: katak markaziga (`y=height/2`) oddiy `.click()` checkbox'ni chetlab o'tib **toggle QILMAYDI** (MCP'da isbotlangan). Ishlaydigan usul — `label.x + min(10, label.w/2)`, `cb.y + cb.h/2` koordinatasiga `page.mouse.click`; shuning uchun `_toggle_checkbox` label ko'rinmas (h:0) bo'lganda shu koordinatali click'ni ishlatadi. Tasdiq: yangi `grid(checkbox="all")` `form_table` grid'ni tanlab bcheckall'ni belgiladi va 50 qator select bo'ldi.
- Testda ishlatish: input qiymatini tekshirishda `input_value(...) != x` deb raise qilish o'rniga `base.input(label="Код", expect_value=x)` ishlatilsin — auto-retry bo'ladi.

### BasePage Semantic Click Helper
Tags: locator, helper, button, tab
Status: code-confirmed
Verified: 2026-07-31
Source: user; `utils/base_page.py:64`; `tests/unit/test_base_page_click.py:61`
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
Source: user; `utils/base_page.py`; `tests/smoke/test_setup/test_13_price_type_uzb.py`
- Qayerda: legacy AngularJS/Biruni add/edit formadan list yoki viewga saqlab
  o'tish.
- Qoida: birlashtirilgan save+heading helperi ishlatilmaydi. Test
  `base.click(name="Сохранить")` (exact kerak bo'lsa `exact=True`), confirm majburiy bo'lsa
  `base.confirm_biruni(...)`, so'ng `base.expect_page(heading=..., url=...)`
  amallarini ochiq yozadi.
- Testda ishlatish: `expect_page(heading=...)` target heading bilan birga
  visible loader overlay yo'qolishini ham kutadi; shu page transitionda
  alohida `base.wait_for_loader()` takrorlanmaydi.

### Order Wizard Save Tugmasi — Exact Role Name Mos Kelmaydi
Tags: order, locator, error
- Qayerda: `order+add`/`order+edit` wizard, 3-step (Завершение). Tugma: `#anor279-button-next_step` — step 1-2 da "Далее", oxirgi stepda "Сохранить" ko'rsatadi.
- Qoida: tugma ichida `<i class="fa fa-save">` ikonka bor; FontAwesome `::before` glyph accessible name'ga qo'shiladi, shuning uchun `get_by_role("button", name="Сохранить", exact=True)` 0 ta element topadi ("element(s) not found"). Exact'siz (substring) qidiruv topadi.
- Testda ishlatish: order final page save uchun
  `base.click(name="Сохранить")` → `base.confirm_biruni(...)` →
  `base.expect_page(...)` ishlatilsin. Oddiy toolbar save tugmalari
  (setup/contract formalari, `b-toolbar` ichidagi matnli tugma) ikonkasiz —
  ularda `exact=True`.

## Loyiha Xususiyatlari

### Legacy Navbar → Forma Navigatsiyasi

- Umumiy primitive `BasePage.navigate_to_form(...)`: `navbar_tab → menu_column
  → menu_item → page_links`.
- Bu primitive faqat navigatsiya qiladi. Forma ochilganini tasdiqlash chaqiruvchi
  testda alohida bajariladi; URL/title tekshiruvi `navigate_to_form()` ichiga
  yashirilmaydi.
- `BasePage.navigate_to_form()` faqat legacy dashboarddan birinchi A2 formaga
  o'tish uchun. Joriy sahifa A2 bo'lsa keyingi menu navigatsiya
  `AngularBasePage.navigate_to(tab=..., name=...)`, filial almashtirish
  `AngularBasePage.switch_filial(...)`, forma tasdig'i esa
  `AngularBasePage.expect_page(title=..., url=...)` bilan bajariladi.
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
    `utils/base_page.py`
- Parent forma ichidagi bir yoki bir nechta yuqori linklar `page_links`ga
  bosilish tartibida beriladi.
- Foydalanuvchi bergan visual namunalar:
  `forms/screenshots/menu-navigation/menu-navigation__navbar-and-column__1036x448.png`
  va `forms/screenshots/menu-navigation/menu-navigation__page-link__361x131.png`.
