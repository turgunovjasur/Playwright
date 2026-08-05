# Forms Monitor Signal and Reporting Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct Forms loader/JS classification and make Allure/system coverage reports concise, structured, and explicit about intentional skips.

**Architecture:** Preserve the existing `FormMonitor` orchestration and public result fields while separating blocking loaders from observational busy state, selecting one effective JavaScript-error channel by shell, and filtering noise only at human-rendering boundaries. Extend the monitor payload to schema version 3 with an explicit inventory while keeping raw network/resource evidence.

**Tech Stack:** Python 3, Playwright sync API, pytest/Allure integration code, Markdown knowledge base.

## Global Constraints

- Work only on branch `dev1`.
- Do not create or modify unit-test files; the user approved the no-unit-test design.
- Do not run pytest, smoke runners, or test collection without a separate explicit `run qil` request.
- Verify with Python syntax parsing, focused pure-function probes, knowledge-base validation, artifact inspection, and `git diff --check`.
- Keep network/resource and promise-rejection signals observation-only.
- Do not add credentials, query strings, or current session identifiers to output or documentation.
- Do not split `form_monitor.py` into new production modules in this change.

---

### Task 1: Correct loader and effective JavaScript semantics

**Files:**
- Modify: `tests/smoke/test_forms/form_monitor.py`
- Modify: `tests/smoke/test_forms/flow.py`
- Modify: `utils/angular_base_page.py`

**Interfaces:**
- Consumes: existing `capture_form_state(page, ready=None)`, `FormMonitor._capture_state(case)`, and `AngularBasePage.wait_for_loader()`.
- Produces: canonical `state["js_errors"]`, `checks["js_error_source"]`, observational busy/promise fields, and corrected loader status.

- [ ] **Step 1: Extend capture script with observation-only promise rejection storage**

Add bounded arrays and unbounded counts alongside the current capture arrays:

```javascript
window.__formMonitorPromiseRejections = [];
window.__formMonitorPromiseRejectionCount = 0;
window.addEventListener("unhandledrejection", (event) => {
  const reason = event && event.reason;
  const message = reason && reason.message ? reason.message : String(reason || "noma'lum promise rejection");
  window.__formMonitorPromiseRejectionCount += 1;
  if (window.__formMonitorPromiseRejections.length < SAMPLE_LIMIT) {
    window.__formMonitorPromiseRejections.push(message);
  }
}, true);
```

Extend read/reset/empty structures with `promise_rejections` and
`promise_rejection_count`.

- [ ] **Step 2: Separate blocking loader from busy observation**

In `capture_form_state`, set `loader_visible` only from:

```python
(".block-ui-overlay:visible", ".smt-skeleton:visible")
```

Record visible `[aria-busy='true']` elements separately as `busy_visible` and
`busy_visible_count`. Do not feed these fields into `usable` or classification.

- [ ] **Step 3: Select one effective JS channel per shell**

In `_capture_state`:

```python
capture = state["capture_signals"]
if "/a2/" in state["actual_url"]:
    state["js_errors"] = list(capture["js_errors"])
    state["js_error_count"] = capture["js_error_count"]
    state["js_error_source"] = "capture"
else:
    state["js_errors"] = list(self.js_errors)
    state["js_error_count"] = self.js_error_count
    state["js_error_source"] = "pageerror"
```

Make `_case_checks` use state counts/source. Preserve raw capture fields for
schema compatibility, but never render the same JS exception in both human
sections.

- [ ] **Step 4: Correct loader classification**

Change `LOADER_NOT_FINISHED` from `NOT_OPENED` to `OPENED_WITH_DEFECT` when the
expected path was reached. Keep `opened=True`, `page_reached=True`, and
`usable=False`.

- [ ] **Step 5: Improve loader appearance wait**

In `AngularBasePage.wait_for_loader`, probe a combined visible loader locator:

```python
loader = root.locator(".smt-skeleton:visible, [aria-busy='true']:visible")
```

Wait briefly for either signal to appear, then wait for both selectors to have
zero visible matches. This retains navigation waiting while post-validation
busy state remains observational.

- [ ] **Step 6: Update per-form detail text**

