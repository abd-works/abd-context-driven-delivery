# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-04 04:51:31 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 1
**Rules with graph hits:** 1
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

Evaluate the current context against this rule (evidence-distinguishes-observed-inferred-and-intended):

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\harness\kanban\.context\story-map.md#L54): SubEpic `Steer Ticket Sessions`: sub-epic 'Steer Ticket Sessions': 10 children (target 4-9)

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-one-to-four`

A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.

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

## Judgment — `harness/kanban/.context/story-map.md`

| Rule | Verdict |
|---|---|
| vocabulary-traces-to-domain-source | Pass |
| read-all-source-context-in-full | Pass |
| do-not-invent-requirements | Pass |
| evidence-distinguishes-observed-inferred-and-intended | **Fail** |
| verb-noun-format | **Fail** |
| story-name-captures-system-mechanic | **Fail** |
| four-to-nine-children | **Fail** (graph rule) |
| story-scenarios-one-to-four | Pass |
| branch-on-mechanical-uniqueness | **Fail** |
| right-size-story-nodes | Pass |
| behaviours-not-one-time-tasks | Pass |
| story-map-links-to-markdown | Pass |

### `evidence-distinguishes-observed-inferred-and-intended` — Fail
- story-map.md:86 `Archive Ticket`: "Observed: the Archive button calls `Ticket.archive`", but the app has no Archive button and `archive_ticket_story.test.py` says it is called as the `ticket.archive` tool.
- story-map.md:82 `Split Ticket Into Child Tickets`: labelled Observed while "No spec presses Split"; pressing Split is Inferred.
- story-map.md:32 `Arrange Board And Details` and story-map.md:172 `Display Violations Band`: a bare "Observed." with no source.

### `four-to-nine-children` — Fail
Graph rule: `Steer Ticket Sessions` (story-map.md:54) has 10 Stories, one over the band.

### `branch-on-mechanical-uniqueness` — Fail
story-map.md:178 `List Ticket Files` says "the folder mode of the files panel", which is the mechanic of `Browse Ticket Folder` (story-map.md:182). Either 178 means the list mode, or the two Stories are one mechanic.

### `story-name-captures-system-mechanic` — Fail
`View Files` (line 184) does not say which files; `Send Sketch Iterate Or Document` (line 148) names three commands instead of the one thing sent.

### `verb-noun-format` — Fail
Sub-epic `Display Board And Details For Repo` (line 20) names something the Board App does rather than a goal.

### Passes
Vocabulary follows `kanban-model.md`; sources are named; no invented interactions; Display Violations Band is now its own Board App Story; every Story is repeatable and links to its story file.
