# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: C:/dev/abd-cdd-session-board/harness/kanban/.context/{scope}-bdd-realization.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 06:55:29 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 204
**Rules with graph hits:** 2
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

### `framework-syntax`

Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L1): Spec `kanban_spec`: Spec file is missing a BDD: SIGNATURE marker.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1): Spec `kanban_tools_spec`: Spec file is missing a BDD: SIGNATURE marker.

Evaluate the current context against this rule (framework-syntax):

### `no-implementation`

No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.

**Graph violations:** 202

- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L68): Observation `should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order`: Observation 'should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L71): Observation `should have story_map, bounded_context, and ia as Discovery's work required`: Observation "should have story_map, bounded_context, and ia as Discovery's work required" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L74): Observation `should give every stage Generate, Validate, and Review, in that order`: Observation 'should give every stage Generate, Validate, and Review, in that order' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L81): Observation `should have behavior as Discovery's work required`: Observation "should have behavior as Discovery's work required" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L84): Observation `should have realization as Specification's work required`: Observation "should have realization as Specification's work required" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L87): Observation `should refuse a column it does not have, naming it`: Observation 'should refuse a column it does not have, naming it' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L99): Observation `should choose every practice`: Observation 'should choose every practice' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L102): Observation `should share its practices with every other board loaded in the process, since they do not change between calls`: Observation 'should share its practices with every other board loaded in the process, since they do not change between calls' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L114): Observation `should show the board of the whole checkout, where sessions keep their folders`: Observation 'should show the board of the whole checkout, where sessions keep their folders' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L118): Observation `should have no active ticket, since main is not on the board`: Observation 'should have no active ticket, since main is not on the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L134): Observation `should show every work session as a ticket`: Observation 'should show every work session as a ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L137): Observation `should leave main off the board`: Observation 'should leave main off the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L140): Observation `should show each backlog item in the Backlog column`: Observation 'should show each backlog item in the Backlog column' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L143): Observation `should leave archived sessions off the board`: Observation 'should leave archived sessions off the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L146): Observation `should show closed sessions in Complete`: Observation 'should show closed sessions in Complete' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L149): Observation `should name the ticket of the current session as active`: Observation 'should name the ticket of the current session as active' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L152): Observation `should show tickets and backlog items alike as the board's cards`: Observation "should show tickets and backlog items alike as the board's cards" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L155): Observation `should count both a ticket and a backlog item as a card`: Observation 'should count both a ticket and a backlog item as a card' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L158): Observation `should give each card one column`: Observation 'should give each card one column' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L161): Observation `should list every column with its tickets or items`: Observation 'should list every column with its tickets or items' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L175): Observation `should be in the Backlog`: Observation 'should be in the Backlog' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L182): Observation `should open its ticket in Discovery`: Observation 'should open its ticket in Discovery' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L189): Observation `should stay in the Backlog`: Observation 'should stay in the Backlog' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L197): Observation `should keep the item's file, text and all, in the new ticket's session folder`: Observation "should keep the item's file, text and all, in the new ticket's session folder" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L201): Observation `should open a ticket in Discovery`: Observation 'should open a ticket in Discovery' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L204): Observation `should name the item's file in the new ticket's session log`: Observation "should name the item's file in the new ticket's session log" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L218): Observation `should be in the Backlog under the heading of that file`: Observation 'should be in the Backlog under the heading of that file' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L221): Observation `should show the text of that file`: Observation 'should show the text of that file' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L228): Observation `should bring its ticket back with the history in its session log`: Observation 'should bring its ticket back with the history in its session log' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L232): Observation `should keep its file in the ticket's session folder`: Observation "should keep its file in the ticket's session folder" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L245): Observation `should be in the Backlog`: Observation 'should be in the Backlog' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L248): Observation `should keep the ticket's whole folder, its history included`: Observation "should keep the ticket's whole folder, its history included" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L251): Observation `should show the ticket's own idea file as its text`: Observation "should show the ticket's own idea file as its text" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L254): Observation `should be off the stages`: Observation 'should be off the stages' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L300): Observation `should be in Discovery, in progress`: Observation 'should be in Discovery, in progress' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L303): Observation `should keep its title, scope, and parent`: Observation 'should keep its title, scope, and parent' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L306): Observation `should name Generate on story_map as next`: Observation 'should name Generate on story_map as next' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L311): Observation `should be in Specification`: Observation 'should be in Specification' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L320): Observation `should show Generate done and Validate and Review remaining for that fidelity`: Observation 'should show Generate done and Validate and Review remaining for that fidelity' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L324): Observation `should still find the practice and fidelity by name`: Observation 'should still find the practice and fidelity by name' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L332): Observation `should still need Validate for that fidelity`: Observation 'should still need Validate for that fidelity' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L339): Observation `should show Validate done for that fidelity`: Observation 'should show Validate done for that fidelity' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L342): Observation `should match the practice's class name in the validate line to its folder name`: Observation "should match the practice's class name in the validate line to its folder name" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L349): Observation `should show the fidelity done`: Observation 'should show the fidelity done' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L356): Observation `should not count the review`: Observation 'should not count the review' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L365): Observation `should be done, waiting in its stage's done part`: Observation "should be done, waiting in its stage's done part" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L368): Observation `should have no next`: Observation 'should have no next' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L375): Observation `should be in the next stage`: Observation 'should be in the next stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L378): Observation `should write the stage it entered to its session log`: Observation 'should write the stage it entered to its session log' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L387): Observation `should stay in its stage`: Observation 'should stay in its stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L394): Observation `should be done in its stage, in the same column`: Observation 'should be done in its stage, in the same column' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L397): Observation `should have no next`: Observation 'should have no next' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L406): Observation `should name Review on that fidelity as next`: Observation 'should name Review on that fidelity as next' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L415): Observation `should be done in that stage`: Observation 'should be done in that stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L424): Observation `should be in progress in that stage`: Observation 'should be in progress in that stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L432): Observation `should be open again, in progress in that stage`: Observation 'should be open again, in progress in that stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L442): Observation `should be done with the one practice it works on`: Observation 'should be done with the one practice it works on' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L451): Observation `should be in Complete`: Observation 'should be in Complete' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L454): Observation `should have its folder in closed`: Observation 'should have its folder in closed' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L463): Observation `should be off the board`: Observation 'should be off the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_spec.py#L466): Observation `should have its folder in the archive`: Observation 'should have its folder in the archive' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L162): Observation `should return every column of the board`: Observation 'should return every column of the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L166): Observation `should name the project the board belongs to`: Observation 'should name the project the board belongs to' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L170): Observation `should say when a backlog item last changed`: Observation 'should say when a backlog item last changed' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L173): Observation `should give a backlog item its text`: Observation 'should give a backlog item its text' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L177): Observation `should say a ticket works on the whole repository until a person chooses a workpath`: Observation 'should say a ticket works on the whole repository until a person chooses a workpath' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L185): Observation `should list the folders at the top of the repository a workpath can be chosen from`: Observation 'should list the folders at the top of the repository a workpath can be chosen from' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L188): Observation `should leave out installed packages and hidden folders`: Observation 'should leave out installed packages and hidden folders' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L191): Observation `should list the folders inside one, as paths from the project`: Observation 'should list the folders inside one, as paths from the project' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L198): Observation `should show the folder as the ticket's workpath`: Observation "should show the folder as the ticket's workpath" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L201): Observation `should keep the folder as the session's work folder`: Observation "should keep the folder as the session's work folder" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L209): Observation `should show the folder as that practice's root, chosen by a person`: Observation "should show the folder as that practice's root, chosen by a person" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L212): Observation `should write that practice's files there`: Observation "should write that practice's files there" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L216): Observation `should leave every other practice on its default root`: Observation 'should leave every other practice on its default root' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L223): Observation `should keep that practice writing to the folder chosen for it`: Observation 'should keep that practice writing to the folder chosen for it' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L230): Observation `should show the practice on its default root again`: Observation 'should show the practice on its default root again' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L237): Observation `should put each practice's default practice root under the ticket's workpath`: Observation "should put each practice's default practice root under the ticket's workpath" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L244): Observation `should open its ticket with that folder as its workpath`: Observation 'should open its ticket with that folder as its workpath' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L248): Observation `should give every stage a limit of 3 tickets until a person sets one`: Observation 'should give every stage a limit of 3 tickets until a person sets one' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L256): Observation `should show the stage over its limit`: Observation 'should show the stage over its limit' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L261): Observation `should show no handoff for a ticket that has none`: Observation 'should show no handoff for a ticket that has none' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L270): Observation `should show the latest handoff`: Observation 'should show the latest handoff' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L274): Observation `should show no report for a fidelity that has none`: Observation 'should show no report for a fidelity that has none' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L285): Observation `should show that fidelity's latest report`: Observation "should show that fidelity's latest report" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L290): Observation `should list each rule the report names with its violations`: Observation 'should list each rule the report names with its violations' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L294): Observation `should give a violation the line it failed on`: Observation 'should give a violation the line it failed on' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L298): Observation `should show no source for a file that is not in the repository`: Observation 'should show no source for a file that is not in the repository' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L308): Observation `should show the source lines around a violation`: Observation 'should show the source lines around a violation' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L324): Observation `should name the violation's file from the project's root`: Observation "should name the violation's file from the project's root" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L328): Observation `should show the source lines of the file in the session's root`: Observation "should show the source lines of the file in the session's root" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L332): Observation `should return exactly the fields ViolationData names`: Observation 'should return exactly the fields ViolationData names' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L336): Observation `should return exactly the fields ReportRuleData names`: Observation 'should return exactly the fields ReportRuleData names' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L340): Observation `should count the violations of each rule`: Observation 'should count the violations of each rule' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L344): Observation `should leave out the violations of other practices in the saved graph`: Observation 'should leave out the violations of other practices in the saved graph' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L348): Observation `should say the report has its saved graph`: Observation 'should say the report has its saved graph' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L358): Observation `should say a report has no saved graph`: Observation 'should say a report has no saved graph' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L362): Observation `should still return the report's text`: Observation "should still return the report's text" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L370): Observation `should show the text of each rule under its name`: Observation 'should show the text of each rule under its name' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L388): Observation `should still show the judged report`: Observation 'should still show the judged report' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L398): Observation `should show the later judged report`: Observation 'should show the later judged report' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L402): Observation `should list each rule the judgment fails after the graph's rules, once each`: Observation "should list each rule the judgment fails after the graph's rules, once each" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L406): Observation `should count each finding of a judged rule`: Observation 'should count each finding of a judged rule' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L410): Observation `should give a judged finding the judged file and its line`: Observation 'should give a judged finding the judged file and its line' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L414): Observation `should show the source lines around a judged finding`: Observation 'should show the source lines around a judged finding' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L418): Observation `should give a finding that names no line its message`: Observation 'should give a finding that names no line its message' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L428): Observation `should leave that rule's hits out of the report`: Observation "should leave that rule's hits out of the report" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L438): Observation `should return the new ticket in Discovery`: Observation 'should return the new ticket in Discovery' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L441): Observation `should leave the current session as it is`: Observation 'should leave the current session as it is' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L448): Observation `should save that folder as the session's workpath`: Observation "should save that folder as the session's workpath" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L456): Observation `should leave the session working on the repository`: Observation 'should leave the session working on the repository' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L465): Observation `should name the ticket it was split from`: Observation 'should name the ticket it was split from' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L473): Observation `should show the item in the Backlog with its text`: Observation 'should show the item in the Backlog with its text' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L476): Observation `should write the title and text to one markdown file`: Observation 'should write the title and text to one markdown file' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L485): Observation `should return the new ticket in Discovery`: Observation 'should return the new ticket in Discovery' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L488): Observation `should take the item off the Backlog`: Observation 'should take the item off the Backlog' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L496): Observation `should show the ticket in Complete`: Observation 'should show the ticket in Complete' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L504): Observation `should leave no ticket active`: Observation 'should leave no ticket active' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L512): Observation `should leave the ticket off the board`: Observation 'should leave the ticket off the board' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L520): Observation `should show the ticket in that stage's Done`: Observation "should show the ticket in that stage's Done" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L528): Observation `should show the ticket in the next stage`: Observation 'should show the ticket in the next stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L531): Observation `should show the ticket in progress there`: Observation 'should show the ticket in progress there' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L539): Observation `should show the ticket in that stage's Done all the same`: Observation "should show the ticket in that stage's Done all the same" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L552): Observation `should close the ticket`: Observation 'should close the ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L555): Observation `should leave a ticket in Complete where it is on another move forward`: Observation 'should leave a ticket in Complete where it is on another move forward' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L562): Observation `should reopen the ticket in Implementation`: Observation 'should reopen the ticket in Implementation' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L569): Observation `should show the ticket in progress in that stage`: Observation 'should show the ticket in progress in that stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L576): Observation `should show the ticket in Discovery`: Observation 'should show the ticket in Discovery' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L579): Observation `should show the ticket in Discovery's Done`: Observation "should show the ticket in Discovery's Done" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L587): Observation `should show the practice off for that ticket`: Observation 'should show the practice off for that ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L590): Observation `should save the choice to the ticket's session.json`: Observation "should save the choice to the ticket's session.json" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L595): Observation `should refuse it, naming the practice`: Observation 'should refuse it, naming the practice' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L604): Observation `should give each fidelity its default format`: Observation 'should give each fidelity its default format' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L608): Observation `should show each fidelity's Generate, Validate, and Review`: Observation "should show each fidelity's Generate, Validate, and Review" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L617): Observation `should show the fidelity's rules`: Observation "should show the fidelity's rules" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L620): Observation `should name the stage a fidelity belongs to`: Observation 'should name the stage a fidelity belongs to' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L623): Observation `should link to the fidelity's page on the forge`: Observation "should link to the fidelity's page on the forge" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L630): Observation `should show the practice's shared rules`: Observation "should show the practice's shared rules" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L633): Observation `should name no fidelity on a practice's help`: Observation "should name no fidelity on a practice's help" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L637): Observation `should refuse it, naming the practice`: Observation 'should refuse it, naming the practice' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L641): Observation `should refuse it, naming the fidelity and the practice`: Observation 'should refuse it, naming the fidelity and the practice' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L662): Observation `should list the files a pattern finds there`: Observation 'should list the files a pattern finds there' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L667): Observation `should list the files a named part of the path finds there, in folders at any depth`: Observation 'should list the files a named part of the path finds there, in folders at any depth' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L682): Observation `should list the file with whether it exists`: Observation 'should list the file with whether it exists' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L686): Observation `should list only the fidelities asked for`: Observation 'should list only the fidelities asked for' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L691): Observation `should render the earlier fidelity into the new format first`: Observation 'should render the earlier fidelity into the new format first' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L696): Observation `should name the ticket's session in the generate command`: Observation "should name the ticket's session in the generate command" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L700): Observation `should give the board the ticket's session.json`: Observation "should give the board the ticket's session.json" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L704): Observation `should return the file's text`: Observation "should return the file's text" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L708): Observation `should return no text for a file that is gone, such as one deleted since the board listed it`: Observation 'should return no text for a file that is gone, such as one deleted since the board listed it' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L712): Observation `should refuse to generate a fidelity the ticket does not have, naming it`: Observation 'should refuse to generate a fidelity the ticket does not have, naming it' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L715): Observation `should refuse a file outside the repository, naming the path and the ticket`: Observation 'should refuse a file outside the repository, naming the path and the ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L729): Observation `should list every file in the session folder`: Observation 'should list every file in the session folder' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L733): Observation `should list the files from the project`: Observation 'should list the files from the project' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L746): Observation `should show an item in the Backlog with the ticket's title`: Observation "should show an item in the Backlog with the ticket's title" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L749): Observation `should give the item's path from the project`: Observation "should give the item's path from the project" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L752): Observation `should take the ticket off the board's stages`: Observation "should take the ticket off the board's stages" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L760): Observation `should bring the ticket back with its work`: Observation 'should bring the ticket back with its work' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L764): Observation `should name generate as the next action`: Observation 'should name generate as the next action' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L767): Observation `should allow only Generate before anything is generated`: Observation 'should allow only Generate before anything is generated' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L780): Observation `should name review as the next action`: Observation 'should name review as the next action' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L789): Observation `should name satisfy as the next action`: Observation 'should name satisfy as the next action' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L792): Observation `should count each finding of the judgment`: Observation 'should count each finding of the judgment' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L799): Observation `should show the fidelity's review done`: Observation "should show the fidelity's review done" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L802): Observation `should write the review to the session log`: Observation 'should write the review to the session log' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L807): Observation `should refuse it, naming the fidelity`: Observation 'should refuse it, naming the fidelity' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L810): Observation `should say which fidelity and which ticket it refused`: Observation 'should say which fidelity and which ticket it refused' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L823): Observation `should write no review for the others named with it`: Observation 'should write no review for the others named with it' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L836): Observation `should name satisfy as the next action`: Observation 'should name satisfy as the next action' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L839): Observation `should allow Validate and Review again on the same output`: Observation 'should allow Validate and Review again on the same output' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L847): Observation `should count the violations of the fidelity on its ticket`: Observation 'should count the violations of the fidelity on its ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L854): Observation `should leave a fidelity with no saved graph uncounted`: Observation 'should leave a fidelity with no saved graph uncounted' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L871): Observation `should list the rules of every fidelity with violations`: Observation 'should list the rules of every fidelity with violations' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L875): Observation `should name the fidelity a rule was broken on`: Observation 'should name the fidelity a rule was broken on' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L879): Observation `should give the folder of the reports for every fidelity`: Observation 'should give the folder of the reports for every fidelity' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L896): Observation `should list only the rules of the fidelities in the ticket's stage`: Observation "should list only the rules of the fidelities in the ticket's stage" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L913): Observation `should list a rule two fidelities share once`: Observation 'should list a rule two fidelities share once' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L927): Observation `should list the scenarios rules and the story map rules`: Observation 'should list the scenarios rules and the story map rules' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L931): Observation `should count the same rules on the ticket`: Observation 'should count the same rules on the ticket' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L939): Observation `should leave the story map rules to the story map report`: Observation 'should leave the story map rules to the story map report' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L943): Observation `should count only the rules the scenarios report answers for`: Observation 'should count only the rules the scenarios report answers for' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L959): Observation `should make the chosen ticket the current session`: Observation 'should make the chosen ticket the current session' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L966): Observation `should create the ticket's branch when a ticket that has none is activated`: Observation "should create the ticket's branch when a ticket that has none is activated" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L969): Observation `should say a ticket has no branch yet`: Observation 'should say a ticket has no branch yet' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L972): Observation `should name no worktree for a ticket that has none`: Observation 'should name no worktree for a ticket that has none' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L984): Observation `should name the ticket's worktree folder`: Observation "should name the ticket's worktree folder" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L995): Observation `should name the folder it opened as the ticket's worktree`: Observation "should name the folder it opened as the ticket's worktree" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L998): Observation `should check out the ticket's branch there`: Observation "should check out the ticket's branch there" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1007): Observation `should say the ticket being left has no branch yet`: Observation 'should say the ticket being left has no branch yet' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1010): Observation `should commit nothing on a ticket that has no branch`: Observation 'should commit nothing on a ticket that has no branch' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1015): Observation `should leave the branch checked out as it was`: Observation 'should leave the branch checked out as it was' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1028): Observation `should say the ticket being left is on its branch`: Observation 'should say the ticket being left is on its branch' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1031): Observation `should commit the branch the ticket being left is on`: Observation 'should commit the branch the ticket being left is on' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1045): Observation `should list only the files the ticket's branch changed`: Observation "should list only the files the ticket's branch changed" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1055): Observation `should commit nothing on a branch that is not checked out`: Observation 'should commit nothing on a branch that is not checked out' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1066): Observation `should leave the board read out of the session log`: Observation 'should leave the board read out of the session log' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1070): Observation `should name each tool after its object`: Observation 'should name each tool after its object' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1079): Observation `should take the ticket's name on every ticket tool that acts on one`: Observation "should take the ticket's name on every ticket tool that acts on one" at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1089): Observation `should return exactly the fields TicketData names`: Observation 'should return exactly the fields TicketData names' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1092): Observation `should return exactly the fields WorkspaceData names`: Observation 'should return exactly the fields WorkspaceData names' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1097): Observation `should return exactly the fields BacklogItemData names`: Observation 'should return exactly the fields BacklogItemData names' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1100): Observation `should return only the fields ColumnData names on a stage`: Observation 'should return only the fields ColumnData names on a stage' at behavior fidelity must not contain tests or imports.
- [X] **ERROR** **[graph rule]** - [kanban_tools_spec.py](C:\dev\abd-cdd-session-board\harness\kanban\kanban_tools_spec.py#L1104): Observation `should state every shared behavior here under the same sentence`: Observation 'should state every shared behavior here under the same sentence' at behavior fidelity must not contain tests or imports.

Evaluate the current context against this rule (no-implementation):
