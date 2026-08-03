# Наборы ТМЦ (Sector) — yaratish

Sector = **Набор ТМЦ** — mahsulot guruhi, product va room'ni birlashtiradi.

## Navigatsiya

- Menyu: **Справочники → ТМЦ → Наборы ТМЦ**
  - ТМЦ menyusiga kirgach `Наборы ТМЦ` link ko'rinadi
- Ro'yxat heading: `Наборы ТМЦ`
- Forma heading: `Набор ТМЦ (создание)`

## Forma maydonlari

Locatorlar oddiy — `get_by_role("textbox")` tartib bilan ishlaydi:

| # | Maydon | Locator | Qiymat |
|---|---|---|---|
| 1 | Kod | `textbox.first` | `c_s_pw{code}` |
| 2 | Название | `textbox.nth(1)` | `sector-pw{code}` |
| 3 | Рабочие зоны | `BasePage.multiselect(label="Рабочие зоны", value=room_name)` | `room-pw{code}` |

Live trace (2026-07-13): field `b-input[multiple][name="rooms"]`, `model="d.rooms"`; room tanlangach
chip ko'rinadi. Shu sabab raw textbox/text click o'rniga `multiselect(label="Рабочие зоны", value=room_name)` ishlatiladi.

## Saqlash

`base.click(name="Сохранить", exact=True)` →
`base.expect_page(heading="Наборы ТМЦ")`; Biruni confirm yo'q.

Natija ro'yxatda:
- `c_s_pw{code}` ko'rinadi
- `sector-pw{code}` ko'rinadi

## Dependency

- **Kerak bo'ladi:** room-pw{code} avval yaratilgan bo'lishi kerak
- **Downstream:** `test_18_product.py` — product yaratishda `sector-pw{code}` ko'rinishi kutiladi
- Standalone pytest wrapper user sifatida login qiladi; `run_sector(page, code)` esa allaqachon login qilingan page qabul qiladi.

## Test

- `tests/smoke/test_setup/test_17_sector.py` → `run_sector(page, code)`
