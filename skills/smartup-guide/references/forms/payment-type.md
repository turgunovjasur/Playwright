# Типы оплат (Payment Type) — ulash

To'lov turlari **yaratilmaydi** — global katalogdan company'ga ulanadi (Прикрепление).

## Navigatsiya

- Menyu: **Справочники → Цены → Типы оплат**
  - "Цены" menyusiga kirgach `Типы оплат` link chiqadi
- Ro'yxat heading: `Типы оплат`
- Prикreplenie heading: `Тип оплат (прикрепление)`

## Ulash flow

```
"Прикрепление" button
→ "Тип оплат (прикрепление)" heading kutish
→ `BasePage.grid(checkbox="all")` — barchasini belgilash
→ "Прикрепить" button
→ confirm_biruni("Прикрепить типы оплат в количестве 4?")
→ wait_for_loader()
→ `BasePage.grid(state="empty", return_bool=True)` natijasi `True` ekanini tekshirish (barcha available bo'sh qolishi kerak)
→ "Закрыть" button
```

## Natija (4 ta to'lov turi)

Ro'yxatda ko'rinishi kerak:
- `Наличные деньги`
- `Перечисление`
- `Терминал`
- `Чековая книжка`

## Muhim

- `code` parametri yo'q — bu global, har bir company'ga bir xil 4 ta to'lov turi ulanadi
- Room prikreplenie (`room.md`) uchun ham shu Типы оплат ro'yxatidan tanlanadi
- Listda view action yo'q; ID gridning `Настройка таблицы` formasidagi `ИД`
  qo'shimcha ustuni orqali olinadi.
- `base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="ИД")`
  ustun va searchni yoqib, `ИД` ustun indeksini qaytaradi.
- `Наличные деньги` qatoridagi musbat ID `data_store.json.payment_type_id`ga
  saqlanadi.
- Standalone pytest wrapper `authorization(page, who="user", code=code)` bilan user sifatida login qiladi; `run_payment_type(page, save_data)` esa allaqachon login qilingan page qabul qiladi.

### Grid-setting link accessible nomiga icon glyph ham kiradi

Tags: payment-type, grid-setting, locator, accessible-name, icon
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI — `https://smartup.online/#/<session>/anor/mkr/price_type_list`
ikki sessionda; `test-results/traces/smoke_trace.zip`;
`test-results/logs/tests_smoke_test_setup_test_0_setup_runner.py__test_16_payment_type_20260827_175016.log`

- `b-grid-controller` bars buttoni menu'ni muvaffaqiyatli ochadi va DOMda
  `a.dropdown-item[ng-click="openGridSetting()"]` matni `Настройка таблицы`.
- Link accessible nomi icon glyph bilan birga ` Настройка таблицы`; shu sabab
  `get_by_role("link", name="Настройка таблицы", exact=True)` ikkala real
  sahifada ham `0`, partial role-name, exact text va
  `a[ng-click="openGridSetting()"]` esa `1` element qaytaradi.
- Muammo server/session yoki katta-kichik harf farqi emas; iconni hisobga
  olmagan exact accessible-name locator xatosi.
- Failure grid-setting route ochilishidan oldin bo'lgan; `Дополнительные поля`,
  `ИД` ustuni va search checkboxi bu run'da bajarilmagan.

### Search card root class token bilan tanlanishi kerak

Tags: payment-type, grid-setting, search, checkbox, xpath, card
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI — `https://smartup.online/#/<session>/biruni/md/biruni/grid_setting?name=table`;
`test-results/traces/smoke_trace.zip`;
`test-results/logs/tests_smoke_test_setup_test_0_setup_runner.py__test_16_payment_type_20260827_180835.log`

- `Настройки поиска` headingining eng yaqin `div[contains(@class, 'card')]`
  ancestori outer card emas, `div.card-header`; unda `ИД` switchi yo'q.
- Outer root exact class tokenli `div.card.card-custom.gutter-b`; class-token
  XPath bilan unda exact `ИД` text `1`, `label.switch input[type="checkbox"]`
  esa price-type real sahifasida `7` element qaytaradi.
- Payment Type runida `ИД` ustuni `Дополнительные поля`dan active listga
  muvaffaqiyatli o'tgan; failure faqat search root noto'g'ri tanlangani sabab
  checkbox helperga yetib bormagan.

## Test

- `tests/smoke/test_setup/test_16_payment_type.py` → `run_payment_type(page, save_data)`
