# Contract View

Qidiruv kalitlari: contract, contract-view, view-form, locator, screenshot, order-precondition

## Quick Lookup

- Form slug: `contract-view`
- Navigation: `Финансы > Договоры` -> contract row -> `Просмотр`
- URL pattern: `*/anor/mkf/contract_view`
- Page container: `b-page`
- Forms inventarida contract **listi** bor. Eski Group A view ssenariysi [tarixda](../history.md#order-va-contract-testlarining-eski-qamrovi) saqlangan.
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

## Flow And Tests

### Open Flow

Legacy listda contract qatorini tanlab `Просмотр` orqali view ochilgan. Hozirgi Forms list case’i `tests/smoke/test_forms/inventory/finansy.py`da. [Order helperi](../../../../tests/smoke/test_life_cycle/flow_order/flow_order_add.py) mavjud contractni nomiga qarab tanlaydi.

## Known Locators

- Page root: `page.locator("b-page")`
- Contract row in list: `page.locator("b-grid").get_by_text(contract_code).first`
- View button: `page.get_by_role("button", name="Просмотр", exact=True)`
- Close button: `page.get_by_role("button", name="Закрыть", exact=True)`
- Contract View qiymatlari readonly input emas: DOM `label + span.form-view` ko'rinishida (`Название`, `Код`, `Контрагент`, `Валюта`, `Сумма договора`, `Тип оплаты`).
- Qiymatni label bo'yicha tekshirish: `BasePage.form_view(label="Валюта", expect_value="Узбекский сум")`.

## Current View Assertions

Arxivlangan view’da kod, nom, kontragent, valyuta, summa va to‘lov turi ko‘rish uchun beriladi. Qiymatlar tanlangan shartnomaga bog‘liq. [Trace metadatasi](screenshots/contract-view/contract-view__default__trace-800x435__contract_code_2375.json).

## Verified Contract Chain

Avvalgi Group A limit va to‘lov turini tekshirgan holatlar [tarixiy contract ssenariysida](../history.md#order-va-contract-testlarining-eski-qamrovi) keltirilgan.

## Business Rules

### Related Business Rules

Order helperi `Договор` maydoniga saqlangan contract nomini uzatadi. Limit, to‘lov turi va boshqa valyutaga o‘tish dalillari [contracts.md](../contracts.md)da.

## Known Issues

### Known Debug Notes

- Contract list grid may not display every contract field. If a field is needed for list search/assert, enable its column/search through grid setting.
- Contract View'da `BasePage.input(label=..., expect_value=...)` ishlamaydi: qiymat `input[readonly]`da emas, `.form-view` spanida. `BasePage.form_view(...)` ishlatilsin.
- During debug iteration, if `contract_code` / `contract_name` already exist in `data_store.json`, reuse them instead of recreating contract.
