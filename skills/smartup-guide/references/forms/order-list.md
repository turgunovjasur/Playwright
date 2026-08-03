# Order List

Tags: order, order-list, grid, row-action, locator, screenshot
Status: trace-confirmed
Verified: 2026-07-21
Source: `tests/smoke/flows/flow_order/flow_order_list.py`; `references/forms/screenshots/order-list/order-list__row-actions-open__desktop-2880x1566__20260720.json`

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Row Selection And View](#row-selection-and-view)
- [Debug Evidence](#debug-evidence)
- [Live UI Toolbar And Grid](#live-ui-toolbar-and-grid)

## Quick Lookup

- Form slug: `order-list`
- Navigation: `Продажа > Заказы`
- URL pattern: `*/trade/tdeal/order/order_list`
- Main grid: `b-grid`
- Main flow: `tests/smoke/flows/flow_order/flow_order_list.py`
- Related docs: `../orders.md`, `../ui-patterns.md`, `order-add.md`

## Screenshot Paths

- Row actionlari ochiq holat:
  `references/forms/screenshots/order-list/order-list__row-actions-open__desktop-2880x1566__20260720.png`
- Metadata:
  `references/forms/screenshots/order-list/order-list__row-actions-open__desktop-2880x1566__20260720.json`

## Row Selection And View

- Order qatori `.tbl-row`; qator yoki uning cell'i bosilganda pastdagi `.tbl-row-menu` ochiladi.
- View actionining ko'rinadigan matni va exact accessible name'i `Просмотр`.
- Tasdiqlangan locator: `get_by_role("button", name="Просмотр", exact=True)`; row ochilganda uni shu row scope'ida qidirish kerak.
- `Просмотреть` exact locator order listda element topmaydi. Bu loader/race emas: row menu ochiq va `Просмотр` tugmasi ko'rinib turgan holatda locator text mismatch sabab timeout beradi.
- Edit actionining ko'rinadigan matni va exact accessible name'i `Редактировать`; `Изменить` exact locator order listda element topmaydi.
- BasePage-first row patterni: `base.grid_controller(search=row_text)` bilan barcha sahifalar bo'yicha qidiruvni toraytirish, `row = base.grid(row_text, click=True)` bilan qatorni ochish, `base.text(root=row.locator(".tbl-row-menu"))` bilan action menu ko'rinishini kutish, keyin actionni `row` scope'ida bosish.
- `flow_order_list` ichida eski `_order_grid_row` va `_ensure_order_grid_row_open` local raw-locator helperlari ishlatilmaydi; grid search/select uchun mavjud `BasePage.grid_controller` va `BasePage.grid` yagona pattern hisoblanadi.
- `view`, `edit` yoki `status` actioni uchun `find_row` majburiy; action tugmasi faqat `base.grid(...)` qaytargan row scope'ida bosiladi. Butun `page` bo'yicha fallback qidiruv ishlatilmaydi, chunki boshqa/yashirin row actionini bosishi mumkin.
- Order listga o'tish uchun alohida `flow_open_order_list` wrapperi yozilmaydi: caller `base.navigate_to(tab="Продажа", name="Заказы")` ni to'g'ridan-to'g'ri chaqiradi. Keyingi `flow_order_list(...)` o'z boshidagi `base.expect_page(heading="Заказы", url="order_list")` bilan page state'ni bir marta tekshiradi.

## Debug Evidence

- 2026-07-20 A-03 failure trace: `7 000` cell click muvaffaqiyatli bajarilgan va row action paneli ochilgan.
- Failure screenshotda `Просмотр`, `Редактировать`, `Изменить статус` actionlari ko'ringan; test esa exact `Просмотреть` kutgani uchun 10 soniyada element topmagan.
- Order save muvaffaqiyatli bo'lgan: URL `*/order_list`, gridda yangi draft row va `7 000` summa mavjud.
- 2026-07-20 verificationda UI screenshotiga mos `Просмотр` va `Редактировать` locatorlari tasdiqlandi.

## Live UI Toolbar And Grid

### Order list asosiy boshqaruvlari
Tags: order, list, toolbar, grid, filter
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `*/trade/tdeal/order/order_list`.
- Qoida: toolbar'da `Создать` (`Импорт`, `Импорт по датам` dropdowni),
  `Создать (beta)`, `Создать розничный заказ`, `Настройки заказа`, `Чаты`,
  audit va widget settings mavjud. Grid default ustunlari `Рабочая зона`,
  `Клиент`, `Штат`, `Дата заказа`, `Дата доставки`, `Валюта`, `Сумма`,
  `Статус`.
- Testda ishlatish: action ko'rinishini grantlar bo'yicha, create variantlar
  navigatsiyasini va grid default ustunlarini alohida assert qil.

### List filter va widgetlar
Tags: order, list, filter, widget, status, payment-type
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order list filter va widget paneli.
- Qoida: default filterlar room, staff, sales rep, manager, order/delivery
  date range, amount range, status va source bo'yicha ishlaydi. Widgetlar
  total order/weight/liter, all orders, payment type va status kesimlarini
  ko'rsatadi va qiymat bosilganda listni filtrlashi mumkin.
- Testda ishlatish: har bir filter chegarasi, kombinatsiyasi, reset va widget
  drill-down natijasini grid rowlari/summary bilan solishtir.

### Order settings modal
Tags: order, list, settings, consignment, delivery-address
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `Настройки заказа` modal.
- Qoida: modalda draft order kunlari, client delivery addressga ruxsat va
  consignment responsible ruxsati mavjud. Draft setting labeli va izohidagi
  status matni deploymentda bir-biriga mos kelmasligi mumkin; test backend
  natijasini ham tekshirishi kerak.
- Testda ishlatish: valid/invalid day values, toggle persistence va yangi/edit
  orderga ta'sirini tekshir; faqat label matniga qarab biznes natija chiqarmang.

### Orderni `Архив` statusiga o'tkazish
Tags: order, list, status, archive, confirmation, debt
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order row action panelidagi `Изменить статус`.
- Qoida: dropdown `Архив` linkini beradi; tanlanganda
  `Изменить статус на Архив?` confirm dialogi va `да`/`нет` tugmalari
  chiqadi. Archive qilingan order clientning `Детали задолженности`
  gridida order ID va qarz summasi bilan ko'rinadi; active order list
  grididan esa yo'qoladi.
- Testda ishlatish: yaratilgan order IDni view formasidan saqla, archive
  actiondan keyin exact active ID yo'qolganini va client debt detaildagi shu
  order ID `Архив` statusida ekanini tekshir. Faqat client + `7 000` +
  `Новый` bilan row tanlash rerunlarda noaniq: live muhitda bir xil uchta
  row mavjud edi.

### Exact row ichidagi status action
Tags: order, list, row, status, modal, locator
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI;
`test-results/logs/tests_smoke_test_groups_test_0_grup_test_0_group_runner.py__test_0_02_archive_base_order_20260731_163648.log`
- Qoida: exact order row konteynerini `row.click()` qilish
  `modal-order-copy` oynasini ochishi mumkin; bu modal keyingi
  status action clickini intercept qiladi. `#status-btn-{order_id}` status
  cellining joriy status linki o'z dropdownini ochadi; uning ichida
  `Архив` buttoni mavjud.
- Testda ishlatish: order ID orqali `#status-btn-{order_id}`ni scope qil,
  cell ichidagi `.dropdown-toggle`ni ochib shu cell ichidagi `Архив` buttonini
  bos; row konteynerini yoki umumiy `Изменить статус` actionini bosma.