Show effective JS count/source once, plus observational busy, promise rejection,
and resource fields. Remove the duplicate human `Capture JS exceptionlar`
line.

- [ ] **Step 7: Run static Task 1 verification**

Run an AST parse on the three files and a direct `classify_form_failure(...)`
probe whose reached/ready state has `loader_visible=True`; expected status is
`OPENED_WITH_DEFECT` with `LOADER_NOT_FINISHED`. Do not invoke pytest.

---

### Task 2: Aggregate network/resource noise in human reports

**Files:**
- Modify: `tests/smoke/test_forms/form_monitor.py`

**Interfaces:**
- Consumes: raw `failed_requests`, capture resource errors, and promise rejections from result checks.
- Produces: concise actionable sections plus known-noise aggregate lines; raw JSON remains unchanged.

- [ ] **Step 1: Add exact known-noise classifiers**

Implement helpers that return stable bucket names only for:

```python
"/page/tour/" -> "legacy tour 404"
"/a2/assets/i18n/kernel-overlay/" -> "A2 optional i18n 404"
"SOURCE" or "IMG https://smartup.online/" -> "empty resource source"
```

Do not classify the Plugin Marketplace `m:load_image_v2` image as known noise.

- [ ] **Step 2: Render actionable network events only per form**

Refactor `_page_event_lines` so JS errors and non-noise failed requests are
listed by form, while known request buckets become one count line each.

- [ ] **Step 3: Render observation-only capture events without duplicate JS**

Replace `_capture_js_error_lines` with an observation renderer for actionable
resource errors and promise rejections. Aggregate exact empty-source resource
noise.

- [ ] **Step 4: Run focused renderer probes**

Call the render helpers with representative dictionaries and assert through a
small read-only script that `/page/tour/` appears only in an aggregate label,
while `m:load_image_v2` remains tied to `Plugin Marketplace`.

---

### Task 3: Add intentional skip inventory without conflating NOT_CHECKED

**Files:**
- Modify: `tests/smoke/test_forms/skipped_forms.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`
- Modify: `tests/smoke/test_forms/test_01_spravochniki_menu_forms.py`
- Modify: `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py`
- Modify: `tests/smoke/test_forms/test_03_prodaja_menu_forms.py`

**Interfaces:**
- Produces: `build_form_case_inventory(...) -> {"planned": list, "skipped": list}`.
- Preserves: `build_form_case_plan(...) -> list` as a compatibility wrapper.
- Extends: `FormMonitor(..., skipped_cases=None)` and payload `schema_version=3`.

- [ ] **Step 1: Expose skipped metadata by canonical path**

Add `skipped_form(path)` returning a copied registry record or `None`.

- [ ] **Step 2: Build active and skipped records together**

Implement `build_form_case_inventory` with the same normalization parameters as
`build_form_case_plan`. Active numbering remains contiguous; skipped records
receive title, expected path, reason, filial, navbar tab, and section but no
active number.

- [ ] **Step 3: Preserve the existing plan-builder API**

Make `build_form_case_plan` return only `inventory["planned"]` so existing
external callers keep their contract.

- [ ] **Step 4: Pass skipped inventory from all three suites**

Each suite collects `inventory["planned"]` and `inventory["skipped"]` in the
same loops that currently call `build_form_case_plan`, then passes the combined
skipped list to `FormMonitor`.

- [ ] **Step 5: Extend monitor payload and summary**

Add:

```json
{
  "schema_version": 3,
  "inventory": {"total": 100, "active": 88, "intentionally_skipped": 12},
  "skipped": [{"title": "...", "expected_path": "...", "reason": "..."}]
}
```

Render a separate `SKIP QILINGAN FORMALAR` section. Do not add these records to
`results`, status counts, or `NOT_CHECKED`.

- [ ] **Step 6: Run inventory probes**

Load the three suite definition constants without running pytest collection,
build inventories, and verify active/skip totals are 88/12, 21/1, and 38/1.

---

### Task 4: Make system summary consume structured form issues

**Files:**
- Modify: `scripts/analyze_test_result.py`

**Interfaces:**
- Consumes: schema-v2/v3 `form-monitor.json` attachments.
- Produces: precise `failed_tests[].reason`, richer `form_issues`, Forms-03 coverage key `prodaja`, and concise Markdown.

