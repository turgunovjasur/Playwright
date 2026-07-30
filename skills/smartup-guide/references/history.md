# Smartup Knowledge History

Bu fayl faqat superseded qoidalar, eski implementatsiya kontraktlari va tarixiy
verification natijalari uchun. Agent joriy test yoki locator yozishda bu
fayldagi ma'lumotni current truth sifatida ishlatmasin.

## Mundarija

- [Entry formati](#entry-formati)
- [Superseded runner scope](#superseded-runner-scope)
- [Removed runner va test entrypointlari](#removed-runner-va-test-entrypointlari)
- [Eski server xatti-harakati](#eski-server-xatti-harakati)

## Entry formati

```markdown
### <mavzu>
Status: superseded
Observed: YYYY-MM-DD
Superseded: YYYY-MM-DD
Source: <fayl, trace yoki live UI>
Replaced by: <joriy reference heading yoki kod path>
- Old behavior: <eski qoida>
```

## Superseded runner scope

### Global smoke/regression scope
Status: superseded
Observed: 2026-05
Superseded: 2026-07
Source: historical smoke skill/reference entries
Replaced by: `scripts/run_tests.py` target modeli va
`skills/smartup-guide/references/smoke-runner.md`
- Old behavior: runner `--regression` yoki `--scope=regression` orqali global
  mode uzatgan.
- Current behavior: global scope konfiguratsiyasi yo'q; suite faqat amaldagi
  smoke targetlari bilan ishlaydi.

## Removed runner va test entrypointlari

### Outer `test_all_runner.py`
Status: superseded
Observed: 2026-05
Superseded: 2026-07-21
Source: historical smoke run va A-group trace yozuvlari
Replaced by: `scripts/run_tests.py`, `tests/smoke/test_setup/test_setup_runner.py`
va `tests/smoke/test_groups/**/test_*_group_runner.py`
- Old behavior: setup va grouplar `tests/smoke/test_all_runner.py` outer chaini
  orqali bitta yoki bir nechta wrapper test sifatida ishga tushirilgan.
- Old evidence: 2026-05-25 run 21 passed bo'lgan; 2026-07-20 A-group locator
  tuzatishi outer runner orqali tekshirilgan.
- Current behavior: har setup/group case alohida pytest item; `scripts/run_tests.py`
  kerakli runner fayllarini bevosita collect qiladi.

### Bitta `test_license.py` moduli
Status: superseded
Observed: 2026-06
Superseded: 2026-07
Source: historical setup structure
Replaced by: `tests/smoke/test_setup/test_buy_license.py` va
`tests/smoke/test_setup/test_attach_license.py`
- Old behavior: license sotib olish va userga ulash bitta
  `tests/smoke/test_setup/test_license.py` modulida saqlangan.

### A2 URL-only diagnostika harnessi
Status: superseded
Observed: 2026-07-07
Superseded: 2026-07-27
Source: historical `tests/smoke/test_life_cycle/test_a2_new_forms.py`
Replaced by: `tests/smoke/test_forms/test_a2_admin_menu_forms.py` va
`tests/smoke/test_forms/test_forms_runner.py`
- Old behavior: 53 ta A2 route `direct`, `via_list` va `skip` modelida URL
  orqali admin/head profillarda diagnostika qilingan.
- Current behavior: faqat real menu/page-link yo'li yozilgan formalar current
  coverage hisoblanadi; 53 formalik inventar joriy test docstringida backlog
  konteksti sifatida saqlanadi.

### 2026-07 runner migratsiya verifikatsiyalari
Status: superseded
Observed: 2026-07-14..2026-07-21
Superseded: 2026-07-30
Source: historical setup va group run natijalari
Replaced by: `skills/smartup-guide/references/smoke-runner.md` current runner
qoidalari
- Old evidence: compact entity codelari bilan setup 02–19 o'tgan, Init Balance
  warehouse preconditionida to'xtagan.
- Old evidence: setup wrapperlari va A/B/C/Report caselari alohida Allure
  testlarga migratsiya qilinganda vaqtinchalik collection sonlari qayd etilgan.
- Current behavior: collection tarkibi `scripts/run_tests.py` targetlari va
  joriy runner fayllaridan olinadi; eski collection sonini hard-code qilma.

## Eski server xatti-harakati

### Xtrade OnlyOffice ulanmagan davr
Status: superseded
Observed: 2026-06-12
Superseded: 2026-06-16
Source: CI run 27402337118
Replaced by: `skills/smartup-guide/references/orders.md` Custom Invoice Report
Template qoidasi
- Old behavior: xtrade'da custom invoice report endpointi OnlyOffice viewer
  o'rniga `.xlsx` attachment qaytargan; popup `url=':'`da qolgan.
- Current behavior: xtrade va smartup.online ikkalasida report OnlyOffice
  spreadsheet iframe ichida ochiladi.
