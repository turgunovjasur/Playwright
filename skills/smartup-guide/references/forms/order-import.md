# Order Import

Order wizardga Excel fayldan TMC pozitsiyalarini import qilish formasi.

## Quick Lookup

- Form slug: `order-import`
- URL pattern: `*/anor/mdeal/order/order_import`
- Navigation: order wizard step 2 -> `Импорт`
- Heading: `Заказ (импорт ТМЦ)`
- Query konteksti: inventory kind va client

## Screenshot Paths

- N/A — 2026-07-31 live tekshiruvda fayl yuklanmadi va setting saqlanmadi.

## Known Locators

- Main actions: `Загрузить файл`, `Настройки`, `Закрыть`.
- File input: single `input[type="file"]`, `accept=".xls, .xlsx"`.
- Required `b-input`: `warehouses` (`q.warehouse_name`) va `price_types`
  (`q.price_type_name`).
- Product grid: `products`; error grid: `error_messages`.
- Settings actions: `saveSetting()`, `changeSection('I')`.
- Row range: `d.starting_row`, `d.ending_row`.
- Identify mode: `d.identify_product_by`.

## Flow And Tests

- Reusable flow: N/A.
- 2026-07-31 holatida `tests/smoke/` ichida `order_import` uchun alohida
  avtomatlashtirilgan test topilmadi.

## Business Rules

### Fayl turi va import natijasi
Tags: order, import, excel, validation, grid
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `order/order_import` main section.
- Qoida: faqat bitta `.xls` yoki `.xlsx` fayl button yoki drag/drop bilan
  tanlanadi. Warehouse va price type required. Muvaffaqiyatli parse qatorlari
  `products`, xatolar row number bilan `error_messages` gridida ko'rsatiladi.
- Testda ishlatish: ikkala file type, noto'g'ri extension, empty/all-invalid/
  partially-valid fayl, button va drop yo'lini; parsed rowlar, error row number
  va wizardga transferni tekshir.

### Import mapping sozlamalari
Tags: order, import, mapping, excel, settings
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: import form `Настройки` sectioni.
- Qoida: start row default `1`, end row optional. Productni aniqlash variantlari
  `Код продукции`, `Код на продукцию`, `ИД продукции`. Raqamli column mapping:
  code, balance, serial number, card number, expiry, quantity, margin kind,
  margin percent.
- Testda ishlatish: har identify mode, row-range chegaralari, required/duplicate/
  invalid column number, saved setting persistence va real parse natijasini
  tekshir.

## Known Issues

- UI fayl size limiti yoki header majburiyligini ko'rsatmaydi; testda mavjud
  bo'lmagan limitni taxmin qilib hardcode qilmaslik kerak.
- Split-card grantga bog'liq; oddiy userda disabled bo'lishi mumkin.
