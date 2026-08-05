# Forms Monitor Signal and Reporting Hardening Design

**Date:** 2026-08-05
**Branch:** `dev1`
**Status:** Approved and implemented on `dev1`; pytest/smoke verification awaits explicit user run permission

## Goal

Make the Forms smoke monitor distinguish an unopened page from an opened but
degraded page, turn the A2 capture channel into a reliable JavaScript-error
signal, and present the same structured cause clearly in terminal, Allure,
system summary, and coverage output without promoting known network/resource
noise to test failures.

## Evidence Behind the Design

- The Forms-03 `Коммерческий дашборд` artifact reached the expected URL, matched
  the expected title, had ready content, and showed a fully rendered dashboard
  screenshot, but one visible `[aria-busy='true']` caused `NOT_OPENED /
  LOADER_NOT_FINISHED`.
- A live Chrome session showed that an A2 route can reach the expected URL and
  then render `Нет доступа к форме ...` within roughly 500 ms. The visible-error
  check and its 1200 ms wait therefore remain correctness checks.
- `Plugin Marketplace` loaded through the real A2 SPA menu in roughly 400 ms.
  Its console was clean, but one image remained broken (`naturalWidth == 0`).
  Resource capture is therefore useful evidence, but not a generic hard-fail
  signal.
- The existing full-group measurement found 204 known `/page/tour/` 404s and no
  real JavaScript exception across 147 active forms. Listing every known 404 in
  the human report hides the actionable failure.
- `form-monitor.json` already carries a precise failure reason, while the
  generated `system-summary.md` falls back to a generic expected/actual message
  and prints empty diagnostic fields.

## Scope

### In Scope

1. Separate blocking loaders from non-blocking busy state.
2. Correct loader failure status semantics.
3. Use one effective JavaScript-error channel per shell.
4. Observe unhandled promise rejections without failing forms yet.
5. Keep network/resource events raw in JSON but aggregate known noise in human
   output.
6. Make system summary use structured form-monitor issues and recognize
   Forms-03 coverage.
7. Include intentionally skipped form inventory in the central monitor report
   and payload.
8. Synchronize the improvement plan and current knowledge-base references.

### Out of Scope

- Splitting the 1467-line `form_monitor.py` into multiple production modules.
  The signal semantics must stabilize before that higher-risk refactor.
- Turning HTTP, resource, or promise-rejection observations into failures.
- Adding or changing unit-test files, because the repository requires separate
  explicit permission for unit-test work.
- Running pytest/smoke suites, because the repository requires an explicit
  `run qil` request.
- Guessing a Commercial Dashboard component selector from a screenshot. A
  route-specific `ready` selector will only be added after its operational-role
  DOM is observed. This implementation fixes the proven false-fail without
  inventing a locator.

## Loader and Readiness Semantics

`loader_visible` will mean a blocking loading surface only:

- visible `.block-ui-overlay`; or
- visible `.smt-skeleton`.

Visible `[aria-busy='true']` will be recorded separately as observational
`busy_visible`/`busy_visible_count`. A nested widget may remain busy while the
page is already usable, so busy state alone will not fail a form.

`AngularBasePage.wait_for_loader()` will continue to wait for both skeleton and
busy signals during navigation. Its appearance probe will observe either
signal, rather than only skeletons. The post-validation monitor state is the
authoritative classification snapshot.

Classification order remains URL → visible application error → JavaScript
error → loader → content → title. When the expected path was reached but a
blocking loader remains, the result becomes:

- status: `OPENED_WITH_DEFECT`;
- reason: `LOADER_NOT_FINISHED`;
- `opened/page_reached`: `true`;
- `usable`: `false`.

`NOT_OPENED` remains reserved for a missing/wrong target route or content that
never became reachable.

## JavaScript Signal Model

The monitor will expose one effective JavaScript error list:

- legacy shell: Playwright `pageerror` is canonical;
- A2 shell: init-script capture-phase `error` events are canonical.

The raw capture arrays may remain in the JSON compatibility surface, but human
output and classification will use only the effective channel. This prevents a
legacy exception from appearing twice when both listeners observe it.

The init script will also listen for `unhandledrejection`. Promise rejections
will be stored and reported separately with a bounded sample and unbounded
count. They remain observation-only until a real Forms baseline measures their
noise.

Resource load errors remain separate from JavaScript exceptions. They never
feed `JS_ERROR` or `usable` in this change.

## Network and Resource Reporting

Raw per-form values remain in `form-monitor.json`, including query-stripped
URLs and true counts. Human text applies two layers:

1. Actionable observations are listed by form.
2. Known noise is aggregated by pattern and total count.

