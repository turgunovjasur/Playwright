# Лицензии — sotib olish va ulash

<a id="лицензии--legacy-biruni-sotib-olish-va-ulash"></a>

## Quick Lookup

Tags: license, biruni, angularjs, setup, server
Status: trace-confirmed
Verified: 2026-08-13
Source: user; `test-results/allure-results/d9911418-1c48-4e7f-ab31-e5b6ec17f96a-result.json`;
`test-results/allure-results/cbf15b21-512a-4369-9d3d-71cf528ce5b5-attachment.png`

- 2026-08-13 trace’dagi legacy route `/#/!<session>/biruni/kl/license_list`, sahifa nomi `Лицензии`.
- Yuqori linklar: `Баланс`, `Лицензии и документы`, `Покупка`,
  `Как продлить лицензии`.

### Joriy kirish va server guardlari

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/flow_setup/flow_license.py:9`
- Buy va Attach `Главное → Лицензии` yo‘lini `open_admin_licenses()` orqali ochadi. A2’da admin menusi qayta qurilishi kerak bo‘lsa, helper dashboardda filialni almashtiradi va sahifani yangilaydi.
- `smartup.online` hostida faqat Buy pytest skip qilinadi; Attach server sabab
  skip qilinmaydi va ishlashda davom etadi. `app3.../xtrade` hostida Buy uchun
  unconditional skip yo'q.
- `COMPANY_CODE=1` + `DISABLE_LICENSE_POLICY=1` bo'lsa ikkala flow policy
  sabab real UI'ga kirmasdan no-op bo'ladi.

## Screenshot Paths

Legacy UI’dan arxivlangan holatlar:

- `references/forms/screenshots/license/license__company-not-activated-error__desktop-1440x783.png`
- `references/forms/screenshots/license/license__company-not-activated-error__desktop-1440x783.json`
- `references/forms/screenshots/license/license__list-balance-mcp-20260713__desktop-1440x1000.png`
- `references/forms/screenshots/license/license__purchase-datepicker-mcp-20260713__desktop-1440x1000.png`

## Known Locators

Tags: license, locator, date-picker, grid
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_10_buy_license.py:41`; `tests/smoke/test_setup/test_11_attach_license.py:42`
- Buy musbat balansni matn bo‘yicha tekshiradi. `Плательщик` va `Договор` uchun `b_input`, `Дата начала` uchun `date_picker` ishlatiladi.
- `Тип лицензии` jadvalida tanlangan qator miqdori beshinchi indeksdagi cell orqali tekshiriladi. Xarid tugmasi `Купить` yoki `Покупка лицензий`; shart tasdig‘i `Да`.
- Xtrade A2’da `xtrade_license_rows` `smt-table-row` ichida exact `ERP users` matnini topadi.

## Flow And Tests

- Buy: `tests/smoke/test_setup/test_10_buy_license.py::run_buy_license`.
- Attach: `tests/smoke/test_setup/test_11_attach_license.py::run_attach_license`.
- Runner items: `test_10_buy_license`, `test_11_attach_license`.
- Shared server/policy guard: `tests/smoke/test_setup/flow_setup/flow_license.py`.
- UI primitives: `utils/base_pages/auto_base_page.py::AutoBasePage`.

## Business Rules

Tags: license, purchase, attach, dependency
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_10_buy_license.py:96`; `tests/smoke/test_setup/test_11_attach_license.py:42`

- Buy sozlangan to‘lovchi va shartnomani tanlaydi, xarid boshlanishidan oldin musbat balansni tekshiradi.
- `Smartup ERP: Базовый пользователь (Обязательный)` ko'rinsa default `5`
  olinadi; bo'lmasa oddiy `Smartup ERP: Базовый пользователь` quantity `1`.
- Xtrade A2 Buy oldingi va keyingi `created_on` qiymatlaridan bitta yangi ERP users yozuvini aniqlaydi, status va miqdorini tekshiradi va `ui_purchased_license`ga code hamda `created_on`ni saqlaydi. Attach joriy setup code mosligini tekshiradi va aynan shu `created_on` bilan yagona qatorni ochadi. Bu hujjatning attached ro‘yxati bo‘sh bo‘lishi kerak.
- Attach `ERP users → Прикрепить пользователей` orqali ishlaydi; non-Xtrade oqimida oldingi biriktirishlar tozalanadi, `Доступные`dan `natural_person-pw{code}` topilib
  biriktiriladi. Smartup.online'da Buy skip bo'lgani uchun mavjud `ERP users`
  license hujjati precondition hisoblanadi.

## Known Issues

Tags: license, failure, router, base-page, dependency
Status: trace-confirmed
Verified: 2026-08-13
Source: `test-results/allure-results/d9911418-1c48-4e7f-ab31-e5b6ec17f96a-result.json`; user

- `10 - Buy License`ni `AngularBasePage`ga migratsiya qilish noto'g'ri bo'lgan:
  real route `/#/!<session>/biruni/kl/license_list` bo'lib, `/a2/...` assertioni
  yiqilgan. Bu xulosa o‘sha run shelliga tegishli.
- `smartup.online` server guard faqat Buy'ni skip qiladi; Attach server sabab
  skip qilinmaydi. Xtrade A2’da Attach’ning yangi xaridga bog‘lanishi [Business Rules](#business-rules)da.
