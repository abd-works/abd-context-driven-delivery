# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 20:01:52 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 98
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

**Graph violations:** 48

- [X] **ERROR** **[graph rule]** - [harness/kanban/.context/story-map.drawio](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.drawio#L352): Epic `Move Work Forward On Session Board`: epic 'Move Work Forward On Session Board': evidence must be observed, inferred, or intended.
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


# Judgment

Judged on `harness/kanban/.context/story-map.md` and `story-map.drawio`, as they are on 2026-11-03. **Result: fails** on four rules; the 48 evidence hits are a reader fault, not the map's.

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | Pass | Names match the model and code: ticket, backlog item, stage, fidelity, WIP limit, handoff, validation report (`kanban-model.md`, `ticket.py`, `board.py`). |
| `read-all-source-context-in-full` | Pass | The header lists the sources read (board.py, ticket.py, backlog_item.py, both specs, the app, the retired pane, module context, the model, the canvas and its comments), and each Story names its code and spec. |
| `do-not-invent-requirements` | Pass | Every Story cites code or a spec that does it, or the canvas; nothing stands without a source. |
| `evidence-distinguishes-observed-inferred-and-intended` | Pass on the map; 48 scanner hits are false | Every Story opens with `Observed:` and the header defines Observed and Live. The markdown reader never reads that line into a story's evidence (`Story.evidence` stays empty), so every Story, and every Epic that takes its children's labels, is reported as unlabelled. Fix the reader, not the map. The drawio epic hit has the same cause. |
| `verb-noun-format` | **Fail** (5 of 7 hits real) | Sub-epics `Tickets`, `Practices`, `Generate`, `Validate`, `Review` are bare nouns or verbs (lines 88, 150, 200, 226, 252). Rename them to goals, such as `Manage Ticket Lifecycle`, `Work Practices On A Ticket`, `Generate Fidelity Output`, `Validate Fidelity Output`, `Review Fidelity Work`. `Run Action Across Practices` and `Run Next Step` are flagged for the generic verb `Run`; see the next row. |
| `story-name-captures-system-mechanic` | **Fail** (2) | `Run Action Across Practices` (line 168) and `Run Next Step` (line 190) hide the mechanic. Better: `Send Stage Action To Every Practice`, `Send Ticket's Next Step To Chat`. |
| `four-to-nine-children` | **Fail** (1) | `Tickets` (line 88) has 10 Stories. Split it, for example into creating and opening sessions (Add Backlog Item, Open Ticket Session, Activate, Close, Restrict) and changing a ticket (Move, Split, Archive, Write Handoff, Display Latest Handoff). |
| `story-scenarios-one-to-four` | Expected at this fidelity (40) | No Story has scenarios: this is the Discovery story map, and scenarios are the Specification fidelity (`stories-scenarios`), the ticket's next step. Some Stories carry acceptance criteria, which the counter does not count. These hits close when scenarios are written, not by editing the map. |
| `branch-on-mechanical-uniqueness` | Pass | Distinct mechanics are separate Stories (Move Ticket vs Mark Ticket Done In Stage vs Activate Ticket); shared mechanics sit as acceptance criteria (Move Ticket To Next/Previous Column). |
| `right-size-story-nodes` | Pass with one note | Stories are one interaction at one boundary. `Arrange Side Panel` folds four interactions (resize, expand, close, scroll) into criteria, which is right for display-only behaviour. |
| `behaviours-not-one-time-tasks` | Pass | Every Story is repeatable; no migrations or renames are on the map. |
| `story-map-links-to-markdown` | **Fail** (drawio) | Headings are at column 0 in the markdown. Not checked by the scanner: whether every drawio cell carries a `link` to its `story-map.md#…` anchor. The drawio reader loads only the epic cell (it reads cells in document order), so the links were not verified. |

**Also seen, outside these rules:** several Stories still describe the retired pane (`register.test`, the → arrow on a backlog card, the Archive and Switch to buttons). The board app no longer has them: the details buttons are now card icons, starting asks for a root, and Archive is gone from the page.

**To fix:** rename the five sub-epics and two Stories, split `Tickets`, update the Stories that describe the retired pane, and fix the markdown reader so `Observed:` lines count as evidence.
