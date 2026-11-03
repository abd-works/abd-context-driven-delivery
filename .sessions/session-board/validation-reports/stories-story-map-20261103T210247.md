# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 21:02:47 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 97
**Rules with graph hits:** 5
**AI rules in scope:** 12

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

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L20): Epic `Move Work Forward On Session Board`: epic 'Move Work Forward On Session Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L22): SubEpic `Display Board And Details For Repo`: sub-epic 'Display Board And Details For Repo': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L24): Story `Open Board`: story 'Open Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L28): Story `Display Board`: story 'Display Board': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L39): Story `Arrange Board And Details`: story 'Arrange Board And Details': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): SubEpic `Tickets`: sub-epic 'Tickets': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): Story `Display Backlog Items As Tickets`: story 'Display Backlog Items As Tickets': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L52): Story `Display Ticket Card`: story 'Display Ticket Card': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L63): Story `Display Ticket Details`: story 'Display Ticket Details': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L73): Story `Set Stage WIP Limit`: story 'Set Stage WIP Limit': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L77): Story `Arrange Side Panel`: story 'Arrange Side Panel': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L90): Story `Add Backlog Item`: story 'Add Backlog Item': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L98): Story `Open Ticket Session`: story 'Open Ticket Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L106): Story `Close Active Session`: story 'Close Active Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L110): Story `Restrict Actions To Active Session`: story 'Restrict Actions To Active Session': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L114): Story `Move Ticket`: story 'Move Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L126): Story `Activate Ticket`: story 'Activate Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L134): Story `Split Ticket Into Child Tickets`: story 'Split Ticket Into Child Tickets': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L138): Story `Archive Ticket`: story 'Archive Ticket': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L142): Story `Write Ticket Handoff`: story 'Write Ticket Handoff': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L146): Story `Display Latest Handoff`: story 'Display Latest Handoff': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L150): SubEpic `Practices`: sub-epic 'Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L152): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Generate`: sub-epic 'Generate': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Validate`: sub-epic 'Validate': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Review`: sub-epic 'Review': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L160): Story `Open Practice Tile`: story 'Open Practice Tile': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L164): Story `Choose Ticket Practices`: story 'Choose Ticket Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L168): Story `Run Action Across Practices`: story 'Run Action Across Practices': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L172): Story `Mark Ticket Done In Stage`: story 'Mark Ticket Done In Stage': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L176): Story `Add Active Ticket To System Prompt`: story 'Add Active Ticket To System Prompt': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L180): Story `Open Help`: story 'Open Help': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L190): Story `Run Next Step`: story 'Run Next Step': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L202): Story `Choose Action And Formats`: story 'Choose Action And Formats': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L206): Story `Resolve Fidelity Output Paths`: story 'Resolve Fidelity Output Paths': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L210): Story `Generate Fidelity Output`: story 'Generate Fidelity Output': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L218): Story `Render Fidelity Format`: story 'Render Fidelity Format': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L222): Story `Send Sketch Iterate Or Document`: story 'Send Sketch Iterate Or Document': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L228): Story `Validate Fidelity`: story 'Validate Fidelity': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L232): Story `Save Validation Report`: story 'Save Validation Report': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L236): Story `Open Validation Report`: story 'Open Validation Report': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L240): Story `Fix Report Violations`: story 'Fix Report Violations': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L244): Story `Satisfy Violations From Band`: story 'Satisfy Violations From Band': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L254): Story `List Ticket Files`: story 'List Ticket Files': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L258): Story `Browse Ticket Folder`: story 'Browse Ticket Folder': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L262): Story `View Files`: story 'View Files': evidence must be observed, inferred, or intended.
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L266): Story `Review Fidelity`: story 'Review Fidelity': evidence must be observed, inferred, or intended.

