# Ввод начальных остатков ТМЦ — boshlang'ich qoldiq

## Navigatsiya

- Menyu: **Склад → Ввод начальных остатков ТМЦ**
- Ro'yxat heading: `Ввод начальных остатков ТМЦ`
- Yaratish heading: `Ввод начальных остатков ТМЦ (создание)`
- URL pattern: `/anor/mkw/init_balance/init_inventory_balance_list`, add forma `init_inventory_balance+add`

## Screenshotlar

- `screenshots/init-balance/create-form-2026-07-09.png` — create forma, MCP orqali tasdiqlangan.

## Forma maydonlari

| Maydon | Turi | Test helper |
|---|---|---|
| Номер | oddiy input, `d.balance_number` | `base.input(label="Номер", value=...)` |
| Склад | b-input, `d.warehouse_name` | Label resolver tuzatilmaguncha `base.b_input(ng_model="d.warehouse_name", value="Основной склад", clear=True)` |
| Название | product editable grid column, `item.product_name` | `base.b_input(label="Название", value=product_code, root=product_grid, expect_value=re.compile(r".+"))` |
| Кол-во | editable grid column, `item.quantity` | `base.input(label="Кол-во", value=..., root=product_grid)` |
| Цена | editable grid column, `item.price` | `base.input(label="Цена", value=..., root=product_grid)` |

## Locator qoidalari

- `Склад` display text auto-fill ko'rinsa ham `warehouse_id` backendga set bo'lmasligi mumkin; test `Склад` b-inputini real dropdown orqali qayta tanlaydi.
- Init Balance DOMida `BasePage.b_input(label="Склад", ...)` xavfsiz emas: `_field_locator_by_label(target="b-input")` ishlatadigan `following::b-input[1]` warehouse o'rniga keyingi `Валюта` b-inputiga tushadi. Shu sabab warehouse uchun aniq `ng_model="d.warehouse_name"` locator ishlatiladi.
- `Название`, `Кол-во`, `Цена` oddiy `<label>` emas, `b-pg-grid` column headerlari. `BasePage._field_locator_by_grid_header(...)` fallback shu header ostidagi input/b-inputni topadi.
- Product `c_p_pw{code}` bilan qidirilganda b-input value `product-pw{code}` bo'lib qoladi; shuning uchun product tanlashda `expect_value=re.compile(r".+")` yoki expected product name ishlatiladi.

## Test

- `tests/smoke/test_setup/test_21_init_balance.py`:
  - yagona `run_init_balance(page, code)` `product-pw{code}` uchun 100 dona,
    UZS valyutasida 5000 kirim narxini va `product-usa-pw{code}` uchun 100 dona,
    `Доллар США` valyutasida 1 kirim narxini ketma-ket yaratadi.
- Setup runner **21 - Init Balance** wrapperida shu bitta `run_init_balance`
  funksiyasini chaqiradi.
- USD hujjat raqami birinchi hujjat bilan to'qnashmasligi uchun `1{code}`.
- Setup 22-qadam `Остатки ТМЦ` sahifasida ikkala productni ham tekshiradi.

## Debug Notes

### 2026-07-14 fresh setup run
Tags: init-balance, warehouse, b-input, error
- **User tasdiqlagan root cause:** `base.b_input(label="Склад", value="Основной склад", clear=True)` label resolver sabab `Валюта` b-inputini target qilgan va unga `Основной склад` yozgan. Currency dropdownida bunday option bo'lmagani uchun `Locator expected to be visible` chiqqan; keyingi `base.b_input(label="Валюта", ...)` qatori umuman bajarilmagan.

### 2026-07-30 — Ikki valyutadagi product qoldiqlari
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
