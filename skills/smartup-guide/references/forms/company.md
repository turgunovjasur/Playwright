# Компания (Company) — yaratish va sozlash

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [Navigatsiya](#navigatsiya)
- [Screenshotlar](#screenshotlar)
- [Company code](#company-code)
- [Forma tuzilmasi](#forma-tuzilmasi-companyform-smt-control-elementlar)
- [Saqlash](#saqlash)
- [Security sozlamalar](#company-viewda-security-sozlamalar-har-doim)
- [Loyiha xususiyatlari](#loyiha-xususiyatlari-tasdiqlangan)
- [Test](#test)

## Quick Lookup

### Navigatsiya

- `COMPANY_CODE=1` rejimida majburiy `HEAD_ADMIN_EMAIL` /
  `HEAD_ADMIN_PASSWORD` bilan kirish kerak — oddiy user yoki admin emas.
- Entrypointlar `run_company` va `test_company`; head login uchun
  `authorization(page, who="head")`, navigatsiya uchun page-objectning
  `base.navigate_to(tab="Главное", name="Компании")` metodi ishlatiladi.
- Menyu: **Главное → Компании**.
- Ro'yxatda `Компании` / `Companies` matni breadcrumb/navigation sifatida ko'rinadi;
  A2 `company_list` sahifasida u accessibility `heading` role'iga ega emas.
- DOM responsive: desktopda ko'rinadigan title `<span>`, mobile varianti esa
  `h1.lg:hidden`; shu sabab desktopda `get_by_role("heading")` ko'rinadigan element topmaydi.
- List page tayyorligini `get_by_role("heading")` bilan tekshirmaslik kerak.
  `AngularBasePage.expect_page(heading="Компании", url=...)` headingni visible
  text sifatida, URLni esa route sifatida tekshiradi va Angular loaderni kutadi.
  Keyingi `grid_controller()`/`grid()` helperi o'z componentini kutgani uchun
  oddiy navigation checkda takroriy `ready` berilmaydi.
- Aynan title matnini kutish kerak bo'lsa:
  `page.locator("#main-content").get_by_text("Компании", exact=True).filter(visible=True)`.
- Company A2 listida `AngularBasePage.expect_page()` A2 loaderini kutadi.
  Legacy `BasePage` esa `.block-ui-overlay`ni tekshiradi. Ikkalasida ham
  `check_unblocked=True` bo‘lsa, URL-only chaqiruvda loader tekshiriladi.
- `BasePage.navigate_to()` va `switch_filial()` eski dashboard shell'dan Company A2
  listga kirishdan oldin ishlaydi. A2 shell ichida esa menyu `role=menu/menuitem`,
  filiallar `role=option` bo'lgan CDK overlay'da; legacy selectorlarni u yerda qayta
  ishlatib bo'lmaydi.

## Screenshot Paths

### Screenshotlar

- `references/forms/screenshots/company/company__list-heading-role-missing__desktop-1440x783.png`
  — list to'liq render bo'lgan, lekin `heading` role mavjud bo'lmagan failure holati.
- `references/forms/screenshots/company/company__add-initial__desktop-1440x783.png`
  — yangi company formasining boshlang'ich, maydonlar hali to'ldirilmagan holati.
- `references/forms/screenshots/company/company__add-name-label__desktop-1680x933.png`
  — 2026-07-27 app3 holati: company nomi maydoni `Ф.И.О.` o'rniga `Название`
  labeli bilan render bo'lgan failure diagnostikasi.
- `references/forms/screenshots/company/company__save-duplicate-template-error__desktop-2880x1566.png`
  — formani to'ldirish va confirmdan keyin backend qaytargan duplicate template
  nomi xatosi.
- `references/forms/screenshots/company/company__save-template-selection-not-committed__desktop-800x435.png`
  — inputda `UZ Marking` ko'rinib turgan paytda Save'dan so'ng transient
  `Маркировка: ДА` toast chiqqan holat. Screenshot Marking bilan bog'liq
  validation muammosini ko'rsatadi, lekin model commit bo'lmaganining aniq
  texnik sababini o'zi isbotlamaydi.
- `references/forms/screenshots/company/company__license-activation__desktop-1920x1080.png`
  — company viewdagi license activation holati.
- `references/forms/screenshots/company/company__list-search-missing__desktop-1920x1080.png`
  — qidiruv maydonida qiymat kiritilgan va bitta mos qator ko‘rinadi.
- `references/forms/screenshots/company/company__products-after-trade__desktop-1920x1080.png`
  — `trade` tanlangandan keyingi Products card holati.
- `references/forms/screenshots/company/company__view-selected__desktop-1920x1080.png`
  — listdan company tanlangandan keyingi view holati.

## Company code

```python
company_code = f"autotest{code}".lower()
```

- Generated company code inputda ham, A2 list DOMida ham uzluksiz
  `autotest{code}` ko'rinishida turadi. Search, grid visibility va row click uchun
  qo'shimcha `split_code_match`/whitespace regex emas, bevosita `company_code`
  ishlatiladi.

## Known Locators

### Forma tuzilmasi (`#companyForm`, `smt-control` elementlar)

**Agar company allaqachon mavjud bo'lsa** — qayta yaratilmaydi, to'g'ri view ga o'tiladi va security sozlamalar qo'llanadi.

#### Majburiy maydonlar

| Maydon | Qidirish usuli | Qiymat |
|---|---|---|
| Код сервера / Server code | `smt-control` label filter | `autotest{code}` |
| Название / Company name | `smt-control` label filter | `Autotest company {code}` |
| Язык | — | `Русский` (default, tekshiriladi) |

#### Company name label o'zgargan
Tags: company, setup, locator, app3, ui-change
Status: live-ui-confirmed
Verified: 2026-07-27
Source: `screenshots/company/company__add-name-label__desktop-1680x933.json`; `screenshots/company/company__add-initial__desktop-1440x783.png`
- 2026-07-20 arxiv screenshotida company name labeli `Ф.И.О.` bo'lgan.
- 2026-07-27 app3 (`/a2/biruni/md/company_add`) trace va failure screenshotida
  ayni maydon `Название` bo‘lib render bo‘lgan.
- `Ф.И.О.` exact labelini kutadigan test locator shu UI o'zgarishidan keyin
  element topmaydi; bu sahifa yuklanishi yoki `HEADLESS`/trace muammosi emas.

#### Majburiy shablonlar (Шаблоны card)

```
Маркировка → UZ Marking
План счетов → UZ COA
Банки → UZ BANK
```

Joriy setup shablonlarni `AutoBasePage.b_input(label=..., value=...)` bilan tanlaydi.

#### Products card

```
"trade" switch → yoqish → barcha TRADE_CHILD_PRODUCTS switchlarni yoqish (17 ta)
```

- Trace'da `trade` `aria-checked=true` bo'lgan zahoti child modullar DOM'da
  mavjud; `app-project-module` ichida `.smt-skeleton` yoki `aria-busy=true`
  chiqmaydi. Shu sabab switchdan keyingi alohida `wait_for_loader()` kerak emas
  va faqat loader appearance probe vaqtini sarflaydi; birinchi child
  `switch(label=...)` modul ko'rinishini o'zi kutadi.

## Saqlash

`run_company` `Сохранить`, `confirm_biruni()` va `expect_page(heading="Компании", url="biruni/md/company_list", timeout=COMPANY_SAVE_TIMEOUT)` ketma-ketligini bajaradi. Keyin company kodi bilan qatorni qayta qidiradi.

- App3 head companyda UZ template nusxalash vaqtida ichki
  `Подоходный налог` nomi dublikat bo'lsa backend save'ni rad etadi. Bu Angular
  locator xatosi emas, server template data konflikti; screenshot yuqorida.

### Template select matni model selectionni isbotlamaydi

Tags: company, angular, select, validation, save, trace
Status: trace-confirmed
Verified: 2026-07-23
Source: `screenshots/company/company__save-template-selection-not-committed__desktop-800x435.json` (toast, confirm va request kuzatuvi); shu nomli PNG

- Saqlash paytida selectda `UZ Marking` matni turgan, lekin `Маркировка: ДА` toast chiqqan. Arxiv tavsifida confirm ochilmagani va save so‘rovi yuborilmagani qayd etilgan. Rasmning o‘zi model nega selectionni qabul qilmaganini aniqlamaydi.

## Business Rules

### Company viewda security sozlamalar (har doim)

```
Company qatori → Просмотреть → "Безопасность" tab
→ "Ограничение количества одновременных сеансов" → Отключено (MAJBURIY)
→ agar COMPANY_CODE=1 va DISABLE_LICENSE_POLICY=1:
  "Политика лицензирования" → off
→ alohida Сохранить/confirm kerak emas
```

## Loyiha Xususiyatlari (tasdiqlangan)

### Company View
- Company viewda `Безопасность`/Security tab ichida `Политика лицензирования` radio/switch control bor; company setup runida `--company-code 1 --disable-license-policy` berilsa off qilinadi.
- `Политика лицензирования` control view tabning o'zida interaktiv `smt-switch` sifatida turadi (`id="licensing_policy_enabled"`, `role="switch"`). Uni off qilish uchun global `Изменить` tugmasini bosmaslik kerak, chunki u oddiy `company_edit` formaga olib kiradi va tablar yo'qoladi.
- Policy off qilingan runlarda setup zanjiri `Buy License` va `Attach License`
  qadamlari real license flowga kirmaydi. Policy yoqiq qolsa yangi company uchun
  `Активация для лицензии` majburiy precondition: u bajarilmasa `license_list`
  URLida `Ошибка | Компания не активирована` chiqadi (setup runner,
  2026-07-23 tasdiqlangan).
- Company setup runida `Безопасность`/Security tabdagi `Ограничение количества одновременных сеансов` segmenti doim `Отключено` qilinadi; aks holda keyingi group/user loginlarda `Активные сеансы`/`concurrent_session_list` blokeri chiqadi.
- Concurrent-session segmenti tanlanganda sozlama `company_view$set_concurrent_session_limit`
  so'rovi bilan darhol saqlanadi; confirm dialog ochilmaydi. Security sahifasidagi
  ko'rinadigan `Сохранить` tugmasi password-policy bo'limiga tegishli, shuning
  uchun faqat concurrent-session yoki license-policy sozlamasi o'zgarganda uni
  bosmaslik kerak.

### Company Add

Tags: company, setup, locator, wait
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_00_company.py:48`
- `Компания (создание)` ochilgach `AutoBasePage.input` kod va nomni label orqali to‘ldiradi. `b_input` bilan `Язык` qiymati tekshiriladi va `Маркировка`, `План счетов`, `Банки` shablonlari tanlanadi.
- `trade` va child modullar `app-project-module` ichida `checkbox(label=...)` orqali tanlanadi. Test saqlashdan oldin barcha child modullarning checked holatini qayta tekshiradi.

### Angular DOM va BasePage mosligi (live audit, 2026-07-23)

- Add form: `#companyForm`, `smt-control`, `smt-input`,
  `smt-data-select/smt-select-trigger`, `smt-switch`, `smt-checkbox`.
  Legacy `b-input` va `.ui-select-container` yo'q.
- List: `smt-data-table/smt-table`, `.smt-data-row`,
  `[data-smt-col-key]`, native `input[type=search]`. Legacy `b-grid`,
  `b-grid-controller` va `.tbl-row` yo'q.
- View main info qiymatlari `.form-view` emas; `smt-control` ichidagi
  `input[readonly]`. Security tab switchlari `role=switch`, checkboxlari
  `role=checkbox`, concurrent-session control esa button group.
- A2 list qidiruvida yuklanish `.smt-skeleton` bilan ko'rsatiladi;
  `.block-ui-overlay` yo'q.
- 2026-07-23 auditida legacy `BasePage` bilan tekshirilgan amallar:
  `input()` (native editable/readonly input), `text()` (aniq Angular root bilan),
  `expect_page(url=...)`. `checkbox(locator=<visible role switch>)` ham direct
  locator bilan ishlashi mumkin, lekin `checkbox(label=...)` universal emas.
- Legacy DOMga bog'langan va A2 Company'da ishlamaydigan qismlar:
  `b_input()`, `ui_select()`, `multiselect()`, `form_view()`, `grid()`,
  `grid_controller()`, A2 ichidagi `navigate_to()`/`switch_filial()` va
  `.block-ui-overlay`ga qaraydigan `wait_for_loader()`.
- `date_picker()` va `radio()` Company list/add/viewda mavjud emas; ular bu forma
  bilan tasdiqlanmagan. Save confirm va A2 error dialogi live targeted run bilan
  tasdiqlangan.

## Flow And Tests

### Test

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_00_company.py:16`
- `run_company(page, code)` `AutoBasePage` bilan ishlaydi. Head loginidan keyin `Администрирование → Главное → Компании` yo‘lida kod bo‘yicha qidiradi.
- Company mavjud bo‘lsa yaratilish bosqichi tashlab o‘tiladi. Har ikki holatda view’dagi `Безопасность` bo‘limiga o‘tib concurrent-session va tegishli policy sozlamalarini qo‘llaydi, keyin `company_code`ni saqlaydi. Keyingi Legal Person admin logini shu company kontekstida ishlaydi.

## Known Issues

2026-07-23 trace’da ko‘rinadigan template matni saqlashga yetarli bo‘lmagan. [Template validatsiyasi](#template-select-matni-model-selectionni-isbotlamaydi) bo‘limida toast va confirm belgilarini, [screenshotlar](#screenshotlar) bo‘limida backend duplicate-template xatosining alohida holatini ko‘ring.
