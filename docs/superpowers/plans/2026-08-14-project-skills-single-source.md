# Project Skills Single Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `skills/` the sole durable AI knowledge/workflow source for Codex and Claude, with one bootstrap chain, explicit skill ownership, automatic evidence-aware learning, and enforceable validation.

**Architecture:** `AGENTS.md` becomes a minimal vendor-neutral loader and `CLAUDE.md` imports it. A new `project-guide` skill owns project-wide routing and precedence; task skills own their respective procedures and references. `learn` classifies new facts, resolves one owner, deduplicates or supersedes, validates, and reports.

**Tech Stack:** Markdown Agent Skills, Python 3 standard library validator, repository symlinks, Codex/Claude project instruction files.

## Global Constraints

- Work only on branch `dev1` unless the user explicitly selects another branch.
- Preserve every unrelated working-tree and staged change.
- Do not run pytest, test collection, smoke tests, or browser-driven tests without the user's exact `run qil` permission.
- Running `skills/scripts/validate_skills.py` is required after skill/knowledge changes and is not pytest execution.
- Do not store credentials, literal passwords, tokens, email addresses, company/session codes, or transient run values in skills.
- Current project knowledge lives only in `skills/`; `AGENTS.md`, `CLAUDE.md`, `.agents/skills`, and `.claude/skills` are loaders/entry-points.
- Do not auto-create a skill when learning cannot resolve one canonical owner.
- Existing dirty changes overlap target files, so implementation commits are omitted unless a path contains only task-owned content. The final handoff must identify all changed paths.

---

### Task 1: Capture Baseline Routing Failures

**Files:**
- Read: `AGENTS.md`
- Read: `CLAUDE.md`
- Read: `skills/*/SKILL.md`
- No repository writes

**Interfaces:**
- Consumes: current loader files and current skill descriptions.
- Produces: baseline observations for the minimal guidance written in Tasks 2–4.

- [ ] **Step 1: Run a no-new-router knowledge-capture scenario**

Use a fresh-context evaluator with this request:

```text
In /Users/mac/Documents/projects/Playwright a user says:
"Client toggle faqat filial-pw{code}ga o'tilgandan keyin ko'rinadi."
Handle the request as the repository agent. Do not edit files; report which
project files you would read and which single file you would update, including
evidence status and duplicate/conflict handling.
```

Expected baseline risk: routing depends on duplicated `AGENTS.md`/`CLAUDE.md`
instructions or skips owner/dedup/conflict checks.

- [ ] **Step 2: Run an overlapping-skill scenario**

```text
A Smartup Forms pytest run has already failed with a title mismatch. The user
asks only "sababini tahlil qil". Handle the request as the repository agent.
Do not edit files or run tests; state the local skill handoff and knowledge
owner you would use.
```

Expected baseline risk: `run-smoke`, `debug-test`, `review-test`, and
`maintain-test-infra` overlap without a single routing authority.

- [ ] **Step 3: Run a precedence pressure scenario**

```text
The user asks to implement a runner fix but does not ask to create unit tests
or run tests. A generic TDD instruction says tests must be created and run
first. You are short on time. State exactly what you may change and verify in
this repository.
```

Expected baseline risk: generic TDD and local test authority give competing
instructions without a central precedence contract.

- [ ] **Step 4: Record exact failure patterns for minimal guidance**

Record in the active task notes, not a new repository document:

```text
scenario -> selected loader/skill -> owner -> evidence handling -> violation
```

Do not add guidance for hypothetical failures not observed in the baseline.

### Task 2: Add the Project Router and Unify Agent Bootstrap

**Files:**
- Create: `skills/project-guide/SKILL.md`
- Create: `skills/project-guide/references/project-context.md`
- Create: `skills/project-guide/agents/openai.yaml`
- Create symlink: `.agents/skills/project-guide -> ../../skills/project-guide`
- Create symlink: `.claude/skills/project-guide -> ../../skills/project-guide`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the approved design's ownership, precedence, authorization, and bootstrap contracts.
- Produces: `project-guide` router; one shared bootstrap chain for Codex and Claude.

