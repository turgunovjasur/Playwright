# `test_forms` Directory Organization Design

Date: 2026-08-10  
Status: user-approved structure; implementation pending  
Scope: `tests/smoke/test_forms/`

## Goal

`test_forms/` rootida faqat pytest runner va user o'qiydigan leaf testlar
qolsin. Forma inventorysi va FormMonitor texnik infrasi alohida package'larda
saqlansin. Testning amaldagi biznes qamrovi, monitoring natijalari va A2'ning
alohida migratsiya suite'i o'zgarmaydi.

## Target Structure

```text
tests/smoke/test_forms/
├── __init__.py
├── test_0_forms_runner.py
├── test_01_spravochniki_forms.py
├── test_02_prodaja_forms.py
├── test_03_a2_angular_forms.py
├── inventory/
│   ├── __init__.py
│   ├── constants.py
│   ├── spravochniki.py
│   └── prodaja.py
├── monitoring/
│   ├── __init__.py
│   ├── cases.py
│   ├── monitor.py
│   ├── navigation.py
│   ├── reporting.py
│   ├── suite_runner.py
│   ├── checks/
│   └── diagnostics/
└── skipped_forms.py
```

## File Mapping

| Current path | Target path |
|---|---|
| `form_inventory/` | `inventory/` |
| `form_checks/` | `monitoring/checks/` |
| `form_diagnostics/` | `monitoring/diagnostics/` |
| `form_monitor.py` | `monitoring/monitor.py` |
| `forms_suite_runner.py` | `monitoring/suite_runner.py` |
| `form_cases.py` | `monitoring/cases.py` |
| `form_reporting.py` | `monitoring/reporting.py` |
| `flow.py` | `monitoring/navigation.py` |
| `test_01_spravochniki_menu_forms.py` | `test_01_spravochniki_forms.py` |
| `test_02_prodaja_menu_forms.py` | `test_02_prodaja_forms.py` |
| `test_03_a2_angular_menu_forms.py` | `test_03_a2_angular_forms.py` |

`skipped_forms.py` rootda qoladi: u inventory definitionlarini filtrlovchi
kichik, umumiy registry va alohida package talab qilmaydi.

## Dependency Direction

Importlar quyidagi bir tomonlama yo'nalishda bo'ladi:

```text
leaf tests / test_0_forms_runner
        ↓
inventory + monitoring.suite_runner
        ↓
monitoring.monitor + monitoring.navigation
        ↓
monitoring.cases/reporting/checks/diagnostics
```

`checks/` va `diagnostics/` leaf testlarni import qilmaydi. `inventory/` faqat
deklarativ forma ro'yxatlari va public `get_legacy_form_buckets()` API'sini
saqlaydi. `monitoring/__init__.py` kichik public import surface beradi; ichki
modullar bir-birini aniq package path orqali import qiladi.

## Runtime And Discovery Contracts

- `test_0_forms_runner.py` joyi va nomi o'zgarmaydi; `smoke_config.py` hamda
  default Forms target shu runnerni topishda davom etadi.
- Runner uchta leaf `run_*` funksiyasini yangi module pathlardan import qiladi.
- `scripts/run_tests.py`dagi standalone A2 path yangi
  `test_03_a2_angular_forms.py` nomiga yangilanadi.
- `run_spravochniki_forms`, `run_prodaja_forms` va `run_a2_angular_forms`
  public funksiya nomlari o'zgarmaydi.
- Forma sonlari va skiplar o'zgarmaydi: `Справочники` 88 active + 12 skip,
  `Продажа` 38 active + 1 skip; A2 inventory o'z leafida qoladi.

## Compatibility Boundary

Yangi unit test yozilmaydi, mavjud unit testning scenario, fixture va
expectationlari o'zgartirilmaydi hamda unit suite ishlatilmaydi. Structural
move sabab `tests/unit/test_form_flow.py`dagi eski module importlari yangi
canonical pathlarga almashtiriladi; bu yangi test yoki test logikasi emas.
Eski root module nomlari uchun parallel wrapper fayllar saqlanmaydi: rootni
yana texnik fayllar bilan to'ldirish target strukturaga zid. Repositorydagi
boshqa haqiqiy import consumerlar ham yangi canonical pathga o'tkaziladi;
tarixiy matn yoki report sample stringlari faqat runtime consumer bo'lsa
yangilanadi.

## Error Handling

Bu structural refactor runtime error handlingni o'zgartirmaydi. Authorization,
filial preconditionlari, per-form checks, HTTP `4xx/5xx` diagnostikasi va
`monitor.finish()` lifecycle'i aynan hozirgi semantikada qoladi. Faqat import
path va fayl joylashuvi o'zgaradi.

## Documentation Updates

Joriy canonical pathlarni tilga olgan `skills/write-test/` va
`skills/smartup-guide/` reference'lari yangi strukturaga yangilanadi. Eski
pathlar tarixiy entryning dalil qismi bo'lsa saqlanishi mumkin; current truth
sifatida ko'rsatilmaydi.

## Verification

Foydalanuvchi qaroriga ko'ra unit test yozilmaydi va unit test suite
ishlatilmaydi. Foydalanuvchi alohida `run qil` demagani uchun pytest/smoke ham
ishga tushirilmaydi. Quyidagi statik tekshiruvlar bajariladi:

1. O'zgargan Python modullarini `py_compile` qilish.
2. `test_0_forms_runner` va standalone A2 leaf importlarini tekshirish.
3. Inventory sonlari va shell/navbar kontraktlarini Python assertion bilan
   tekshirish.
4. Runtime kod va current knowledge-base ichida eski canonical import/pathlar
   qolmaganini `rg` bilan tekshirish.
5. Smartup knowledge-base validatorini bajarish.
6. `git diff --check` bilan whitespace xatolarini tekshirish.

## Out Of Scope

- FormMonitor logikasini soddalashtirish yoki qayta yozish.
- Forma definitionlari va skip qarorlarini o'zgartirish.
- A2 testining ichki 584 qatorlik inventar/orchestrationini ajratish.
- Yangi unit test yaratish yoki mavjud unit test scenario/fixture/expectationini
  o'zgartirish.
- Smoke testni ishga tushirish.
