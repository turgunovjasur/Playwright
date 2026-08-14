# Project Skills Single Source of Truth

**Date:** 2026-08-14
**Branch:** `dev1`
**Status:** Approved architecture; pending written-spec review

## Goal

Make the repository-root `skills/` tree the only durable source of project
knowledge and AI workflow rules. Codex and Claude Code may use different
bootstrap files and discovery directories, but both must route to the same
canonical skill files and reach the same task-specific rules.

The system must also capture concrete knowledge learned during a conversation:
classify the fact, find its single owning skill/reference, detect duplicates or
conflicts, write it with provenance, and validate the result.

## Non-goals

- Packaging these skills for unrelated repositories.
- Loading every reference into every conversation.
- Treating unverified user statements as confirmed application behavior.
- Saving secrets, credentials, literal session data, or temporary failures.
- Allowing an external generic skill to override repository policy.

## Startup and Discovery Model

The two supported agents use different native bootstrap files:

```text
Codex ------> AGENTS.md ---------\
                                  > project-guide -> task skill -> references
Claude -----> CLAUDE.md --------/
               @AGENTS.md
```

- `AGENTS.md` is a short, vendor-neutral bootstrap. It contains no duplicated
  Smartup behavior, runner topology, test convention, or branch detail.
- `CLAUDE.md` imports `AGENTS.md` with `@AGENTS.md`; it does not maintain a
  second copy of project instructions.
- `.agents/skills/<name>` and `.claude/skills/<name>` remain symlink
  entry-points to `../../skills/<name>`.
- `skills/project-guide/SKILL.md` is the small always-read router for project
  governance, ownership, precedence, and handoffs.
- Task skills load only when their metadata matches the current request.
- Heavy references load only when the selected skill routes to them.

## Canonical Components

### `AGENTS.md`

The bootstrap owns only these instructions:

1. `skills/` is the sole durable knowledge and workflow source.
2. Read `project-guide` before project work, then invoke relevant task skills.
3. Use `learn` for automatic capture of newly learned concrete project facts.
4. Treat `.agents/skills/` and `.claude/skills/` as read-only entry-points.
5. Run the repository skill validator after knowledge-base changes.

All current project facts and policies move to an owning skill/reference.

### `CLAUDE.md`

`CLAUDE.md` contains only:

```markdown
@AGENTS.md
```

This prevents Codex and Claude from receiving diverging copies of the same
project instructions.

### `project-guide`

`skills/project-guide/SKILL.md` is concise and contains:

- the skill ownership and routing table;
- instruction and evidence precedence;
- the discussion-versus-implementation boundary;
- the default branch rule;
- test creation/execution authority;
- cross-skill handoff rules;
- the automatic learning decision contract;
- links to detailed owners instead of repeated rules.

Frequently changing details do not live in the router. They remain in their
task or domain owner.

## Skill Ownership

Every durable fact has exactly one current owner.

| Knowledge or workflow | Canonical owner |
|---|---|
| Project-wide AI governance, precedence, branch and authorization | `project-guide` |
| Smartup form behavior and form-specific locator/navigation | `smartup-guide/references/forms/<slug>.md` |
| Global legacy navigation | `smartup-guide/references/legacy-form-navigation.md` |
| A2 migration behavior | `smartup-guide/references/a2-migrated-forms.md` |
| Contract rules | `smartup-guide/references/contracts.md` |
| Current order and settlement business behavior | `smartup-guide/references/orders.md` |
| Order/settlement scenario coverage registry | `smartup-guide/references/order-settlement-scenarios.md` |
| Shared UI, locator, modal and grid patterns | `smartup-guide/references/ui-patterns.md` |
| Runtime, fixture, session and data-store facts | `smartup-guide/references/testing-debug.md` |
| Setup/group runner topology and dependency behavior | `smartup-guide/references/smoke-runner.md` |
| Test authoring conventions | `write-test/references/project-rules.md` |
| Navbar Forms suite authoring | `write-test/references/navbar-form-suite.md` |
| Reusable UI flow authoring | `new-flow` |
| Failure investigation procedure | `debug-test` |
| Test/flow/runner review procedure | `review-test` |
| Runner, reporting, Allure, Telegram and CI infrastructure | `maintain-test-infra` references |
| Test execution permission and commands | `run-smoke` |
| Unit-test artifact creation permission | `write-test/references/project-rules.md` |
| Superseded knowledge | `smartup-guide/references/history.md` |
| Knowledge classification and write procedure | `learn` |

