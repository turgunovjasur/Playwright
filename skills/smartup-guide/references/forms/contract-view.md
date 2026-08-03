# Contract View

Tags: contract, contract-view, view-form, locator, screenshot, order-precondition

## Quick Lookup

- Form slug: `contract-view`
- Navigation: `Финансы > Договоры` -> contract row -> `Просмотр`
- URL pattern: `*/anor/mkf/contract_view`
- Page container: `b-page`
- Joriy automated test yo'q; avvalgi Group A testlari 2026-07-31 kuni o'chirilgan.
- Contract testlari self-contained; `flow_contract` ishlatilmaydi.
- Related domain docs:
  - `../contracts.md`
  - `../ui-patterns.md`
  - `../testing-debug.md`

## Screenshot Paths

- Screenshot archive folder: `references/forms/screenshots/contract-view/`
- Metadata folder: `references/forms/screenshots/contract-view/`
- Archived trace screenshot: `references/forms/screenshots/contract-view/contract-view__default__trace-800x435__contract_code_2375.png`
- Archived trace metadata: `references/forms/screenshots/contract-view/contract-view__default__trace-800x435__contract_code_2375.json`
- Expected file naming:
  - `contract-view__default__desktop-1440x783__<contract_code>.png`
  - metadata: `contract-view__default__desktop-1440x783__<contract_code>.json`
- If screenshot is missing, open contract view in stable UI state, take screenshot, save it to `references/forms/screenshots/contract-view/`, save metadata in the same folder, and update this section with exact file path.
- Visual regression note: loader, dropdown, confirm/error modal, and transient notifications must be closed/hidden before taking baseline-ready screenshot.

## Open Flow

1. Har test faylida `BasePage.navigate_to(tab="Финансы", name="Договоры")` bilan list ochiladi.
2. `Создать` bosilib add heading/URL tekshiriladi; barcha inputlar shu test faylining `run_*` funksiyasida to'ldiriladi.
3. `base.click(name="Сохранить", exact=True)` va
   `base.expect_page(heading="Договоры", url="anor/mkf/contract_list")` bilan
   saqlanadi.
4. `grid_controller(search=contract_code)` va `grid(..., click=True)` bilan row tekshiriladi.
5. `Просмотр` bosilib qiymatlar `BasePage.form_view(...)` bilan tekshiriladi; `Закрыть` orqali listga qaytiladi.

## Known Locators

- Page root: `page.locator("b-page")`
- Contract row in list: `page.locator("b-grid").get_by_text(contract_code).first`
- View button: `page.get_by_role("button", name="Просмотр", exact=True)`
- Close button: `page.get_by_role("button", name="Закрыть", exact=True)`
- Contract View qiymatlari readonly input emas: DOM `label + span.form-view` ko'rinishida (`Название`, `Код`, `Контрагент`, `Валюта`, `Сумма договора`, `Тип оплаты`).
- Qiymatni label bo'yicha tekshirish: `BasePage.form_view(label="Валюта", expect_value="Узбекский сум")`.

## Current View Assertions

For UZS contract:

- `contract_code`
- `contract_name`
- `natural_client-pw{code}`
- `Узбекский сум`
- `500000`

For payment type contract:

- same as above
- `Перечисление` if contract was created with `Типы оплат = Перечисление`

## Verified Contract Chain

- 2026-07-21: A-01 va A-02 alohida self-contained test fayllarga ajratilgach runner orqali live tekshirildi — 2 passed (29.98s).
- 2026-07-21: A-01 yaratgan `500000` limitli contract A-03 limit/valid-order testida, A-02 saqlagan payment-type keylari A-04 auto-fill testida live tekshirildi — 2 passed.

## Related Business Rules

- Contract code and name are saved to `data_store.json` for order tests.
- Order form selects contract by `contract_name`, not by contract code.
- Contract `Сумма договора` is used as order total amount limit.
- Contract `Типы оплат` auto-fills order `Тип оплаты`, but user may change it; validation is still based on sum limit.
- Contract currency filters products in order; changing to another currency contract clears already selected products.

## Known Debug Notes

- Contract list grid may not display every contract field. If a field is needed for list search/assert, enable its column/search through grid setting.
- Contract View'da `BasePage.input(label=..., expect_value=...)` ishlamaydi: qiymat `input[readonly]`da emas, `.form-view` spanida. `BasePage.form_view(...)` ishlatilsin.
- During debug iteration, if `contract_code` / `contract_name` already exist in `data_store.json`, reuse them instead of recreating contract.
