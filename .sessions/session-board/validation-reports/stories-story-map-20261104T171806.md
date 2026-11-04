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


# Graph rule validation

**Generated:** 2026-11-04 17:18:06 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 40
**Rules with graph hits:** 1
**AI rules in scope:** 11

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

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, and restructure at 3 or fewer or 10 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-one-to-four`

A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.

**Graph violations:** 40

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L22): Story `Open Board`: story 'Open Board': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L26): Story `Display Board`: story 'Display Board': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L30): Story `Arrange Board And Details`: story 'Arrange Board And Details': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L34): Story `Display Backlog Items As Tickets`: story 'Display Backlog Items As Tickets': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L38): Story `Display Ticket Card`: story 'Display Ticket Card': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L42): Story `Display Ticket Details`: story 'Display Ticket Details': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L46): Story `Set Stage WIP Limit`: story 'Set Stage WIP Limit': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L50): Story `Arrange Side Panel`: story 'Arrange Side Panel': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L54): Story `Restrict Actions To Active Session`: story 'Restrict Actions To Active Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L60): Story `Add Backlog Item`: story 'Add Backlog Item': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L64): Story `Open Ticket Session`: story 'Open Ticket Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L68): Story `Close Active Session`: story 'Close Active Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L72): Story `Move Ticket`: story 'Move Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L76): Story `Activate Ticket`: story 'Activate Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L80): Story `Split Ticket Into Child Tickets`: story 'Split Ticket Into Child Tickets': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L84): Story `Archive Ticket`: story 'Archive Ticket': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L88): Story `Write Ticket Handoff`: story 'Write Ticket Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L92): Story `Display Latest Handoff`: story 'Display Latest Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L98): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L102): Story `Open Practice Tile`: story 'Open Practice Tile': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L106): Story `Choose Ticket Practices`: story 'Choose Ticket Practices': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L110): Story `Send Action To Stage Practices`: story 'Send Action To Stage Practices': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L114): Story `Mark Ticket Done In Stage`: story 'Mark Ticket Done In Stage': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L118): Story `Add Active Ticket To System Prompt`: story 'Add Active Ticket To System Prompt': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L122): Story `Open Help`: story 'Open Help': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L126): Story `Send Next Fidelity Action`: story 'Send Next Fidelity Action': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L132): Story `Choose Action And Formats`: story 'Choose Action And Formats': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L136): Story `Resolve Fidelity Output Paths`: story 'Resolve Fidelity Output Paths': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L140): Story `Generate Fidelity Output`: story 'Generate Fidelity Output': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L144): Story `Render Fidelity Format`: story 'Render Fidelity Format': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L148): Story `Send Tile Action To Chat`: story 'Send Tile Action To Chat': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L154): Story `Validate Fidelity`: story 'Validate Fidelity': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L158): Story `Save Validation Report`: story 'Save Validation Report': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L162): Story `Open Validation Report`: story 'Open Validation Report': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L166): Story `Fix Report Violations`: story 'Fix Report Violations': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L170): Story `Display Violations Band`: story 'Display Violations Band': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L176): Story `List Ticket Files`: story 'List Ticket Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L180): Story `Browse Ticket Folder`: story 'Browse Ticket Folder': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L184): Story `View Fidelity Files`: story 'View Fidelity Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L188): Story `Review Fidelity`: story 'Review Fidelity': 0 scenarios (target 1-7)

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