If a rule appears outside its owner, the non-owner links to the owner instead
of repeating the text.

## Cross-skill Boundaries

- `write-test` writes testcase behavior; `new-flow` owns UI choreography that
  is genuinely reused by multiple tests.
- `run-smoke` owns execution and immediate result summarization; `debug-test`
  owns root-cause analysis of a failure.
- `debug-test` owns one observed runtime failure; `maintain-test-infra` owns a
  runner, collection, reporting, Allure, Telegram, or CI subsystem defect.
- `review-test` reports static quality and architecture findings;
  `debug-test` explains an observed failure.
- `smartup-guide` reads domain truth; `learn` writes new durable knowledge to
  the owner selected by this design.

## Precedence

Workflow authority and factual evidence use separate precedence models.

### Workflow authority

```text
current explicit user instruction
  > project-guide governance
  > selected local task skill
  > external or generic skill
```

An external TDD rule cannot grant permission to create or execute tests. The
unit-test artifact policy is owned by `write-test`; pytest, collection and
smoke execution authority is owned by `run-smoke`. When permission required by
those owners is absent, the agent performs permitted static verification and
states that strict TDD or runtime verification was not completed. Read-only UI
inspection requested or authorized for diagnosis is not itself a smoke/test
run and remains governed by the active task's scope.

### Factual evidence

```text
trace-confirmed / live-ui-confirmed
  > code-confirmed
  > user-reported
  > legacy entry without complete provenance
```

Newer evidence wins only within the same evidence tier or when it has stronger
provenance. Historical content is never current truth.

## Automatic Knowledge Capture

### Trigger

The agent invokes `learn` without a separate prompt when a conversation or
task establishes a concrete project-specific fact:

- the user explains actual Smartup behavior;
- the user identifies a failure cause;
- code, live UI, log, or trace confirms a new behavior;
- a previous solution is shown to be wrong;
- the user states a project test/workflow rule.

Automatic capture is narrowly pre-authorized for those concrete facts. It does
not authorize implementation of a discussed idea or product change.

Do not capture questions, hypotheses, rejected design alternatives,
unapproved future behavior, one-session values, credentials, or transient
failures as current knowledge.

### Routing algorithm

```text
new observation
  -> extract one atomic fact
  -> reject secret/session/transient content
  -> assign evidence status
  -> classify domain and artifact type
  -> resolve one owner from the ownership table
  -> search owner and history for the same subject
  -> duplicate / confirmation / new fact / conflict
  -> write or intentionally make no change
  -> validate
  -> report destination, status and outcome
```

The routing steps are:

1. **Atomize:** split multiple observations so each entry contains one rule.
2. **Sanitize:** reject or parameterize credentials, email, company values,
   generated codes, literal passwords, tokens, and session-specific data.
3. **Classify evidence:** choose `user-reported`, `code-confirmed`,
   `live-ui-confirmed`, or `trace-confirmed`.
4. **Classify ownership:** use task type, domain, form slug, tags, and relevant
   repository paths to select exactly one owner.
5. **Search before writing:** search the candidate owner, its routed sibling
   references, and `history.md` for equivalent or contradictory knowledge.
6. **Apply one outcome:**
   - exact duplicate: do not write;
   - stronger confirmation: update provenance/status of the current entry;
   - genuinely new fact: append it to the canonical section;
   - confirmed conflict: move the superseded entry to `history.md`, then write
     the new current fact;
   - ambiguous owner or evidence: ask the user and do not guess;
   - no appropriate owner: propose a location; do not auto-create a skill.
