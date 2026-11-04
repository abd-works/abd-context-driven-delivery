# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Write the judgment in this shape, because the session board reads it and lists each finding beside the graph's hits, with a Fix that sends it back:

   ```markdown
   ## Judgment — `path/of/the/judged/file.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   One `###` heading per rule that fails, with Fail after the dash. One bullet per finding, opening with the judged file's name and the line, so a person can open the finding at that line. Leave passing rules out of these headings; a table or a Passes paragraph may list them.


# Graph rule validation

**Generated:** 2026-11-04 17:29:18 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\session-board\edited-graph.json`

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

## Judgment — `harness/kanban/.context/session-board-realization.md`

The realization fidelity "does not restate GWT scenarios; it traces the describe/`that`/`with` tree already fixed at behavior". This file is the story map's 155 scenarios with Given, When, and Then, and its 174 call graphs hang under When steps, copied from the `*_story.test.py` comments. None hangs under an `it should` from `session-board-behavior.md`. Most of the failures below follow from that one choice of source.

### `hierarchy-preservation` — Fail
- session-board-realization.md:1 `Scenario Realizations: Session Board`: the file is organised by Story and Scenario, not by the spec files, `describe` blocks, and `it should` names that `session-board-behavior.md` lists, so no observation can be matched to its graph.
- session-board-realization.md:3 `Source`: it names the `*_story.test.py` files as its source rather than the behavior specs (`board-client.spec`, `kanban_spec`, `kanban_tools_spec`, and the others), so the hierarchy being deepened is the story map's, not the behavior's.
- session-board-realization.md:10 `Open Board`: the behavior file has no Open Board section, so this adds observations that behavior never agreed.
- session-board-realization.md:1888 `Add Active Ticket To System Prompt`: the behavior file has no such section, so these are added observations too.
- session-board-realization.md:1347 `Split Ticket Into Child Tickets`: behavior names two observations (`should name the ticket it was split from`, `should name a split ticket by its parent`), but the file has five graphs on scenarios instead, so the count of observations changed.

### `full-surface-coverage` — Fail
- session-board-realization.md:2702 `Fix Report Violations`: behavior names seven `it should` under `with Fix pressed on one violation` and `with Fix all pressed on a rule` (send one message, name the rule, give the file and line, quote the content, name the session, send every violation), but the file has four scenario graphs, so most of those observations have no graph.
- session-board-realization.md:53 `Display Board`: behavior lists `Display Connected Status`, `Refresh Board After Tool Calls`, and `Announce Ticket Changes` across four spec files, but the file traces scenarios, so there is no graph for each of those `describe` blocks' observations.
- session-board-realization.md:190 `Arrange Board And Details`: behavior lists `Resize Board And Details` and `Expand Board Or Details`, neither of which appears as a traced subject.

### `state-not-when` — Fail
- session-board-realization.md:22 `When the Person opens the session board`: every graph sits under a `**When**` trigger (174 of them), so observations are grouped by the event that fires them rather than by the `that` or `with` state the behavior tree names.

### `nest-by-enabling-events` — Fail
- session-board-realization.md:14 `Scenario: Open the board on a project`: graphs are grouped under scenario titles and Given lines, not under nested `that` or `with` preconditions, so the nesting does not say which state each observation requires.

### `sketch-fidelity` — Fail
- session-board-realization.md:31 `Then the header reads cdd-board-surface-fixture · 9 tickets`: each graph sits between Then and And lines that state the expected outcome, which are assertions; a realization holds signatures and interaction arrows only.
- session-board-realization.md:16 `Evidence: observed: board-page.ts start()`: evidence lines that name production files and spec titles are not call graphs, and they belong in the story map, not the realization.

### `full-call-graph-per-observation` — Fail
- session-board-realization.md:2482 `Chat.send('command', '/actions-validate stories-story-map')`: it stops at the first call, while :2324-2326 shows the same send going through `Chat.check_in` and `command.run`, so most send graphs leave out how the command reaches the chat.
- session-board-realization.md:2734 `Chat.send(... each rule with every violation of it, each with its content)`: `BoardPage.fixReport` sends `fixReportPrompt`, which is only `Fix all violations found in this report: <path>` (`report-client.ts:33`), so the graph describes a message the code does not send.
- session-board-realization.md:385 `Ticket.to_json(): title, last_activity, progress, practices`: one hop with no collaborators, although `last_activity` and `progress` come from the session log through `Session`.
- session-board-realization.md:1019 `Chat.command('/space:session:close-session')`: it jumps from the chat straight to `Session.close()`, which leaves out the chat mod and the agent calling the cdd tool.
- session-board-realization.md:2498 `Graph.load_files(...)`: arguments elided and no return, so the graph does not show what was built or what the report receives.
- session-board-realization.md:2827 `Repo.files_changed_on('pet-visits')`: no return, so the files the list shows are not traced.

### `strip-helpers-to-domain-calls` — Fail
- session-board-realization.md:1097 `Ticket.record('move Specification')`: `record` appends to the session log, so the graph should show the session log call it delegates to rather than stopping at the ticket's helper.
- session-board-realization.md:826 `Ticket.keep(gift-cards.md)`: a helper that moves a file into the session folder; the domain call it delegates to is not shown.

### `external-systems-at-their-boundary` — Fail
- session-board-realization.md:44 `[External: Claude Code]`: the rule's label is `[ExternalSystem]`, so the boundary marker uses a different form that a reader or a scanner looking for the rule's label will miss.
- session-board-realization.md:124 `cdd.restart()  [External: cdd server]`: the cdd server is this system's own MCP server, not an external system.
- session-board-realization.md:1046 `Repo.push_commit('checkout-flow: leave session', sync_remote=True)`: it pushes to the git remote, but no graph marks git or origin as the external boundary.

### `no-typescript-internals` — Fail
- session-board-realization.md:203 `BoardLayoutClient.setBoardHeight(300, 900)`: pixel layout inside the page's own client is a front-end detail, not a domain operation.
- session-board-realization.md:1648 `TileClient.hoverOut(billing-report, story_map tile)`: pointer hover state is a front-end detail.
- session-board-realization.md:1728 `Person -> nothing: a tile in the details opens on TileClient.toggle`: a prose explanation of a front-end event, not a call graph.

### `domain-practice-alignment` — Fail
- session-board-realization.md:164 `Ticket.record('done Discovery')`: `Ticket.move_to` writes `move <stage>` and the mark (`kanban-model.md` :210, and :1115-1116 here), so this graph of the same operation leaves out the move line.
- session-board-realization.md:1174 `Ticket.close()`: the model's operation is `close(leaving)`, so the call does not match the model's signature.
- session-board-realization.md:2733 `BoardPage.fixReport`: everywhere else the actor is `Board page` (:6), so the same participant has two names.

**Passes:** `observable-behavior` (the outcomes the scenarios name are things a person sees), `usage-order-behaviors` (sections follow the story map's usage order), `describe-is-subject-not-internal`, `describe-is-plain-english`, `shared-describe-subject`, and `context-setup-expresses-state` (the file has no `describe` blocks or setup to break them), and `scan-fixture-pair` (no mechanical mistake specs).
