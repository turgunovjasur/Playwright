# Компания (Company) — yaratish va sozlash

## Mundarija

- [Navigatsiya](#navigatsiya)
- [Screenshotlar](#screenshotlar)
- [Company code](#company-code)
- [Forma tuzilmasi](#forma-tuzilmasi-companyform-smt-control-elementlar)
- [Saqlash](#saqlash)
- [Security sozlamalar](#company-viewda-security-sozlamalar-har-doim)
- [Loyiha xususiyatlari](#loyiha-xususiyatlari-tasdiqlangan)
- [Test](#test)

## Navigatsiya

- `CREATE_COMPANY=1` rejimida majburiy `HEAD_ADMIN_EMAIL` /
  `HEAD_ADMIN_PASSWORD` bilan kirish kerak — oddiy user yoki admin emas.
- `run_company` va `test_company_add` boshida mavjud flowlardan foydalanadi: `authorization(page, who="head")`, so'ng `navigate_to(page, tab="Главное", name="Компании")`.
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
- `BasePage.expect_page(url=...)` URL uchun ishlaydi, lekin A2 component mountini
  kutmaydi. Amaldagi `check_unblocked` faqat `heading` branchida va faqat legacy
  `.block-ui-overlay` bo'yicha ishlaydi. Company listda `.smt-skeleton` yo'qolishi
  hamda stabil element (`Создать`, search yoki `.smt-data-row`) alohida kutiladi.
- `BasePage.navigate_to()` va `switch_filial()` eski dashboard shell'dan Company A2
  listga kirishdan oldin ishlaydi. A2 shell ichida esa menyu `role=menu/menuitem`,
  filiallar `role=option` bo'lgan CDK overlay'da; legacy selectorlarni u yerda qayta
  ishlatib bo'lmaydi.

## Screenshotlar

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
  — listda kutilgan search boshqaruvi ko'rinmagan diagnostika holati.
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

## Forma tuzilmasi (`#companyForm`, `smt-control` elementlar)

**Agar company allaqachon mavjud bo'lsa** — qayta yaratilmaydi, to'g'ri view ga o'tiladi va security sozlamalar qo'llanadi.

### Majburiy maydonlar

| Maydon | Qidirish usuli | Qiymat |
|---|---|---|
| Код сервера / Server code | `smt-control` label filter | `autotest{code}` |
| Название / Company name | `smt-control` label filter | `Autotest company {code}` |
| Язык | — | `Русский` (default, tekshiriladi) |

### Company name label o'zgargan
Tags: company, setup, locator, app3, ui-change
- 2026-07-20 arxiv screenshotida company name labeli `Ф.И.О.` bo'lgan.
- 2026-07-27 app3 (`/a2/biruni/md/company_add`) trace va failure screenshotida
  ayni maydon `Название` bo'lib render bo'ldi; forma va `#companyForm` to'liq
  yuklangan, `Код сервера` muvaffaqiyatli to'ldirilgan.
- `Ф.И.О.` exact labelini kutadigan test locator shu UI o'zgarishidan keyin
  element topmaydi; bu sahifa yuklanishi yoki `HEADLESS`/trace muammosi emas.

### Majburiy shablonlar (Шаблоны card)

```
Маркировка → UZ Marking
План счетов → UZ COA
Банки → UZ BANK
```

Select `AngularBasePage.select()` bilan boshqariladi: trigger → CDK overlaydagi
`smt-select-dropdown li` → tashqi sahifa nuqtasini bosib overlay/backdrop yopilishini
kutish.

### Products card

```
"trade" switch → yoqish → barcha TRADE_CHILD_PRODUCTS switchlarni yoqish (17 ta)
```

- Trace'da `trade` `aria-checked=true` bo'lgan zahoti child modullar DOM'da
  mavjud; `app-project-module` ichida `.smt-skeleton` yoki `aria-busy=true`
  chiqmaydi. Shu sabab switchdan keyingi alohida `wait_for_loader()` kerak emas
  va faqat loader appearance probe vaqtini sarflaydi; birinchi child
  `switch(label=...)` modul ko'rinishini o'zi kutadi.

## Saqlash

```
"Сохранить" button → biruni confirm (да) → wait_for_loader(600_000)
→ URL /a2/biruni/md/company_list (timeout 600_000)
→ visible heading "Компании"
→ listning stabil elementi: "Создать" tugmasi yoki grid
```

- A2 `company_list`da ko'rinadigan `Компании` desktop title'i `span`, mobile
  `h1` esa yashirin. Shu sabab semantic heading role qidiradigan legacy
  `BasePage.expect_page(heading=...)` mos emas.
  `AngularBasePage.save_and_expect_page(expected_heading="Компании", ...)`
  ko'rinadigan A2 matnini tekshiradi.
- Save confirm live tasdiqlangan. Confirm yopilgach target list readiness va A2
  error dialog bir vaqtda kutiladi; error chiqsa `Angular save failed` target URL,
  actual URL va UI matni bilan darhol fail qiladi. Shu fail-fast race uchun
  `save_and_expect_page()`da listga xos unikal `ready` (`Создать` button) saqlanadi.
- App3 head companyda UZ template nusxalash vaqtida ichki
  `Подоходный налог` nomi dublikat bo'lsa backend save'ni rad etadi. Bu Angular
  locator xatosi emas, server template data konflikti; screenshot yuqorida.

### Template select matni model selectionni isbotlamaydi
Tags: company, angular, select, validation, save, trace
- 2026-07-23 trace'da `AngularBasePage.select(label="Маркировка",
  value="UZ Marking")` input value assertidan o'tgan, ammo Save paytida
  screenshotda aniq `Маркировка: ДА` toast ko'ringan va confirm ochilmagan.
- Networkda `company_add:save` so'rovi yo'q; Save'dan keyingi
  Marking toast'i hamda confirm ochilmagani client-side flow Marking bosqichida
  to'xtaganini ko'rsatadi. `template-group-161` aynan `Маркировка` controlining
  DOM idsi. Bu dalillar model qiymati nima sababdan qabul qilinmaganini hali
  ko'rsatmaydi; keyingi `confirm_biruni()` timeouti esa birlamchi sabab emas.
- Trace'da `page.mouse.click(1, 1)` faqat `Маркировка` uchun emas,
  `План счетов` va `Банки` selectlaridan keyin ham bajarilgan. Shu trace'ning
  o'zi bu tashqi clickni Marking selection commit bo'lmasligining sababi deb
  isbotlamaydi. Tasdiqlangan fakt: `select()`ning `to_have_value()` tekshiruvi
  faqat display textni tasdiqlagan, Save validatsiyasi esa Marking selectionni
  qabul qilmagan; aniq commit-race sababi alohida reproduksiya bilan tekshiriladi.
- Debugda save clickdan keyingi transient error toast va save network request
  bor-yo'qligi tekshirilsin; oddiy confirm timeouti bilan cheklanilmasin.

## Company viewda security sozlamalar (har doim)

```
Company qatori → Просмотреть → "Безопасность" tab
→ "Ограничение количества одновременных сеансов" → Отключено (MAJBURIY)
→ agar CREATE_COMPANY=1 va DISABLE_LICENSE_POLICY=1:
  "Политика лицензирования" → off
→ alohida Сохранить/confirm kerak emas
```

## Loyiha Xususiyatlari (tasdiqlangan)

### Company View
- Company viewda `Безопасность`/Security tab ichida `Политика лицензирования` radio/switch control bor; company setup runida `--create-company --disable-license-policy` berilsa off qilinadi.
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
- `Создать` bosilgandan keyin `Компания (создание)` headeri `#companyForm`
  mount bo'lishidan oldin ko'rinishi mumkin. Ammo matn bermasdan
  `text(root="#companyForm")` bilan alohida kutish takroriy: keyingi
  `input(label="Код сервера", ...)` tegishli `smt-control` ko'rinishini o'zi kutadi.
- `BasePage.input()`/`b_input()`/`checkbox()`ga `root="app-main-info"` kabi selector string berilganda u avval Locatorga normalizatsiya qilinishi shart; aks holda stringda `.locator()` chaqirilib `AttributeError` chiqadi. Bu barcha field helperlar uchun `BasePage._resolve_root()` orqali bajariladi.
- `Шаблоны` card ichidagi `Маркировка` inputidan `UZ Marking` optioni tanlanadi; company setupda `План счетов=UZ COA`, `Банки=UZ BANK`, `Маркировка=UZ Marking` shablonlari majburiy.
- A2 `Язык`, `Маркировка`, `План счетов` va `Банки` control'lari legacy
  `b-input` emas: `smt-control` ichida `smt-select-trigger` va oddiy text input
  bor. Shu sabab ularga `BasePage.b_input()` ishlatilsa
  `Field container not found ... (target=b-input)` chiqadi.
- `Язык` boshlang'ich holatda `Русский` qiymati bilan to'ldirilgan; uni qayta
  tanlash shart emas, scoped input value bilan tekshirish yetarli.
- Products card headerida markup tartibi `smt-switch` → `span` label. Shu sabab
  labeldan `following::input[type=checkbox]` qidiradigan umumiy
  `BasePage.checkbox(label="trade")` aynan Trade switchini emas, keyingi project
  inputini olishi mumkin. Project va child product switchlari card/row ichida
  labelga scoped `_product_switch()` kabi locator bilan boshqariladi.

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
- Hozirgi `BasePage`dan A2 Company'da ishonchli qayta ishlatiladigan qismlar:
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

## Test

- `tests/smoke/test_setup/test_00_company.py` → `run_company(page, code, save_data)`
- `save_data("company_code", company_code)` — data_store.json ga saqlanadi
- Keyingi `test_01_legal_person` admin authorizationda aynan shu saqlangan
  `company_code`ni login suffix sifatida ishlatadi.
- Legacy dashboarddan A2 listga kirishda mavjud navigation helperlari ishlatiladi;
  A2 form/list/view ichida `AngularBasePage` ishlatiladi.
- `AngularBasePage`da live tasdiqlangan primitivlar: `click`, `tab`, `control`,
  `input`, `select`, `switch`, `checkbox`, `choice`, `text`, `form_view`,
  `wait_for_loader`, `expect_page`, `grid`, `grid_controller`, A2
  `navigate_to`/`switch_filial`, confirm/alert va `save_and_expect_page`.
- Angular form helperlarining default root'i `main`; unique label bilan ishlaganda
  har chaqiruvda `root` berilmaydi. Root faqat bir xil label bir necha card/sectionda
  uchrasa yoki component scope'ini qat'iy cheklash kerak bo'lsa beriladi. A2 shell
  helperlari default `header`, confirm/alert helperlari default `body`dan qidiradi;
  har bir helper o'z operatsiyasiga mos component/text/loader/transition timeoutiga ega.
- Company setup Russian UI bilan ishlaydi; `Просмотреть`, `Безопасность` kabi
  tasdiqlangan button/tab nomlari aniq string va default `exact=True` bilan olinadi.
  Bilingual yoki partial `re.compile(...)` locator ishlatilmaydi.
- Company create idempotent: listda code qidiriladi; mavjud bo'lsa qayta
  yaratilmaydi, view/security flow bajariladi.
- A2 `expect_page()` chaqiruvida heading mavjud bo'lsa doim beriladi: `heading`
  sahifa identifikatsiyasini, `url` route'ni tekshiradi. Keyingi action helperi
  o'z elementini kutsa `ready` takrorlanmaydi; `ready` faqat shu chaqiruvning
  o'zida alohida component readiness yoki save/error race kerak bo'lsa beriladi.