7. **Validate:** run `skills/scripts/validate_skills.py` after a write.
8. **Report:** name the changed file, evidence status, validation result, and
   whether an older rule was superseded.

### Learning write format

Domain entries use the existing provenance contract:

```markdown
### <short topic>
Tags: <searchable tags>
Status: user-reported | code-confirmed | live-ui-confirmed | trace-confirmed
Verified: YYYY-MM-DD | pending
Source: user | <file:line> | live UI | <trace/log path>
- Qayerda: <page, form, flow, runner, or subsystem>
- Qoida: <one atomic fact>
- Testda ishlatish: <assertion, fixture, flow, or N/A>
```

Process/governance owners may use a shorter owner-specific structure, but
must retain `Status`, `Verified`, and `Source` for learned facts.

## Conflict Prevention

The validator is extended to check mechanically enforceable parts:

- every canonical skill has both entry-point symlinks;
- `CLAUDE.md` imports `AGENTS.md` and does not duplicate project instructions;
- the bootstrap contains no known project-fact sections;
- the ownership table names existing skills/references;
- skill names and descriptions satisfy discovery requirements;
- Markdown links and referenced repository paths exist;
- form dossiers remain indexed;
- new knowledge entries have complete provenance;
- no tracked `__pycache__`, `.pyc`, or other generated cache is inside
  `skills/`.

Semantic conflicts cannot be proven reliably by regex alone. Forward-testing
uses realistic prompts to verify that fresh agents select the intended skill,
route learned facts to the same owner, avoid duplicates, and respect
precedence under conflicting external guidance.

## Migration Scope

1. Add the small `project-guide` skill and both symlink entry-points.
2. Move current project-wide policy from `AGENTS.md` to `project-guide` or the
   appropriate existing owner.
3. Reduce `AGENTS.md` to the bootstrap contract.
4. Replace duplicated `CLAUDE.md` content with `@AGENTS.md`.
5. Extend `learn` with the ownership lookup and duplicate/conflict outcomes.
6. Tighten task-skill descriptions and handoffs where triggers overlap.
7. Replace duplicated rules with links to the canonical owner.
8. Extend validation for loaders, ownership references, and generated cache.
9. Fix current stale `test_0_grup` knowledge-base paths so the shared
   validator passes against the current tree.
10. Forward-test routing and automatic learning with fresh-agent scenarios.

No Playwright production/test behavior is changed by this migration.

## Acceptance Criteria

- Codex and Claude receive one equivalent bootstrap instruction chain.
- `AGENTS.md` and `CLAUDE.md` contain no duplicated project knowledge.
- Every durable rule has one documented owner.
- The same request routes both supported agents to the same local skill.
- A new concrete fact is atomized, sanitized, classified, deduplicated, written
  to one owner with provenance, validated, and reported.
- A question or unapproved proposal is not captured as current truth.
- A weaker observation cannot silently overwrite stronger evidence.
- External generic skills cannot override repository authority.
- `skills/scripts/validate_skills.py` completes with zero errors.
- Existing Smartup dossiers, screenshots, history, and action-skill coverage
  remain available through progressive disclosure.

## Risks and Mitigations

- **Router becomes another large knowledge dump:** keep `project-guide` short
  and link to owners.
- **Automatic learning writes speculation:** require concrete-fact triggers and
  route ambiguous cases back to the user.
- **Two owners claim the same rule:** ownership table chooses one current owner;
  other skills link to it.
- **A stale user report replaces verified behavior:** evidence precedence
  blocks replacement and keeps the report separately marked.
- **Validator passes while semantics conflict:** supplement mechanical checks
  with fresh-agent routing and pressure scenarios.
- **Dirty worktree hides migration mistakes:** implement in small, reviewable
  steps and stage only agreed knowledge-infrastructure files.
