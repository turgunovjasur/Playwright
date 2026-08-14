# Client Offset

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)

## Quick Lookup

- Form slug: `client-offset`
- Navigation: `Продажа > Продажа > Взаиморасчеты с клиентами`
- URL pattern: `*/anor/mdeal/order/offset/offset_list`
- Heading: `Взаиморасчеты с клиентами`
- Debt detail URL pattern:
  `*/anor/mdeal/order/offset/offset_detail_list?person_id=*&currency_id=*`
- Related dossiers: [order-list.md](order-list.md),
  [client-payment.md](client-payment.md)

## Screenshot Paths

- N/A

## Known Locators

### Settlement list va actionlar
Tags: client-offset, grid, locator, settlement
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `*/anor/mdeal/order/offset/offset_list`.
- Qoida: grid ustunlari `Клиент`, `Валюта`, `Задолженность`,
  `Предоплата`, `Заказ`, `Забронированная предоплата`, `Баланс`.
  Toolbar actionlari `Взаиморасчет`, `Дебиторы`,
  `История взаиморасчетов`. Client row checkbox bilan tanlanganda emas,
  row yoki undagi ko'rinadigan client cell bosilib sliding menu ochilganda
  `Детали` actioni ko'rinadi.
- Testda ishlatish: `Детали` uchun `base.grid(client, click=True)` bilan rowni
  och; `Взаиморасчет` toolbar actioni row selection talab qilmaydi.

### Settlement row sliding action'i
Tags: client-offset, grid, row, sliding, details
Status: trace-confirmed
Verified: 2026-07-31
Source: `test-results/traces/test_0_group_runner.zip`;
`tests/smoke/test_groups/test_a_grup/test_02_archive_base_order.py`; live UI
- Qoida: settlement row yoki ko'rinadigan client cell bosilganda checkbox
  checked bo'lmaydi; row `tbl-row open` holatiga o'tadi va
  `sliding.tbl-row-menu` ichida `Детали` actioni paydo bo'ladi.
- Testda ishlatish: raw client-cell click va class assertion yozma;
  `row = base.grid(client, root="b-grid:visible", click=True)` qilib,
  `Детали`ni shu row scope'ida `base.click(...)` bilan bos.

### `Взаиморасчет` modali
Tags: client-offset, modal, date, checkbox, confirm
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: settlement toolbaridagi `Взаиморасчет` bosilganda.
- Qoida: modalda required `Дата взаиморасчета` (`d.offset_date`) va
  default yoqilgan to'rtta option bor: `с учетом консигнации`, `по проекту`,
  `по договору`, `по типу оплаты`. Yakuniy actionlar `Подтвердить`
  (`autoOffset()`) va `Закрыть`.
- Testda ishlatish: row checkboxini tanlamasdan toolbar actionni bos; modalni
  heading `Взаиморасчет` bilan scope qil;
  kerakli option defaultlarini tekshir, so'ng `Подтвердить`dan keyin
  client qarzi va prepayment natijasini qayta qidir.

### Debt detail gridi
Tags: client-offset, debt-detail, order-id, archive
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: client row tanlangandan keyingi `Детали` actioni.
- Qoida: `Детали задолженности` grid ustunlari `ИНН`, `Клиент`,
  `ИД заказа`, `Срок оплаты`, `Валюта`, `Предоплата`,
  `Сумма задолженности`, `Статус`.
- Testda ishlatish: archive qilingan orderning aniq IDsi, qarz summasi va
  `Архив` statusini shu detail gridda tekshir.

## Flow And Tests

- Mavjud reusable flow: N/A
- Mavjud group-0 testlar:
  `tests/smoke/test_groups/test_a_grup/test_02_archive_base_order.py`,
  `tests/smoke/test_groups/test_a_grup/test_04_offset_client_balance.py`.

## Business Rules

### Archive order qarzdorlikka o'tadi
Tags: client-offset, order, archive, debt
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `Детали задолженности`.
- Qoida: `Архив` statusidagi order debt detail gridda order IDsi va
  `Сумма задолженности` bilan ko'rinadi. Live dalilda bitta archive order
  `7 000` qarz yaratgan.
- Testda ishlatish: orderni archive qilgandan keyin faqat order list statusini
  emas, client debt detaildagi order ID va qarz summasini ham assert qil.

### Settlement list agregatlari
Tags: client-offset, debt, prepayment, open-order, balance
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: settlement list client rowi va footer totalari.
- Qoida: `Задолженность`, `Предоплата`, hali archive qilinmagan `Заказ` va
  booked prepayment alohida ko'rsatiladi; `Баланс` ularning umumiy ta'sirini
  beradi. Live holatda `7 000` debt + `21 000` order, prepaymentlarsiz,
  `-28 000` balans berdi.
- Testda ishlatish: rerunlardan qolgan orderlar client bo'yicha agregatlarni
  o'zgartirishi mumkin; testcase aniq order ID/delta yoki toza baseline bilan
  ishlasin, global totalni ko'r-ko'rona `7 000` deb kutmasin.

## Known Issues

- Bir xil `{client, amount, status}`li orderlar rerunlarda ko'payadi;
  settlement list client bo'yicha ularni bitta rowga agregatlaydi.
- To'liq settlementdan keyin client rowning nol qiymatlar bilan qolishi yoki
  listdan yo'qolishi ushbu read-only tahlilda tasdiqlanmadi; implementatsiyada
  post-confirm state'ni live aniqlab, shundan keyin final assertion tanlansin.