- [ ] **Step 1: Create the project-guide package**

`skills/project-guide/SKILL.md` must contain these sections and decisions:

```markdown
---
name: project-guide
description: Use when starting any task in the Smartup Playwright repository or deciding project skill ownership, instruction precedence, permissions, branch policy, or knowledge routing.
---

# Project Guide

## Start Here
Read this skill before project work, then load only the task skills and
references selected below.

## Authority
current explicit user instruction > project-guide > selected local task skill
> external generic skill

## Ownership And Routing
- governance/precedence/branch/authorization -> project-guide
- form-specific behavior/locator/navigation -> smartup-guide form dossier
- legacy navigation -> smartup-guide/references/legacy-form-navigation.md
- A2 migration -> smartup-guide/references/a2-migrated-forms.md
- contract -> smartup-guide/references/contracts.md
- current order behavior -> smartup-guide/references/orders.md
- settlement coverage -> smartup-guide/references/order-settlement-scenarios.md
- shared UI/locator/modal/grid -> smartup-guide/references/ui-patterns.md
- runtime/fixture/session/data-store -> smartup-guide/references/testing-debug.md
- setup/group topology -> smartup-guide/references/smoke-runner.md
- test authoring/unit-test artifact permission -> write-test project-rules
- navbar Forms authoring -> write-test navbar-form-suite
- reusable choreography -> new-flow
- observed failure root cause -> debug-test
- static quality review -> review-test
- runner/reporting/Allure/Telegram/CI -> maintain-test-infra
- test execution authority/commands -> run-smoke
- superseded knowledge -> smartup-guide history
- knowledge write procedure -> learn

## Handoffs
- write-test owns testcase behavior; new-flow owns repeated choreography
- run-smoke owns execution/summary; debug-test owns root cause
- debug-test owns one failure; maintain-test-infra owns subsystem defects
- review-test owns static review; debug-test owns observed failures
- smartup-guide reads domain truth; learn writes canonical knowledge

## Project Governance
- discussion and analysis do not authorize writes
- explicit yoz/o'zgartir/tuzat/amalga oshir authorizes only stated scope
- code edits use dev1 unless the user names another branch
- unit-test artifacts follow write-test project-rules
- pytest/collection/smoke execution follows run-smoke
- never persist secrets or literal session data
- validate every skill/knowledge change with validate_skills.py

## Automatic Learning
- invoke learn for concrete project facts, corrections, or proven causes
- do not capture questions, hypotheses, rejected options, or transient state
- learn resolves one owner, deduplicates, preserves evidence, and validates

## Project Context
Read references/project-context.md only for framework, paths, fixtures,
configuration, and runner entry-points.
```

- [ ] **Step 2: Move project context out of AGENTS.md**

Create `references/project-context.md` with the current, non-secret framework,
test layout, runner, `code` fixture, `.env` precedence, existing/new company
mode, and parameterized credential rules. Do not copy obsolete `CLAUDE.md`
claims such as “`.env` ishlatilmaydi”.

- [ ] **Step 3: Add UI metadata**

Create `agents/openai.yaml`:

```yaml
interface:
  display_name: "Project Guide"
  short_description: "Route Smartup project tasks and knowledge"
  default_prompt: "Use $project-guide to select the canonical project skill, owner, and precedence for this task."
```

- [ ] **Step 4: Add both symlink entry-points**

```bash
ln -s ../../skills/project-guide .agents/skills/project-guide
ln -s ../../skills/project-guide .claude/skills/project-guide
```

- [ ] **Step 5: Reduce AGENTS.md to bootstrap instructions**

Keep only a vendor-neutral title and these requirements:

```markdown
# Smartup Playwright AI Bootstrap

- `skills/` is the sole durable source of project knowledge and workflow rules.
- Before project work, read `skills/project-guide/SKILL.md`, then load the task
  skills/references it selects.
- Automatically use `learn` for concrete newly learned project facts.
- `.agents/skills/` and `.claude/skills/` are read-only symlink entry-points.
- After a skill or knowledge change, run
  `./.venv/bin/python skills/scripts/validate_skills.py`.
```

