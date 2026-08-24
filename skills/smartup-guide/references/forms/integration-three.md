# Integration №3 NEON (`trade/rep/integration/integration_three`)

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

### Settings defaultlari
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_02_integration_three.py`
- Documents bo'limida barcode, article code, measure, sold price, input price va section ID default checked.
- Client name turi `Полное название` default, `Альтернативное название` unchecked.
- Balances bo'limida barcode, article code, measure, begin/end amount, section ID, debit va credit quantity default checked.
- Warehouses bo'limida warehouse name va address default checked.
- Settings sahifasi `Настройки типов документов` mappingini `Заказ`dan `Инвентаризация расход`gacha ko'rsatadi.

### HTML preview sheetlari
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_02_integration_three.py`
- Preview `iframe.report-frame` ichida render bo'ladi; iframe `src` atributi bo'sh bo'lishi mumkin, shuning uchun `src*="integration_three"` locatoriga tayanilmaydi.
- Aynan uchta `a.nav-link` bor: `Склады`, `Документы`, `Остатки`.
- `Склады` default active va `#sheet1` visible; keyingi tablar mos ravishda `#sheet2` va `#sheet3`ni ko'rsatadi.
- Archived UI evidence: `screenshots/integration-three/integration_three__report-sheets__desktop__20260611.png`.
