# Лицензии — sotib olish va ulash

Litsenziya 2 ta alohida funksiya: `run_buy_license` va `run_attach_license`.

## Skip sharti

Faqat `CREATE_COMPANY=1` va `DISABLE_LICENSE_POLICY=1/true/yes/on` birga
bo'lsa — **ikkala funksiya ham o'tkazib yuboriladi** (Allure attach bilan).
`CREATE_COMPANY=0` bilan `DISABLE_LICENSE_POLICY=1` invalid konfiguratsiya va
pytest startupda xato beradi. Ikkala test ishlatadigan policy tekshiruvi va skip
xabari `tests/smoke/flows/flow_license.py` ichida; test fayllari bir-birining
private helperlarini import qilmaydi.

## run_buy_license — sotib olish

**Standart format (2026-07):** `run_buy_license` **auth qilmaydi** (eski `logout` + `authorization` olib tashlandi — `page` login qilingan deb keladi). `authorization(page, who='admin')` `test_buy_license` wrapper'ida. `switch_filial("Администрирование")` esa `run_` **ichida qoladi**: setup zanjirida bu — `filial-pw{code}` dan `Администрирование` ga o'tuvchi birinchi qadam, chain shunga suyanadi (`run_room` filialga birinchi o'tgani bilan bir xil mantiq). Re-login shart emas — allaqachon login qilingan sessiyada filial switcher orqali o'tiladi (MCP 2026-07 tasdiqlangan).

```
switch_filial("Администрирование")
→ navigate_to(tab="Главное", name="Лицензии")
→ expect_page(heading="Лицензии")
```

### Yangi company uchun activation precondition
Tags: license, company, activation, setup, error
- `CREATE_COMPANY=1` va `DISABLE_LICENSE_POLICY=0` bo'lsa, yangi company license
  flowga kirishdan oldin Company Viewdagi `Активация для лицензии` jarayoni
  bajarilgan bo'lishi shart.
- Activation bajarilmasa navigation baribir `/biruni/kl/license_list` URLiga
  o'tadi, lekin `Лицензии` headingi o'rniga `Ошибка` /
  `Компания не активирована` modali chiqadi. Bu locator, timeout yoki
  `navigate_to()` xatosi emas; server qaytargan business precondition xatosi.
- 2026-07-23 setup runnerda tasdiqlangan screenshot:
  `references/forms/screenshots/license/license__company-not-activated-error__desktop-1440x783.png`.
- `DISABLE_LICENSE_POLICY=1` bo'lsa company setup policy'ni off qiladi va
  `Buy License` / `Attach License` real license flowga kirmaydi; activation
  precondition ham qo'llanmaydi.

**Balans tekshiruvi:** `p.text-success[ng-if="q.balance > 0"]` — 5s timeout bilan `base.text(root=page.locator(...), timeout=5_000)`. MCP live (2026-07-13): selector 1 ta, visible va musbat balans matnini ko'rsatadi. `BasePage.text()` avval root locator visibleligini tekshiradi, keyin (berilsa) matnlarni tekshiradi; shu sabab dinamik balans qiymatini hardcode qilmasdan faqat element ko'rinishini assert qilish mumkin.
- screenshot: `references/forms/screenshots/license/license__list-balance-mcp-20260713__desktop-1440x1000.png`

**Sotib olish form:**
- Покупка link (agar ko'rinmasa)
- Payer: `base.b_input(ng_model="purchase.payer.name", value="AUTOTEST GWS", clear=True)`
- Kontrakt: `base.b_input(ng_model="purchase.contract_name", value="Договор № bn от 01.01.2025", clear=True)`
- Sana: `base.date_picker("Дата начала", date="today")`. MCP live (2026-07-13): label `Дата начала*` shu visible `purchase.begin_date` inputini topadi; Bootstrap calendarida kunlar `data-action="selectDay"` va `data-day="DD.MM.YYYY"` bilan beriladi. `date_picker` aynan shu kunni real click qiladi va input qiymatini tekshiradi.
- `date` parametri: `"today"`, `"first_day"`, `"last_day"` yoki `"DD.MM.YYYY"`.
- screenshot: `references/forms/screenshots/license/license__purchase-datepicker-mcp-20260713__desktop-1440x1000.png`

**Litsenziya qatorlari va OYLIK majburiy qoida (MUHIM, 2026-07 o'rganilgan):**
- `Smartup ERP: Базовый пользователь (Обязательный)` — **majburiy obuna**, `Количество` default 5
- `Smartup ERP: Базовый пользователь ... За пользователя` — oddiy, 1 dona

**Qoida:** date tanlangandan keyin majburiy qator UI'da bo'lsa, default 5 bilan o'sha qator sotib olinadi. U ko'rinmasa oddiy qator tanlanib, `Количество` ga 1 kiritiladi.

### Date tanlangandan keyingi license tanlovi
Tags: license, purchase, datepicker, grid, business-rule
- `base.date_picker("Дата начала", date="today")` dan keyin ro'yxat yangilanadi; qaror `Тип лицензии` ustunidagi UI qatorining ko'rinishiga qarab qilinadi, `Итого лицензий: 0` matniga qarab emas.
- MCP live (2026-07-13): purchase ro'yxati `b-grid` emas, `Тип лицензии` headerli visible HTML `<table>`; shu sabab `base.grid()` bu jadvalga mos emas. Optional presence check uchun `base.text(..., root=purchase_table, timeout=3_000)` ishlatiladi.
- `Smartup ERP: Базовый пользователь (Обязательный)` qatori visible bo'lsa, u birinchi sotib olinadi; `Количество` ustunida default 5 allaqachon tanlangan bo'ladi, qiymatni qayta yozmasdan `Купить` bosiladi.
- Majburiy qator visible bo'lmasa, `Smartup ERP: Базовый пользователь` qatori tanlanadi, `Количество` ga 1 kiritilib sotib olinadi.

Har bir qatorda: miqdor → `Купить` → `Я ознакомился...` → `Да` → wait_for_loader.

**Sotib olgandan keyin `#biruniAlertExtended` (kvitansiya modali):** har bir muvaffaqiyatli xariddan so'ng Smartup natija/kvitansiya modalini (`#biruniAlertExtended`) ochadi. U ochiq qolsa keyingi qadamni (`run_attach_license`ning "Лицензии и документы" bosishi) **bloklaydi** (modal-body pointer eventlarni ushlaydi). Shuning uchun `run_buy_license` `wait_for_loader`dan keyin modal chiqsa uni inline yopadi (5s kutib, chiqmasa o'tkazib yuboradi). Bu **xato modali emas** — muvaffaqiyat kvitansiyasi.

## run_attach_license — foydalanuvchiga ulash

`run_` auth/navigatsiya qilmaydi — Лицензии sahifasida (Администрирование) bo'lish kerak. Setup zanjirida `run_buy_license` shu holatni qoldiradi; standalone uchun `test_attach_license` wrapper `authorization(admin)` + `switch_filial("Администрирование")` + `navigate_to(Лицензии)` qiladi.

**Base funksiyalar (raw locator EMAS):** license moduli standart grid komponentini ishlatadi — `b-grid-controller input[ng-model="o.searchValue"]` + `b-grid .tbl-row` (MCP 2026-07 list sahifasida tasdiqlangan). Shuning uchun:
- qator tanlash: `BasePage.grid("ERP users", click=True)` va `BasePage.grid(f"natural_person-pw{code}", click=True)` (raw `get_by_text(...).click()` EMAS)
- qidiruv: `BasePage.grid_controller(search=f"natural_person-pw{code}", root="b-grid-controller:visible")` — grid_controller o'zi Enter bosib `wait_for_loader` qiladi
- qator: `BasePage.grid(f"natural_person-pw{code}", root='b-grid[name="table"]', click=True)`
- heading: `expect_page(page, heading="Прикрепленные пользователи")`

**MUHIM — 2 ta grid controller (MCP 2026-07 tasdiqlangan):** "Доступные пользователи" (`license_user_list?mode=detached`) sahifasida **2 ta** `b-grid-controller` bor — yashirin (`b-grid[name="table_license"]` uchun, `input[ng-model="o.searchValue"]` **hidden**) va ko'rinadigan (`b-grid[name="table"]` = mavjud userlar). `grid_controller` default `.first` yashiринiga tushib "Locator expected to be visible: hidden" bilan yiqiladi. Shuning uchun `root="b-grid-controller:visible"` (ko'rinadigan search) va `root='b-grid[name="table"]'` (userlar gridi) **majburiy** beriladi. Qatorni `grid(..., click=True)` bilan bosish uni tanlaydi (checkbox) → "Прикрепить" tugmasi chiqadi.

```
"Лицензии и документы" link → b-page "Лицензии и документы"
→ grid("ERP users", click=True) → "Прикрепить пользователей" → heading "Прикрепленные пользователи"
→ agar biriktirilgan bor: checkbox(check_all) → "Открепить" → confirm → "нет данных"
→ "Доступные" → wait_for_loader(120_000)
→ grid_controller(search=..., root="b-grid-controller:visible")
→ grid(..., root='b-grid[name="table"]', click=True) → "Прикрепить" → confirm_biruni() → "Закрыть"
```

**Eslatma:** attach modali (`Прикрепить пользователей`) faqat sotib olingan litsenziya hujjati (`ERP users` qatori) bo'lganda ochiladi — aks holda "Лицензии и документы" ro'yxati "нет данных". To'liq oqim setup zanjirida (test_12) green: `run_buy_license` → `run_attach_license` (MCP + chain 2026-07 tasdiqlangan).

## Muhim

- `run_attach_license` `run_buy_license` bilan ketma-ket chaqiriladi (runner'da)
- wait_for_loader timeout = **120_000** (2 min) — litsenziya yuklanishi sekin bo'lishi mumkin
- Agar company'da Политика лицензирования o'chirilgan (`company.md`) — bu step skip qilinadi

## Test

- `tests/smoke/test_setup/test_buy_license.py` → `run_buy_license`
- `tests/smoke/test_setup/test_attach_license.py` → `run_attach_license`
