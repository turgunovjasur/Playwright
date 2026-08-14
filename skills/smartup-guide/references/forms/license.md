# Лицензии — legacy Biruni sotib olish va ulash

## Quick Lookup

Tags: license, biruni, angularjs, setup, server
Status: trace-confirmed
Verified: 2026-08-13
Source: user; `test-results/allure-results/d9911418-1c48-4e7f-ab31-e5b6ec17f96a-result.json`;
`test-results/allure-results/cbf15b21-512a-4369-9d3d-71cf528ce5b5-attachment.png`

- Joriy route: `/#/!<session>/biruni/kl/license_list`; visible page text:
  `Лицензии`. `/a2/...` deb assert qilish mumkin emas.
- Shell yo'li: `Главное → Лицензии`. Forma `BasePage` bilan boshqariladigan
  legacy Biruni/AngularJS komponentlarini ishlatadi.
- Yuqori linklar: `Баланс`, `Лицензии и документы`, `Покупка`,
  `Как продлить лицензии`.
- `smartup.online` hostida faqat Buy pytest skip qilinadi; Attach server sabab
  skip qilinmaydi va ishlashda davom etadi. `app3.../xtrade` hostida Buy uchun
  unconditional skip yo'q.
- `CREATE_COMPANY=1` + `DISABLE_LICENSE_POLICY=1` bo'lsa ikkala flow policy
  sabab real UI'ga kirmasdan no-op bo'ladi.

## Screenshot Paths

Joriy legacy forma screenshotlari:

- `references/forms/screenshots/license/license__company-not-activated-error__desktop-1440x783.png`
- `references/forms/screenshots/license/license__company-not-activated-error__desktop-1440x783.json`
- `references/forms/screenshots/license/license__list-balance-mcp-20260713__desktop-1440x1000.png`
- `references/forms/screenshots/license/license__purchase-datepicker-mcp-20260713__desktop-1440x1000.png`

## Known Locators

Tags: license, locator, b-input, date-picker, b-grid
Status: code-confirmed
Verified: 2026-08-13
Source: `tests/smoke/test_setup/test_10_buy_license.py`;
`tests/smoke/test_setup/test_11_attach_license.py`

- Musbat balans: `p.text-success[ng-if="q.balance > 0"]`.
- `Плательщик` va `Договор`: `BasePage.b_input(...)`; sana:
  `BasePage.date_picker(...)`.
- Purchase ro'yxati `Тип лицензии` headerli visible HTML table; bu `b-grid`
  emas. Qator quantitysi row ichidagi textbox orqali tekshiriladi/to'ldiriladi.
- Xarid actioni `Купить`; shart checkboxi `Я ознакомился...`; tasdiq `Да`.
- `Лицензии и документы` attach oqimi `b-grid`, `b-grid-controller` va Biruni
  confirm dialoglaridan foydalanadi.

## Flow And Tests

- Buy: `tests/smoke/test_setup/test_10_buy_license.py::run_buy_license`.
- Attach: `tests/smoke/test_setup/test_11_attach_license.py::run_attach_license`.
- Runner items: `test_10_buy_license`, `test_11_attach_license`.
- Shared server/policy guard: `tests/smoke/flows/flow_license.py`.
- UI primitives: `utils/base_page.py::BasePage`.

## Business Rules

Tags: license, purchase, attach, dependency
Status: code-confirmed
Verified: 2026-08-13
Source: `tests/smoke/test_setup/test_10_buy_license.py`; `tests/smoke/test_setup/test_11_attach_license.py`

- Payer `AUTOTEST GWS` tanlangach contract `Договор № bn от 01.01.2025`
  mavjud va balance shu payerga mos yangilanadi.
- `Smartup ERP: Базовый пользователь (Обязательный)` ko'rinsa default `5`
  olinadi; bo'lmasa oddiy `Smartup ERP: Базовый пользователь` quantity `1`.
- Attach `ERP users → Прикрепить пользователей` orqali ishlaydi; eski attached
  userlar tozalanadi, `Доступные`dan `natural_person-pw{code}` topilib
  biriktiriladi. Smartup.online'da Buy skip bo'lgani uchun mavjud `ERP users`
  license hujjati precondition hisoblanadi.

## Known Issues

Tags: license, failure, router, base-page, dependency
Status: trace-confirmed
Verified: 2026-08-13
Source: `test-results/allure-results/d9911418-1c48-4e7f-ab31-e5b6ec17f96a-result.json`; user

- `10 - Buy License`ni `AngularBasePage`ga migratsiya qilish noto'g'ri bo'lgan:
  real route `/#/!<session>/biruni/kl/license_list` bo'lib, `/a2/...` assertioni
  30 sekunddan keyin yiqilgan. Buy va Attach legacy `BasePage`da qoladi.
- `smartup.online` server guard faqat Buy'ni skip qiladi; Attach server sabab
  skip qilinmaydi. Xtrade'da Buy va Attach bajariladi. Attach uchun mavjud
  `ERP users` license hujjati precondition hisoblanadi.
