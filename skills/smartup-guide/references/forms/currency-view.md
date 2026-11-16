# Currency View

## Quick Lookup

### URL va asosiy sahifa
Tags: currency, currency-view, rate, modal
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_15_currency.py:34`
- URL pattern: `anor/mk/currency_view?currency_id=<id>`.
- Sahifa headingi: `Валюта (просмотр)`.
- `Курсы` tabida `Установить курс` tugmasi kurs qo'shish modalini ochadi.
- Related test: `tests/smoke/test_setup/test_15_currency.py`.
- USD view URLdagi `currency_id` musbat integer sifatida tekshirilib
  `data_store.json.currency_id`ga saqlanadi.

## Business Rules

### USD va UZS ID keylari
Tags: currency, setup, usd, uzs, data-store
Status: live-ui-confirmed
Verified: 2026-08-28
Source: live UI; `tests/smoke/test_setup/test_15_currency.py`
- Qoida: `currency_id` USD view IDsi; UZS row listda `860`, `сум`,
  `Узбекский сум` qiymatlari bilan ko'rinadi va uning view IDsi alohida
  `currency_id_uzb` keyiga saqlanadi.
- Testda ishlatish: UZS price type/productli order `currency_id_uzb`ni,
  USD order esa `currency_id`ni ishlatadi; ikkala keyni almashtirma.

## Known Locators

### Добавить курс modali

Tags: currency, rate, modal, dialog, heading, locator
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_15_currency.py:92`; `screenshots/currency-view/currency-view__add-rate-modal__desktop-1440x315__usd.json`

- `Установить курс` bosilgach `page.get_by_role("dialog")` ichida `Добавить курс` headingi kutiladi. `Дата курса`, `Курс валют`, `Базовая валюта` va `Сохранить` ham shu dialogga scope qilinadi.
- Setup sanani `date="today", auto_fill=True` bilan tekshiradi, raqamli kursni kiritadi va saqlangach view gridida bugungi sana bilan aynan manual kursni tekshiradi.

## Screenshot Paths

[USD view’dagi ochiq kurs modali](screenshots/currency-view/currency-view__add-rate-modal__desktop-1440x315__usd.png).

## Flow And Tests

`tests/smoke/test_setup/test_15_currency.py::run_currency` CBU so‘rovi, qaytgan kurs, manual kurs va ikki valyuta IDlarini tekshiradi.

## Known Issues

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_15_currency.py:61`

CBU yangilashda ma’lum HTTP 500 connect-timeout yoki HTTP 200 dan keyin bo‘sh kurslar jadvali qaytsa, test manual kursni va IDlarni tekshirib, oxirida `SetupDependencyReadyError` beradi. Muvaffaqiyatli CBU yangilashda eng so‘nggi qaytgan sana bugundan oldin bo‘lishi mumkin.