Evaluate the current context against this rule (evidence-distinguishes-observed-inferred-and-intended):

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): SubEpic `Tickets`: SubEpic 'Tickets': name should start with a verb (got single-word).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L150): SubEpic `Practices`: SubEpic 'Practices': name should start with a verb (got single-word).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Generate`: SubEpic 'Generate': name should start with a verb (got single-word).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Validate`: SubEpic 'Validate': name should start with a verb (got single-word).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): SubEpic `Review`: SubEpic 'Review': name should start with a verb (got single-word).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L168): Story `Run Action Across Practices`: Story 'Run Action Across Practices': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L190): Story `Run Next Step`: Story 'Run Next Step': name should start with a verb (got generic-verb).

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L168): Story `Run Action Across Practices`: Story 'Run Action Across Practices' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L190): Story `Run Next Step`: Story 'Run Next Step' names a generic handler; use the system mechanic (e.g. 'Submit Order').

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): SubEpic `Tickets`: sub-epic 'Tickets': 10 children (target 4-9)

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-one-to-four`

A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.

**Graph violations:** 40

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L24): Story `Open Board`: story 'Open Board': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L28): Story `Display Board`: story 'Display Board': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L39): Story `Arrange Board And Details`: story 'Arrange Board And Details': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L48): Story `Display Backlog Items As Tickets`: story 'Display Backlog Items As Tickets': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L52): Story `Display Ticket Card`: story 'Display Ticket Card': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L63): Story `Display Ticket Details`: story 'Display Ticket Details': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L73): Story `Set Stage WIP Limit`: story 'Set Stage WIP Limit': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L77): Story `Arrange Side Panel`: story 'Arrange Side Panel': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L90): Story `Add Backlog Item`: story 'Add Backlog Item': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L98): Story `Open Ticket Session`: story 'Open Ticket Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L106): Story `Close Active Session`: story 'Close Active Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L110): Story `Restrict Actions To Active Session`: story 'Restrict Actions To Active Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L114): Story `Move Ticket`: story 'Move Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L126): Story `Activate Ticket`: story 'Activate Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L134): Story `Split Ticket Into Child Tickets`: story 'Split Ticket Into Child Tickets': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L138): Story `Archive Ticket`: story 'Archive Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L142): Story `Write Ticket Handoff`: story 'Write Ticket Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L146): Story `Display Latest Handoff`: story 'Display Latest Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L152): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L160): Story `Open Practice Tile`: story 'Open Practice Tile': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L164): Story `Choose Ticket Practices`: story 'Choose Ticket Practices': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L168): Story `Run Action Across Practices`: story 'Run Action Across Practices': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L172): Story `Mark Ticket Done In Stage`: story 'Mark Ticket Done In Stage': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L176): Story `Add Active Ticket To System Prompt`: story 'Add Active Ticket To System Prompt': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L180): Story `Open Help`: story 'Open Help': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L190): Story `Run Next Step`: story 'Run Next Step': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L202): Story `Choose Action And Formats`: story 'Choose Action And Formats': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L206): Story `Resolve Fidelity Output Paths`: story 'Resolve Fidelity Output Paths': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L210): Story `Generate Fidelity Output`: story 'Generate Fidelity Output': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L218): Story `Render Fidelity Format`: story 'Render Fidelity Format': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L222): Story `Send Sketch Iterate Or Document`: story 'Send Sketch Iterate Or Document': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L228): Story `Validate Fidelity`: story 'Validate Fidelity': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L232): Story `Save Validation Report`: story 'Save Validation Report': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L236): Story `Open Validation Report`: story 'Open Validation Report': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L240): Story `Fix Report Violations`: story 'Fix Report Violations': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L244): Story `Satisfy Violations From Band`: story 'Satisfy Violations From Band': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L254): Story `List Ticket Files`: story 'List Ticket Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L258): Story `Browse Ticket Folder`: story 'Browse Ticket Folder': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L262): Story `View Files`: story 'View Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L266): Story `Review Fidelity`: story 'Review Fidelity': 0 scenarios (target 1-7)

Evaluate the current context against this rule (story-scenarios-one-to-four):

### `branch-on-mechanical-uniqueness`

Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.

Evaluate the current context against this rule (branch-on-mechanical-uniqueness):

### `right-size-story-nodes`

Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.

Evaluate the current context against this rule (right-size-story-nodes):

### `behaviours-not-one-time-tasks`

Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

Evaluate the current context against this rule (behaviours-not-one-time-tasks):

### `story-map-links-to-markdown`

Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

Evaluate the current context against this rule (story-map-links-to-markdown):

---

# AI judgment

**Artifact:** `harness/kanban/.context/story-map.md` (discovery fidelity, 6 sub-epics, 40 stories)

## Graph report problems

- **Line numbers are wrong for several nodes.** Each one points at the first line containing the node's name, not at its heading. `Tickets` is reported at L48 (the `Display Backlog Items As Tickets` line; its heading is L88). `Generate`, `Validate`, and `Review` are all reported at L154, the line that reads "Generate, Validate, and Review" (their headings are L200, L226, L252). This points at the source-location lookup in `cdd_guidance/practices/stories/model/source_location.py`.
- **The evidence-label hits look like false positives.** Every story has an `Observed:` line under its heading, but the scanner does not read it as an evidence label.
- **The scenario-count hits don't apply at this fidelity.** This file is a discovery story map: stories carry acceptance criteria, and scenarios belong to the scenarios fidelity.

## Per rule

| Rule | Verdict | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | **FAIL** | The actor `Board Pane` (L16 and 15 stories) is the retired pane. The live actor is the board app in `harness/kanban/app/`. Ticket, fidelity, practice, and backlog item all match `kanban-model.md`. |
| `read-all-source-context-in-full` | **FAIL** | The evidence cites retired pane code and tests (`register.tsx`, `register.test`, `ColumnView`, `split-grip.tsx`, `side-panel-view.tsx`) instead of the app's `src/kanban/*` and `tests/kanban/*`. The sources line does not list `tests/kanban/`. |
| `do-not-invent-requirements` | PASS | Each story traces to code, a spec, or a canvas comment. "Differs from the canvas" notes keep pane limits apart from requirements. |
| `evidence-distinguishes-observed-inferred-and-intended` | **FAIL** | Labels are present but stale: "Observed" points at retired code, and "Differs from the canvas" (L71, L75, L86, L108, L204) describes pane-only limits the app may not have. Some acceptance criteria have no label at all: L69, L158, L186–188, L197, L122–123. |
| `verb-noun-format` | **FAIL** | Sub-epics `Tickets` (L88) and `Practices` (L150) are nouns. `Generate` (L200), `Validate` (L226), and `Review` (L252) are verbs with no noun. Warning: `Run Next Step` and `Run Action Across Practices` use the generic verb "Run". "Run next" is a button name, but the mechanic underneath is sending the next fidelity's commands. |
| `story-name-captures-system-mechanic` | WARN | `Run Action Across Practices` would read better as e.g. `Send Action To Stage Practices`, and `Run Next Step` as e.g. `Send Next Fidelity Command`. |
| `four-to-nine-children` | WARN | `Tickets` has 10 stories, the warning level. The other sub-epics have 4–8. |
| `story-scenarios-one-to-four` | N/A | Discovery fidelity; see the note on scenario hits above. |
| `branch-on-mechanical-uniqueness` | **FAIL** | `Mark Ticket Done In Stage` (L172) is the same mechanic as `Move Ticket` (L114): both are `Ticket.move_next`. Make it an acceptance criterion of Move Ticket. `Create Ticket Branch And Worktree` sits under `Open Ticket Session` (L104) but happens on activation, so it belongs under `Activate Ticket`. |
| `right-size-story-nodes` | PASS with note | The Claude Code system stories (`Resolve Fidelity Output Paths`, `Save Validation Report`) each sit at their own boundary. `Mark Ticket Done In Stage` is one step inside Move Ticket (see above). |
| `behaviours-not-one-time-tasks` | PASS | No migrations or renames among the stories. |
| `story-map-links-to-markdown` | **FAIL** | No epic, sub-epic, or story heading has an anchor link back to its entry. The top epic `# (E) Move Work Forward On Session Board` (L20) uses the same `#` level as the document title (L8), so the heading depth does not show the hierarchy. |

## Failures to fix

1. Rename the actor `Board Pane` to the board app, and re-point every "Observed" citation at `harness/kanban/app/src/kanban/*` and `tests/kanban/*`. Drop or re-check the pane-only "Differs from the canvas" notes.
2. Rename the sub-epics with a verb and noun, for example `Manage Ticket Lifecycle`, `Configure Ticket Practices`, `Generate Fidelity Outputs`, `Validate Fidelity Outputs`, `Review Fidelity Outputs`.
3. Fold `Mark Ticket Done In Stage` into `Move Ticket` (this also brings `Tickets` under 10 if it moves), and move `Create Ticket Branch And Worktree` under `Activate Ticket`.
4. Label the unlabelled acceptance criteria.
5. Add heading anchors and fix the top epic's heading level.
6. Separately, fix the source-location lookup so graph hits point at node headings.