Initial known-noise patterns:

- `/page/tour/` 404s;
- `/a2/assets/i18n/kernel-overlay/` 404s;
- empty-source resource artifacts rendered as `SOURCE` or
  `IMG https://smartup.online/`.

`Plugin Marketplace` image failure is not in the ignore list and remains
visible as an observation.

## Human and Machine Reports

### Per-form and central Allure report

- Keep the precise failure attachment and redacted screenshot.
- Replace contradictory `OCHILMADI` wording for loader defects with
  `OCHILDI, LEKIN NUQSON BOR` through the corrected status.
- Show effective JS source (`pageerror` or `capture`) once.
- Show busy state as observation, not as a blocker.
- Keep passed-form inventory, but move known network noise to one aggregated
  subsection.

### System summary

When a failed pytest item contains `form-monitor.json`, the first actionable
form issue becomes the deterministic reason. The summary will include form
number/title, status, reason code, expected path, actual URL, and the most
relevant readiness facts. Empty generic fields will not be rendered.

Forms-03 will receive its own `prodaja` suite key so combined coverage includes
all three Forms suites.

### Progress log

`SMARTUP_PROGRESS` remains unchanged because it is a machine-consumed contract.
This design does not suppress it at the producer. Human report cleanup happens
in the rendered summary, avoiding a breaking change to Telegram progress.

## Intentionally Skipped Inventory

The active planned count and intentional skip count remain different concepts.
`NOT_CHECKED` continues to mean a planned case that did not execute; it is not
used for registry skips.

A new inventory builder will return:

- normalized active `planned` cases; and
- normalized `skipped` records with title, canonical path, reason, filial, and
  section.

`FormMonitor` receives both lists. The payload adds an `inventory` object and a
top-level skipped-record list, and the human summary prints:

- total inventory;
- active planned count;
- intentional skip count;
- each skipped title/path/reason.

Because this extends the JSON contract, `schema_version` moves from 2 to 3.
Existing result and status fields remain unchanged.

## Code Boundaries

This change deliberately keeps the existing module layout while introducing
small focused helpers:

- loader/busy state helpers near `capture_form_state`;
- effective JS selection near `_capture_state`;
- known-noise classification near report rendering;
- form inventory normalization near `build_form_case_plan`;
- structured form-issue formatting inside `analyze_test_result.py`.

Repeated result construction and the two report-rendering families are noted
for a later module split, but will not be refactored in the same behavioral
change.

## Error Handling and Safety

- Listener installation/read/reset remains best-effort and cannot block the
  Forms suite when the browser object lacks an optional API.
- Signal samples remain bounded while counts remain accurate.
- Query strings are never written to reports.
- Passwords, tokens, credentials, and current session identifiers are not
  added to docs or report text.
- Known-noise filters affect only human rendering, never raw evidence.

## Verification Strategy

Repository authority limits this implementation to non-pytest verification:

1. Parse every changed Python file with `ast.parse`/`py_compile`-equivalent
   syntax checks that do not execute tests.
2. Run the Smartup knowledge-base validator after reference changes.
3. Generate representative monitor/analyzer text from existing artifacts or
   direct pure-function calls without invoking pytest.
4. Inspect the resulting dictionaries/text for:
   - loader defect → `OPENED_WITH_DEFECT`;
   - A2 capture error → one effective `JS_ERROR`;
   - resource error → observation only;
   - known 404s → aggregate human line while raw JSON remains intact;
   - Forms-03 issue → precise deterministic summary;
   - intentional skip inventory → separate from `NOT_CHECKED`.
5. Run the knowledge-base validator and `git diff --check`.

Unit-test changes and pytest execution remain a separately authorized follow-up.

## Acceptance Criteria

- A reached Commercial Dashboard with matching title/content cannot be labeled
  `NOT_OPENED` solely because a nested element is `aria-busy=true`.
- A visible overlay/skeleton after validation produces
  `OPENED_WITH_DEFECT / LOADER_NOT_FINISHED`.
- A captured A2 uncaught exception produces exactly one effective `JS_ERROR`.
- A legacy pageerror produces exactly one effective `JS_ERROR`, even if the
  capture listener also observed it.
- Resource errors and promise rejections remain visible observations and do not
  fail a form.
- Known network noise is aggregated in human output; raw events remain in JSON.
- System summary names the failing form and structured reason without empty
  Expected/Actual/UI rows.
- Forms-01, Forms-02, and Forms-03 are recognized as distinct coverage suites.
- Registry-skipped forms are listed separately from planned-but-not-checked
  forms.
- Plan and knowledge-base files describe the implemented behavior, not the
  superseded one.
