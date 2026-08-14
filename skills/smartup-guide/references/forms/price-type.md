# Цены / Narx turi (Price Type) — yaratish

Price type = **Цена** / narx turi. Setup smoke testda ikkita sotuv narxi
yaratiladi va `room-pw{code}` ga biriktiriladi:

| Nomi | Kod | Valyuta | Downstream |
|---|---|---|---|
| `Price Type UZB-pw{code}` | `c_p_t_uzb_pw{code}` | `Узбекский сум` | `product-pw{code}` — 7000 UZS |
| `Price Type USA-pw{code}` | `c_p_t_usa_pw{code}` | `Доллар США` | `product-usa-pw{code}` — 1 USD |

## Navigatsiya

- Menyu: **Справочники → Цены**
- Ro'yxat heading: `Цены`
- Yaratish heading: `Цена (создание)`

## Forma maydonlari

| Maydon | Locator | Qiymat |
|---|---|---|
| Код | `#anor183-input-text-code` textbox | `c_p_t_uzb_pw{code}` yoki `c_p_t_usa_pw{code}` |
| Название | `#anor183-input-text-name` textbox | `Price Type UZB-pw{code}` yoki `Price Type USA-pw{code}` |
| Рабочие зоны | `b-input.filter("Выбранных").get_by_placeholder("Поиск")` → `room-pw{code}` → Escape | `room-pw{code}` |
| Валюта | `BasePage.b_input(label="Валюта", ...)` | UZB uchun `Узбекский сум`, USA uchun `Доллар США` |

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

### NPS helper failure'ni yashirishi mumkin

Tags: nps, modal, timeout, exception, flaky
Status: code-confirmed
Verified: 2026-08-14
Source: `tests/smoke/flows/flow_modal.py::fill_nps_survey`

- Helper modalni `20_000 ms` kutadi va butun flow'ni `except Exception` bilan
  yutadi. Modal chiqib, rating yoki submit bosqichi xato qilsa ham log uni
  “modal yo'q” deb ko'rsatishi mumkin.
- Root cause tahlilida bu helperni optional-modal absence bilan real interaction
  failure'ni ajratmaydigan known risk deb hisobla.

## Saqlash

`base.click(name="Сохранить", exact=True)` →
`base.expect_page(heading="Цены")`; Biruni confirm yo'q va `expect_page`
loader overlay yo'qolishini ham kutadi.

Natijada ikkala price type ham alohida qidirilib, gridda tekshiriladi.

- `price_type_name_UZB` → `Price Type UZB-pw{code}`
- `price_type_name_USA` → `Price Type USA-pw{code}`

## Room bilan munosabat

UZB va USA price type'lar yaratish formasidagi `Рабочие зоны` orqali
`room-pw{code}` ga ulanadi (room formasidagi "Выбранных" rooms, room
prikreplenie "Тип цены" tabidan farqli).

Room prikreplenie "Тип цены" tabida esa `Акция` narx turi ulanadi — bu boshqa. Qarang: [room.md], [action.md].

## Test

- `tests/smoke/test_setup/test_13_price_type_uzb.py` →
  `run_price_type_uzb(page, code, logger, save_data)`; setup zanjiridagi optional
  NPS Survey modalini shu run birinchi qadamda qayta ishlaydi.
- `tests/smoke/test_setup/test_14_price_type_usa.py` →
  `run_price_type_usa(page, code, save_data)`.
- Setup 15-qadam `run_currency` bilan bugungi USD kursini 10000 qilib saqlaydi.
- UZB, USA va Currency setup runnerda uchta alohida pytest case sifatida collect qilinadi.

## 2026-07-30 — USA price type downstream ishlatildi

Tags: price-type, usd, product, setup
Status: live-ui-confirmed
Verified: 2026-07-30
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `smartup.online` headless
Setup run `20 passed, 1 deselected`

- `Price Type USA-pw{code}` faqat yaratilmaydi: Setup 16-qadamdagi
  `product-usa-pw{code}` narxi aynan shu row orqali `1 USD` qilib qo'yiladi.
