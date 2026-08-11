# Склад Navbar Forms Suite Design

## Goal

Add `Склад` as Forms-03 in the shared Forms runner while preserving
`A2Angular` as an independently runnable, cross-navbar aggregate test.

## Coverage Model

Form coverage has two independent axes:

1. Navbar suites own every form visible under one `navbar_tab`, regardless of
   whether the destination uses the legacy shell or A2 Angular.
2. `A2Angular` owns every A2 Angular form, regardless of its `navbar_tab`.

The axes intentionally overlap. An A2 form under `Склад` is tested both by the
`Склад` navbar suite and by the standalone `A2Angular` aggregate. This is not a
duplicate-inventory defect because the suites answer different coverage
questions.

## Runner Composition

`tests/smoke/test_forms/test_0_forms_runner.py` contains exactly three sibling
pytest items, in this order:

1. Forms-01 — `Справочники`
2. Forms-02 — `Продажа`
3. Forms-03 — `Склад`

The runner imports `run_spravochniki_forms`, `run_prodaja_forms`, and
`run_sklad_forms`. It does not import or call `run_a2_angular_forms`.

## Склад Inventory

Create `tests/smoke/test_forms/inventory/sklad.py` as the declarative source
for all `Склад` navbar tracks discovered in the 2026-08-11 live inventory.

The inventory contains:

- Operational filial: 38 direct menu tracks.
  - 30 legacy destinations.
  - 8 A2 destinations, marked with `shell: "a2"`.
- Operational filial: 38 first-level legacy `page_links` tracks.
- Administration: 7 direct A2 report-constructor tracks, marked with
  `shell: "a2"`.
- One intentionally skipped A2 page-link track:
  `Инвентаризации → Инвентаризация КМ`.

The active plan therefore contains 83 cases and the skip plan contains one
case. Repeated canonical destinations reached through different parents remain
separate because their `parent + page_links` user traces are different.

The public inventory registry adds `"Склад"` to
`_LEGACY_FORM_BUCKETS_BY_NAVBAR`. The existing registry name is retained for
compatibility; individual definitions already support a per-case `shell`
override.

## Forms-03 Leaf Test

Create `tests/smoke/test_forms/test_03_sklad_forms.py`, following the existing
navbar leaf pattern:

1. Authorize as company admin.
2. Resolve `get_legacy_form_buckets("Склад")`.
3. Pass the buckets to the shared navbar monitoring façade.

The leaf uses:

- `NAVBAR_TAB = "Склад"`
- suite name `Forms-03 — Склад`
- progress id `forms_03_sklad`
- Allure story `Склад menu formalarini ochish`

One `FormMonitor` lifecycle covers the full mixed-shell suite. Case-level
`shell` controls URL/title validation, while navigation selects `BasePage` or
`AngularBasePage` from the current page shell as it already does today.

## Standalone A2Angular Test

Rename `tests/smoke/test_forms/test_03_a2_angular_forms.py` to
`tests/smoke/test_forms/test_a2_angular_forms.py`.

The standalone test keeps its complete current inventory, including all
`Склад` A2 definitions. It is not numbered as a Forms runner item and is not
collected through `test_0_forms_runner.py`.

Its reporting identity becomes independent of Forms numbering:

- suite name: `A2Angular`
- progress id: `a2_angular`
- standalone pytest entry: `test_a2_angular_forms`

The dedicated `setup-a2-admin` target continues to run the renamed file.
Analyzer and documentation references that identify the old numbered A2 path
or runner item are updated to the standalone identity.

## Monitoring And Failure Behavior

No new monitor implementation is introduced. Existing behavior remains:

- inventory normalization honors `definition["shell"]` before suite default;
- form identity includes shell, navbar, column, filial, track, and path;
- navigation can cross legacy and A2 shells between cases;
- hard checks run in the fixed order URL, loader, application error,
  content-ready, and title;
- a suite precondition failure blocks the affected case and leaves the
  remaining planned cases as not checked;
- `FormMonitor.finish()` runs from the existing `finally` boundary.

## Files

Create:

- `tests/smoke/test_forms/inventory/sklad.py`
- `tests/smoke/test_forms/test_03_sklad_forms.py`

Rename:

- `tests/smoke/test_forms/test_03_a2_angular_forms.py`
  → `tests/smoke/test_forms/test_a2_angular_forms.py`

Modify:

- `tests/smoke/test_forms/inventory/__init__.py`
- `tests/smoke/test_forms/test_0_forms_runner.py`
- `scripts/run_tests.py`
- `scripts/analyze_test_result.py`
- A2 and Forms architecture references that name the old numbered file or
  runner item

## Verification

Verification proceeds in increasing scope:

1. Collection initially fails after the Forms-03 leaf references the missing
   `Склад` inventory, establishing the TDD red state.
2. Forms collection succeeds with exactly three runner items and one separate
   A2 standalone item.
3. Inventory normalization reports 83 planned and one skipped `Склад` case,
   with per-case shell identities intact.
4. `scripts/run_tests.py setup-a2-admin --dry-run` points to
   `test_a2_angular_forms.py`.
5. Relevant repository checks and the Smartup knowledge-base validator pass.
6. The Forms runner and standalone A2 test are executed according to the
   repository smoke-run policy when credentials and environment allow it.

## Non-Goals

- Removing `Склад` forms from `A2Angular`.
- Deduplicating intentional navbar/A2 overlap.
- Adding `A2Angular` to the Forms runner.
- Changing locator, hard-check, reporting schema, or skip semantics.
- Adding creation-form `+add` coverage.
