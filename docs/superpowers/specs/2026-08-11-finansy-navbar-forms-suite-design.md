# Финансы Navbar Forms Suite Design

## Goal

Add the complete `Финансы` navbar inventory as `Forms-04`, place it in the
shared Forms runner in Smartup navbar order, and renumber `Справочники` to
`Forms-05`.

## Live Inventory Evidence

The 2026-08-11 Chromium inventory compared the first operational filial with
`Администрирование`.

- Operational direct forms: 42.
  - `Основное`: 13.
  - `Денежный поток`: 4.
  - `Справочники`: 6.
  - `Отчеты`: 19.
- Operational recursive page-link traces: 67, with a maximum depth of five.
- Total active operational plan: 109 cases across 58 unique canonical paths.
- Shell split: 106 legacy cases and three A2 direct forms.
- Administration direct forms: eight. All eight and their two reachable child
  destinations already exist in the operational graph, so admin-only coverage
  is empty and no administration bucket is created.
- `Обороты по контрагентам` opens with visible heading
  `Обороты по контрагентам(6006)`; the inventory stores this title explicitly.
- No intentional skip was discovered during inventory collection.

The three A2 direct forms are:

1. `Конструктор отчетов по финансам` → `anor/rep/mbi/mkcs/operation`.
2. `Отчет о прибылях и убытках` → `anor/rep/mkr/pnl`.
3. `Бухгалтерский баланс` → `anor/rep/mku/balance_sheet`.

## Coverage Model

`Финансы` owns every form reachable through its navbar, regardless of legacy
or A2 shell. Every distinct `menu item + page-link chain` remains a separate
user trace even when another trace reaches the same canonical path.

Administration contributes only canonical forms missing from the operational
filial. Because the current admin graph is a subset of the operational graph,
the suite contains only the operational bucket.

The three A2 forms also belong to the standalone, unnumbered `A2Angular`
aggregate. `Бухгалтерский баланс`, currently missing there, is added; the two
existing Finance definitions remain unchanged. `A2Angular` is not added to the
Forms runner.

Creation icon links are outside this navigation suite. Only named navbar forms
and confirmed breadcrumb page-link traces are included.

## Numbering And Runner Order

Forms numbering follows visible Smartup navbar order:

1. `Forms-01 — Главное`
2. `Forms-02 — Продажа`
3. `Forms-03 — Склад`
4. `Forms-04 — Финансы`
5. `Forms-05 — Справочники`

The `Справочники` leaf filename, runner wrapper, suite name and progress ID are
renumbered together. Reporting keeps the previous
`test_forms_04_spravochniki` identity as a historical compatibility alias.

## Implementation Shape

Create `tests/smoke/test_forms/inventory/finansy.py` with 42 direct definitions
and 67 page-link definitions in one operational bucket. Register `Финансы` in
the central inventory package.

Create `tests/smoke/test_forms/test_04_finansy_forms.py` using the existing
three-step navbar façade:

1. authorize as company admin;
2. load `get_legacy_form_buckets("Финансы")`;
3. call `run_legacy_form_monitoring(...)` with suite identity
   `Forms-04 — Финансы` / `forms_04_finansy`.

Rename the current `Справочники` leaf to
`test_05_spravochniki_forms.py`, then update the Forms runner to contain five
thin sibling wrappers in the order above.

Update current knowledge and infra references that describe Forms order,
numbering, coverage, and reporting identities. Historical run evidence keeps
its original identity with an explicit compatibility note where needed.

## Failure And Reporting Behavior

No new navigation, monitor, hard-check, skip, or reporting architecture is
introduced. Existing behavior remains:

- case shell is selected per inventory definition;
- URL, loader, application error, content readiness and title checks run in
  their existing order;
- all 109 cases share one `FormMonitor` lifecycle;
- inventory normalization reports active and intentional-skip counts;
- terminal, Allure and Telegram reporting use the same suite identity.

## Verification

The user did not request test execution. Verification is therefore limited to:

1. Python syntax and import checks;
2. inventory normalization assertions for 109 planned, zero skipped, three A2
   cases and 58 unique canonical paths;
3. runner source/order and reporting compatibility inspection;
4. Smartup knowledge-base and shared-skill validators;
5. `git diff --check`.

No pytest collection, smoke run, unit-test addition, or unit-test modification
is in scope without a separate `run qil` instruction.

## Non-Goals

- Testing anonymous `+add` creation icons.
- Duplicating operational forms in an administration bucket.
- Adding `A2Angular` to the Forms runner.
- Refactoring FormMonitor, navigation helpers, hard checks, or reporting
  schemas.
