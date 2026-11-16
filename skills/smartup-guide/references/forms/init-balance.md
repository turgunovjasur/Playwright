# Ввод начальных остатков ТМЦ — boshlang'ich qoldiq

## Quick Lookup

### Navigatsiya

- Menyu: **Склад → Ввод начальных остатков ТМЦ**
- Ro'yxat heading: `Ввод начальных остатков ТМЦ`
- Yaratish heading: `Ввод начальных остатков ТМЦ (создание)`
- URL pattern: `/anor/mkw/init_balance/init_inventory_balance_list`, add forma `init_inventory_balance+add`

## Screenshot Paths

### Screenshotlar

- `screenshots/init-balance/create-form-2026-07-09.png` — create forma, MCP orqali tasdiqlangan.

## Known Locators

### Forma maydonlari

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_23_init_balance.py:35`

| Maydon | Joriy setup amali |
|---|---|
| `Номер` | `base.input(label="Номер", value=document_number)` |
| `Склад` va `Валюта` | Har ikkalasi nomlangan `b_input` orqali, `clear=True` bilan tanlanadi |
| `Название` | TMC kodi bilan qidiriladi, tanlangan qiymat aynan kutilgan nomga tengligi tekshiriladi |
| `Кол-во` va `Цена` | Har biri alohida `base.input(label=...)` orqali to‘ldiriladi |

## Business Rules

### Locator qoidalari

Ombor va valyutani tanlagach product kodi bilan row tanlanadi. UZS va USD uchun alohida hujjat saqlanadi va `Провести` bilan o‘tkaziladi. UZS provodkalari alohida oynada tekshiriladi.

## Flow And Tests

### Test

- `tests/smoke/test_setup/test_23_init_balance.py`:
  - yagona `run_init_balance(page, code)` `product-pw{code}` uchun 100 dona,
    UZS valyutasida 5000 kirim narxini va `product-usa-pw{code}` uchun 100 dona,
    `Доллар США` valyutasida 1 kirim narxini ketma-ket yaratadi.
- Setup runner **23 - Init Balance** wrapperida shu bitta `run_init_balance`
  funksiyasini chaqiradi.
- USD hujjat raqami birinchi hujjat bilan to'qnashmasligi uchun `1{code}`.
- Setup 24-qadam `Остатки ТМЦ` sahifasida ikkala productni ham tekshiradi.

## Known Issues

### Debug Notes

#### 2026-07-14 fresh setup run

Eski label resolver bo‘yicha user tasdiqlagan `Склад` / `Валюта` almashishi [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi)da. Joriy ikkala hujjatda test ombor va valyutani label bilan tanlaydi.

#### 2026-07-30 — Ikki valyutadagi product qoldiqlari
Tags: init-balance, product, usd, stock, order
Status: live-ui-confirmed
Verified: 2026-07-30
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `smartup.online` headless
Setup run `20 passed, 1 deselected`

- UZS va USD productlar uchun alohida boshlang'ich qoldiq hujjati yaratilib
  o'tkaziladi.
- Har bir productga 100 dona qoldiq beriladi. Bu keyingi Order testida ikkala
  product ham stock filtri sabab yo'qolib qolmasligi uchun precondition.
- USD qoldiq hujjatining `Валюта` maydoni `Доллар США`; product esa
  `c_p_usa_pw{code}` kodi orqali tanlanadi.
