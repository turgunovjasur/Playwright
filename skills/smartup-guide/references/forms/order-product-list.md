# Order Product List

Order wizard ichidan ko'p mahsulot tanlash formasi.

## Quick Lookup

- Form slug: `order-product-list`
- URL pattern: `*/anor/mdeal/order/product_list`
- Navigation: order wizard step 2 -> `Подбор`
- Heading: `Заказ (подбор): <client>`
- Query konteksti: room, inventory kind, active tab va client

## Screenshot Paths

- N/A — 2026-07-31 tekshiruvda yangi screenshot arxivlash locator/debug
  qiymatini oshirmadi.

## Known Locators

- Toolbar: `Закрыть`, initial setting save/delete ikonkalari.
- Required `b-input`: `warehouses` (`q.warehouse_name`) va `price_types`
  (`q.price_type_name`).
- Tablar: `Доступные` va `Выбранные`.
- Gridlar: `available_products`; selected products gridi.
- Filter modal: `#biruniPgGridFilter`.
- Split card: `toggleSplitCard('Y')`; balance ignore:
  `changeIgnoreBalance()`.

## Flow And Tests

- Reusable flow: N/A.
- 2026-07-31 holatida `tests/smoke/` ichida `product_list` uchun alohida
  avtomatlashtirilgan test topilmadi.

## Business Rules

### Warehouse, price type va ikki tabli tanlash
Tags: order, product-list, warehouse, price-type, grid
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `order/product_list`.
- Qoida: warehouse va price type required. `Доступные` gridida code, name,
  card, price, stock, quantity, case quantity, margin va sold; `Выбранные`
  gridida bularga amount va margin amount qo'shiladi.
- Testda ishlatish: required validatsiya, available->selected va selected->
  available o'tishi, qiymatlar/totallar va close orqali wizardga transferni
  tekshir.

### Product list filterlari va summary
Tags: order, product-list, filter, summary
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `Доступные` tabidagi filter.
- Qoida: filter `ИД ТМЦ`, `Название`, `Код`, `Группа`, `Категория`,
  `Торговая марка`, `Производитель` maydonlarini qo'llaydi. Text fieldlarda
  `Равно`, `Не равно`, `Поиск`, `Исключить`; categorical fieldlarda
  `Равно`, `Не равно` operatorlari bor. Selected summary SKU, positions,
  net/gross weight, quantity, amount, margin va revaluationni ko'rsatadi.
- Testda ishlatish: har operator, combined filter, show-all/reset hamda summary
  qiymatlarini selected rowlar bilan hisoblab solishtir.

## Known Issues

- Price type tanlanmagan kontekstda available grid bo'sh ko'rinishi mumkin;
  buni loader xatosi deb baholashdan oldin required contextni tekshir.
- Split-card va ignore-balance boshqaruvlari grant/feature flagga bog'liq.
