# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 22:22:45 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 52
**Rules with graph hits:** 4
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

**Graph violations:** 47

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L20): Epic `Move Work Forward On Session Board`: epic 'Move Work Forward On Session Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L22): SubEpic `Display Board And Details For Repo`: sub-epic 'Display Board And Details For Repo': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L24): Story `Open Board`: story 'Open Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L28): Story `Display Board`: story 'Display Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L39): Story `Arrange Board And Details`: story 'Arrange Board And Details': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): Story `Display Backlog Items As Tickets`: story 'Display Backlog Items As Tickets': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L52): Story `Display Ticket Card`: story 'Display Ticket Card': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L63): Story `Display Ticket Details`: story 'Display Ticket Details': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L73): Story `Set Stage WIP Limit`: story 'Set Stage WIP Limit': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L77): Story `Arrange Side Panel`: story 'Arrange Side Panel': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L88): SubEpic `Steer Ticket Sessions`: sub-epic 'Steer Ticket Sessions': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L90): Story `Add Backlog Item`: story 'Add Backlog Item': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L98): Story `Open Ticket Session`: story 'Open Ticket Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L106): Story `Close Active Session`: story 'Close Active Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L110): Story `Restrict Actions To Active Session`: story 'Restrict Actions To Active Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L114): Story `Move Ticket`: story 'Move Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L126): Story `Activate Ticket`: story 'Activate Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L135): Story `Split Ticket Into Child Tickets`: story 'Split Ticket Into Child Tickets': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L139): Story `Archive Ticket`: story 'Archive Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L143): Story `Write Ticket Handoff`: story 'Write Ticket Handoff': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L147): Story `Display Latest Handoff`: story 'Display Latest Handoff': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L151): SubEpic `Guide Work Through Practices`: sub-epic 'Guide Work Through Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L153): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L161): Story `Open Practice Tile`: story 'Open Practice Tile': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L165): Story `Choose Ticket Practices`: story 'Choose Ticket Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L169): Story `Run Action Across Practices`: story 'Run Action Across Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L173): Story `Mark Ticket Done In Stage`: story 'Mark Ticket Done In Stage': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L177): Story `Add Active Ticket To System Prompt`: story 'Add Active Ticket To System Prompt': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L181): Story `Open Help`: story 'Open Help': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L191): Story `Run Next Step`: story 'Run Next Step': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L201): SubEpic `Generate Fidelity Outputs`: sub-epic 'Generate Fidelity Outputs': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L203): Story `Choose Action And Formats`: story 'Choose Action And Formats': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L207): Story `Resolve Fidelity Output Paths`: story 'Resolve Fidelity Output Paths': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L211): Story `Generate Fidelity Output`: story 'Generate Fidelity Output': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L219): Story `Render Fidelity Format`: story 'Render Fidelity Format': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L223): Story `Send Sketch Iterate Or Document`: story 'Send Sketch Iterate Or Document': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L227): SubEpic `Validate Fidelity Outputs`: sub-epic 'Validate Fidelity Outputs': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L229): Story `Validate Fidelity`: story 'Validate Fidelity': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L233): Story `Save Validation Report`: story 'Save Validation Report': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L237): Story `Open Validation Report`: story 'Open Validation Report': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L241): Story `Fix Report Violations`: story 'Fix Report Violations': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L245): Story `Satisfy Violations From Band`: story 'Satisfy Violations From Band': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L253): SubEpic `Review Fidelity Outputs`: sub-epic 'Review Fidelity Outputs': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L255): Story `List Ticket Files`: story 'List Ticket Files': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L259): Story `Browse Ticket Folder`: story 'Browse Ticket Folder': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L263): Story `View Files`: story 'View Files': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L267): Story `Review Fidelity`: story 'Review Fidelity': evidence must be observed, inferred, or intended.

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

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L88): SubEpic `Steer Ticket Sessions`: sub-epic 'Steer Ticket Sessions': 10 children (target 4-9)

Evaluate the current context against this rule (four-to-nine-children):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L169): Story `Run Action Across Practices`: Story 'Run Action Across Practices' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L191): Story `Run Next Step`: Story 'Run Next Step' names a generic handler; use the system mechanic (e.g. 'Submit Order').

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L169): Story `Run Action Across Practices`: Story 'Run Action Across Practices': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L191): Story `Run Next Step`: Story 'Run Next Step': name should start with a verb (got generic-verb).

Evaluate the current context against this rule (verb-noun-format):

---

# AI judgment

The scenario files have not changed since `stories-scenarios-20261103T221309.md`, so the judgment below is the same and is copied here so this latest report holds the whole result.

**New in this run:** the scenarios validate now also runs story map rules on `story-map.md`, giving 52 graph hits that the earlier run did not report. They are the same hits as the final story map report (`stories-story-map-20261103T210800.md`):

- 47 on `evidence-distinguishes-observed-inferred-and-intended`: a scanner gap. Only `typescript/nodes.py` and `json/nodes.py` set `story.evidence`, so a markdown map with Python story files cannot pass. Every scenario here carries an Observed or Inferred label.
- 2 on `verb-noun-format` and 2 on `story-name-captures-system-mechanic`: `Run Next Step` and `Run Action Across Practices`, kept because the app specs use them as `describe` names.
- 1 on `four-to-nine-children`: Steer Ticket Sessions has 10 stories, the warning level.


