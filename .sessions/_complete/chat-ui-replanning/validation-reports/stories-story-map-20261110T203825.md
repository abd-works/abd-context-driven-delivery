# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the saved graph of the session's folder (`.context/graph.json`, which exists only after `graph.load_working_copy` has run on that folder); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `space/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: C:/dev/abd-context-driven-delivery/harness/.context/stories/story-map.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-10 20:38:28 UTC
**Project:** harness
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\chat-ui-replanning\validation-reports\stories-story-map-20261110T203825.json`

**The session's graph also held, and practice-wide rules compared against:**
- `author-story-maps/author-story-changes-with-ai`
- `author-story-maps/save-and-share-changes`
- `author-story-maps/view-story-map`
- `build-design-canvas-screens/publish-and-release-a-canvas-version`
- `connect-sessions-across-channels-and-apps/check-work-in-generate`
- `connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui`
- `connect-sessions-across-channels-and-apps/read-graph-violations-in-chat-bar`
- `connect-sessions-across-channels-and-apps/read-graph-violations-on-board`
- `explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer`
- `explore-stories-in-story-ui/navigate-the-story-tree`
- `explore-stories-in-story-ui/play-stories-in-the-explorer`
- `explore-stories-in-story-ui/show-screen-frames-in-story-ui`
- `map-work-into-knowledge-graph/review-violations-in-graph-app`
- `move-work-forward-from-chat-bar/capture-session-knowledge`
- `move-work-forward-from-chat-bar/enter-cdd-commands-faster`
- `move-work-forward-from-chat-bar/guide-work-through-practices`
- `move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar`
- `move-work-forward-from-chat-bar/see-work-in-chat-bar`
- `move-work-forward-from-chat-bar/steer-sessions`
- `move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board`
- `move-work-forward-on-session-board/steer-ticket-sessions`

## Summary

**Total graph violations:** 17
**Rules with graph hits:** 4
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

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L407): SubEpic `Run Tickets Through Customized Workflow`: SubEpic 'Run Tickets Through Customized Workflow': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L413): Story `Run Work Type Flows`: Story 'Run Work Type Flows': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L545): Story `Comment On File Selection`: Story 'Comment On File Selection': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1379): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas": name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1811): Story `Comment On A Story Card`: Story 'Comment On A Story Card': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1827): Story `Comment On A Story In Story UI`: Story 'Comment On A Story In Story UI': name should start with a verb (got nominalisation).

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L413): Story `Run Work Type Flows`: Story 'Run Work Type Flows' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1379): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas" names a generic handler; use the system mechanic (e.g. 'Submit Order').

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, and restructure at 3 or fewer or 10 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L385): SubEpic `Customize Board Workflow`: sub-epic 'Customize Board Workflow': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L433): SubEpic `Show Board Quickly`: sub-epic 'Show Board Quickly': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L791): SubEpic `Capture Session Knowledge`: sub-epic 'Capture Session Knowledge': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1775): SubEpic `Read Graph Violations On Board`: sub-epic 'Read Graph Violations On Board': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1789): SubEpic `Read Graph Violations In Chat Bar`: sub-epic 'Read Graph Violations In Chat Bar': 3 children (target 4-9)

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-at-most-seven`

A story holds at most 7 code scenarios. More than 7 and the story is huge — split it, because one story should be one interaction a reader can test in a few examples. A story with no scenarios passes: its scenarios are simply not written yet.

Evaluate the current context against this rule (story-scenarios-at-most-seven):

### `branch-on-mechanical-uniqueness`

Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.

Evaluate the current context against this rule (branch-on-mechanical-uniqueness):

### `right-size-story-nodes`

Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.

Evaluate the current context against this rule (right-size-story-nodes):

### `behaviours-not-one-time-tasks`

Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L437): Story `Check Ticket Branches Once Per Board Build`: Story 'Check Ticket Branches Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L445): Story `Read Session File Once Per Board Build`: Story 'Read Session File Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1285): Story `Store Each Screenshot Once By Content Hash`: Story 'Store Each Screenshot Once By Content Hash' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/stories/story-map.md](C:\dev\abd-context-driven-delivery\harness\.context\stories\story-map.md#L1359): Story `Reattach A Screen Once Its Change Reaches Production`: Story 'Reattach A Screen Once Its Change Reaches Production' reads like a one-time task, not a repeatable behaviour.

Evaluate the current context against this rule (behaviours-not-one-time-tasks):

### `kebab-case-paths`

Name every epic, sub-epic, and story folder in lowercase kebab-case (`onboard-a-customer/`) and every story file in lowercase (`create_customer_story.test.ts`, `create-customer.story.shared.ts`), never CamelCase (`HandleRequest_story.test.ts`), because the folders mirror the story map and a reader finds a story's file from its name only when one case holds everywhere.

Evaluate the current context against this rule (kebab-case-paths):

### `story-map-links-to-markdown`

Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

Evaluate the current context against this rule (story-map-links-to-markdown):
