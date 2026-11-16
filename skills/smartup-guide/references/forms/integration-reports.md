# Integration reportlar (`trade/rep/integration/*`)

Alohida dossierlar: [cislink.md](cislink.md), [integration-three.md](integration-three.md).

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [Umumiy navigatsiya va filial](#umumiy-navigatsiya-va-filial)
- [Download tekshiruvi](#download-tekshiruvi)
- [SalesWork](#saleswork-saleswork)
- [Optimum](#optimum-optimum)
- [Spot2D](#spot2d-spot)
- [Integration Two / Monolith](#integration-two--monolith-integration_two)

## Quick Lookup

### Umumiy navigatsiya va filial

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/flow_report/report_helpers.py:16`; `tests/smoke/test_groups/test_report_grup/test_01_cislink.py:31`; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py:71`
- `open_report()` `base.open_route("trade/rep/integration/<report>")`ni chaqiradi. Report-02–05 birinchi operatsion filialga, Report-06 `Администрирование`ga o‘tadi. [CisLink](cislink.md) setup saqlagan filial nomini ishlatadi.
- Template va lokal download nomlari uchun run-local UUID suffix ishlatiladi.

## Flow And Tests

### Download tekshiruvi
Status: code-confirmed
Verified: 2026-08-24
Source: `tests/smoke/test_groups/test_report_grup/flow_report/report_helpers.py`
- `generate_and_verify_download()` accessible button nomi bilan actionni bosadi, download failure yo'qligini, filename prefiksini va non-zero fayl hajmini tekshiradi.
- Filename aniq prefiksi noma'lum outputlarda helper kutilgan suffixni (`.xlsx`/`.xml`) tekshiradi; timeoutda URL, Biruni alert va full-page screenshot Allurega biriktiriladi.
- Downloadlar `test-results/downloads/` ostiga saqlanadi.

## SalesWork (`saleswork`)

### Main va template contract
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_03_saleswork.py`
- Main tugmalar: `Экспорт`, `Сформировать(MQ)`, `Шаблоны`, `Закрыть`; period defaulti joriy oy boshi–bugun.
- Main `Шаблон` b-inputi tanlangan template nomini ko'rsatadi.
- 2026-08-20 legacy kuzatuvida list route `saleswork_template_list`, create route `saleswork_template+add`; list create actioni `Создать` deb nomlangan.
- Create required maydonlari `Название` va `Продуктовое направление`.
- Defaultlar: `Активный`, barcha product subtype, report type `MarevenFoodCentral`; `ParentCompanies`, `Outlets`, `ArchivedStocks`, `LocalProducts`, `SalOuts`, `SalIns` checked, `OutletDebts` unchecked.
- Test har bir run uchun UUID suffixli yangi template yaratadi, main formada aynan shu template tanlanganini tekshiradi va uni mavjud template bilan almashtirmaydi. `Экспорт` natijasi `sales_work` prefiksli non-empty ZIP.

## Optimum (`optimum`)

### Main va settings contract
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_04_optimum.py`
- Main tugmalar: `Сформировать`, `Сформировать(MQ)`, `Настройки`, `Закрыть`.
- Period defaulti joriy oy boshi–bugun; UI `Выбранный период не должен превышать 3 месяца` cheklovini ko'rsatadi.
- Live main formada `Все филиалы` checkboxi yo'q; oldingi all-filials/sticky-overlay taxmini joriy kontrakt emas.
- Settingsdagi real label `Продуктовое группа`; product subtype default `Все`.
- Sakkiz prefiks: warehouse transfer out/in, inventory write-off/receipt, distributor site out/in, production write-off/receipt; default/saqlanadigan qiymatlar `1`–`8`.
- `Сформировать` natijasi `optimum` prefiksli non-empty ZIP.

## Spot2D (`spot`)

### Main, settings va template contract
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_05_spot.py`
- Heading `Spot2D(<dynamic-id>)`; tugmalar `Сформировать`, `Настройки`, `Шаблоны`.
- `Последние 45 дней` default checked, custom period unchecked, `Дата окончания периода` default kechagi sana.
- Settingsda `Разделить по дням (файл receive)` va `Дублировать Код клиента ERP (ID#ID)` default unchecked; VAT default `Системный ввод НДС(%)`; `Сброс настроек` actioni mavjud. Test destructive resetni bosmaydi.
- 2026-08-20 legacy kuzatuvida list route `spot_template_list`, create route `spot_template+add`; list create actioni `Добавить`.
- Create required maydonlari `Название` va `Продуктовое направление`; product subtype `Все`, status `Активный`.
- Template form delivery, stocks, clients, ttoptions, ta, cancellations, receive, sku va warehouse file mappinglarini ko'rsatadi.
- Test har bir run uchun UUID suffixli yangi template yaratadi, main formada aynan shu template tanlanganini tekshiradi va uni mavjud template bilan almashtirmaydi. `Сформировать` natijasi `Spot2D` prefiksli non-empty ZIP.

## Integration Two / Monolith (`integration_two`)

### Settings contract
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py`
- Heading `Интеграция с системой монолит`; tugmalar `Генерировать`, `Настройки`, `Закрыть`.
- Required settings: `User`, `URL`, `Тип цены`, `Ед. измерения (количество)`, `Ед. измерения (блок)`, `Характеристика ТМЦ`; `ИД компании` ham ko'rinadi.
- `Тип цены` setup `code` bilan qidirilmaydi;
  `BasePage.b_input(clear=True, select_first=True)` birinchi mavjud optionni
  tanlaydi.
- Checkboxlar: `Редактирование контрагента`, `Отправлять данные по всем заказам`, `Игнорировать обновление существующих заказов`, `Отображать код владельца`.
- Combined export flaglari default `Нет`; person identity default `код лица`.

### Oltita exchange mode
Status: live-ui-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py`
- `Импорт заказа` va `Экспорт статусов` period maydonlarini ko'rsatmaydi.
- `Экспорт заказа`, `Экспорт остатков`, `Экспорт приходов`, `Экспорт внутренних перемещений` `Начало периода` va `Конец периода` maydonlarini ko'rsatadi; ikkalasi default bugungi sana.
- `Экспорт приходов` qo'shimcha `Исключение по организациям (только для экспорта приходов)` maydonini ko'rsatadi.
- Oldingi test faqat to'rtta modeni qamragan; `Экспорт остатков` va `Экспорт внутренних перемещений` endi testga qo'shilgan.

### Endpoint preconditioni va XML natijalari

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/test_06_integration_two.py:80`; `tests/smoke/test_groups/test_report_grup/flow_report/report_helpers.py:53`
- Report-06 konfiguratsiyadagi `User` va HTTP(S) `URL` qiymatini tekshiradi. `INTEGRATION_TWO_XML_URL` berilgan bo‘lsa endpoint maydoniga shu qiymat kiritiladi. Olti mode, jumladan `Экспорт заказа`, yuklangan XML bilan tekshiriladi; download helperi uni parse qiladi va HTML rootni rad etadi.
- `INTEGRATION_TWO_DEMO=1` bo‘lsa Monolith GET/POST proxy javoblari lokal mockdan keladi. Bu rejim tashqi endpoint natijasini tekshirmaydi.

### Export order error modal

Eski deploymentda user `Экспорт заказа` uchun Biruni error modalini bildirgan. Joriy Report-06 bu mode uchun ham XML talab qiladi. Eski natija [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi)da.

## Screenshot Paths

[Integration Two uchun kirish rad etilgan arxiv holati](screenshots/integration-reports/integration-two__access-denied__desktop-2880x1566.png).

## Known Locators

Report-06 mode’ni nomlangan radio orqali tanlaydi. SalesWork va Spot testlarida A2 template drawerlarining headinglari page scope’da tekshiriladi. [SalesWork](../../../../tests/smoke/test_groups/test_report_grup/test_03_saleswork.py), [Spot](../../../../tests/smoke/test_groups/test_report_grup/test_05_spot.py).

## Business Rules

SalesWork uchun `Экспорт`, Optimum va Spot uchun `Сформировать` ZIP qaytarishi kutiladi. Monolith mode’laridan XML chiqishi kerak.

## Known Issues

[Integration Two access-error rasmi](#screenshot-paths) forma ochilmagan deploymentga tegishli. Report-06 admin filialini, konfiguratsiyadagi user va endpointni talab qiladi.
