# Цены / Narx turi (Price Type) — yaratish

Price type = **Цена** / narx turi. Smoke testda `Price Type UZB-pw{code}` yaratiladi va room-pw{code} ga biriktiriladi.

## Navigatsiya

- Menyu: **Справочники → Цены**
- Ro'yxat heading: `Цены`
- Yaratish heading: `Цена (создание)`

## Forma maydonlari

| Maydon | Locator | Qiymat |
|---|---|---|
| Код | `#anor183-input-text-code` textbox | `c_p_t_pw{code}` |
| Название | `#anor183-input-text-name` textbox | `Price Type UZB-pw{code}` |
| Рабочие зоны | `b-input.filter("Выбранных").get_by_placeholder("Поиск")` → `room-pw{code}` → Escape | `room-pw{code}` |

Room tanlanganidan keyin **"Цена продажи"** avtomatik tanlangan bo'lishi kerak. Live trace
(2026-07-13): `input[name="price_type_kind"][value="S"]` (`Цена продажи`) `checked=true`,
`value="P"` (`Цена закупки`) esa `checked=false`. Tekshiruv:
`BasePage(page).radio("Цена продажи", expect_checked=True)`. Faqat matn ko'rinishini
tekshirish yoki umumiy `BasePage.text("Цена продажи")` false-positive berishi mumkin.

## Label Helper Mapping

Tags: price-type, locator, helper, mcp
- MCP Playwright bilan 2026-06-26 da `Цена (создание)` real DOM'da tekshirildi.
- `BasePage.input(label="Код", value=value)` → `ng-model="d.code"`.
- `BasePage.input(label="Название", value=value)` → `ng-model="d.name"` (`Название*` labeli bilan ham mos tushadi).
- `BasePage.b_input(label="Валюта", value="Узбекский сум")` → `b-input name="currencies"`, `ng-model="d.currency_name"`.
- `BasePage.checkbox(label="Статус", checked=enabled)` → checkbox `ng-model="d.state"`.
- Screenshot: `references/forms/screenshots/price-type/price-type__add-default__desktop-mcp-20260626.png`.

## NPS Survey modali

Bu test `fill_nps_survey(page, logger)` bilan boshlanadi — step 0. Agar NPS modal chiqsa o'tkazib yuboriladi.

## Saqlash

`save_and_expect_heading("Цены")` — biruni confirm yo'q.

Natija qidiruvda: `Price Type UZB-pw{code}` ko'rinadi.

`save_data("price_type_name_UZB", f"Price Type UZB-pw{code}")` — data_store.json ga saqlanadi.

## Room bilan munosabat

Bu `Price Type UZB-pw{code}` room attachment orqali room'ga **alohida** ulanadi (room formasidagi "Выбранных" rooms, room prikreplenie "Тип цены" tabidan farqli).

Room prikreplenie "Тип цены" tabida esa `Акция` narx turi ulanadi — bu boshqa. Qarang: [room.md], [action.md].

## Test

- `tests/smoke/test_setup/test_price_type.py` → `run_price_type_uzb(page, code, logger, save_data)`
