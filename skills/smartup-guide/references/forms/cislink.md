# CisLink integration report (`trade/rep/integration/cislink`)

## Quick Lookup

### Joriy main forma
Status: trace-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `test-results/traces/tests_smoke_test_groups_test_report_grup_test_0_group_runner.zip`; `tests/smoke/test_groups/test_report_grup/test_01_cislink.py`
- Qoida: `smartup.online`da CisLink template-based inline formaga migratsiya qilingan; report endi global skip qilinmaydi.
- Heading doim `CisLink(7008)`; `7008` dynamic qiymat emas. Report code’da `open_report(base, "cislink", ...)` orqali ochiladi.
- Main tugmalar: `Сформировать`, `Сформировать(MQ)`, `Шаблоны`, `Закрыть`. `Настройки` tugmasi yo'q.
- Main maydonlar: `Шаблон*`, `Тип периода`, `До*`.
- `Последние 45 дней` default checked, `Пользовательский период` unchecked, `До` default bugungi sana.
- Aktiv template bo'lmasa `Шаблон` bo'sh qolishi live UI'da tasdiqlangan, lekin bu doimiy default invariant emas. Joriy test run uchun yangi template yaratadi.

## Known Locators

### Template list va create forma

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/test_01_cislink.py:45`
- A2’da `Шаблоны` list drawerini, undagi `Добавить` esa create drawerini shu URLda ochadi. Test headingni page scope’da tekshiradi va nested main ichidan `Активный` checkboxini topadi.
- `Название`, `manfid` qatnashadigan label, `Характеристики`, `Продуктовое направление` va `Тип цены` to‘ldiriladi. Test `Табуляция`, `ANSI` hamda `Подтипы характеристик` holatlarini tekshiradi.

## Flow And Tests

### End-to-end test flowi

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_groups/test_report_grup/test_01_cislink.py:31`
- Report-01 admin sifatida setup saqlagan `filial_name`ga o‘tadi, template uchun `price_type_name_UZB`ni ishlatadi. Saqlagach asosiy formadagi `Шаблон` yangi nomga tengligini tekshiradi. Template ro‘yxatidan nomi va `Активный` statusini ham tekshiradi.
- Hisobotni yaratishdan oldin shu template yana aniq tanlanadi. `Сформировать` tugmasidan kelgan faylning `cislink` prefiksi, `.zip` suffiksi va musbat hajmi tekshiriladi.

## Screenshot Paths

N/A — CisLink formasining alohida arxiv rasmi yo‘q.

## Business Rules

Setup filialida mavjud narx turiga tegishli template tanlanadi. Standart period `Последние 45 дней`, `До` joriy sana.

## Known Issues

Eski `Настройки` modaliga asoslangan oqim va global skip [tarixda](../history.md) saqlangan. A2 list va create drawerlari URLni almashtirmaydi.
