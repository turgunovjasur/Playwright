# Order List View Settings

Order listning table column va widget ko'rinishini boshqaruvchi ikkita setting
formasi.

## Quick Lookup

- Form slug: `order-list-view-settings`
- Table setting URL: `*/biruni/md/biruni/grid_setting?name=table`
- Table heading: `Настройка таблицы: Заказы`
- Widget modal heading: `Настройки виджетов`
- Navigation: order list grid settings menu yoki widget settings ikonka

## Screenshot Paths

- N/A — 2026-07-31 tekshiruvda preference o'zgartirilmadi.

## Known Locators

- Table actions: `Сохранить`, `По умолчанию`, `Закрыть`.
- Table selected list: `#deal_id`; additional field list; search-setting
  checkboxlari.
- Widget save/close: `saveWidgetSettingModal()`,
  `closeWidgetSettingModal()`.
- Widget position: `p.widget_bar_position_config` (`T` yoki `B`).

## Flow And Tests

- Table helper:
  `tests/smoke/flows/flow_order/flow_order_list.py::flow_order_list_grid_setting`.
- Existing lifecycle coverage:
  `tests/smoke/test_life_cycle/test_order.py::run_order_add_column_order_id`.
- Widget settings uchun alohida avtomatlashtirilgan test 2026-07-31 holatida
  topilmadi.

## Business Rules

### Table column setting
Tags: order, list, view-setting, grid, column
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI; `tests/smoke/flows/flow_order/flow_order_list.py`
- Qayerda: `Настройка таблицы: Заказы`.
- Qoida: default selected fieldlar room, client, staff, order/delivery date,
  currency, amount va status. Qo'shimcha fieldlardan order ID, source,
  contract, payment/price type, warehouse, product, weights, addresses,
  invoice/TTN, marking, consignment, audit va boshqa order atributlari
  tanlanadi. Selected fieldlar remove/reorder qilinadi; default reset mavjud.
- Testda ishlatish: add/remove/reorder/default/save/close, reload va yangi login
  persistence, shuningdek search-setting checkboxlarining grid qidiruviga
  ta'sirini tekshir.

### Widget setting
Tags: order, list, view-setting, widget, status, payment-type
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `Настройки виджетов` modal.
- Qoida: widget bar yuqori/pastga joylanadi; total orders, gross/net weight,
  liters, all-deals, status va payment-type widgetlari yoqib/o'chiriladi.
  All-deals/status/payment-type guruhlarida quantity va amount child toggles
  mavjud.
- Testda ishlatish: parent-child dependency, quantity/amount kombinatsiyalari,
  position, save/close va reload/login persistence'ni tekshir.

## Known Issues

- Table settings va widget settings alohida persistence mexanizmlaridir;
  bitta formadagi save ikkinchisiga ta'sir qilmasligi kerak.
- Setting testlari shared user preference'ni o'zgartiradi; parallel run uchun
  alohida user yoki teardown/default restore talab qilinadi.

### Table helper generic emas

Tags: order, grid-setting, helper, locator, typo
Status: code-confirmed
Verified: 2026-08-14
Source: `tests/smoke/flows/flow_order/flow_order_list.py`

- `flow_order_list_grid_setting(page, colum_name, search_name)` generic nomga
  ega bo'lsa ham `#deal_id`ga hardcode qilingan va faqat Order table settingiga
  mos; `colum_name` parametri ham tarixiy typo bilan qolgan.
- Uni boshqa gridlar uchun reusable helper deb ishlatma. Umumlashtirish kerak
  bo'lsa avval consumerlar va form-specific selected-list rootlarini ajrat.