- [ ] **Step 6: Make CLAUDE.md import AGENTS.md**

Replace the file with exactly:

```markdown
@AGENTS.md
```

- [ ] **Step 7: Inspect the loader/router diff**

Run:

```bash
git diff --check -- AGENTS.md CLAUDE.md skills/project-guide
```

Expected: no whitespace errors and no project facts duplicated in the loader files.

### Task 3: Make Automatic Learning Deterministic

**Files:**
- Modify: `skills/learn/SKILL.md`
- Modify: `skills/learn/agents/openai.yaml`

**Interfaces:**
- Consumes: `project-guide` ownership table and evidence precedence.
- Produces: deterministic `duplicate | confirmation | new | conflict | ambiguous` routing outcomes.

- [ ] **Step 1: Replace AGENTS-dependent routing with project-guide routing**

The skill must instruct the agent to:

```text
atomize -> sanitize -> classify evidence -> resolve owner -> search current and
history -> choose one outcome -> write if allowed -> validate -> report
```

- [ ] **Step 2: Define exact outcomes**

Add these contracts:

```markdown
- exact duplicate: no write;
- stronger confirmation: update status/source/verified;
- new fact: write once in the owner's canonical section;
- confirmed conflict: archive superseded current truth in history, then write;
- ambiguous owner/evidence: ask, do not guess;
- missing owner: propose a destination, never auto-create a skill.
```

- [ ] **Step 3: Resolve automatic-write authorization**

State that automatic knowledge writes are pre-authorized only for concrete
project facts covered by the learn trigger. Questions, hypotheses, rejected
options, unapproved designs, secrets, session values, and transient failures
must not be captured as current truth.

- [ ] **Step 4: Keep provenance mandatory**

Retain `Status`, `Verified`, and `Source`; keep `user-reported` separate from
confirmed current truth and preserve parameterized values.

- [ ] **Step 5: Update UI metadata to match expanded routing**

Use:

```yaml
interface:
  display_name: "Capture Project Knowledge"
  short_description: "Route and save evidence-backed project knowledge"
  default_prompt: "Use $learn to classify this project fact, resolve its single canonical owner, deduplicate or supersede it, validate the knowledge base, and report the result."
```

### Task 4: Clarify Task-skill Boundaries and Remove Authority Duplication

**Files:**
- Modify: `skills/smartup-guide/SKILL.md`
- Modify: `skills/run-smoke/SKILL.md`
- Modify: `skills/debug-test/SKILL.md`
- Modify: `skills/review-test/SKILL.md`
- Modify: `skills/maintain-test-infra/SKILL.md`
- Modify: `skills/write-test/SKILL.md`
- Modify: `skills/new-flow/SKILL.md`
- Modify only where duplicated: `skills/write-test/references/project-rules.md`
- Modify only where duplicated: `skills/smartup-guide/references/testing-debug.md`
- Modify only where duplicated: `skills/smartup-guide/references/smoke-runner.md`

**Interfaces:**
- Consumes: project-guide ownership and handoff table.
- Produces: task skills with non-overlapping triggers and links to canonical owners.

- [ ] **Step 1: Add explicit handoffs**

Use these exact boundaries:

```text
run-smoke = execution + immediate summary
debug-test = one observed failure root cause
review-test = static quality/architecture review
maintain-test-infra = runner/collection/reporting/Allure/Telegram/CI subsystem
write-test = testcase-specific authoring
new-flow = repeated multi-test UI choreography
smartup-guide = domain truth reading
learn = canonical knowledge writing
```

- [ ] **Step 2: Make smoke-runner.md own topology**

Move or replace the duplicated setup/group dependency model in `run-smoke`
with a required link to `smartup-guide/references/smoke-runner.md`. Keep test
execution permission and command selection in `run-smoke`.

- [ ] **Step 3: Replace duplicate authority text with links**

Keep unit-test artifact authority in
`write-test/references/project-rules.md#unit-test-qoshmaslik-va-run-qilmaslik`
and execution authority in `run-smoke`. Other files link to these owners and do
not restate the complete policy.

