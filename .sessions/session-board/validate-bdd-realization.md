# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then write a matching validate report.


# Graph rule validation

**Generated:** 2026-10-31 06:09:57 UTC
**Project:** abd-context-driven-delivery
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `/home/user/abd-context-driven-delivery/.sessions/session-board/edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 17

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `observable-behavior`

Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.

Evaluate the current context against this rule (observable-behavior):

### `domain-practice-alignment`

Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.

Evaluate the current context against this rule (domain-practice-alignment):

### `usage-order-behaviors`

Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.

Evaluate the current context against this rule (usage-order-behaviors):

### `describe-is-subject-not-internal`

A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.

Evaluate the current context against this rule (describe-is-subject-not-internal):

### `describe-is-plain-english`

Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.

Evaluate the current context against this rule (describe-is-plain-english):

### `shared-describe-subject`

Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.

Evaluate the current context against this rule (shared-describe-subject):

### `state-not-when`

Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?

Evaluate the current context against this rule (state-not-when):

### `nest-by-enabling-events`

Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.

Evaluate the current context against this rule (nest-by-enabling-events):

### `context-setup-expresses-state`

Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).

Evaluate the current context against this rule (context-setup-expresses-state):

### `full-surface-coverage`

Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.

Evaluate the current context against this rule (full-surface-coverage):

### `scan-fixture-pair`

A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

Evaluate the current context against this rule (scan-fixture-pair):

### `strip-helpers-to-domain-calls`

Same rule as story realizations: show the domain call the helper delegates to.

Evaluate the current context against this rule (strip-helpers-to-domain-calls):

### `full-call-graph-per-observation`

Follow every named domain or external-system collaborator from the entry operation through returns; do not stop at the first hop.

Evaluate the current context against this rule (full-call-graph-per-observation):

### `external-systems-at-their-boundary`

Label `[ExternalSystem]` at the seam; do not recurse inside vendor code.

Evaluate the current context against this rule (external-systems-at-their-boundary):

### `no-typescript-internals`

Omit framework and language-native steps unless the observation is entirely infrastructure.

Evaluate the current context against this rule (no-typescript-internals):

### `sketch-fidelity`

Signatures and interaction arrows only; no assertions, mocks, or production imports in the realization artifact.

Evaluate the current context against this rule (sketch-fidelity):

### `hierarchy-preservation`

One graph per `it should`; do not add or remove observations when deepening to realization.

Evaluate the current context against this rule (hierarchy-preservation):


Validation report for artifacts under {session.path}/.