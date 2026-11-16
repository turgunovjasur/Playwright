# Integration №3 NEON (`trade/rep/integration/integration_three`)

## Quick Lookup

### Main parametrlar
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_02_integration_three.py`
- Report menyuda yo'q; joriy session tokeni bilan direct URL orqali ochiladi. Heading `Интеграция №3 NEON`.
- Rejim tugmalari: `Параметры`, `Просмотреть`, `Настройки`; output actionlari `Сформировать`, `HTML`, `EXCEL`, `CSV`, `XML`.
- `Начало периода` default joriy oyning birinchi kuni, `Конец периода` bugungi sana.
- `Характеристики ТМЦ` default `Группа`, `Подтипы характеристик` default `Все`.
- Primary `Сформировать` actioni `run('html', true)` bilan sahifadagi HTML previewni yaratadi; alohida `HTML` actioni download formatidir.
- Report-02 HTML preview sheetlaridan tashqari `EXCEL` actioni orqali non-empty `.xlsx` downloadni ham tekshiradi.
- Lokal XLSX save nomi setup `code`ga emas, run-local UUID suffixga bog'langan.

## Business Rules

### Settings defaultlari
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_02_integration_three.py`
- Documents bo'limida barcode, article code, measure, sold price, input price va section ID default checked.
- Client name turi `Полное название` default, `Альтернативное название` unchecked.
- Balances bo'limida barcode, article code, measure, begin/end amount, section ID, debit va credit quantity default checked.
- Warehouses bo'limida warehouse name va address default checked.
- Settings sahifasi `Настройки типов документов` mappingini `Заказ`dan `Инвентаризация расход`gacha ko'rsatadi.

## Known Locators

### HTML preview sheetlari

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/test_02_integration_three.py:76`
- Test `iframe.report-frame` ichida uchta `button.sheet-tab`ni matnlari va tartibi bo‘yicha tekshiradi: `Склады`, `Документы`, `Остатки`. Birinchi tabda `data-active="true"` kutiladi. Har bir tabga mos `#sheet1`, `#sheet2` yoki `#sheet3` ko‘rinishi tekshiriladi.

## Screenshot Paths

[Arxivlangan HTML preview va uchta sheet](screenshots/integration-three/integration_three__report-sheets__desktop__20260611.png).

## Flow And Tests

`tests/smoke/test_groups/test_report_grup/test_02_integration_three.py::run_report_integration_three_check` period va settings maydonlari, HTML preview va `EXCEL` orqali yuklangan `.xlsx` faylni tekshiradi.

## Known Issues

Preview iframe manzili bo‘sh bo‘lishi mumkin. Test uni `iframe.report-frame` selektori bilan topadi.
