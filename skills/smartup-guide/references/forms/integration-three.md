# Integration №3 (NEON) report — trade/rep/integration/integration_three

"Интеграция №3 NEON" — sotuv/qoldiq ma'lumotlarini HTML hisobot ko'rinishida (iframe ichida) render qiluvchi integration report. Natija **download emas**, sahifadagi `<iframe>` ichida 3 ta sheet bo'lib chiqadi.

## Navigatsiya

- Sahifa **menyuda yo'q** — URL orqali ochiladi: `#/<session_token>/trade/rep/integration/integration_three` (token login'dan keyingi `page.url` dan olinadi).
- Sahifa heading/tugma: `get_by_role("button", name="Настройки")` ko'rinsa sahifa ochilgan.

## Sahifa elementlari (barqaror selektorlar)

Tugmalar `ng-click` orqali (mode/run):
- **Настройки** — `button[ng-click="setRunMode('S')"]` (settings rejimi)
- **Параметры** — `setRunMode('P')`, **Просмотреть** — `setRunMode('V')`
- **Сохранить настройки** — `button[ng-click="saveSettings()"]` (faqat settings rejimida)
- **Сформировать (HTML)** — `button.btn-primary[ng-click="run('html', true)"]` ⚠️ ikkita `run('html', true)` tugma bor (biri `ng-hide` icon); ko'rinadigani `.btn-primary`.
- Boshqa formatlar: `run('html', false)` HTML, `run('xlsx', false)` EXCEL, `run('csv', false)` CSV, `run('xml', false)` XML.

Inputlar:
- `input[ng-model="d.begin_date"]` / `d.end_date` — `bootstrap-datetimepicker` (typing mumkin, readonly emas). Fill + `Escape` → datepicker (`.bootstrap-datetimepicker-widget`) yopiladi.
- `q.is_all_filials`, `d.product_group_name` (Поиск), `q.is_all_product_types` va h.k.

## Flow (tasdiqlangan)

1. Настройки (`setRunMode('S')`) → **Сохранить настройки** (`saveSettings()`) → settings yopilib parametr rejimi qaytadi (begin_date + Сформировать ko'rinadi). Bu qadam report default config (product group va h.k.) ni saqlaydi.
2. begin_date = bir oy oldingi sana (fill + Escape).
3. Сформировать (`run('html', true)`) → `block-ui-overlay` loader → hisobot **iframe** render bo'ladi.

## Hisobot iframe va sheetlar

- Iframe: `iframe[src*="integration_three"]` (sahifada 1 ta). Src: `.../b/trade/rep/integration/integration_three:run?rt=html&begin_date=...&filial_id=...&product_group_id=...`. Same-origin.
- Iframe ichida **3 ta sheet** Bootstrap nav-tab orqali: `a.nav-link` (aniq 3 ta) — nomlari **Склады / Документы / Остатки**.
  - tab `nth(0)` (Склады, default active) → `#sheet1` visible
  - tab `nth(1)` (Документы) → `#sheet2` visible
  - tab `nth(2)` (Остатки) → `#sheet3` visible
- Playwright: `report = page.frame_locator('iframe[src*="integration_three"]')`; `report.locator("a.nav-link").nth(n).click()`; `expect(report.locator(f"#sheet{n}")).to_be_visible()`.

## Checklistdan FARQLAR (gaps)

- Iframe id/name **"report-frame" emas** — id/name bo'sh; `src*="integration_three"` bilan topiladi.
- Sheet tablari index/nom: checklistdagi "document 1/2/3" = sheet indekslari; UI'da named tablar (Склады/Документы/Остатки). Test **index** bilan klik qiladi (data-nomga bog'lanmaslik uchun).
- Login: admin (`authorization(page, who="admin")`), CisLink kabi. Report aktiv filial uchun → admin `switch_filial(filial-pw{code})`.

## Test

- `tests/smoke/test_groups/test_report_grup/test_integration_three.py::run_report_integration_three_check`
- Report group'da **Report-02** (`test_report_02_integration_three`), all-runner `test_05_report_group_runner` zanjirida.
- Screenshot: `skills/smartup-guide/references/forms/screenshots/integration-three/integration_three__report-sheets__desktop__20260611.png`.
