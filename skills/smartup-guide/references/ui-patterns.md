# UI Patterns

## Qidiruv Kalitlari

Tags: locator, b-input, grid, modal, biruni, screenshot, list

### Locator Tanlash
Tags: locator, angular
- Qoida: Angular `ng-model` locatorlardan iloji boricha qoch.
- Qoida: Yangi testlarda raw CSS/XPath/`ng-model` locator yozma; avval `page.get_by_role(...)`, `page.get_by_text(...)` yoki label/textga tayangan helper ishlat.
- Afzal locatorlar:
  - `BasePage.fill_textbox_by_label(...)`
  - `BasePage.select_b_input_by_label(...)`
  - `BasePage.expect_b_input_value_by_label(...)`
  - label/text asosidagi local yoki umumiy helper
  - `page.get_by_role(...)`
- Sabab: UI Angular migratsiya/yangilanishlarida semantik locatorlar barqarorroq.

### Heading Tekshirish — Ko'p Heading Muammosi
Tags: locator, heading, get_by_role
- `expect(page.get_by_role("heading")).to_contain_text("...")` faqat sahifada bitta ko'rinadigan heading bo'lganda ishonchli (masalan oddiy list/create forma).
- Wizard yoki ko'p bo'limli formalarda bir vaqtda bir nechta ko'rinadigan heading bo'ladi (masalan Акция create: `Акция (создание)`, `Главное`, `Условия`); bunda nomsiz `get_by_role("heading")` bir nechta elementga to'g'ri kelib `to_contain_text` fail bo'ladi.
- Yechim: sarlavhani aniq nom bilan nishonla — `expect(page.get_by_role("heading", name="Акция (создание)")).to_be_visible()` (substring match; `exact=True` ishlatma, list heading'larda ko'pincha oldida icon/probel bo'ladi).

### View (Просмотр) label→value olish — exact match
Tags: locator, order-view, label, xpath
- Order list row action tugmasi hozir `Просмотр`, eski deploymentlarda `Просмотреть`; `flow_order_list(..., view=True)` ikkala variantni regex bilan qabul qiladi va tugmani row ichida scope qiladi.
- `flow_order_view` view sahifasida label→value ni `//t[normalize-space()="{key}"]/../../span` orqali oladi.
- `contains(text(),"{key}")` ISHLATMA: ilova label'larga yangi uzun matn qo'shsa (masalan `Статус` yoniga `Статус заказов, которые более 90 (дней)` tooltip/label qo'shilgan — 2026-06-21), `contains` ikkala `<t>` ga mos kelib strict mode violation beradi. Aniq (`normalize-space()=`) moslik shart.

### Form Field Discovery
Tags: form, discovery, checkbox, switch, radio
- Yangi add/edit forma o'rganilganda faqat `input[type=text]`, `textarea`, `select` va `b-input`larni yig'ish yetarli emas.
- Smartup switchlar ko'pincha styled checkbox sifatida chiqadi; `input[type="checkbox"]`, `input[type="radio"]`, ularning label/group texti, `ng-model`, `checked`, `disabled`, `visible` holati alohida yig'ilsin.
- Switch yoqilgandan keyin yangi required maydon paydo bo'lishi mumkin; masalan filial add’da `НДС` (`d.vat_enabled`) yoqilganda `Ставка НДС (%)` (`d.vat_percent`) majburiy input bo'ladi.
- Formani "full" qilishdan oldin field discovery kamida ikki holatni tekshirsin: default state va switch/checkbox yoqilgandan keyingi state.

### b-input
Tags: b-input, locator
- Qoida: `b-input` tanlash uchun umumiy helper ishlatiladi.
- Helperlar:
  - `BasePage.select_b_input_by_label(label, option_text, clear=False, exact=True)`
  - `BasePage.expect_b_input_value_by_label(label, expected_value)`
- Eslatma: ba'zi input value'lar sahifa textiga kirmaydi; input value assert qilish kerak.

### b-input Server-Search (report group)
Tags: b-input, server-search, hint, clear
- Ba'zi `b-input`lar client-side emas, server-side qidiradi (masalan `price_types`).
- Placeholder `"Поиск..."` (nuqta bilan) yoki `"Поиск"` bo'lishi mumkin — locator sifatida `b_input.locator("input[placeholder]").first` ishlatiladi.
- Allaqachon tanlangan qiymat bo'lsa: X tugmasi `.edit` (Angular `ng-hide`) — `is_visible()` tekshirish kerak, `count() > 0` emas.
- Agar `.edit` ko'rinsa — avval clear qil, keyin yoz; ko'rinmasa — to'g'ri click qil.
- Server-search uchun `press_sequentially(search_text, delay=50)` ishlatiladi (debounce trigger); client-search uchun oddiy `fill()` yetarli.
- Dropdown locator: `b_input.locator(".hint-item").filter(has_text=option).first` — `expect(...).to_be_visible(timeout=30_000)`.
- Radio button ustida label span tursa `label:has(input[value="..."])` orqali click qilinadi (force=True ishlamaydi — Angular ng-model update bo'lmaydi).
- Shared helper: `report_helpers.select_b_input_option(page, b_input_name, option, search_text=None)`.

### Masked Date/Amount Inputs
Tags: input, mask, date, amount
- Qoida: date/amount mask inputlarda qiymatni almashtirishdan oldin focus + `ControlOrMeta+A` + `Backspace` qiling; faqat `fill(new_value)` ba'zan eski invalid qiymatga append qiladi.
- Testda ishlatish: label/text helperlar inputni label orqali topsin, keyin clear-and-fill patternini bajarsin va `Tab` bilan mask formatini yakunlasin.

### Biruni Confirm
Tags: biruni, confirm, modal
- Preferred: confirm oynasini `page.get_by_role("dialog")` orqali topib, `да` buttonni shu dialog ichida bosing.
- Pattern:
  - `confirm = page.get_by_role("dialog").filter(has=page.get_by_role("button", name="да"))`
  - `expect(confirm).to_be_visible()`
  - `confirm.get_by_role("button", name="да").click()`
  - `confirm.wait_for(state="hidden")`
- Qoida: `да` button har doim confirm modal ichida scope qilinadi.
- Order status o'zgartirish confirm matni: `Изменить статус на {status}?` (masalan `Изменить статус на Отменен?`). Ilgari `Изменить на {status}?` edi — 2026-06-21 da ilova matni o'zgargan, `confirm_biruni` `to_contain_text` mosligi buzilgan (modal ochiq qolib ketgan ko'rinadi). `flow_order_list` shu yangi matnga moslangan.

### Biruni Error
Tags: biruni, error, modal
- Selector: `#biruniAlertExtended`.
- Close button: `#biruniAlertExtended button.close`.
- Qoida: ba'zan `Закрыть` textli button yo'q.
- Qoida: Modal yopilmasa menu/list clicklari intercept bo'lishi mumkin.
- Save/transition debug: `Сохранить` bosilgandan keyin list/view heading kutishdan oldin umumiy Biruni error modal tekshirilsin; aks holda haqiqiy xato add/edit formdagi save error bo'lsa ham test keyingi list/viewda timeout bo'lgandek ko'rinadi.
- Testda ishlatish: save helper xabari aralash formatda `Before page`, `Action`, `Expected`, `Actual`, `UI error`, `Location hint` maydonlarini chiqarsin.

### List va Grid Setting
Tags: list, grid, search, column
- Qoida: Smartup list formalarida kerakli ustun yoki search field ko'rinmasa, grid setting orqali ustun va shu ustun bo'yicha searchni yoqish mumkin.
- Bu pattern barcha listlarda umumiy.
- Testda ishlatish: qo'shilgan elementni listda topish uchun kerakli ustun/search yo'q bo'lsa, avval grid settingdan yoq.
- Qoida: Listda qatorlar ko'p bo'lsa grid faqat birinchi sahifadagi qatorlarni render qiladi; yaratilgan entity 50 tadan keyin bo'lsa `b-grid` bo'yicha to'g'ridan-to'g'ri `to_contain_text` fail qiladi. List assertdan oldin global `Поиск`ga unique code/name yozib `Enter` bos.

### Screenshot Arxivi
Tags: screenshot, debug, url
- Screenshotlar kelajakdagi visual regression/baseline taqqoslashga tayyor formatda saqlansin.
- Saqlash joylari:
  - `skills/smartup-guide/references/forms/screenshots/<form-slug>/` — forma bo'yicha doimiy screenshot va metadata arxivi.
  - `test-results/allure-results/` — faqat pytest/Allure failure attachment outputi; forma bilim arxivi sifatida ishlatilmaydi.
  - `test-results/screens/smartup/` — ishlatilmasin, chunki run output tozalanishi mumkin va skill bilim manbasi emas.
- Naming: `<form-slug>__<state>__<viewport>__<stable-id>.png`.
  - Misol: `contract-view__default__desktop-1440x783__contract_code_4986.png`
  - URL asosida saqlash kerak bo'lsa: `<form-slug>__url-<sanitized-url-hash>__<viewport>.png`
- Metadata: har screenshot bilan bir xil arxiv papkasida `.json` saqlansin:
  - URL
  - form slug
  - state
  - viewport
  - code/session id
  - entity id/code/name
  - created_at
  - browser
  - dynamic areas yoki mask kerak bo'lishi mumkin bo'lgan joylar
- Qoida: yangi formaga kirilganda yoki URL/form state sezilarli o'zgarganda skill arxividagi screenshotni yangilab bor.
- Debug tartibi: muammo chiqqanda avval mavjud screenshotlardan qaraladi; kerakli screen yo'q bo'lsa UI ochilib yangi screenshot olinadi.
- Release visual check qo'shilganda current screenshot baseline bilan solishtiriladi; shuning uchun screenshotlar random modal/loader/dropdown ochiq holda emas, barqaror UI state’da olinishi kerak.

### Umumiy Forma Helper'lari (DRY)
Tags: locator, form, helper, setup
- Qayerda: `tests/smoke/flows/flow_form.py` va `utils/base_page.py`.
- Qoida: ng-model asosidagi forma amallari uchun yangi helper yozilmasin — `flow_form.py` dagi tayyorlari ishlatilsin: `fill_input`, `fill_textarea`, `set_checkbox`, `select_b_input_by_search`, `select_tashkent_region`, `assert_visible_page_text`. `root` sifatida `page` ham, modal locator (`.modal.show`) ham beriladi — alohida `_modal_*` variant kerak emas.
- Qoida: label matni orqali input/switch bilan ishlash `BasePage` metodlari orqali: `input_by_label_text`, `fill_input_by_label_text`, `input_value_by_label_text`, `set_switch_by_label_text`, `switch_checkbox_by_label_text`, `switch_checked_by_label_text`.
- Testda ishlatish: input qiymatini tekshirishda `input_value(...) != x` deb raise qilish o'rniga `expect(input_by_label_text(...)).to_have_value(x)` ishlatilsin — auto-retry bo'ladi.

### Order Wizard Save Tugmasi — Exact Role Name Mos Kelmaydi
Tags: order, locator, error
- Qayerda: `order+add`/`order+edit` wizard, 3-step (Завершение). Tugma: `#anor279-button-next_step` — step 1-2 da "Далее", oxirgi stepda "Сохранить" ko'rsatadi.
- Qoida: tugma ichida `<i class="fa fa-save">` ikonka bor; FontAwesome `::before` glyph accessible name'ga qo'shiladi, shuning uchun `get_by_role("button", name="Сохранить", exact=True)` 0 ta element topadi ("element(s) not found"). Exact'siz (substring) qidiruv topadi.
- Testda ishlatish: order final page save uchun `save_and_expect_heading(..., exact_button=False)` ishlatilsin. Oddiy toolbar save tugmalari (setup/contract formalari, `b-toolbar` ichidagi matnli tugma) ikonkasiz — ularda default `exact_button=True` ishlayveradi.
