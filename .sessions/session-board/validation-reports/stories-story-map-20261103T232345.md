# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


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

No graph-rule hits were attached to this run (no `paths` or `graph` given), so every verdict below is AI judgment on the story map and the 40 story files it links.

| Rule | Verdict |
|---|---|
| vocabulary-traces-to-domain-source | Pass |
| read-all-source-context-in-full | Pass |
| do-not-invent-requirements | Pass |
| evidence-distinguishes-observed-inferred-and-intended | **Fail** |
| verb-noun-format | Warn |
| story-name-captures-system-mechanic | Warn |
| four-to-nine-children | Warn |
| story-scenarios-one-to-four | Pass |
| branch-on-mechanical-uniqueness | Pass |
| right-size-story-nodes | Warn |
| behaviours-not-one-time-tasks | Pass |
| story-map-links-to-markdown | Pass |

### `vocabulary-traces-to-domain-source` — Pass
Stories use the names in `kanban-model.md` and the code: ticket, session, stage, column, fidelity, practice, backlog item, validation report, WIP limit. The button labels (Run next, Fix, Fix all, Reviewed) match the board's labels.

### `read-all-source-context-in-full` — Pass
The header lists the sources (board.py, ticket.py, backlog_item.py, both specs, the app's specs and tests, register.ts, module-context, kanban-model, and the canvas at Version 72), and most Stories name the class, method, or view behind them.

### `do-not-invent-requirements` — Pass
Every Story and acceptance criterion traces to code, a spec, or a canvas comment. The only system-to-system Stories (Resolve Fidelity Output Paths, Save Validation Report) have a named caller, `Generate` and `Validate`.

### `evidence-distinguishes-observed-inferred-and-intended` — Fail
- story-map.md:141 `Archive Ticket` says "Observed: the Archive button calls `Ticket.archive`", but its scenario (`archive_ticket_story.test.py:15`) says "Called as the ticket.archive tool; the board app has no Archive button." The two disagree; one of them is wrong.
- story-map.md:41 `Arrange Board And Details` and story-map.md:247 `Satisfy Violations From Band` say only "Observed." with no source. Several acceptance criteria do the same (lines 34, 36, 37, 45, 46, 58–60, 69–71, 83–86, 104, 122, 123, 133, 159, 187, 188, 199, 273). The header points to `session-board-behavior.md` for spec signatures, which partly covers this, but the line itself names nothing.
- story-map.md:137 `Split Ticket Into Child Tickets` is labelled Observed while saying "No spec presses Split." By the header's own definition (Observed = code and specs do it), the pressing of Split is Inferred; the parts the specs do cover (the parent is recorded) are Observed. Say which is which.

### `verb-noun-format` — Fail
All names are base-form verb + noun. The sub-epic `Display Board And Details For Repo` (line 22) names something the Board App does, not a goal the Person is reaching; a goal such as "See Work On Session Board" fits the rule better. The other sub-epics (Steer Ticket Sessions, Guide Work Through Practices, Generate/Validate/Review Fidelity Outputs) name goals.

### `story-name-captures-system-mechanic` — Fail
Most Story names give the operation and the thing it acts on (Set Stage WIP Limit, Move Ticket, Save Validation Report, Send Action To Stage Practices). Weaker ones:
- `View Files` (line 263): "Files" does not say which files; the Story is about the fidelity's output files in format tabs. E.g. "View Fidelity Output Files".
- `Send Sketch Iterate Or Document` (line 223): names three commands joined by "Or" instead of the one thing being sent. E.g. "Send Exploration Action".
- `Arrange Board And Details` / `Arrange Side Panel` (lines 39, 77): "Arrange" is broad; the acceptance criteria show it means resize and expand. Acceptable, but "Resize ..." would be more exact.

### `four-to-nine-children` — Fail
Top epic 6, Display Board And Details For Repo 8, Guide Work Through Practices 8, Generate Fidelity Outputs 5, Validate Fidelity Outputs 5, Review Fidelity Outputs 4 — all inside the band. `Steer Ticket Sessions` has 10 Stories (lines 90–149): warn. Moving the handoff pair (Write Ticket Handoff, Display Latest Handoff) or the backlog Story elsewhere would bring it back inside the band.

### `story-scenarios-one-to-four` — Pass
Every linked story file has between 1 and 7 `scenario` blocks (fewest: Archive Ticket 1; Open Board and Render Fidelity Format 2). None has zero and none needs splitting.

### `branch-on-mechanical-uniqueness` — Pass
Separate mechanics have separate Stories (Generate, Render, Validate, Review; Move vs Mark Done In Stage). Send Sketch Iterate Or Document puts three commands that share one mechanic, filling and sending a command from a tile, in one Story, which is what the rule asks for.

### `right-size-story-nodes` — Fail
- story-map.md:61 `Show Active Ticket On Status Line` is an acceptance criterion of `Display Ticket Card`, but it happens at a different boundary: the chat's status line, through `statusOf` in `tools/chat-mod/hooks/register.ts`, not the board card. It is its own observable interaction, like `Add Active Ticket To System Prompt` (line 177), and belongs beside it as a Story.
- story-map.md:207 `Resolve Fidelity Output Paths` is an internal call made by `Generate` (`Session.fidelity_outputs`). It has its own spec and a caller, so it stands, but check whether it is a callee boundary in its own right or a step inside Generate Fidelity Output.

### `behaviours-not-one-time-tasks` — Pass
Every Story is a repeatable interaction. No renames, migrations, or repository chores are on the map.

### `story-map-links-to-markdown` — Pass
All 40 Story headings link to story files that exist. Headings are at column 0. Each story file links back with a `Map:` anchor. Epic headings carry no link, which is right since there is no separate file for them.

### Failures to fix
1. Archive Ticket: make the map and the scenario agree on whether the board has an Archive button (story-map.md:141 vs `archive_ticket_story.test.py:15`).
2. Split Ticket Into Child Tickets: label the unpressed Split as Inferred (story-map.md:137).
3. Bare "Observed." lines: name the source (story-map.md:41, 247, and the acceptance criteria listed above).