- [ ] **Step 1: Recognize Forms-03**

Add `"prodaja": "Продажа"` to `FORM_SUITE_LABELS` and detect
`test_forms_03_prodaja`, `test_03_prodaja_menu_forms`, or `Forms-03` identity.

- [ ] **Step 2: Preserve structured form evidence**

Extend `_form_monitor_issues` with expected path, actual URL, page reached,
content readiness, loader state, busy state, and visible UI error. Read all
fields defensively so schema-v2 artifacts still work.

- [ ] **Step 3: Prefer the first form issue as deterministic reason**

Format a concise reason such as:

```text
022 — Коммерческий дашборд: LOADER_NOT_FINISHED — Forma yuklanish indikatori belgilangan vaqtda tugamadi.; target URLga yetilgan; title/kontent mos.
```

Auth diagnostics remain higher priority than form issues.

- [ ] **Step 4: Hide empty Markdown fields and show form issues**

Render only non-empty generic diagnostic rows. Add a `Form issues` subsection
with title/status/reason, expected path, and actual URL.

- [ ] **Step 5: Probe the existing failed Allure artifact**

Run `collect_allure_results`/`build_deterministic_summary` against the current
artifact directory and verify the local summary names `Коммерческий дашборд`
and `LOADER_NOT_FINISHED`, with no empty Expected/Actual/UI rows.

---

### Task 5: Synchronize plan and knowledge base

**Files:**
- Modify: `docs/forms-monitor-improvement-plan-2026-08-04.md`
- Modify: `skills/smartup-guide/references/ui-patterns.md`
- Modify: `skills/smartup-guide/references/a2-migrated-forms.md`
- Modify: `skills/maintain-test-infra/references/reporting.md`
- Modify: `skills/maintain-test-infra/references/summaries.md`

**Interfaces:**
- Documents only current implemented behavior and keeps historical measurements labeled as history.

- [ ] **Step 1: Update the improvement plan header/status**

Correct current line counts and phase commit/status entries, move completed
Phase 5 out of misleading “remaining work” wording, and replace the Phase 7
decision text with the implemented canonical-channel behavior.

- [ ] **Step 2: Record loader/busy and browser evidence**

Add a provenance-complete `live-ui-confirmed` entry to `ui-patterns.md` covering
permission alert timing, the broken Plugin Marketplace image with clean
console, and the non-blocking `aria-busy` lesson from the Allure screenshot.

- [ ] **Step 3: Update A2 current behavior**

Document that A2 capture is the effective JS channel, generic busy is
observation-only after validation, and route-specific readiness requires a
confirmed selector.

- [ ] **Step 4: Update reporting and summary contracts**

Document Forms-03 coverage, schema version 3 inventory, human noise aggregation,
and structured form-issue system summaries.

- [ ] **Step 5: Validate documentation**

Run:

```bash
./.venv/bin/python skills/smartup-guide/scripts/validate_knowledge_base.py
```

Expected: exit code 0.

---

### Task 6: Final static verification and review

**Files:**
- Inspect all modified files.

**Interfaces:**
- Produces: evidence that code parses, focused contracts behave as designed, docs validate, and the diff is clean.

- [ ] **Step 1: Parse changed Python files**

Use a temporary standalone script under `/private/tmp` or a short existing
workspace script to call `ast.parse` on every changed `.py` file. Expected:
all files parse.

- [ ] **Step 2: Run focused pure-function probes**

Exercise loader classification, JS shell selection inputs, report noise
aggregation, inventory counts, and analyzer summary against existing artifacts.
Expected: all acceptance checks print `OK` and no test runner starts.

- [ ] **Step 3: Run repository-safe validators**

Run the knowledge-base validator and `git diff --check`. Expected: both exit 0.

- [ ] **Step 4: Review the final diff**

Confirm no unit-test file changed, no credential/session value entered docs,
schema-v2 analyzer reads remain defensive, and unrelated files are untouched.

- [ ] **Step 5: Commit implementation**

Commit the reviewed implementation on `dev1` with a concise message describing
loader, signal, and report hardening.
