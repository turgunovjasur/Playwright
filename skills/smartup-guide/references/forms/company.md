# Компания (Company) — yaratish va sozlash

## Navigatsiya

- **Head admin** (--head-email/--head-password) bilan kirish kerak — oddiy user yoki admin emas
- `run_company` va `test_company_add` boshida mavjud flowlardan foydalanadi: `authorization(page, who="head")`, so'ng `navigate_to(page, tab="Главное", name="Компании")`.
- Menyu: **Главное → Компании**.
- Ro'yxat heading: `Компании` / `Companies`

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
- `Шаблоны` card ichidagi `Маркировка` inputidan `UZ Marking` optioni tanlanadi; company setupda `План счетов=UZ COA`, `Банки=UZ BANK`, `Маркировка=UZ Marking` shablonlari majburiy.

## Test

- `tests/smoke/test_setup/test_company.py` → `run_company(page, code, save_data)`
- `save_data("company_code", company_code)` — data_store.json ga saqlanadi
- Test BasePage-first yozilgan: navigation/page state uchun `navigate_to`/`expect_page`, list uchun `grid_controller`/`grid`, maydonlar uchun `input`, switchlar uchun `checkbox`, save/confirm uchun `save_and_expect_heading`/`confirm_biruni` ishlatiladi.
- `smt-select-trigger`, Products card ichidagi switchni labelga bog'lash va Security'dagi segmented `Отключено` control uchun BasePage'da mos universal primitive yo'q; shu uch custom UI qismida scoped raw locator saqlanadi.
