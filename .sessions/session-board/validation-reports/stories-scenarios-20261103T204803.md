# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 20:48:03 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 22

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-domain-source`

Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-requirements`

Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

Evaluate the current context against this rule (do-not-invent-requirements):

### `evidence-distinguishes-observed-inferred-and-intended`

Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

Evaluate the current context against this rule (evidence-distinguishes-observed-inferred-and-intended):

### `gwt-steps-trace-to-domain-operations`

Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour.

Evaluate the current context against this rule (gwt-steps-trace-to-domain-operations):

### `behavioral-and-system-observable-outcomes`

Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour.

Evaluate the current context against this rule (behavioral-and-system-observable-outcomes):

### `explore-full-interaction-surface`

Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.

Evaluate the current context against this rule (explore-full-interaction-surface):

### `examples-trace-domain-model`

Provide an example for every domain concept the scenario mentions. Use that concept's own terms and the values the source gives, because a step that names a concept without an example leaves the behaviour unagreed.

Evaluate the current context against this rule (examples-trace-domain-model):

### `reconcile-live-immediately`

In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.

Evaluate the current context against this rule (reconcile-live-immediately):

### `flagged-writes-intended-gwt`

When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact.

Evaluate the current context against this rule (flagged-writes-intended-gwt):

### `scenario-names-continuation`

Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories.

Evaluate the current context against this rule (scenario-names-continuation):

### `given-only-what-the-system-checks`

Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.

Evaluate the current context against this rule (given-only-what-the-system-checks):

### `given-names-complex-state-root-first`

Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate.

Evaluate the current context against this rule (given-names-complex-state-root-first):

### `but-marks-missing-state`

Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.

Evaluate the current context against this rule (but-marks-missing-state):

### `when-holds-the-operation`

Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result.

Evaluate the current context against this rule (when-holds-the-operation):

### `when-names-intent-not-interface-gesture`

Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.

Evaluate the current context against this rule (when-names-intent-not-interface-gesture):

### `expressive-system-interactions`

Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.

Evaluate the current context against this rule (expressive-system-interactions):

### `and-chaining`

Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together.

Evaluate the current context against this rule (and-chaining):

### `outline-requires-many-permutations`

Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure.

Evaluate the current context against this rule (outline-requires-many-permutations):

### `plain-english-gwt-steps`

Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code.

Evaluate the current context against this rule (plain-english-gwt-steps):

### `seed-prior-story-as-given`

Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.

Evaluate the current context against this rule (seed-prior-story-as-given):

### `domain-terms-link-to-model`

Link each domain term in Given, When, and Then text and in example tables to its definition in the domain model markdown, `domain-model.md` (DDD) or `class-model.md` (Clean Engineering), anchored at the class or term heading (`domain-model.md#sim-aggregate-root-entity`). With no model file, write the term without a link, because a step that leads to its definition keeps the Scenario and the model on one meaning, and a link to a missing file misleads.

Evaluate the current context against this rule (domain-terms-link-to-model):

# Judgment

Scope: the 40 `harness/kanban/.context/*_story.test.py` files and `harness/kanban/.context/session-board-realization.md` (151 scenarios).

