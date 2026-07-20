# Компания (Company) — yaratish va sozlash

## Navigatsiya

- **Head admin** (--head-email/--head-password) bilan kirish kerak — oddiy user yoki admin emas
- `run_company` va `test_company_add` boshida mavjud flowlardan foydalanadi: `authorization(page, who="head")`, so'ng `navigate_to(page, tab="Главное", name="Компании")`.
- Menyu: **Главное → Компании**.
- Ro'yxatda `Компании` / `Companies` matni breadcrumb/navigation sifatida ko'rinadi;
  A2 `company_list` sahifasida u accessibility `heading` role'iga ega emas.
- DOM responsive: desktopda ko'rinadigan title `<span>`, mobile varianti esa
  `h1.lg:hidden`; shu sabab desktopda `get_by_role("heading")` ko'rinadigan element topmaydi.
- List page tayyorligini `get_by_role("heading")` bilan tekshirmaslik kerak; URL va
  listning stabil elementi (`Создать` tugmasi yoki grid) bilan tekshiriladi.
- Aynan title matnini kutish kerak bo'lsa:
  `page.locator("#main-content").get_by_text("Компании", exact=True).filter(visible=True)`.
- `BasePage.expect_page(url=...)`ning o'zi loader spinnerni kutmaydi: amaldagi
  `check_unblocked` faqat `heading` berilgan branchda ishlaydi. Company navigationda
  spinnerni undan oldingi `BasePage.navigate_to()` kutadi; `expect_page(url=...)`
  standalone ishlatilsa undan keyin `BasePage.wait_for_loader()` alohida chaqiriladi.

## Screenshotlar

- `references/forms/screenshots/company/company__list-heading-role-missing__desktop-1440x783.png`
  — list to'liq render bo'lgan, lekin `heading` role mavjud bo'lmagan failure holati.
- `references/forms/screenshots/company/company__add-initial__desktop-1440x783.png`
  — yangi company formasining boshlang'ich, maydonlar hali to'ldirilmagan holati.

## Company code pattern

```python
company_code = f"autotest{code}".lower()  # masalan: autotest7576
```

## Forma tuzilmasi (`#companyForm`, `smt-control` elementlar)

**Agar company allaqachon mavjud bo'lsa** — qayta yaratilmaydi, to'g'ri view ga o'tiladi va security sozlamalar qo'llanadi.

### Majburiy maydonlar

| Maydon | Qidirish usuli | Qiymat |
|---|---|---|
| Код сервера / Server code | `smt-control` label filter | `autotest{code}` |
| Название / Company name | `smt-control` label filter | `Autotest company {code}` |
| Язык | — | `Русский` (default, tekshiriladi) |

### Majburiy shablonlar (Шаблоны card)

```
Маркировка → UZ Marking
План счетов → UZ COA
Банки → UZ BANK
```

Select trigger: `smt-select-trigger.click()` yoki textbox.click() (fallback).

### Products card

```
"trade" switch → yoqish → wait_for_loader → "Warehouse - Advanced" kutish (30s)
→ barcha TRADE_CHILD_PRODUCTS switchlarni yoqish (17 ta)
```

## Saqlash

```
"Сохранить" button → biruni confirm (да) → wait_for_loader(600_000)
→ heading Компании/Companies (timeout 600_000)
```

## Company viewda security sozlamalar (har doim)

```
Company qatori → Просмотреть → "Безопасность"/"Security" tab
→ "Ограничение количества одновременных сеансов" → Отключено (MAJBURIY)
→ agar DISABLE_LICENSE_POLICY: "Политика лицензирования" → off
→ Сохранить → confirm → wait_for_loader(600_000)
```

## Loyiha Xususiyatlari (tasdiqlangan)

### Company View
- Company viewda `Безопасность`/Security tab ichida `Политика лицензирования` radio/switch control bor; company setup runida `--create-company --disable-license-policy` berilsa off qilinadi.
- `Политика лицензирования` control view tabning o'zida interaktiv `smt-switch` sifatida turadi (`id="licensing_policy_enabled"`, `role="switch"`). Uni off qilish uchun global `Изменить` tugmasini bosmaslik kerak, chunki u oddiy `company_edit` formaga olib kiradi va tablar yo'qoladi.
- Policy off qilingan runlarda setup zanjiri `Buy License` va `Attach License` qadamlari real license flowga kirmaydi; policy yoqiq bo'lsa yangi company uchun `Активация для лицензии` precondition emas.
- Company setup runida `Безопасность`/Security tabdagi `Ограничение количества одновременных сеансов` segmenti doim `Отключено` qilinadi; aks holda keyingi group/user loginlarda `Активные сеансы`/`concurrent_session_list` blokeri chiqadi.

### Company Add
Tags: company, setup, locator, wait
- `Создать` bosilgandan keyin `Компания (создание)` headeri `#companyForm` mount bo'lishidan oldin ko'rinishi mumkin; required fieldlarni to'ldirishdan oldin `#companyForm` va kamida bitta `smt-control` ko'rinishini kutish kerak.
- `BasePage.input()`/`b_input()`/`checkbox()`ga `root="app-main-info"` kabi selector string berilganda u avval Locatorga normalizatsiya qilinishi shart; aks holda stringda `.locator()` chaqirilib `AttributeError` chiqadi. Bu barcha field helperlar uchun `BasePage._resolve_root()` orqali bajariladi.
- `Шаблоны` card ichidagi `Маркировка` inputidan `UZ Marking` optioni tanlanadi; company setupda `План счетов=UZ COA`, `Банки=UZ BANK`, `Маркировка=UZ Marking` shablonlari majburiy.

## Test

- `tests/smoke/test_setup/test_company.py` → `run_company(page, code, save_data)`
- `save_data("company_code", company_code)` — data_store.json ga saqlanadi
- Test BasePage-first yozilgan: navigation/page state uchun `navigate_to`/`expect_page`, list uchun `grid_controller`/`grid`, maydonlar uchun `input`, switchlar uchun `checkbox`, save/confirm uchun `save_and_expect_heading`/`confirm_biruni` ishlatiladi.
- `smt-select-trigger`, Products card ichidagi switchni labelga bog'lash va Security'dagi segmented `Отключено` control uchun BasePage'da mos universal primitive yo'q; shu uch custom UI qismida scoped raw locator saqlanadi.
