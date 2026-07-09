# Лицензии — sotib olish va ulash

Litsenziya 2 ta alohida funksiya: `run_buy_license` va `run_attach_license`.

## Skip sharti

`DISABLE_LICENSE_POLICY` env var = `1/true/yes/on` bo'lsa — **ikkala funksiya ham o'tkazib yuboriladi** (allure attach bilan). `--disable-license-policy` flag berilganda shu env set qilinadi.

## run_buy_license — sotib olish

**Standart format (2026-07):** `run_buy_license` **auth qilmaydi** (eski `logout` + `authorization` olib tashlandi — `page` login qilingan deb keladi). `authorization(page, who='admin')` `test_buy_license` wrapper'ida. `switch_filial("Администрирование")` esa `run_` **ichida qoladi**: setup zanjirida bu — `filial-pw{code}` dan `Администрирование` ga o'tuvchi birinchi qadam, chain shunga suyanadi (`run_room` filialga birinchi o'tgani bilan bir xil mantiq). Re-login shart emas — allaqachon login qilingan sessiyada filial switcher orqali o'tiladi (MCP 2026-07 tasdiqlangan).

```
switch_filial("Администрирование")
→ navigate_to(tab="Главное", name="Лицензии")
→ expect_page(heading="Лицензии")
```

**Balans tekshiruvi:** `p.text-success[ng-if="q.balance > 0"]` — 5s timeout; musbat bo'lmasa `logger.fail(raise_error=True)`. (MCP 2026-07: selector mavjud, balans musbat.)

**Sotib olish form:**
- Покупка link (agar ko'rinmasa)
- Payer: `base.b_input(ng_model="purchase.payer.name", value="AUTOTEST GWS", clear=True)`
- Kontrakt: `base.b_input(ng_model="purchase.contract_name", value="Договор № bn от 01.01.2025", clear=True)`
- Sana: today (ng_model="purchase.begin_date")

**Litsenziya qatorlari va OYLIK majburiy qoida (MUHIM, 2026-07 o'rganilgan):**
- `Smartup ERP: Базовый пользователь (Обязательный)` — **majburiy obuna**, `editable_quantity=False` (soni avtomatik, 5 dona)
- `Smartup ERP: Базовый пользователь ... За пользователя` — oddiy, 1 dona

**Qoida:** kompaniya **joriy oyda birinchi marta** litsenziya olayotgan bo'lsa — avval majburiy 5 talik obunani sotib olishi SHART, faqat undan keyin oddiy 1 talikni olsa bo'ladi. Bir oyda majburiy bir marta olinadi; keyingi xaridlarda majburiy talab qilinmaydi.

**Idempotentlik (test qayta run bo'lishi uchun):** majburiy soni cartga avtomatik qo'shiladi — talab bo'lsa `Итого лицензий: 5`, bu oy uchun allaqachon olingan bo'lsa `Итого лицензий: 0`. Kod `mandatory_already_bought = page.get_by_text("Итого лицензий: 0").is_visible()` bilan tekshiradi: 0 bo'lsa majburiy branch skip qilinadi, to'g'ridan-to'g'ri oddiy 1 talik olinadi. Shuning uchun test fresh company'da (majburiy 5 → oddiy 1) ham, majburiy allaqachon olingan holatda (faqat oddiy 1) ham yashil bo'ladi.

Har bir qatorda: miqdor → `Купить` → `Я ознакомился...` → `Да` → wait_for_loader.

**Sotib olgandan keyin `#biruniAlertExtended` (kvitansiya modali):** har bir muvaffaqiyatli xariddan so'ng Smartup natija/kvitansiya modalini (`#biruniAlertExtended`) ochadi. U ochiq qolsa keyingi qadamni (keyingi sotib olish yoki `run_attach_license`ning "Лицензии и документы" bosishi) **bloklaydi** (modal-body pointer eventlarni ushlaydi). Shuning uchun `_buy_license_row` `wait_for_loader`dan keyin modal chiqsa test faylidagi `_close_extended_alert(page)` bilan yopadi (5s kutib, chiqmasa o'tkazib yuboradi). Bu **xato modali emas** — muvaffaqiyat kvitansiyasi (majburiy 5 sotib olingach 5→0 bo'lgani MCP bilan tasdiqlandi).

## run_attach_license — foydalanuvchiga ulash

`run_` auth/navigatsiya qilmaydi — Лицензии sahifasida (Администрирование) bo'lish kerak. Setup zanjirida `run_buy_license` shu holatni qoldiradi; standalone uchun `test_attach_license` wrapper `authorization(admin)` + `switch_filial("Администрирование")` + `navigate_to(Лицензии)` qiladi.

**Base funksiyalar (raw locator EMAS):** license moduli standart grid komponentini ishlatadi — `b-grid-controller input[ng-model="o.searchValue"]` + `b-grid .tbl-row` (MCP 2026-07 list sahifasida tasdiqlangan). Shuning uchun:
- qator tanlash: `BasePage.grid("ERP users", click=True)` va `BasePage.grid(f"natural_person-pw{code}", click=True)` (raw `get_by_text(...).click()` EMAS)
- qidiruv: `BasePage.grid_controller(search=f"natural_person-pw{code}", controller_selector="b-grid-controller:visible")` — grid_controller o'zi Enter bosib `wait_for_loader` qiladi
- qator: `BasePage.grid(f"natural_person-pw{code}", grid_selector='b-grid[name="table"]', click=True)`
- heading: `expect_page(page, heading="Прикрепленные пользователи")`

**MUHIM — 2 ta grid controller (MCP 2026-07 tasdiqlangan):** "Доступные пользователи" (`license_user_list?mode=detached`) sahifasida **2 ta** `b-grid-controller` bor — yashirin (`b-grid[name="table_license"]` uchun, `input[ng-model="o.searchValue"]` **hidden**) va ko'rinadigan (`b-grid[name="table"]` = mavjud userlar). `grid_controller` default `.first` yashiринiga tushib "Locator expected to be visible: hidden" bilan yiqiladi. Shuning uchun `controller_selector="b-grid-controller:visible"` (ko'rinadigan search) va `grid_selector='b-grid[name="table"]'` (userlar gridi) **majburiy** beriladi. Qatorni `grid(..., click=True)` bilan bosish uni tanlaydi (checkbox) → "Прикрепить" tugmasi chiqadi.

```
"Лицензии и документы" link → b-page "Лицензии и документы"
→ grid("ERP users", click=True) → "Прикрепить пользователей" → heading "Прикрепленные пользователи"
→ agar biriktirilgan bor: checkbox(check_all) → "Открепить" → confirm → "нет данных"
→ "Доступные" → wait_for_loader(120_000)
→ grid_controller(search=..., controller_selector="b-grid-controller:visible")
→ grid(..., grid_selector='b-grid[name="table"]', click=True) → "Прикрепить" → confirm_biruni() → "Закрыть"
```

**Eslatma:** attach modali (`Прикрепить пользователей`) faqat sotib olingan litsenziya hujjati (`ERP users` qatori) bo'lganda ochiladi — aks holda "Лицензии и документы" ro'yxati "нет данных". To'liq oqim setup zanjirida (test_12) green: `run_buy_license` → `run_attach_license` (MCP + chain 2026-07 tasdiqlangan).

## Muhim

- `run_attach_license` `run_buy_license` bilan ketma-ket chaqiriladi (runner'da)
- wait_for_loader timeout = **120_000** (2 min) — litsenziya yuklanishi sekin bo'lishi mumkin
- Agar company'da Политика лицензирования o'chirilgan (`company.md`) — bu step skip qilinadi

## Test

- `tests/smoke/test_setup/test_license.py` → `run_buy_license`, `run_attach_license`