**Graph note:** the saved graph (`stories-scenarios-20261103T204803.json`) holds no Stories nodes for these files (stories: 0 nodes; the files were read only as 40 BDD Spec nodes), so "No graph rule violations" did not exercise any Stories graph rule. The judgments below are the whole check.

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | Pass | Steps use the model's words (board, column, stage, ticket, backlog item, session log, fidelity, In progress, Done) and the operation names in realizations are the code's (`Ticket.move_to`, `Ticket.finish_review`, `BacklogItem.start`, `Board.folders`). The actor `Board Pane` is kept from the map although the running product is the board app. |
| `read-all-source-context-in-full` | Partial | Read board.py, ticket.py, backlog_item.py, kanban_spec.py, kanban_tools_spec.py, the app's clients and their specs, story-actions.spec.ts, board-surface.spec.ts, fixture-repo.ts, register.ts, chat.py, the session and validate specs. Did not read data.py, the `tests/kanban/**` page drivers, help-panel-view.tsx, or file-views-view.tsx line by line. |
| `do-not-invent-requirements` | Pass | Every scenario cites a spec or the code. Two show a refusal the code raises but no spec drives through the app (`Refuse a file outside the repository`, `Refuse a move into a column that is not a stage`); both are labelled inferred/code-only. |
| `evidence-distinguishes-observed-inferred-and-intended` | Pass | Each scenario carries an `# Evidence:` line, observed with the spec names or inferred with the missing evidence named (the chat mod has no spec: Open Board's chat answer, status line, system prompt). No intended-only behaviour was written. |
| `gwt-steps-trace-to-domain-operations` | Partial | Ticket, backlog, review, validate, and generate steps trace to Python domain operations. Layout stories (Arrange Board And Details, Arrange Side Panel, Open Practice Tile) trace only to page clients (`BoardLayoutClient`, `SidePanelClient`, `TileClient`), which is where that behaviour lives; several Thens on Run/Validate gating trace to `TileActionsClient.barOf` without naming it. |
| `behavioral-and-system-observable-outcomes` | Pass | Thens are toasts, column placement, panel contents, prompt text, commands a chat receives, log lines, and saved files. |
| `explore-full-interaction-surface` | Partial | Main flows plus refusals, gating (no chat, locked ticket, nothing to check), and failures are covered. Not covered: opening a worktree on activation, the header Refresh button, the chat picker beyond one scenario, and the help text formatting in help-text.spec.ts. |
| `examples-trace-domain-model` | Pass | Concrete fixture values throughout: checkout-flow, billing-report, move-me, back-to-backlog, ready-to-move, second-spec, almost-shipped, shipped-work, pet-visits, sign-up, Gift cards, `validate Stories story_map graph-rule verb-noun-format tests/story-map.md:6`, report `stories-story-map-20261101T100000.md`. |
| `reconcile-live-immediately` | Partial | Scenarios describe the running app (drag in place of arrows, Start through the roots dialog, Review on the board, Restart cdd / Connect). The map was not edited, as the caller asked; the contradictions are listed as proposed map changes in the handback. |
| `flagged-writes-intended-gwt` | Pass | Where only code exists (the chat mod), the GWT is written and the evidence line says no spec runs it. |
| `scenario-names-continuation` | Partial | Main flow first in every Story. Few Thens name the next Story; the live paths that continue without a map node (Choose Session Root, Send commands to a chat, Browse Ticket's Session Folder, Drag Ticket To A Stage) are proposed as map changes instead. |
| `given-only-what-the-system-checks` | Pass | Givens name the log lines, files, active session, chat connection, and lock the decision reads. Titles appear only where a Then shows them. |
| `given-names-complex-state-root-first` | Pass | Givens open on the board or the ticket, then its log, files, or fidelity progress. |
| `but-marks-missing-state` | Partial | But marks absent records and actions not taken (no chat, no branch, no heading, no review line). One But joins two alternatives ("no chat is connected, or the ticket is not the active session") in Choose Action And Formats. |
| `when-holds-the-operation` | Partial | One When per operation almost everywhere. Display Board's "Keep the newer board when an older read answers late" puts another chat's move and the board's read in one When. |
| `when-names-intent-not-interface-gesture` | Pass | Whens name intent (moves, starts, activates, reviews, satisfies). Open Practice Tile names hover and press because that difference is the behaviour under test. |
| `expressive-system-interactions` | Pass | The Claude Code stories (Resolve Fidelity Output Paths, Save Validation Report) state what that system asks and saves in its own terms; chat hops name the command a chat receives. |
| `and-chaining` | Pass | Given/When/Then open each block and And continues; a second When starts only for a new interaction. No Background is used. |
| `outline-requires-many-permutations` | Pass | No outlines; the few alternatives are separate scenarios. |
| `plain-english-gwt-steps` | Pass | Readable sentences with named actors; example names are the product's own identifiers (ticket names, fidelity slugs, commands), which are what a person sees on the board. |
| `seed-prior-story-as-given` | Pass | Later Stories seed state as Givens (a generated story map, a clean validate, a ticket in the Backlog) without replaying earlier Whens. |
| `domain-terms-link-to-model` | Partial | Terms link to `kanban-model.md` (this module's class model) at GitHub anchors (`#ticket--card`, `#stage--column`, `#backlogitem--card`, `#fidelityprogress`, `#session`, `#repo`, `#validate--guidanceaction`). Links are mostly on the first mention in Givens; many later mentions in When and Then steps are unlinked. The model file is named kanban-model.md, not class-model.md. |