**Artifacts:** the 40 story files under `harness/kanban/.context/move-work-forward-on-session-board/` (151 scenarios, 168 When steps), checked against `story-map.md` and `kanban-model.md`. The judgment uses checks across every file for each rule, plus reading the files named below.

| Rule | Verdict | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | WARN | Steps use the model's terms (ticket, stage, column, backlog item, board, session). But 22 Whens name the actor "the session board", while the map's actor is now Board App. |
| `read-all-source-context-in-full` | PASS | Each scenario cites the spec or code it comes from. |
| `do-not-invent-requirements` | PASS | Every scenario traces to a spec, code, or a canvas comment. |
| `evidence-distinguishes-observed-inferred-and-intended` | PASS | All 151 scenarios carry an Evidence line: 143 observed, 8 inferred. Gaps are stated where they exist, e.g. Split Ticket Into Child Tickets: "No spec presses Split". |
| `gwt-steps-trace-to-domain-operations` | WARN | 34 Whens have no realization line (`Actor -> Object.operation`) under them. Most are page-only steps (open a tile, move the pointer away, choose render), e.g. `choose_action_and_formats_story.test.py`, `open_practice_tile_story.test.py`. They should trace to the page client's operation (`TileClient`, `SidePanelClient`) as the other UI scenarios do. |
| `behavioral-and-system-observable-outcomes` | PASS with note | Thens name toasts, columns, panels, and files. Several assert session log lines or `.sessions/` folders (e.g. "its session log ends with move Specification"). The session log is the domain's record of progress, read back by the board and other tools, so it is observable system state, not an internal flag. |
| `explore-full-interaction-surface` | PASS | Failure paths are covered: no chat connected, cdd lost, an unreadable file list, a fidelity that does not exist, a move into a column that is not a stage. |
| `examples-trace-domain-model` | PASS | Named example tickets (pet-visits, checkout-flow, billing-report, ready-to-move) carry concrete state and values. |
| `reconcile-live-immediately` | PASS | Scenario evidence already cites the app's specs, not the retired pane. |
| `flagged-writes-intended-gwt` | PASS | Where no spec exercises the behaviour, the scenario is labelled inferred and states what is missing. |
| `scenario-names-continuation` | WARN | No Then names the next Story where a flow continues, e.g. Add Backlog Item → Start Backlog Item, Activate Ticket → the work on it. |
| `given-only-what-the-system-checks` | PASS | Givens set the ticket, its stage, its log, and the panel or dialog the page checks. "The files panel is open" is page state the refresh decision reads. |
| `given-names-complex-state-root-first` | PASS | Givens open with the ticket, then its stage and work. |
| `but-marks-missing-state` | PASS | `but_` marks absent state: "no chat is connected", "no limit is saved", "no format is picked", "that branch is not checked out". |
| `when-holds-the-operation` | **FAIL** | 10 Whens have no operation: "the Person looks at the story_map bar" (×4), "looks at billing-report's practices", "looks at billing-report's Run next", "looks at checkout-flow's card" (×2), "looks at billing-report's card and tiles", "looks at the band". The system does nothing when a person looks, so the result has no cause. For display stories, the When is the board reading the ticket (as 22 other scenarios already write it). |
| `when-names-intent-not-interface-gesture` | PASS with note | Presses and hovers appear only in Open Practice Tile, Run Action Across Practices, and Arrange Side Panel, where how a tile opens or a panel narrows is the behaviour under test. |
| `expressive-system-interactions` | PASS | System steps name results in their own terms (the report saved with its graph, the outputs a fidelity declares). |
| `and-chaining` | PASS | Given/When/Then open each block, `and_` continues it. No Background is used, and none is needed. |
| `outline-requires-many-permutations` | PASS | Two files use an outline (Display Ticket Card, Activate Ticket) for data that varies on the same steps. |
| `plain-english-gwt-steps` | WARN | 109 steps use fidelity keys as names: `story_map` (99), `bounded_context` (7), and `no_such_fidelity`, `stories-story_map`. A report reader would read "the story map tile". Keep the key only where the page shows it as text. |
| `seed-prior-story-as-given` | PASS | Later stories start from seeded tickets and logs, not by replaying earlier Whens. |
| `domain-terms-link-to-model` | PASS | 148 links into `kanban-model.md`, all to headings that exist (`#ticket--card` is `## Ticket : Card`). Terms are linked at first mention in a scenario. |

## Failures to fix

1. Replace the 10 "the Person looks at …" Whens with the operation that produces the result, e.g. "the Board App reads billing-report".

## Warnings

2. Rename the "the session board" actor in Whens to the Board App, to match the map.
3. Add realization lines to the 34 untraced Whens, naming the page client operation.
4. Write fidelity names in plain English ("story map") unless the page shows the key.
5. Where a flow continues into another story, name that story in the last Then.