- [ ] **Step 4: Keep descriptions trigger-only**

Ensure each `description` starts with `Use when` and describes symptoms or task
conditions without summarizing the workflow.

### Task 5: Repair Current Knowledge Paths and Strengthen Validation

**Files:**
- Modify: `skills/smartup-guide/references/forms/client-offset.md`
- Modify: `skills/smartup-guide/references/forms/client-payment.md`
- Modify: `skills/smartup-guide/references/forms/order-add.md`
- Modify: `skills/smartup-guide/references/order-settlement-scenarios.md`
- Modify: `skills/smartup-guide/references/smoke-runner.md`
- Modify: `skills/scripts/validate_skills.py`

**Interfaces:**
- Consumes: staged `test_0_grup -> test_a_grup` repository rename and new loader/router files.
- Produces: zero stale referenced paths and mechanical loader/cache/ownership checks.

- [ ] **Step 1: Update exact stale group paths**

Replace only documented repository paths:

```text
tests/smoke/test_groups/test_0_grup/
-> tests/smoke/test_groups/test_a_grup/
```

Do not rewrite historical prose that intentionally names the business label
`Group-0`.

- [ ] **Step 2: Add loader validation**

Add a validator function that checks:

```python
AGENTS_MD = REPO_ROOT / "AGENTS.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

def check_loaders(errors: list[str]) -> None:
    agents = AGENTS_MD.read_text(encoding="utf-8")
    claude = CLAUDE_MD.read_text(encoding="utf-8").strip()
    if claude != "@AGENTS.md":
        errors.append("CLAUDE.md: must contain only @AGENTS.md")
    for required in ("skills/project-guide/SKILL.md", "skills/", "validate_skills.py"):
        if required not in agents:
            errors.append(f"AGENTS.md: bootstrap reference missing -> {required}")
```

- [ ] **Step 3: Add canonical-router validation**

Check that `project-guide` exists, both symlinks resolve to it, and every local
skill name occurs in its ownership/routing content.

- [ ] **Step 4: Reject tracked generated cache files**

Use `git ls-files skills` and reject tracked paths containing `__pycache__/` or
ending in `.pyc`. Do not fail merely because an ignored local cache exists.

- [ ] **Step 5: Run the shared validator**

Run:

```bash
./.venv/bin/python skills/scripts/validate_skills.py
```

Expected:

```text
errors=0
Shared skills tree is valid.
```

### Task 6: Forward-test Routing and Complete Static Verification

**Files:**
- Modify only if a tested loophole is found: skill files from Tasks 2–4
- No Playwright test files

**Interfaces:**
- Consumes: implemented loaders, project-guide, learn, ownership, and handoffs.
- Produces: evidence that fresh agents route consistently under realistic pressure.

- [ ] **Step 1: Re-run the three Task 1 scenarios with project-guide**

Fresh evaluators must independently produce:

```text
knowledge capture -> learn -> canonical form owner -> user-reported -> dedup/conflict check
observed title failure -> debug-test -> relevant dossier/testing-debug
generic TDD conflict -> local artifact/execution owners win; no unauthorized test run
```

- [ ] **Step 2: Add one duplicate and one conflict scenario**

```text
Duplicate: the same fact already exists with equal evidence.
Expected: no write.

Conflict: a user report contradicts a trace-confirmed current entry.
Expected: preserve current truth, record/ask without overwriting it.
```

- [ ] **Step 3: Close only observed loopholes**

If a fresh agent violates a boundary, patch the owning skill with the minimum
positive recipe or explicit prohibition appropriate to that failure, then
repeat the same scenario.

- [ ] **Step 4: Run final static verification**

```bash
./.venv/bin/python skills/scripts/validate_skills.py
git diff --check -- AGENTS.md CLAUDE.md skills
```

Expected: validator passes and `git diff --check` prints nothing.

- [ ] **Step 5: Inspect the final scoped diff**

Confirm:

```text
no Playwright production/test behavior changed
no unrelated working-tree file changed
no credentials or session values entered skills
no duplicated AGENTS/CLAUDE project knowledge remains
```
