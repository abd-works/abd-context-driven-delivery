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

**Generated:** 2026-11-04 06:33:35 UTC
**Project:** chat-ui
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\cdd-chat-ui\edited-graph.json`

## Summary

**Total graph violations:** 20
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

**Graph violations:** 20

- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L22): Story `Display Server Health Mark`: story 'Display Server Health Mark': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L26): Story `Open Server Health Panel`: story 'Open Server Health Panel': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L30): Story `Reconnect CDD Server`: story 'Reconnect CDD Server': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L34): Story `Reinstall CDD Tools`: story 'Reinstall CDD Tools': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L40): Story `Display Stage Strip`: story 'Display Stage Strip': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L44): Story `Display Fidelity Progress`: story 'Display Fidelity Progress': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L48): Story `Display Session Card`: story 'Display Session Card': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L52): Story `Open Board`: story 'Open Board': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L58): Story `Create New Session`: story 'Create New Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L62): Story `Open Session`: story 'Open Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L66): Story `Write Session Handoff`: story 'Write Session Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L70): Story `Close Active Session`: story 'Close Active Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L76): Story `Invoke Next Fidelity Action`: story 'Invoke Next Fidelity Action': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L80): Story `Choose Fidelity Action`: story 'Choose Fidelity Action': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L84): Story `Display Stage Fidelities`: story 'Display Stage Fidelities': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L88): Story `Move Session To Next Stage`: story 'Move Session To Next Stage': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L94): Story `List Session Files`: story 'List Session Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L98): Story `View Fidelity Files`: story 'View Fidelity Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L102): Story `Browse Session Folder`: story 'Browse Session Folder': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [story-map.md](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\story-map.md#L106): Story `Review Fidelity`: story 'Review Fidelity': 0 scenarios (target 1-7)

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

## Judgment — `harness/chat-ui/story-map.md`

Passes: `vocabulary-traces-to-domain-source`, `read-all-source-context-in-full` (the health Stories name `server-health-view.tsx` and `server-health-client.ts`), `do-not-invent-requirements` (health Stories are Observed in chat-mod; placement left of the session name and the one-line panel are the person's requests), `verb-noun-format`, `story-name-captures-system-mechanic` (Run CDD Install renamed Reinstall CDD Tools after the previous run's graph hit), `four-to-nine-children` (five sub-epics of four Stories), `branch-on-mechanical-uniqueness`, `right-size-story-nodes`, `behaviours-not-one-time-tasks` (reinstall is repeatable whenever tools go missing), `story-map-links-to-markdown`.

### `story-scenarios-one-to-four` — Fail
- story-map.md:22 `Display Server Health Mark` and the 19 Stories after it: no Story has scenarios yet; the scenarios fidelity writes them.
