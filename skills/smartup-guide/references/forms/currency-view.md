# Currency View

### URL va asosiy sahifa
Tags: currency, currency-view, rate, modal
- URL pattern: `anor/mk/currency_view?currency_id=<id>`.
- Sahifa headingi: `Валюта (просмотр)`.
- `Курсы` tabida `Установить курс` tugmasi kurs qo'shish modalini ochadi.
- Related test: `tests/smoke/test_setup/test_15_currency.py`.

### Добавить курс modali
Tags: currency, rate, modal, dialog, heading, locator
- Live DOM (2026-07-28): ko'rinadigan modal `div.modal.fade.show[role="dialog"]`,
  header esa `h4.modal-title.ng-binding` va accessible
  `heading` nomi `Добавить курс`.
- `BasePage.expect_page()`ning `root` parametri sahifa ichidagi scope'ni qabul
  qiladi; modal headingini ham shu helper bilan tasdiqlash afzal:

  ```python
  modal = page.get_by_role("dialog")
  base.expect_page(heading="Добавить курс", root=modal)
  ```

- `Дата курса` inputi modal ochilganda joriy sana bilan avtomatik to'ldiriladi.
  Uni qayta tanlamasdan tekshirish:

  ```python
  base.date_picker(
      label="Дата курса",
      date="today",
      auto_fill=True,
      root=modal,
  )
  ```

- Keyingi input va button locatorlari umumiy sahifadan emas, shu `modal` ichidan
  scope qilinsin.
- Kurs saqlangach gridda bugungi qatorni literal sana bilan emas,
  `base.grid(base.date("today"), expected_rate)` orqali tekshirish kerak.
- `Курсы` gridi oldingi yoki takroriy runlardan kurs saqlagani uchun test
  boshida bo'sh bo'lmasligi normal; bu flow'ni buzmaydi. Shu holat `warning`
  emas, kerak bo'lsa `info` sifatida loglanadi yoki tekshiruv olib tashlanadi.
- Markaziy bank kursini olish actionidan keyin bugungi qator mavjudligini
  tekshirish:

  ```python
  if not base.grid(base.date("today"), return_bool=True):
      logger.warning("Kurs Markaziy bankdan olinmadi!")
  ```

  `base.grid(return_bool=True)`ni `text` bermasdan chaqirish helper validationda
  `ValueError` beradi va UI umuman tekshirilmaydi. Faqat grid bo'shligini
  aniqlash kerak bo'lsa `base.grid(state="empty", return_bool=True)` ishlatiladi.
- `Курс валют` inputi live DOMda `b-number="positive"`; inputga `10_000` kabi
  underscore'li matn emas, `10000` kabi raqam matni beriladi. `BasePage.grid()`
  default whitespace-insensitive bo'lgani uchun assertda ham `"10000"` berish
  mumkin; u UI'dagi `"10 000"` qiymatiga mos keladi.
- Screenshot:
  `screenshots/currency-view/currency-view__add-rate-modal__desktop-1440x315__usd.png`.
