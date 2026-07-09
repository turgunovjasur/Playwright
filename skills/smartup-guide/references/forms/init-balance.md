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
| Склад | b-input, `d.warehouse_name` | `base.b_input(label="Склад", value="Основной склад", clear=True)` |
| Название | product editable grid column, `item.product_name` | `base.b_input(label="Название", value=product_code, root=product_grid, expect_value=re.compile(r".+"))` |
| Кол-во | editable grid column, `item.quantity` | `base.input(label="Кол-во", value=..., root=product_grid)` |
| Цена | editable grid column, `item.price` | `base.input(label="Цена", value=..., root=product_grid)` |

## Locator qoidalari

- `Склад` display text auto-fill ko'rinsa ham `warehouse_id` backendga set bo'lmasligi mumkin; test `Склад` b-inputini real dropdown orqali qayta tanlaydi.
- `Название`, `Кол-во`, `Цена` oddiy `<label>` emas, `b-pg-grid` column headerlari. `BasePage._field_locator_by_grid_header(...)` fallback shu header ostidagi input/b-inputni topadi.
- Product `code_product-pw{code}` bilan qidirilganda b-input value `product-pw{code}` bo'lib qoladi; shuning uchun product tanlashda `expect_value=re.compile(r".+")` yoki expected product name ishlatiladi.

## Test

- `tests/smoke/test_life_cycle/init_balance.py` → `run_init_balance(page, code)`
