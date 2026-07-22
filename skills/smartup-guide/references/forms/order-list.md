# Order List

Tags: order, order-list, grid, row-action, locator, screenshot

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
- 2026-07-20 fix verificationning birinchi A-group rerunida A-03 va A-04 passed; A-05 shu action panelidagi eski `Изменить` locatorini ochib berdi. UI screenshotiga mos `Редактировать` locator ishlatiladi.
- 2026-07-20 yakuniy verification: `tests/smoke/test_all_runner.py::test_02_a_group_runner` to'liq passed (`1 passed`); `Просмотр` va `Редактировать` row actionlari A-03/A-04/A-05 zanjirida tasdiqlandi.
