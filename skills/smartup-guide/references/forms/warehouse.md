# Склад (Warehouse)

## Quick Lookup

- Form slug: `warehouse`
- Navigation: `Склад → Склады`
- List URL: `anor/mkw/warehouse_list`
- View URL: `anor/mkw/warehouse_view?warehouse_id=<id>`
- View heading: `Склад (просмотр)`

## Screenshot Paths

N/A

## Known Locators

- Asosiy ombor qatori: `Основной склад`
- Qator actioni: `Просмотреть`
- View yopish actioni: `Закрыть`
- Viewda tekshiriladigan matnlar: `Основной склад`, `Активный`

## Flow And Tests

Tags: warehouse, setup, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_22_warehouse.py`;
`tests/smoke/test_setup/test_0_setup_runner.py`

- `run_warehouse(page, save_data)` omborlar ro'yxatini ochadi, `Основной склад`
  view formasiga o'tadi va view URLdagi `warehouse_id`ni musbat integer sifatida
  tekshirib `data_store.json.warehouse_id`ga saqlaydi.
- Setup runnerda bu mustaqil **22 - Warehouse** pytest case hisoblanadi.
- Standalone `test_warehouse` avval setup user sifatida authorization qiladi.

## Business Rules

- `Основной склад` company setupda mavjud bo'lgan asosiy ombor.
- Roomga omborni biriktirish `run_room_attachment` vazifasi; ombor ID sini olish
  esa alohida `run_warehouse` vazifasi.

## Known Issues

N/A
